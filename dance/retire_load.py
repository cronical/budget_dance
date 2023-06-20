#! /usr/bin/env python
'''
Reads data from "data/retire_income_template.tsv" and "data/retire_medical_template.tsv to create the retir_vals table and retir_medical table
'''
import argparse


import pandas as pd

from dance.util.files import tsv_to_df

def prepare_retire(data_info):
  '''setup the retir_vals dataframe'''
  string_fields='Item,Election,Start Date,Anny Dur Yrs,Anny Rate'.split(',')
  df=tsv_to_df(data_info['path'],skiprows=3,nan_is_zero=False,string_fields=string_fields)
  df['Start Date']=pd.to_datetime(df['Start Date'])
  df[['Type','Who','Firm']]=df.Item.str.split(' - ',expand=True)
  return df

def prepare_retire_medical(data_info):
  '''setup the retir_medical dataframe'''
  string_fields='Item,Package,Start Date,End Date'.split(',')
  df=tsv_to_df(data_info['path'],skiprows=3,nan_is_zero=False,string_fields=string_fields)
  df['Start Date']=pd.to_datetime(df['Start Date'])
  df['End Date']=pd.to_datetime(df['End Date'])
  df[['Type','Who','Firm']]=df.Item.str.split(' - ',expand=True)
  return df

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description ='Prepares the retirement table from the input template')
  parser.add_argument('type',choices=['i','m'],help='i for income, m for medical')
  parser.add_argument('--path','-p',default= 'data/retire_template.tsv',help='The path and name of the input file')
  args=parser.parse_args()
  match args.type:
    case 'i':
      prepare_retire(data_info={'path':args.path})
    case 'm':
      prepare_retire_medical(data_info={'path':args.path})
