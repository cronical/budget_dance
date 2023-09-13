#! /usr/bin/env python
'''reseal file opened by reveal'''
from dance.util.files import zip_up
filename='data/test_wb.xlsx'
zip_up(filename,'tmp')
print("OK, try to open file")