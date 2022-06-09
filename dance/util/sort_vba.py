#!/usr/bin/env python
'''takes an input file with vba source code and puts the functions and subs into alpha order and writes to the output file'''
import argparse

def process(input,output):
  '''
  Read and process the input stream and send it to the output.
  The in and out files are already open - they are of type _io.TextIOWrapper
  They are closed at the end.
  '''
  keys=['Function','Sub']
  in_header=True
  in_item=False
  header=[]
  code_bits=dict()
  for line in input.readlines():
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
    output.write(line)
  for name,val in sorted_code_bits.items():
    print(name)
    output.write('\n')
    for line in val['code_rows']:
      output.write(line)
  for fn in input,output:
    fn.close()

  

if __name__ == "__main__":
  # execute only if run as a script
  parser = argparse.ArgumentParser(description ="takes an input file with vba source code and puts the functions and subs into alpha order and writes to the output file")
  parser.add_argument('in_file',type=argparse.FileType('r'), help='provide the name of the input file')
  parser.add_argument('out_file', type=argparse.FileType('w',encoding='UTF-8'),help='provide the name of the output file')
  args=parser.parse_args()
  process(args.in_file,args.out_file)