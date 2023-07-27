#! /usr/bin/env python
'''reseal file opened by reveal'''
from dance.util.files import zip_up
filename='data/test_wb.xlsm'
zip_up(filename,'tmp')
print("OK, try to open file")