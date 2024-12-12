# tax_tables

Selected (for our case) tax tables:
- Federal tax tables, 
- Connecticut tax tables, 

And required minimum distribution tables (two types).

## Federal Tax Table Married Joint
Multiple years of tax tables for this filing status.

These use the subtraction method in IRS pub detailed here: https://www.irs.gov/pub/irs-pdf/i1040gi.pdf.  This takes 6 rows and 4 columns per year.  These are organized in a single table.  

The program `bracket_fix.py` computes the numbers for the subtraction table based on a csv file which is shows the values using the additive method. Not sure where I found that file, most recently, I recreated the format.  Kind of painful.  May be best to wait for the 1040 Instructions to be published each year. (Or find a reliable source)

Sources:
- [Tax Foundation](https://taxfoundation.org/data/federal-tax/?_sf_s=tax%20brackets#results)

## CT Tax Table Married Joint

Multiple years of tax tables for this filing status. For a souce try:
- [IP 2024(7), Is My Connecticut Withholding Correct?](https://portal.ct.gov/-/media/drs/publications/pubsip/2024/ip-2024-7.pdf?rev=f0040b520ba44618a7f87190f9b05355&hash=4738B22405C6BCB9C7679245CD1DE4DE)
- [Tax Foundation](https://taxfoundation.org/data/all/state/state-income-tax-rates-2024/)

## Reqd Min Distr Table I

Table I is for beneficiaries (inherited IRA).

## Uniform Lifetime Table

Also known as Table III, this table is for normal (not inherited) plans.
