'''experiment with defined names'''
from openpyxl import load_workbook
from openpyxl.workbook.defined_name import DefinedName
from dance.util.xl_formulas import prepare_formula

wb=load_workbook('data/test_wb.xlsm',keep_vba=True)
dns=wb.defined_names
dob=dns['DOB']
f='=LAMBDA(a,b,a*b)'
f=prepare_formula(f)
f=f[1:]
d=DefinedName("XYZ",comment='test lambda',attr_text=f,)
wb.defined_names.add(d)

wb.save("data/dn_book.xlsm") # file cannot be opened by excel - doc seems to assume the reference is to a range.
# saving as xlsx gets
# The file 'dn_book.xlsx' is a macro-free file, but contains macro-enabled content.

pass