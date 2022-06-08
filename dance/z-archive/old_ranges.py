from openpyxl import Workbook
from openpyxl import load_workbook

source='long-term-plan-2020.xlsm'
wb=load_workbook(source)
dn=[d for d in wb.defined_names.definedName]
names=[d.name for d in dn]
locn=[d.attr_text for d in dn]
nl=zip(names,locn)

with open('ranges.tsv','w') as f:
  for rw in nl:
    if -1==rw[0].find('Z_9'):
      f.write('{}\t{}\n'.format(rw[0],rw[1]))

