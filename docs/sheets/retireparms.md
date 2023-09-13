# retireparms

## pension facts

Facts about pensions used by retirement sheet. This is a static lookup table with the field `Pension` acting as they key. The columns are attributes to be used in the elections. 

## social security

This table creates a key for the selected social security elections, by which the retirement table can find the value. 
The values need to be entered for amounts available at different ages.

### Data source

It is sourced from `data/social_security.json`, which can be re-written with

```zsh
dance/extract_table.py -t tbl_social_security -w data/test_wb.xlsx
```

## mcare_opt

Medical plan options and selection. This is the menu of medical plan choices.

### Fields

- Year: Idenifies what year the plan is for.
- Package: This idenfifies the elements of a package.  This is used to select a set of items.  The value corresponds to a value in `tbl_retir_medical`, or blank if not selected.
- Class, Firm, Name and ID are labels to help tell what the line is.
- Monthly is the monthly premium.  For part D plans this is the base amount.  Over and above this the surcharge, if any, will be applied.
- Premium is annual
- Cost is the annual premium + the deductible.

### Data source

Setup sources this from: data/mcare_opt.json 
To rewrite that file based on changes in the workbook

```zsh
 dance/extract_table.py -t tbl_mcare_opt -w data/test_wb.xlsx
```

