'''Check on supported languages'''

from pygments.lexers import get_all_lexers

lexers = get_all_lexers()
for lexer in lexers:
  print ("-\t" + lexer[0] + "\n")
  print ("\t-\t" + "\n\t-\t".join(lexer[1]) + "\n")
  