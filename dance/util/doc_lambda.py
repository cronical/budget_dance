#! /usr/bin/env python
'''Reformat the lambda doc in the config file as markdown'''
import pandas as pd
from dance.util.files import read_config

def gen_lambda_docs():
  lams=read_config()['lambdas']
  df=pd.DataFrame(lams)
  df.sort_values(by='name',inplace=True)

  with open("docs/functions/excel_lambdas.md",mode='w') as f:
    f.write('# Defined Excel Lambda functions\n\n')
    df[['name','comment','formula']].to_markdown(f,index=False)

if __name__=="__main__":
  gen_lambda_docs()