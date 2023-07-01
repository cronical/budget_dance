#! /usr/bin/env python
'''Translate a simple get_val formula to an XLOOKUP formula
For use in revising setup.yaml to allow Excel to handle dependencies'''

import pyperclip
import re
from dance.util.files import read_config
def unquote(text):
    '''remove any outside quotes'''
    m=re.search('^"(.*)"$',text)
    if m is None:
        return text
    return m.group(1)

def translate(formula):
    '''input a simple get_val formula
    returns XLOOKUP formula or None'''
    matches=pat.search(formula)
    if matches is None:
        print('Not matching get_val. Skipping: ' + formula)
        return None
    groups=matches.groups()
    start=groups[0].replace('get_val','XLOOKUP')
    end=groups[2]
    if groups is None:
        print('No matching groups. Skipping: ' + formula)
        return None
    args=groups[1].split(',')
    a0=args[0]
    table=unquote(args[1])
    if not table in table_keys:
        print('table not defined: '+ table)
        return None
    a1='%s[%s]'%(table,table_keys[table])
    if 'INDIRECT' not in args[2]:
        if '(' in args[2]:
            a2='INDIRECT("%s["&%s&"]")'% (table,args[2])
        else:
            unq = unquote(args[2])
            a2='%s[%s]'% (table,unq)
    r='%s(%s,%s,%s,0)%s'%(start,a0,a1,a2,end)
    return r

pat=re.compile('(^.*get_val)\((.*)\)(.*$)')

config=read_config()
table_keys={'tbl_iande':'Key',"tbl_bank_sel_invest":"Account"}
for _,sheet in config['sheets'].items():
    for table in sheet['tables']:
        table_keys[table['name']]=table['columns'][0]['name']



while True:
    formula=input('Formula (or empty to exit): ')  
    if len(formula)==0:
        exit()
    revised=translate(formula)
    if revised is None:
        exit()
    pyperclip.copy(revised)
    print('Copied to clipboard: '+revised)      



        