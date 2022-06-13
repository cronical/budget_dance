#!/usr/bin/env python
'''extract the vba from the excel file so it can be stored in source control
:requires: the unarchiver command line utility, unar to handle the OLE compression
'''

import os
from shutil import rmtree, copy2
import zipfile
from oledump import FindAll, SearchAndDecompress
from logs import get_logger

def main():
  '''Pulls out certain components from the Excel file'''
  logger=get_logger(__file__)
  logger.info(f'current working directory is {os.getcwd()}')

  with zipfile.ZipFile('data/fcast.xlsm', 'r') as z:
    z.extractall('./tmp/')

  #make sure the vba project is not already there
  filename='./tmp/vbaProject'
  if os.path.exists(filename):
    rmtree(filename)

  # In addition to the vba project (which is in an OLE2 format)
  # relationships and content types are cached so they can be used for creating new files
  to_copy=['./tmp/xl/vbaProject.bin','./tmp/xl/_rels/workbook.xml.rels','./tmp/[Content_Types].xml']
  for src in to_copy:
    filename=src.split(os.path.sep)[-1]
    dst='./vba/'+filename
    copy2(src,dst)
    logger.info(f'copied vba project to {dst}')

    # 
    if 'vbaProject.bin' in src:
      cmd='unar -q -o tmp/ '+src
      rc=os.system(cmd)
      assert rc == 0, 'could not unarchive '+src

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

  filename='./vba/fcast.vb'
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