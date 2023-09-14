'''TODO DELETE THIS FILE. experiment with defined names'''
from openpyxl import load_workbook
from openpyxl.workbook.defined_name import DefinedName
from dance.util.files import read_config
from dance.util.xl_formulas import prepare_formula

config=read_config()
wb=load_workbook(config['workbook'])
dns=wb.defined_names
for dn in dns:
    print(dns[dn])
dob=dns['DOB']
f='=LAMBDA(a,b,a*b)'
f=prepare_formula(f)
f=f[1:]
d=DefinedName("XYZ",comment='test lambda',attr_text=f,)
wb.defined_names.add(d)

wb.save("data/dn_book.xlsx") 
# saving as xlsx gets
# The file 'dn_book.xlsx' is a macro-free file, but contains macro-enabled content.

pass