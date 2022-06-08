#!/usr/bin/env python
'''extract the vba from the excel file so it can be stored in source control'''

import os
from shutil import rmtree
import zipfile
from oledump import FindAll, SearchAndDecompress
from logs import get_logger

def main():
  logger=get_logger(__file__)

  logger.info(f'current working directory is {os.getcwd()}')

  with zipfile.ZipFile('data/fcast.xlsm', 'r') as z:
    z.extractall('./tmp/')
  filename='./tmp/vbaProject'
  if os.path.exists(filename):
    rmtree(filename)
  filename='./tmp/xl/vbaProject.bin'
  rc=os.system('unar -q -o tmp/ '+filename)
  assert rc == 0, 'could not unarchive '+filename

  filename='./tmp/vbaProject/VBA/Module1'
  with open(filename, 'rb') as f:
    data= f.read()

  positions = FindAll(data, b'\x00Attribut\x00e ')
  vba = ''
  for position in positions:
    result = SearchAndDecompress(data[position - 3:], skipAttributes=False) + '\n\n'
    if result is not None:
      vba += result
  assert vba != '','was not able to get vba'

  filename='./vba/fcast_vba.txt'
  with open(filename,'w') as f:
    f.write(vba)
  logger.info(f'wrote {len(vba)} characters to {filename}')

  filename='./docs/fcast_vba.md'
  with open(filename,'w') as f:
    f.write(f'```vb\n{vba}\n```')
  logger.info(f'wrote markdown version with code formatting to {filename}')

  #cleanup
  tmp='./tmp'
  rmtree(tmp)
  os.mkdir(tmp)
  logger.info(f'cleaned up {tmp}')

if __name__=="__main__":
  main()