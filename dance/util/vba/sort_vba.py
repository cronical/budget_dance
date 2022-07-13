#!/usr/bin/env python
'''takes an input file with vba source code and puts the functions and subs into alpha order and writes to the output file'''
import argparse
from dance.util.logs import get_logger

def process(input,output,index_file,sorted_file):
  '''
  Read and process the input stream and send it to the output. Create index and full text markdown files for documentation.
  The arguments are files that are already open. - they are of type _io.TextIOWrapper
  They are closed at the end.
  '''

  logger=get_logger(__file__)
  keys=['Function','Sub']

  # some flags to keep track of which type of line we are on
  in_header=True
  in_item=False
  in_doc_string=False

  # items to build up
  header=[]
  code_bits=dict()

  # run through the source lines
  for line in input.readlines():

    # once we are in an item (sub or function), accumulate rows into lists until we get an "End"
    if in_item:
      item_line_number+=1
      if line.strip().startswith('\''):
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
      # if we are in a sub or function then figure out the name and signature and set up new lists for code and doc strings
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

  logger.info('read {} header rows and {} functions or subs'.format(len(header),len(code_bits)))
  # put in alpha order by code item name
  sorted_code_bits={key: val for key, val in sorted(code_bits.items(), key = lambda ele: ele[0].lower())}

  def double_write(txt):
    '''write the sorted bits to both the output and marked down'''
    output.write(txt)
    sorted_file.write(txt)

  # start the output
  sorted_file.write('# VBA Code\n``` vbscript\n')
  for line in header:
    double_write(line)
  for name,val in sorted_code_bits.items():
    double_write('\n')
    double_write(val['signature'])
    for line in val['doc_strings']:
      double_write("'"+line)
    for line in val['code_rows']:
      double_write(line)
  sorted_file.write('```\n')
  for fn in input,output,sorted_file:
    fn.close()
  logger.info('Wrote sorted output to {}'.format(output.name))
  logger.info('Wrote sorted output as markdown to {}'.format(sorted_file.name))
  index_file.write('# VBA Code Summary\n\n')
  index_file.write('|Function or Sub|Signature and info|\n')
  index_file.write('|---|---|\n')
  for name,val in sorted_code_bits.items():
    signa=val['signature'].strip()
    index_file.write(f'|{name}|{signa}|\n')
    txt='. '.join([ds.strip().capitalize() for ds in val['doc_strings']])
    index_file.write(f'||{txt}|\n')
  index_file.close()
  logger.info('Wrote index to {}'.format(index_file.name))



if __name__ == '__main__':
  # execute only if run as a script
  parser = argparse.ArgumentParser(description ='takes an input file with vba source code and puts the functions and subs into alpha order and writes to the output file')
  parser.add_argument('-i','--in_file',type=argparse.FileType('r'), default='vba/fcast.vb',help='provide the name of the input file')
  parser.add_argument('-o','--out_file', type=argparse.FileType('w',encoding='UTF-8'),default='vba/fcast_sorted.vb',help='provide the name of the output file')
  parser.add_argument('-x','--index_file', type=argparse.FileType('w',encoding='UTF-8'),default='docs/vba_index.md',help='provide the name of the index documentation file')
  parser.add_argument('-s','--sorted_file', type=argparse.FileType('w',encoding='UTF-8'),default='docs/vba_sorted.md',help='provide the name of the sorted code documentation file')
  args=parser.parse_args()
  process(args.in_file,args.out_file,args.index_file,args.sorted_file)
