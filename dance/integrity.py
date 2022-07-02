"""Determine the rows in used by iande future that will need to exist in the iande-actl import"""
from dance.util.tables import df_for_table_name

def required_lines(forecast_start_year):
  '''Compute the list of required lines given the forecast start year in form y_year
  Args:
    forecast_start_year: The first forecast year as a String (Ynnnn)

  Returns: the required lines and all lines as sets
  '''

  df=df_for_table_name(table_name='tbl_iande')
  cols= list(df)
  ix=cols.index(forecast_start_year)
  c=cols[ix:]

  def not_all_are_empty(a):
    return any([x is not None for x in list(a)])

  must_have=set(df.index[df[c].apply(not_all_are_empty,axis=1)])

  return must_have, set(df.index)

if __name__=='__main__':
  reqd,all=required_lines('Y2022')
  print(reqd)
