<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="utf-8" indent="yes"/>
<xsl:template match="/">
<html>
  <head>
  </head>
  <body>
    <h2>Погода</h2>
      <xsl:for-each select="//channel/item">
        <h4><xsl:value-of select="title"/></h4>
        <p><xsl:value-of select="description"/></p>
      </xsl:for-each>
  </body>
</html>
</xsl:template>
</xsl:stylesheet>
