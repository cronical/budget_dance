#!/usr/bin/env python3
"""increments/sets and writes the new current version as text
"""
from datetime import datetime
import argparse
import json
import os

def main():
  choices=["epoch", "major","minor","point", "alpha", "beta", "rc", "post","dev"]
  description="""
Change the version number.
Bumps the value of a a specified field or resets it to zero if the -r option is used.
Lower levels are all set back to zero in either case.
Only one of alpha, beta or rc are allowed at a time."""
  parser=argparse.ArgumentParser(description=description,formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("field",choices=choices)
  parser.add_argument("--reset","-r",action='store_true')
  args = parser.parse_args()
  ver=Version()
  ver.change(args.field,args.reset)
  ver.write()
  print (ver.text)


class Version():
  def __init__(self):
    head,_=os.path.split(__file__)
    self.datafile=os.path.join(head,"current.json")
    self.histfile=os.path.join(head,"hist.csv")
    head=os.sep.join(head.split(os.path.sep)[:-1])
    self.textfile=os.path.join(head,"dance/version.txt")
    self.order=["epoch", "major","minor","point", "alpha", "beta", "rc", "post","dev"]
    with open(self.datafile) as json_file:
      self.version = json.load(json_file)
    self.format()

  def change(self,field_name,reset=False):
    """zero or increment the field and set any lower ones to zero
    if reset is false, increment.  If reset is True set to zero.
    in the case of alpha, beta, rc ensure only one is set
    """
    
    abc={"alpha","beta","rc"}
    ix=self.order.index(field_name)
    old=self.version[field_name]
    if field_name in abc:
      for f in abc:
        self.version[f]=0
    self.version[field_name]=(old+1)* (not reset)
    for f in self.order[ix+1:]: # reset lower items
      self.version[f]=0
    
    self.format()

  def write(self):
    """write the current version to json, the text file, and the history file
    """
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hist=','.join([now,self.text])
    with open(self.datafile,'w') as f:
      json.dump(self.version,f)
    with open(self.textfile,'w') as f:
      f.write(self.text)
    if not os.path.exists(self.histfile):
      with open(self.histfile,'w') as f:
        f.write("date,version\n")
    with open(self.histfile,'a') as f:
      f.write(hist+"\n")
    
  def format(self):
    """ Convert to the text format: [N!]N(.N)*[{a|b|rc}N][.postN][.devN]
    """
    release=[]
    pre=""
    post=[]
    for ix,f in enumerate(self.order):
      val=self.version[f]
      if (ix==0):
        if self.version[f]==0:
          continue
        else:
          release+=["%d!"%val]
      elif ix in (1,2):        
        release+=["%d"%val]
      elif ix == 3:
        if val!=0:
          release+=["%d"%val]
      else:
        if ix in (4,5,6): # the prerelease ones
          if val!=0:
            pre="%s%d"%(['a','b','rc'][ix-4],val)
        elif ix in (7,8):
          if val!=0:
            post+=["%s%d"%(f,val)]
    if len(post):
      post=[""]+post # to get the .
    self.text =".".join(release)+pre+".".join(post)
    pass


if __name__=="__main__":
  main()

