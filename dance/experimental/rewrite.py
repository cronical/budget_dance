'''Use openpyxl to rewrite a file to see if it messes up the schema'''

from openpyxl import load_workbook
filename='dance/experimental/Book1.xlsx'
wb=load_workbook(filename=filename)

wb.save(filename=filename)
