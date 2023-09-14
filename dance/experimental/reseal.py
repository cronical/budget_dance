#! /usr/bin/env python
'''reseal file opened by reveal'''
from dance.util.files import read_config
from dance.util.files import zip_up
filename=read_config()['workbook']
zip_up(filename,'tmp')
print("OK, try to open file")