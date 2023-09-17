'''Experiment with tables trying to find link to theme colors'''

from openpyxl import open
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Side,Color

from dance.util.files import read_config

fn=read_config()['workbook']
wb=open(fn)
for ws in wb.sheetnames:
  ws=wb[ws]
  for table in ws.tables.values():
    print (table.name)
    tsi=table.tableStyleInfo
    side=Side(color=Color())
    pass
