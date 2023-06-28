'''Worksheet oriented functions'''
import openpyxl.utils.cell
from openpyxl.worksheet.formula import ArrayFormula
import pandas as pd

def df_for_range(worksheet=None,range_ref=None):
  '''get a dataframe given a range reference on a worksheet
  First column becomes the index of the result
  For Array Formulas, just include the text of the formula'''

  data=[]
  rb=openpyxl.utils.cell.range_boundaries(range_ref)
  for src_row in worksheet.iter_rows(min_col=rb[0],min_row=rb[1], max_col=rb[2], max_row=rb[3]):
    row=[]
    for cell in src_row:
      value=cell.value
      if isinstance(value,ArrayFormula): 
        value=value.text
      row.append(value)
    data.append(row)
  cols = data[0][1:]
  idx = [r[0] for r in data[1:]]
  data = [r[1:] for r in data[1:]]
  df = pd.DataFrame(data, index=idx, columns=cols)
  return df