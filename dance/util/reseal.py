#! /usr/bin/env python
'''reseal file opened by reveal'''
from dance.util.files import read_config
from dance.util.files import zip_up
from dance.util.logs import get_logger

logger=get_logger(__file__)
filename=read_config()['workbook']
zip_up(filename,'tmp')
logger.info("%s re-zipped"%filename)