'''get annual various remote data
The following errors may occur and should be caught by caller: 
  json.JSONDecodeError
  requests.exceptions.ConnectTimeout
  ValueError
  ('Response code is %d'%response.status_code)
'''
import requests
import json
from math import ceil, floor
from bs4 import BeautifulSoup
import pandas as pd

#urls={'BLS': 'https://api.bls.gov/publicAPI/v2/timeseries/data/',
#  'FEDREG':'https://www.federalregister.gov/documents/2020/11/12/2020-24723/updated-life-expectancy-and-distribution-period-tables-used-for-purposes-of-determining-minimum'}

user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'

def request(table_info):
  '''retrieve various types of data from internet'''
  data_info=table_info['data']  
  url=data_info['url']
  if data_info['site_code']=='BLS':
    start_year=data_info['parameters']['start_year']
    start_year=max(1914,start_year)-1
    end_year=data_info['parameters']['end_year']
    headers = {'Content-type': 'application/json'}
    parameters=data_info['parameters']
    del parameters['start_year']
    del parameters['end_year']
    parameters['registrationkey']=data_info['api_key']
    cpi={} # the index not the inflation rate
    n=ceil((end_year-start_year)/20)
    for i in range(n):
      s=start_year+i*20
      e=min(end_year,s+20)
      parameters['startyear']=s
      parameters['endyear']=e
      data = json.dumps(parameters)
      p = requests.post(url, data=data, headers=headers,timeout=8 )
      json_data = json.loads(p.text) # may throw json.JSONDecodeError
      for row in json_data['Results']['series'][0]['data']:
        if row['period']=='M12':
          year=row['year']
          value=float(row['value'])
          cpi[year]=value
    inflation={}
    years=sorted(cpi)[1:]
    for y in years:
      ly=str(int(y)-1)
      infl=100*(cpi[y]-cpi[ly])/cpi[ly]
      inflation[int(y)]=round(infl,1)
    return inflation
  
  '''The parsing of HTML is to be replaced with xml as of 9/15/23
  Something like the following - separate the tables with the square bracket notation.
  u='https://www.federalregister.gov/documents/full_text/xml/2020/11/12/2020-24723.xml'
  df=pd.read_xml(u,xpath="//GPOTABLE[1]/ROW")
  '''
  
  if data_info['site_code']=='FEDREG':
    new=True
    match new:
      case True:
        cols=[ci['name']for ci in table_info['columns']]
        xpath=data_info['table']['method_parms']['xpath']
        # regrettably, they put an extra field in sometimes for pagination?
        # this double query method is a work around - iterparse might be better
        df=pd.read_xml(url,xpath=xpath+'[not(PRTPAGE)]',names=cols)
        df['Age']=df.Age.str.replace('\+','') # last row has 120+
        df['Age']=df.Age.astype(int)
        try:
          df2=pd.read_xml(url,xpath=xpath+'[PRTPAGE]',names=['PRTPAGE']+cols)
          df2=df2[cols]
          df=pd.concat([df,df2],ignore_index=True)
        except ValueError: # no records found
          pass
        df.sort_values(by='Age',inplace=True)
        df.reset_index(inplace=True,drop=True) 
        return df
      case False: # old method DEPRECATED
        headers={'User-Agent': user_agent}
        response=requests.get(url,headers=headers, timeout=5)
        if response.status_code!=200:
          raise ValueError('Response code is %d'%response.status_code)
        method=data_info['table']['find_method']
        method_parms=data_info['table']['method_parms']

        if method=='caption': # DEPRECATED in favor of XML
          soup=BeautifulSoup(response.text,'lxml')
          table=soup.find('caption',string=method_parms['text']).find_parent('table')
          data={}
          for tr in table.find_all('tr'):
            class_ = tr.get('class')
            if class_ is not None:
              if 'page_break' in class_:
                continue
            vals=[]
            for i,d in enumerate(tr.find_all('td')):
              v=d.get_text(strip=True)
              try:
                v=float(v)
                if floor(v)==v:
                  v=int(v)
              except ValueError:
                pass  # leave as a string
              if i==0:
                k=v
              else:
                vals+=[v]
            if len(vals)==0:
              continue # skip the headings
            if len(vals)==1:
              vals=vals[0]
            data[k]=vals
          return data
  return None

if __name__=='__main__': # for testing
  from dance.util.files import read_config
  config=read_config()
  table_info=config['sheets']['tax_tables']['tables'][3]
  df=request(table_info)
  print(df)
  pass