"""unwrap the two line mode of investment transactions
works ok, but the report does not contain the transfer field. Arg.
"""
import os.path
import pandas as pd

def main():
  in_file="/Users/george/Downloads/investment_transactions.tsv"
  p,f=os.path.split(in_file)
  n,e=f.split('.')
  f='.'.join([n+"_flat",e])
  out_file=os.path.join(p,f)

  df=pd.read_csv(in_file,sep="\t",skiprows=3)
  stacked_cols=[c for c in df.columns if '_'in c]
  even_cols=[c.split('_')[0] for c in stacked_cols]
  odd_cols=[c.split('_')[1] for c in stacked_cols]
  even_map=dict(zip(stacked_cols,even_cols))
  odd_map=dict(zip(stacked_cols,odd_cols))
  even_range=range(0,df.shape[0],2)
  odd_range = range(1,df.shape[0],2)
  even_df=df.loc[even_range]
  odd_df=df.loc[odd_range,stacked_cols]
  dfe=even_df.rename(columns=even_map)
  dfo=odd_df.rename(columns=odd_map)
  dfe.reset_index(drop=True,inplace=True)
  dfo.reset_index(drop=True,inplace=True)
  df=pd.concat([dfe,dfo],axis=1)
  df.to_csv(out_file,sep="\t",index=False)

if __name__=="__main__":
  main()