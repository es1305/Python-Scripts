#!/usr/bin/python3

import xml.etree.ElementTree as ET
import subprocess
import requests
import time
from urllib.parse import quote_plus

# Configuration
ADMIN = "admin"
PASSWORD = "PASSWORD_HERE"
BASE_URL = "http://127.0.0.1:8000"

STATIONS_STATIC = {
    "mayak": ("Радио «Маяк» Барнаул", "Тел.: (3852) 68-50-10"),
    "russia": ("Радио «Россия» Барнаул", "Тел.: (3852) 68-50-10"),
    "vesti": ("Радио «Вести ФМ» Барнаул", "Тел.: (3852) 68-50-10"),
}

STOP_WORDS = ['$', 'промо', 'джингл', 'новости', 'погода', 'блок', 'реклама']
last_song = "" # Variable to track track changes

def get_xml_from_smb():
    cmd = ['smbclient', '-d', '0', '-A', '/root/creds/.smbcredentials', '//fm-air-11/xml', '-c', 'get cur_playing.xml -']
    try:
        result = subprocess.run(cmd, capture_output=True, text=False, timeout=5)
        return result.stdout
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] [!] SMB error: {e}")
        return None

def update_icecast(mount, artist, title):
    try:
        params = {
            'mount': f"/{mount}",
            'mode': 'updinfo',
            'artist': artist,
            'title': title
        }
        r = requests.get(f"{BASE_URL}/admin/metadata", params=params, auth=(ADMIN, PASSWORD), timeout=3)
        if r.status_code == 200:
            # Log time and what was sent to air
            print(f"[{time.strftime('%H:%M:%S')}] [OK] {mount} -> {artist} - {title}")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] [!] Icecast error ({mount}): {e}")

def process_heartfm():
    global last_song
    xml_data = get_xml_from_smb()

    try:
        root = ET.fromstring(xml_data)
        playing_elem = root.find(".//ELEM[@STATUS='playing']")

        if playing_elem is not None:
            artist = (playing_elem.findtext('ARTIST') or "").strip().replace("''", "")
            name = (playing_elem.findtext('NAME') or "").strip().replace("''", "")

            is_promo = any(word in artist.lower() for word in STOP_WORDS)

            if not artist or not name or is_promo:
                cur_art, cur_tit = "Радио «Heart FM» Барнаул", "Тел.: (3852) 55-10-59"
            else:
                cur_art, cur_tit = artist, name
        else:
            cur_art, cur_tit = "Радио «Heart FM» Барнаул", "Тел.: (3852) 55-10-59"

        # Check for track change
        current_combined = f"{cur_art} - {cur_tit}"
        if current_combined != last_song:
            update_icecast("heartfm", cur_art, cur_tit)
            last_song = current_combined

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] [!] Parsing error: {e}")

# --- Main loop ---
print(f"=== Service started {time.strftime('%Y-%m-%d %H:%M:%S')} ===")

while True:
    # Perform 30 Heart FM checks, each with a 2 second pause
    for _ in range(30):
        process_heartfm()
        time.sleep(2)  # Pause should ALWAYS be here

    # And only after 30 checks (approximately after one minute) update static stations
    for mount, (artist, title) in STATIONS_STATIC.items():
        update_icecast(mount, artist, title)

