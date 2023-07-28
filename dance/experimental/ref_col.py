'''Use regex to create column reference at build time to avoid the two evils
of poor performance and dependency sprawl.
'''
import re

f='CHOOSECOLS(tbl_iande[#Data],XMATCH(this_col_name(),tbl_iande[#Headers]))' # current method has dependency on all of tbl_iande

n = 'tbl_iande[Y1234]' # new method formula fragment to replace above. At build time Y1234 gets replaced with the current column header
m= 'tbl_balances[Y1234-2]'
cols='Y2018	Y2019	Y2020	Y2021	Y2022	Y2023	Y2024	Y2025	Y2026'.split('\t')

pat1=r'\[Y[0-9]{4}\]'
pat2=re.compile(r'\[Y[0-9]{4}(-[0-9])\]')

for f in (n,m):
  for col in cols:
    a=re.sub(pat1,'[%s]'%col,f)
    m=pat2.search(a)
    if m is not None:
      g=m.group(1)
      offset=int(g)
      col2="[Y%d]"%(offset+int(col[1:]))
      a=re.sub(pat2,col2,a)
    print (a)
    pass

