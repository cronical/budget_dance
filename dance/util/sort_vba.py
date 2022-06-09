#!/usr/bin/env python
'''takes an input file with vba source code and puts the functions and subs into alpha order and writes to the output file'''
import argparse
from os import path

def existing_file(fn):
  if path.exists(fn):
    return fn
  return None

def process(in_file,out_file):
  try:
    out=open(out_file,'w')
  except Exception:
    print(f'Cannot open output file {out_file}')
  with open(in_file,'r') as input:
    lines=input.readlines()
  keys=['Function','Sub']
  in_header=True
  in_item=False
  header=[]
  code_bits=dict()
  for line in lines:
    if in_item:
      code_rows+=[line]
      if line.strip().startswith('End'):
        code_bits[name]={'code_type':code_type,'code_rows':code_rows}
        in_item=False
    else:
      if any([line.strip().startswith(k)for k in keys]):
        in_header=False
        in_item=True
        code_type,rest=line.strip().split(' ',maxsplit=1)
        name,_=rest.split('(',maxsplit=1)
        code_rows=[line.strip()]
    if in_header:
      header+=line
  sorted_code_bits={key: val for key, val in sorted(code_bits.items(), key = lambda ele: ele[0].lower())}
  for line in header:
    out.write(line)
  for name,val in sorted_code_bits.items():
    print(name)
    out.write('\n')
    for line in val['code_rows']:
      out.write(line)
  out.close()

  

if __name__ == "__main__":
  # execute only if run as a script
  parser = argparse.ArgumentParser(description ="takes an input file with vba source code and puts the functions and subs into alpha order and writes to the output file")
  parser.add_argument('in_file', help='provide the name of the input file',type=existing_file)
  parser.add_argument('out_file', help='provide the name of the output file')
  args=parser.parse_args()
  process(args.in_file,args.out_file)