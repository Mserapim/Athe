PORTRAIT = 1
LANDSCAPE = 2

OPTIONS_REPORT = {
    "--footer-right": "Página: [page]/[topage]",
    "--footer-font-size": "9",
    "--header-font-size": "10",
    "--footer-spacing": "12",
    "--margin-top": "10mm",
    "--margin-bottom": "25mm",
    "--margin-left": "15mm",
    "--margin-right": "15mm",
    "--footer-line": "",
    "--enable-local-file-access": "",
}

STYLE_HEAD_ROW = """
    align:
      wrap off,
      vert center,
      horiz center;
    borders:
      left THIN,
      right THIN,
      top THIN,
      bottom THIN;
    font:
      name Arial,
      bold on,
      colour_index gray80,
      height 0xA0;
    pattern:
      pattern solid,
      fore-colour 0x16;  
"""

STYLE_DATA_ROW = """
    align:
      wrap on,
      vert center,
      horiz left;
    font:
      name Arial,
      bold off,
      height 0XA0;
    borders:
      left THIN,
      right THIN,
      top THIN,
      bottom THIN;
"""
