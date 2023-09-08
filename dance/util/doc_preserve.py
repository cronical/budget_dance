#! /usr/bin/env python
'''Get the table items in concerns from config file as markdown'''
from dance.util.files import read_config
concerns=['data','preserve']
with open("docs/preserve.md",mode='w') as f:
  f.write('# Preserve definitions\n\n')
  config=read_config()
  for _,sheet in config['sheets'].items():
    for table in sheet['tables']:
      tn=table['name'].replace('tbl_','Table: ')
      f.write('## %s\n\n'%tn)
      for concern in concerns:
        f.write('### %s\n\n'%concern)
        if concern in table:
          kv=table[concern]
          f.write('|Key|Value|\n|---|---|\n')
          for k,v in kv.items():
            if isinstance(v,list):
              v=', '.join(v)
            f.write('|%s|%s|\n'%(k,v))
        else:
          f.write('No %s key.\n'%concern)
        f.write('\n\n')
          

