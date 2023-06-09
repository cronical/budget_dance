'''Discover logic to set array formula'''

from dance.util.tables import load_workbook

source='data/test_wb.xlsm'
table_name='tbl_transfers_plan'
ws_name='transfers_plan'

wb = load_workbook(filename = source, read_only=False, keep_vba=True,data_only=True)
ws=wb[ws_name]
for i in range(3,25):
    ws['F'+str(i)]= 'cat'
#wb.save(source)
#print('saved values')
c=ws['f3']

wb = load_workbook(filename = source, read_only=False, keep_vba=True)
ws=wb[ws_name]

formula= '=FILTER(tbl_accounts[Account],tbl_accounts[Active]=1)'

# seems to need the prefixes - otherwise excel complains and strips out formula
formula=formula.replace('FILTER','_xlfn._xlws.FILTER')

# ws['F3']=formula
ws['a6']='junk'

# if the size of ref is less than the size of the result of filter, it gets truncated.
# if its is greater then its filled with #N/A
# this appears to work but it does wrap the visible formula with curly braces
ws.formula_attributes['F3']={'t':'array','ref': 'F3:F24'}

# what if formula is manually entered:
#       <c r="F3" s="13" t="str" cm="1">
#       <f t="array" ref="F3:F24">_xlfn._xlws.FILTER(tbl_accounts[Account],tbl_accounts[Active]=1)</f>
#       <v>Bank Accounts</v>
#     </c>

# created by code resulting in curly braces
#       <c r="F3" s="13">
#        <f t="array" ref="F3:F24">_xlfn._xlws.FILTER(tbl_accounts[Account],tbl_accounts[Active]=1)</f>
#        <v></v>
#      </c>

wb.save(source)
print('saved formula')