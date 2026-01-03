#!/usr/bin/env python
"""
Start the root document in a browser
"""
import importlib, importlib.resources
import webbrowser

def start_help():
  anchor = importlib.__import__("dance")

  with importlib.resources.path(anchor, "docu/index.html") as fspath:
    uri=fspath.as_uri()
    webbrowser.open(uri)


if __name__=="__main__":
  start_help()

