# Formula patterns that are NOT recommended

Avoid use of INDIRECT, OFFSET, as these are "volitile" functions, which trigger recalculation at every change. 

Use care with [#Data] references; depending on the situation, they may create circular logic.

## Use the indirect method

Getting the column can be done with indirect which should be avoided

```title="Refer to this column by indexing the headers"
INDIRECT("tbl_balances["&INDEX([#Headers],COLUMN())&"]")
```

```title="Locate a value with a common key"
XLOOKUP([@AcctName],tbl_retir_vals[Item],INDIRECT("tbl_retir_vals["&this_col_name()&"]"),0)
```

## Use of the structured [#Data] notation

These create a dependency on the whole table, which is fine for looking up values that themselves don't depend on other tables. But it is not appropriate for year-to-year calculations, as it will create circular logic.

## Value OFFSET to get prior column for this row

Its volitile and should be avoided.

```title="Use OFFSET"
=OFFSET(INDIRECT(ADDRESS(ROW(),COLUMN())),0,-1,1,1)
```