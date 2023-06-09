'''Manually set cm attribute'''
from os.path import exists
from shutil import rmtree
import zipfile
from dance.setup.create_wb import zip_up

filename='data/test_wb.xlsm'
if exists('./tmp'):
  rmtree('./tmp')
with zipfile.ZipFile(filename, 'r') as z:
  z.extractall('./tmp/')
print("edit files in ./tmp")
pass
zip_up(filename,'tmp')
print("OK, try to open file")