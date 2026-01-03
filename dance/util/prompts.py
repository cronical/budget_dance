import sys


def prompt_no_yes():
  """Prompt to continue. Default No. Display issue outside of this call
  No causes a sys.exit(-1)
  Yes just returns
  """
  yn = 'Q'
  while yn not in 'YN':
    yn = input("Continue? (N/y):").strip().upper() + 'N'
    if yn == 'N':
      sys.exit(-1)
