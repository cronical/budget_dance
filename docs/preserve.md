# Preserve definitions

## Table: accounts

### data

|Key|Value|
|---|---|
|source|local|
|type|md_acct|
|path|./data/acct-bals/2023.tsv|
|group|Bank Accounts, Credit Cards, Real Estate, Other Asset, Liabilities, Mortgage Loans, Non Mort Loans|
|no_details_for|Assets, Loans, Investment Accounts|
|include_zeros|529 - ML, BKG - JNT - CP1, 401K - GBD MML - Pre-tax, 401K - GBD MML - Roth, CHET - Ben, HSA - GBD - Devenir, HSA - G - Invest, HSA - G - HSA Bank, LON - JNT - HED|
|tax_free_keys|401K, CHET, 529, HSA, IRA|
|force_active|LON - JNT - HED|


### preserve

|Key|Value|
|---|---|
|method|sparse|
|non-year-cols|Income Txbl, Active, No Distr Plan, Near Mkt Rate, Rate Cap, Reinv Rate, Notes|


## Table: balances

### data

|Key|Value|
|---|---|
|source|local|
|type|md_bal2|
|path|./data/acct-bals/2017.tsv|
|group|Bank Accounts, Credit Cards, Real Estate, Other Asset, Liabilities, Mortgage Loans, Non Mort Loans|
|no_details_for|Assets, Loans, Investment Accounts|
|include_zeros|529 - ML, BKG - JNT - CP1, 401K - GBD MML - Pre-tax, 401K - GBD MML - Roth, CHET - Ben, HSA - GBD - Devenir, HSA - G - Invest, HSA - G - HSA Bank, LON - JNT - HED|
|tax_free_keys|401K, CHET, 529, HSA, IRA|
|force_active|LON - JNT - HED|
|hier_separator|:|


### preserve

|Key|Value|
|---|---|
|method|sparse|


## Table: transfers_plan

### data

|Key|Value|
|---|---|
|source|local|
|type|json_records|
|path|data/transfers_plan.json|


### preserve

No preserve key.


## Table: iande

### data

|Key|Value|
|---|---|
|source|local|
|type|md_iande_actl|
|path|./data/iande.tsv|
|sheet|iande|
|hier_insert_paths|Income:I:Invest income:CapGn:Sales, Income:I:Invest income:CapGn:Shelt:Sales, Income:I:Retirement income:Social Security:SS - GBD - SSA, Income:I:Retirement income:Social Security:SS - VEC - SSA, Income:I:Retirement income:Pension:DB - VEC - PNX, Income:I:Retirement income:Pension:DB - GBD - TRV, Income:I:Retirement income:Pension:DB - VEC - MML, Income:I:Sheltered income:ER health acct contrib:ER HIA contribution - V, Income:J:Distributions:IRA:IRA - VEC - ML, Income:J:Distributions:IRA:IRA - GBD - Vanguard, Income:J:Distributions:IRA:IRA - VEC - Vanguard, Income:J:Distributions:Roth:IRA Roth - GBD - Vanguard, Income:J:Distributions:Roth:IRA Roth - VEC - Vanguard, Income:J:Distributions:HSA:HSA - GBD - Fidelity, Income:J:Distributions:HSA:HSA - GBD - Devenir, Income:J:Distributions:HSA:HSA - VEC - UHG, Income:J:Distributions:529:CHET - Fidelity, Income:J:Distributions:529:CHET - Ben, Income:J:Distributions:529:529 - ML, Income:J:Distributions:401K:401k - GBD - TRV, Income:J:Distributions:401K:401k - VEC - UHG, Income:J:Distributions:401K:Rollover:401k - GBD - TRV, Income:J:Distributions:401K:Rollover:401k - VEC - UHG, Expenses:T:Income Tax:Current Yr:Fed:Soc Sec WH - G, Expenses:T:Income Tax:Current Yr:Fed:Soc Sec WH - V, Expenses:X:Health:Prem:Post Ret Med Ins - GBD, Expenses:X:Health:Prem:Post Ret Med Ins - VEC, Expenses:X:Health:OOP, Expenses:Y:Invest:Reinv, Expenses:Y:Invest:Account Fees, Expenses:Y:Invest:Action Fees, Expenses:Y:Invest:Inherit:Normal, Expenses:Y:Invest:Rollover:DB - GBD - MML, Expenses:Y:Invest:Rollover:DB - GBD - TRV, Expenses:Y:To Asst:Invest:BKG - GBD - FID, Expenses:Y:To Asst:Invest:BKG - JNT - CP1, Expenses:Y:To Asst:Invest:BKG - JNT - ML, Expenses:Y:To Asst:Invest:BKG - JNT - Vanguard, Expenses:Y:To Asst:Invest:LON - JNT - HED, Expenses:Y:To Asst:Invest:BND - GBD - TRY, Expenses:Y:To Asst:Invest:BND - VEC - TRY, Expenses:Y:To Asst:Bank Accounts, Expenses:Y:To Asst:Other Asset, Expenses:Y:To Asst:Real Estate, Expenses:Y:To Liab:Credit Cards, Expenses:Y:To Liab:Liabilities, Expenses:Y:To Liab:Mortgage Loans, Expenses:Y:To Liab:Non Mort Loans, Expenses:Y:Payroll Savings:401K - GBD - TRV, Expenses:Y:Payroll Savings:401K - GBD MML - Pre-tax, Expenses:Y:Payroll Savings:401K - GBD MML - Roth, Expenses:Y:Payroll Savings:401K - VEC - UHG, Expenses:Y:Payroll Savings:ESP - VEC - Fidelity, Expenses:Y:Payroll Savings:HSA - GBD - Devenir, Expenses:Y:Payroll Savings:HSA - GBD - Fidelity, Expenses:Y:Payroll Savings:HSA - VEC - UHG|


### preserve

|Key|Value|
|---|---|
|method|sparse|


## Table: current

### data

|Key|Value|
|---|---|
|source|local|
|type|md_iande_actl|
|path|data/iande_ytd.tsv|
|sheet|current|
|hier_separator|:|
|hier_insert_paths|Income:I:Invest income:CapGn:Sales, Income:I:Invest income:CapGn:Shelt:Sales, Income:I:Retirement income:Social Security:SS - GBD - SSA, Income:I:Retirement income:Social Security:SS - VEC - SSA, Income:I:Retirement income:Pension:DB - VEC - PNX, Income:I:Retirement income:Pension:DB - GBD - TRV, Income:I:Retirement income:Pension:DB - VEC - MML, Income:I:Sheltered income:ER health acct contrib:ER HIA contribution - V, Income:J:Distributions:IRA:IRA - VEC - ML, Income:J:Distributions:IRA:IRA - GBD - Vanguard, Income:J:Distributions:IRA:IRA - VEC - Vanguard, Income:J:Distributions:Roth:IRA Roth - GBD - Vanguard, Income:J:Distributions:Roth:IRA Roth - VEC - Vanguard, Income:J:Distributions:HSA:HSA - GBD - Fidelity, Income:J:Distributions:HSA:HSA - GBD - Devenir, Income:J:Distributions:HSA:HSA - VEC - UHG, Income:J:Distributions:529:CHET - Fidelity, Income:J:Distributions:529:CHET - Ben, Income:J:Distributions:529:529 - ML, Income:J:Distributions:401K:401k - GBD - TRV, Income:J:Distributions:401K:401k - VEC - UHG, Income:J:Distributions:401K:Rollover:401k - GBD - TRV, Income:J:Distributions:401K:Rollover:401k - VEC - UHG, Expenses:T:Income Tax:Current Yr:Fed:Soc Sec WH - G, Expenses:T:Income Tax:Current Yr:Fed:Soc Sec WH - V, Expenses:X:Health:Prem:Post Ret Med Ins - GBD, Expenses:X:Health:Prem:Post Ret Med Ins - VEC, Expenses:X:Health:OOP, Expenses:Y:Invest:Reinv, Expenses:Y:Invest:Account Fees, Expenses:Y:Invest:Action Fees, Expenses:Y:Invest:Inherit:Normal, Expenses:Y:Invest:Rollover:DB - GBD - MML, Expenses:Y:Invest:Rollover:DB - GBD - TRV, Expenses:Y:To Asst:Invest:BKG - GBD - FID, Expenses:Y:To Asst:Invest:BKG - JNT - CP1, Expenses:Y:To Asst:Invest:BKG - JNT - ML, Expenses:Y:To Asst:Invest:BKG - JNT - Vanguard, Expenses:Y:To Asst:Invest:LON - JNT - HED, Expenses:Y:To Asst:Invest:BND - GBD - TRY, Expenses:Y:To Asst:Invest:BND - VEC - TRY, Expenses:Y:To Asst:Bank Accounts, Expenses:Y:To Asst:Other Asset, Expenses:Y:To Asst:Real Estate, Expenses:Y:To Liab:Credit Cards, Expenses:Y:To Liab:Liabilities, Expenses:Y:To Liab:Mortgage Loans, Expenses:Y:To Liab:Non Mort Loans, Expenses:Y:Payroll Savings:401K - GBD - TRV, Expenses:Y:Payroll Savings:401K - GBD MML - Pre-tax, Expenses:Y:Payroll Savings:401K - GBD MML - Roth, Expenses:Y:Payroll Savings:401K - VEC - UHG, Expenses:Y:Payroll Savings:ESP - VEC - Fidelity, Expenses:Y:Payroll Savings:HSA - GBD - Devenir, Expenses:Y:Payroll Savings:HSA - GBD - Fidelity, Expenses:Y:Payroll Savings:HSA - VEC - UHG|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: aux

### data

|Key|Value|
|---|---|
|source|none|
|hier_separator|:|
|hier_insert_paths|401K - GBD - TRV:contributions:ER, 401K - GBD - TRV:Withdrawal, 401K - VEC - UHG:contributions:ER, 401K - VEC - UHG:contributions:EE, 401K - VEC - UHG:Withdrawal, Bank Interest:Rate, Bank Interest:Start Bal, HSA - GBD - Fidelity:avail, HSA - GBD - Fidelity:demand, HSA - VEC - UHG:avail, HSA - VEC - UHG:demand, IRA - GBD - Vanguard:Rollover, IRA - GBD - Vanguard:Withdrawal, IRA - VEC - Vanguard:Rollover, IRA - VEC - Vanguard:Withdrawal, IRA - VEC - ML:Rollover, IRA - VEC - ML:Withdrawal, Other Asset:plans, Other Asset:depreciation, WH:Medicare:G:Base, WH:Medicare:G:Rate, WH:Medicare:V:Base, WH:Medicare:V:Rate, WH:Soc Sec:G:Base:Gross, WH:Soc Sec:G:Base:Cap, WH:Soc Sec:G:Rate, WH:Soc Sec:V:Base:Gross, WH:Soc Sec:V:Base:Cap, WH:Soc Sec:V:Rate|
|hier_alt_agg|{'Bank Interest': 'PRODUCT', 'HSA - GBD - Fidelity': 'MIN', 'HSA - VEC - UHG': 'MIN', 'WH:Medicare:G': 'PRODUCT', 'WH:Medicare:V': 'PRODUCT', 'WH:Soc Sec:G:Base': 'MIN', 'WH:Soc Sec:V:Base': 'MIN', 'WH:Soc Sec:G': 'PRODUCT', 'WH:Soc Sec:V': 'PRODUCT'}|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: retir_vals

### data

|Key|Value|
|---|---|
|source|local|
|type|retire_template|
|path|data/retire_template.tsv|
|template|{'fields': ['Item', 'Election', 'Start Date', 'Anny Dur Yrs', 'Anny Rate']}|


### preserve

|Key|Value|
|---|---|
|method|full|


## Table: retir_medical

### data

|Key|Value|
|---|---|
|source|local|
|type|retire_medical_template|
|path|data/retire_medical_template.tsv|
|template|{'fields': ['Item', 'Package', 'Start Date', 'End Date']}|


### preserve

|Key|Value|
|---|---|
|method|full|


## Table: pens_facts

### data

|Key|Value|
|---|---|
|source|local|
|type|json_index|
|path|data/pension_facts.json|


### preserve

|Key|Value|
|---|---|
|method|full|


## Table: social_security

### data

|Key|Value|
|---|---|
|source|local|
|type|json_records|
|path|data/social_security.json|


### preserve

|Key|Value|
|---|---|
|method|full|


## Table: mcare_opt

### data

|Key|Value|
|---|---|
|source|local|
|type|json_records|
|path|data/mcare_opt.json|


### preserve

|Key|Value|
|---|---|
|method|full|


## Table: manual_actl

### data

|Key|Value|
|---|---|
|source|local|
|type|json_index|
|path|data/manual_actl.json|


### preserve

|Key|Value|
|---|---|
|method|full|


## Table: payroll_savings

### data

|Key|Value|
|---|---|
|source|local|
|type|md_pr_sav|
|path|data/payroll_to_savings.tsv|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: roth_contributions

### data

|Key|Value|
|---|---|
|source|local|
|type|md_roth|
|path|data/roth_contributions.tsv|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: 529_distr

### data

|Key|Value|
|---|---|
|source|local|
|type|md_529_distr|
|path|data/529-distr.tsv|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: ira_distr

### data

|Key|Value|
|---|---|
|source|local|
|type|md_ira_distr|
|path|data/ira-distr.tsv|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: hsa_disb

### data

|Key|Value|
|---|---|
|source|local|
|type|md_hsa_disb|
|path|data/hsa-disbursements.tsv|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: bank_sel_invest

### data

|Key|Value|
|---|---|
|source|local|
|type|md_sel_inv|
|path|data/trans_bkg.tsv|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: transfers_actl

### data

|Key|Value|
|---|---|
|source|local|
|type|md_transfers_actl|
|path|./data/transfers.tsv|
|file_sets|{'balances': './data/acct-bals/'}|
|preserve|{'method': 'none'}|


### preserve

No preserve key.


## Table: invest_iande_values

### data

|Key|Value|
|---|---|
|source|local|
|type|md_invest_iande_values|
|path|data/invest-iande.tsv|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: invest_iande_ratios

### data

|Key|Value|
|---|---|
|source|local|
|type|md_invest_iande_values|
|path|data/invest-iande.tsv|


### preserve

|Key|Value|
|---|---|
|method|sparse|


## Table: invest_actl

### data

|Key|Value|
|---|---|
|source|local|
|type|md_invest_actl|
|path|data/invest-x.tsv|
|file_sets|{'performance': 'data/invest-p/', 'balances': './data/acct-bals/'}|


### preserve

No preserve key.


## Table: taxes

### data

|Key|Value|
|---|---|
|source|local|
|type|tax_template|
|path|data/taxes_template.tsv|
|template|{'fold_spacing': 3, 'fold_field': 'Line', 'fields': ['Line', 'Tax_doc_ref', 'Notes', 'Source', 'Tab', 'Sign']}|


### preserve

|Key|Value|
|---|---|
|method|sparse|


## Table: cap_gn

### data

No data key.


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: fed_tax

### data

|Key|Value|
|---|---|
|source|local|
|type|json_records|
|path|data/tax_rates/fed_tax_rates.json|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: ct_tax

### data

|Key|Value|
|---|---|
|source|local|
|type|json_records|
|path|data/tax_rates/ct_tax_rates.json|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: rmd_1

### data

|Key|Value|
|---|---|
|source|remote|
|site_code|FEDREG|
|table|{'find_method': 'caption', 'method_parms': {'text': 'Table 1 to Paragraph (b)'}}|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: rmd_3

### data

|Key|Value|
|---|---|
|source|remote|
|site_code|FEDREG|
|table|{'find_method': 'caption', 'method_parms': {'text': 'Table 2 to Paragraph (c)'}}|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: people

### data

|Key|Value|
|---|---|
|source|local|
|type|json_index|
|path|data/people.json|


### preserve

|Key|Value|
|---|---|
|method|full|


## Table: gen_state

### data

|Key|Value|
|---|---|
|source|internal|
|type|json_index|
|name|general_state|
|path|data/gen_state.json|


### preserve

|Key|Value|
|---|---|
|method|full|


## Table: state_tax_facts

### data

|Key|Value|
|---|---|
|source|local|
|type|json_index|
|path|data/state_tax_facts.json|


### preserve

|Key|Value|
|---|---|
|method|full|


## Table: part_b

### data

|Key|Value|
|---|---|
|source|local|
|type|json_records|
|path|data/part_b.json|


### preserve

|Key|Value|
|---|---|
|method|full|


## Table: infl

### data

|Key|Value|
|---|---|
|source|remote|
|site_code|BLS|
|api_key|bls|
|parameters|{'start_year': 1970, 'end_year': 2021, 'seriesid': ['CUUR0000SA0']}|


### preserve

|Key|Value|
|---|---|
|method|none|


## Table: table_map

### data

|Key|Value|
|---|---|
|source|internal|
|name|table_map|


### preserve

|Key|Value|
|---|---|
|method|none|


