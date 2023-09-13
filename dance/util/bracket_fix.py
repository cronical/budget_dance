#! /usr/bin/env python
'''Take the IRS format of tax bracket and format it for inclusion in the test_wb.xlsx tax table

# See https://www.irs.gov/pub/irs-pdf/i1040gi.pdf
# Section called YYYY Tax Computation Worksheet - Line 16
# in 2022 on page 75

# See https://portal.ct.gov/-/media/DRS/Forms/2022/Income/CT-1040-TCS_1222.pdf
# Table B Initial Tax Calculation for 2022 Taxable Year


Note the file should be unicode since it has an em-dash in the first column
'''

import argparse
import pandas as pd
def main():
  parser = argparse.ArgumentParser(description ='Take the IRS format of tax bracket as a comma separated file and format it for inclusion in the test_wb.xlsx tax table. ')
  parser.add_argument('file_name', nargs=1)
  args=parser.parse_args()

  filename=args.file_name[0]
  df=pd.read_csv(filename,sep=',',skiprows=0)

  def fix_punc(dollar):
    digits=list(dollar)
    digits=[d for d in digits if not d in ['$',',',' ']]
    return float(''.join(digits))

  for _,row in df.iterrows():
    ti=row['Taxable Income']
    digits=ti.split(' ')[0]# will include a comma and a $ sign
    lower=max(0,fix_punc(digits)-1)
    tr=row['Tax Rate'].split('%')
    if len(tr[1]) == 0:
      rate=float(tr[0])/100
      subtr=0
    else:
      cp=tr[0].split('+')
      rate=float(cp[1])/100
      base=fix_punc(cp[0])
      subtr=(rate * lower) - base
    print(f'{lower},{rate:.2f},{subtr}')
  print ('Copy the above numbers into the table and add the year')

if __name__=='__main__':
  main()
  