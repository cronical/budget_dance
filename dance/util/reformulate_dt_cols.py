#! /usr/bin/env python
'''Translate a XLOOKUP formula to a design time approach which sets directly access column name
For use in revising setup.yaml to allow Excel to handle dependencies'''

import pyperclip
import re
from dance.util.files import read_config
# look for this pattern
sample='=XLOOKUP([@AcctName],tbl_transfers_actl[Account],CHOOSECOLS(tbl_transfers_actl[#Data],XMATCH(this_col_name(),tbl_transfers_actl[#Headers])))'
#pat=re.compile('(^.*get_val)\((.*)\)(.*$)')
pat=r'^.*(CHOOSECOLS\((tbl_[0-9a-z_]*)\[#Data\],XMATCH\(this_col_name\(\),(tbl_[0-9a-z_]*)\[#Headers\]\)\)).*$'
pat=re.compile(pat)

config=read_config()
table_keys={'tbl_iande':'Key',"tbl_bank_sel_invest":"Account"}
for _,sheet in config['sheets'].items():
    for table in sheet['tables']:
        table_keys[table['name']]=table['columns'][0]['name']


def unquote(text):
    '''remove any outside quotes'''
    m=re.search('^"(.*)"$',text)
    if m is None:
        return text
    return m.group(1)

def translate(formula):
    '''input a simple get_val formula
    replaces certain XLOOKUP phrases in formula or None'''
    matches=pat.search(formula)
    if matches is None:
        print('Not matching XLOOKUP criteria. Skipping: ' + formula)
        return None
    groups=matches.groups()
    if groups is None:
        print('No matching groups. Skipping: ' + formula)
        return None
    assert len(groups)==3, 'Expected 3 groups, got %d'% (len(groups))
    assert groups[1]==groups[2],'Table names do not match: %s != %s'%(groups[1],groups[2])
    if not groups[1] in table_keys:
        print('table not defined: '+ groups[1])
        return None
    old=groups[0]
    new=groups[1]+'[Y1234]'
    r=formula.replace(old,new)
    return r

while True:
    formula=input('Formula (or empty to exit): ')  
    if len(formula)==0:
        exit()
    revised=translate(formula)
    if revised is None:
        exit()
    pyperclip.copy(revised)
    print('Copied to clipboard: '+revised)      



        