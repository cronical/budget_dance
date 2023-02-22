# aux
This is a set of rows needed to establish forecasts in some cases.  The rows may be input or calculated.  The need arises for aux data and calcs, for instance, in handling 401K accounts, where the EE contribution is tax deductable but is only part of the amount for add/wdraw at the balance level.  That value plus the pre-tax deductions amounts from the paychecks need to be summed to produce the W2 exclusions.  This is the place where those calcs happen. 

The calculations are flexible, but they often use the form of looking up a value and multiplying it by the value in the sign field.  Mostly the sign field is used to change or retain the sign, but it can be used to apply a scalar value such as a tax rate. 

The following style is used to allow the table to be relocated and makes the formula apparent from the values in cells.

```=@get_val([@Source],[@[Source Table]],this_col_name())*[@Sign]```

this_col_name is a VBA function that gets the current column table name.

The field 'Accum_by' is intended to allow summations using the `accum` function.  If a value needs more than one tag, create another row with the same data and a different tag.  An example of this 401K deductions, which generate W2 exclusions on one hand and the need to deposit amounts into the 401K account.

