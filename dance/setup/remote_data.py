'''get annual various remote data
raises JSON decode error if site is unavailable'''
import requests
import json
from math import ceil, floor
from bs4 import BeautifulSoup

urls={'BLS': 'https://api.bls.gov/publicAPI/v2/timeseries/data/',
  'FEDREG':'https://www.federalregister.gov/documents/2020/11/12/2020-24723/updated-life-expectancy-and-distribution-period-tables-used-for-purposes-of-determining-minimum'}

user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'

def request(data_info):
  '''retrieve various types of data from internet'''
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
      url=urls[data_info['site_code']]
      p = requests.post(url, data=data, headers=headers,timeout=5 )
      try:
        json_data = json.loads(p.text)
      except json.JSONDecodeError as e:
        raise e

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
  if data_info['site_code']=='FEDREG':
    headers={'User-Agent': user_agent}
    try:
      response=requests.get(urls['FEDREG'],headers=headers, timeout=5)
    except requests.exceptions.ConnectTimeout as e:
      raise e
    assert response.status_code==200,'trouble'
    soup=BeautifulSoup(response.text,'lxml')
    method=data_info['table']['find_method']
    if method=='caption':
      method_parms=data_info['table']['method_parms']
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

