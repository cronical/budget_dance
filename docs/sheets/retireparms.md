# retireparms

## pension facts

Facts about pensions used by retirement sheet.  

## social security

This table creates a key for the selected social security election, by which the retirement table can find the value.

## mcare_opt

Medical plan options and selection. This is the menu of medical plan choices.

### Fields

- Year: Idenifies what year the plan is for.
- Package: This idenfifies the elements of a package.  This is used to select a set of items.  The value corresponds to a value in `tbl_retir_medical`, or blank if not selected.
- Class, Firm, Name and ID are labels to help tell what the line is.
- Monthly is the monthly premium.  For part D plans this is the amount over and above the surcharge, if any.
- Premium is annual
- Cost is the annual premium + the deductible.

### Setup

Setup sources this from: data/mcare_opt.json 
To refresh that file:

```zsh
dance/util/extract_table.py -w data/test_wb.xlsm -t tbl_mcare_opt -j data/mcare_opt.json -o records
```

