'''get annual various local data'''

types={'Assets':'A','Bank Accounts':'B','Credit Cards':'C','Investment Accounts':'I','Liabilities':'L','Loans':'N'}
def read_data(data_info):
  groups=data_info['group']
  no_details_for=data_info['no_details_for']
  gtotal=[g+' - Total' for g in groups]
  data={}
  with open(data_info['path']) as f:
    for line in f:
      if '@' in line:
        continue # skip the securities
      row=line.split('\t')
      # set the type if it is a new major heading
      if row[0]in types.keys() and len(row[1])==0:
        group=row[0]
        type_=types[group]
        continue
       # skip securities (and probably currencies but I don't care)
      if len(row)!=3:
        continue
      # skip the headings
      if row[2]=='Notes\n' or row[0]=='':
        continue
      # keep any group totals
      if row[0] in gtotal:
        name=row[0].split(' - ')[0]
        data[name]=type_
        continue
      # skip the details if we are grouping them together or expect them to be in sub-totals
      if group in groups + no_details_for:
        continue
      if '$ 0.00' in row[1]:
        if row[0] not in data_info['include_zeros']:
          continue
      data[row[0]]=type_
  return data