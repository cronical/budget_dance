# tax_tables

Selected (for our case) tax tables:
- Federal tax tables, 
- Connecticut tax tables, 

And required minimum distribution tables (two types).

## Federal tax tables

These use the subtraction method in IRS pub detailed here: https://www.irs.gov/pub/irs-pdf/i1040gi.pdf.  This takes 6 rows and 4 columns per year.  These are organized in a single table.  A VBA function is used to select the right values for use on the `taxes` tab. 

The program `bracket_fix.py` computes the numbers for the subtraction table based on a csv file which is shows the values using the additive method. Not sure where I found that file, most recently, I recreated the format.  Kind of painful.  May be best to wait for the 1040 Instructions to be published each year. (Or find a reliable source)

## CT Tax Table Married Joint

Multiple years of tax tables for this slice.

## Reqd Min Distr Table I

Table I is for beneficiaries (inherited IRA).

## Uniform Lifetime Table

Also known as Table III, this table is for normal (not inherited) plans.
