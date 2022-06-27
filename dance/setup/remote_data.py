'''get annual cpi data'''
import requests
import json
from math import ceil 

urls={'BLS': 'https://api.bls.gov/publicAPI/v2/timeseries/data/'}

def request(site_code,registration_key,start_year,end_year,parameters):
  start_year=max(1914,start_year)-1

  headers = {'Content-type': 'application/json'}
  parameters["registrationkey"]=registration_key
  cpi={} # the index not the inflation rate
  n=ceil((end_year-start_year)/20)
  if site_code=='BLS':
    for i in range(n):
      s=start_year+i*20
      e=min(end_year,s+20)
      parameters["startyear"]=s
      parameters["endyear"]=e
      data = json.dumps(parameters)
      url=urls[site_code]
      p = requests.post(url, data=data, headers=headers)
      json_data = json.loads(p.text)
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
  return None