#!/usr/bin/env python
'''takes an input file with vba source code and puts the functions and subs into alpha order and writes to the output file'''
import argparse

def process(input,output,doc_file=None):
  '''
  Read and process the input stream and send it to the output. If doc_file is given a markdown file is also created.
  The arguments are files that are already open. - they are of type _io.TextIOWrapper
  They are closed at the end.
  '''
  keys=['Function','Sub']
  in_header=True
  in_item=False
  in_doc_string=False
  header=[]
  code_bits=dict()
  for line in input.readlines():
    if in_item:
      item_line_number+=1
      if line.strip().startswith("'"):
        if item_line_number==1: 
          in_doc_string=True
      else:
        in_doc_string=False
      if in_doc_string:
        doc_strings+=[line.strip()[1:]+'\n']
      else:
        code_rows+=[line]
      if line.strip().startswith('End '+code_type):
        code_bits[name]={'signature':signature,'code_type':code_type,'doc_strings':doc_strings,'code_rows':code_rows}
        in_item=False
    else:
      if any([line.strip().startswith(k)for k in keys]):
        in_header=False
        in_item=True
        item_line_number=0
        code_type,rest=line.strip().split(' ',maxsplit=1)
        name,_=rest.split('(',maxsplit=1)
        signature=line.strip()+'\n'
        code_rows=[]
        doc_strings=[]
    if in_header:
      header+=[line]
  sorted_code_bits={key: val for key, val in sorted(code_bits.items(), key = lambda ele: ele[0].lower())}
  for line in header:
    output.write(line)
  for name,val in sorted_code_bits.items():
    print(name)
    output.write('\n')
    output.write(val['signature'])
    for line in val['doc_strings']:
      output.write("'"+line)
    for line in val['code_rows']:
      output.write(line)
  for fn in input,output:
    fn.close()
  if doc_file:
    doc_file.write("# VBA Code Summary\n\n")
    doc_file.write("|Function or Sub|Signature and info|\n")
    doc_file.write("|---|---|\n")
    for name,val in sorted_code_bits.items():
      doc_file.write(f'|{name}|{val["signature"].strip()}|\n')
      txt='. '.join([ds.strip().capitalize() for ds in val['doc_strings']])
      doc_file.write(f'||{txt}|\n')
    doc_file.close()


  

if __name__ == "__main__":
  # execute only if run as a script
  parser = argparse.ArgumentParser(description ="takes an input file with vba source code and puts the functions and subs into alpha order and writes to the output file")
  parser.add_argument('in_file',type=argparse.FileType('r'), help='provide the name of the input file')
  parser.add_argument('out_file', type=argparse.FileType('w',encoding='UTF-8'),help='provide the name of the output file')
  parser.add_argument('-d','--doc_file', type=argparse.FileType('w',encoding='UTF-8'),help='provide the name of the documentation file')
  args=parser.parse_args()
  doc_file=None
  if args.doc_file:
    doc_file=args.doc_file
  process(args.in_file,args.out_file,doc_file)