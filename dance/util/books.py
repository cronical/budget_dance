'''Work book oriented utilities'''
from dance.util.logs import get_logger

def fresh_sheet(wb,sheet_name,tab_color='58BD2D'):
  '''Create or refresh a worksheet in a workbook.

  Removes the named sheet (if it exists) from the work book and created a fresh one at the same location (or at the end)
  If not already existing will create the new sheet at the end. Copies tab color if the sheet already exists.

  args:
    wb: An openpyxl workbook
    sheet_name: The name of the worksheet
    tab_color: An RGB color as a 6 character hex string. Only used if the worksheet does not already exist

  Returns: the workbook
  '''
  logger=get_logger(__file__)
  ix=len(wb.sheetnames)
  if sheet_name in wb.sheetnames:
    ix= wb.sheetnames.index(sheet_name)
    ws = wb[sheet_name]
    tab_color=ws.sheet_properties.tabColor
    wb.remove(ws)
    logger.info('deleted worksheet {}'.format(sheet_name))
  ws=wb.create_sheet(sheet_name,ix)
  logger.info('created worksheet {}'.format(sheet_name))
  ws.sheet_properties.tabColor=tab_color
  return wb
  