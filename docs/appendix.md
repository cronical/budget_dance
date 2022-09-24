# Appendix

## tax rates

## Worksheets removed that were previously on long-term-plan.

- Sweep
- Plan (goes to iande and taxes)
- Variance
- Tax Tables (-> tables)
- 401K
- RetireMedic
- States (-> tables)
- RMD (-> tables)
- Pension (-> tables)
- Actual (->iande-map)
- M-Actual (->iande_actl)
- HSA-V (->hsa)
- HSA-G (->hsa)
- Act-401K (->401K)
- SettleAccts
- Real Estate Act
- College
- Clg-Actual
- Criteria
- Inflation (->tables)
- Loan Calc
- (other) Inflation
- AcctNameChg
- InvestAct (->invest_actl)
- InvestXfersAct (->invest_actl)
- OtherAct (->other-x)

## Changes to existing categories

The following changes were made to enable the invest iande enhancements.

- ✓ Create X:Investing:Fees
- ✓ Find and replace the records under X:Misc:Commisions & Fees to X:Investing:Fees 
- 3 types under Invest Income: CapGn, Div, Int
- ✓ Create CapGn
- ✓ Create CapGn:Sale
- ✓ Rename/Move CapGn - LT as CapGn:Mut LT 
- ✓ Rename/Move CapGn - ST as CapGn:Mut ST
- ✓ Rneame/Move SCapGn - LT' as CapGn:Shelt
- ✓ Find and replace: change 'SCapGn - ST' to '...CapGn:Shelt'

- ✓ Rename Div as Reg
- ✓ Create new Div under Invest Income
- ✓ Move Reg under Div
- ✓ Rename/Move Div Tax-exempt to Div:Tax-exempt
- ✓ Rename/Move 'Sdiv' to Div:Shelt
- Find and replace InvestInc:SDiv -> Div:Shelt

- ✓ Create Int:Reg
- ✓ Find/replace Int:Bkg and Int:Other to Int:reg
- ✓ Rename/Move Int Tax-exempt to Int:Tax-exempt
- Rename/Move 'SInterest Income' to Int:Shelt
- ✓ Creaate Int:Shelt
- ✓ Find and replace Sint:bank and sint:bkg -> Int:Shelt

- Make the taxes support the last two parts method
  - Club state and federal together. 
    - Create: T:Income Tax
    - Create T:Income Tax:Current Yr and T:Income Tax:Prior Yr
  - ✓ Rename / Move T:Fed income tx pd to T:Income Tax:Current Yr:Fed
  - ✓ Drop all the Fed tax pd - legends
  - ✓ Add WH to payroll for consistency
  - ✓ Change prior year to Fed Prior Year under T:Income Tax
  - ✓ Rename/Move State income tax pd to Income Tax:State
  - ✓ Rename CT and MA to include 'tax'
  - ✓ Add WH and remove CT Tax - from the state lines
  - ✓ Move the prior year items to T:Income Tax:Prior Year

- ✓ Find and replace Sheltered:Employer Health Acct contributions to I:Sheltered income:ER health acct contrib:ER HSA contribution - V

- ✓ remove 'SCapGn - ST', S invest income, InvestInc:SInterest Income, 
  InvestInc:SDiv, Sheltered:InvestInc and what's left under Sheltered
  X:Misc:Commissions & Fees

- ✓ Clean up a few transactions
  - ✓ Optum Bank - HSA move interest to :Bank
  - ✓ Passthru:Pass-IRA-VEC-ML 3 rounding adjustments to misc:asset adj