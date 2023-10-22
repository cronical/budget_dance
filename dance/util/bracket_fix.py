#! /usr/bin/env python
'''Take the IRS format of tax bracket and format it for inclusion in the tax table

# See https://www.irs.gov/pub/irs-pdf/i1040gi.pdf
# Section called YYYY Tax Computation Worksheet - Line 16
# in 2022 on page 75

# CNBC has version earlier than IRS
# https://www.cnbc.com/2022/10/19/irs-here-are-the-new-income-tax-brackets-for-2023.html

# See https://portal.ct.gov/-/media/DRS/Forms/2022/Income/CT-1040-TCS_1222.pdf
# Table B Initial Tax Calculation for 2022 Taxable Year


Note the file should be unicode since it has an em-dash in the first column
'''

import argparse
import os.path
import pandas as pd
import pyperclip

def fix_punc(dollar):
  digits=list(dollar)
  digits=[d for d in digits if not d in ['$',',',' ']]
  return float(''.join(digits))
def subtract_table(df,year):
  '''Convert the plus style to the subtract style and adds the year column'''
  srows=[]
  fields=df.columns
  assert 2==len(fields),'Oops, expected two columns'
  for _,row in df.iterrows():      
    ti=row[fields[0]]
    if 'or less' in ti: # CNBC version
      ti="$0 to "+ti.split(' ')[0]
    digits=ti.split(' ')[0]# will include a comma and a $ sign
    lower=max(0,fix_punc(digits)-1)
    tax_formula=row[fields[1]].split('%')
    if len(tax_formula[1]) == 0:
      rate=float(tax_formula[0])/100
      subtr=0
    else:
      if '+' in tax_formula:
        cp=tax_formula[0].split('+')
      else:
        cp=tax_formula[0].split('plus')
      if len(cp)==1:
        cp=['0']+cp
      rate=float(cp[1])/100
      base=fix_punc(cp[0])
      subtr=(rate * lower) - base
    srows+=[[year,lower,rate,subtr]]
  s_df=pd.DataFrame(data=srows,columns='Year,Range,Rate,Subtract'.split(','))
  return s_df
  #print(f'{lower},{rate:.2f},{subtr}')

def main():
  description ='Take the IRS format of tax bracket as a comma separated file and format it for inclusion in the tax table. '
  parser = argparse.ArgumentParser(description =description)
  parser.add_argument('file_name', nargs=1, help='Prefix file with year YYYY_ or provide -y')
  parser.add_argument('-y','--year',type=int,help='provide tax year')
  
  args=parser.parse_args()
  filename=args.file_name[0]
  if args.year is None:
    fn=os.path.split(filename)[1]
    y = fn.split('_')[0]
    if not y.isnumeric():
      raise ValueError('First part of filename is not numeric and no --year provided.')
    else:
      year=int(y)
  else:
    year=args.year
  df=pd.read_csv(filename,sep=',',skiprows=0)
  s_df=subtract_table(df,year)
  print (s_df.to_string(index=False))
  to_copy=s_df.to_string(index=False,justify='left',header=False)
  pyperclip.copy(to_copy)
  print ('The above numbers copied into paste buffer.\nPaste into the table')

if __name__=='__main__':
  main()
  