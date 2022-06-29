'''get annual various local data'''

types={'Assets':'A','Bank Accounts':'B','Credit Cards':'C','Investment Accounts':'I','Liabilities':'L','Loans':'N'}
def read_data(data_info):
  groups=data_info['group']
  skip_type_totals=set(types.keys())-set(groups)
  no_details_for=data_info['no_details_for']
  gtotal=[g+' - Total' for g in groups]
  data=[]
  names={} # keep track of account names, in order to manage name collision between account name and type
  # defaults for gains/losses percentages
  rlz=0
  unrlz=1
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
      # infer inactive if zero balance
      active=1 
      if '$ 0.00' in row[1]:
        active=0
      actl_source='=@[Account]' # formula for when it is a type or individual account
      actl_source_tab='tbl_tranfers_actl' # unless its an investment
      # keep any group totals
      if row[0] in gtotal:
        name=row[0].split(' - ')[0]
        if name not in types:
          actl_source+='& " - TOTAL"' # formula when its an account (with subaccounts)
        if name in names: # occurs if an account has same name as the category 
          # amend the formula for actual
          data[names[name]][6]='=@[Account] & " - TOTAL"' 
        else:
          data.append([name,type_,1,active,rlz,unrlz,actl_source,actl_source_tab])
          names[name]=len(data)-1
        continue
      # skip the details if we are grouping them together or expect them to be in sub-totals
      if group in groups + no_details_for:
        continue
      if type_ == 'I':
        parts=row[0].split(' - ')
        # skip over the cash value, in favor of the total
        if parts[-1] != 'Total':
          continue
        row[0]=' - '.join(parts[:-1])
        actl_source_tab='tbl_invest_actl' # unless its an investment

      # don't keep totals from non specified groups
      if row[0]in skip_type_totals:
        continue
      # drop zero balance (non group) rows unless called for 
      if active==0:
        if row[0] not in data_info['include_zeros']:
          continue
        else:
          actl_source=None
          actl_source_tab=None
      taxable=int(not any([a in row[0] for a in data_info['tax_free_keys']]))
      data.append([row[0],type_,taxable,active,rlz,unrlz,actl_source,actl_source_tab])
      names[row[0]]=len(data)-1
  data=sorted(data,key=lambda x: (x[1],x[0]))
  return data