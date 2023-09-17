'''functions for user interface formatting
'''
from openpyxl.styles.colors import Color

def tab_color(config_color):
  '''Convert the config color to openpyxl Color
  config_color is either
   int, indicating the index into the the theme color, or
   str, a 6 letter rgb code
  '''
  # <sheetPr>
  #  <tabColor rgb="FF4FA3DB"/>
  # </sheetPr>
  # Want to generate:
  # <sheetPr>
  #  <tabColor theme="3"/>
  # </sheetPr>
  # note tints are used for the variants. 60% in the UI translates to:
  # <tabColor theme="3" tint="0.59999389629810485"/>
  # use: int VALUE
  #  tabColor=openpyxl.styles.colors.Color(theme=VALUE, type='theme')
  # 4FA3DB,BDAE2D,910DBD,58BD2D,BD710D,"7E0505"

  if isinstance(config_color,int):
    return Color(theme=config_color, type='theme')
  if isinstance(config_color,str):
    return Color(rgb=config_color,type="rgb")
  else:
    raise ValueError("Defined color is neither int nor str")