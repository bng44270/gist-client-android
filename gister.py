##########################################
# gister.py
#   Github Gist Library for Python
#
# Usage:
#   from gister import Gister
#
#   mygist = Gister("bng44270")
#
#   mygist.ListGists()
#   --> returns ["gist1","gist2",...]
#
#   mygist.GetGist(name)
#   --> return { "url":"http://github.com/url/to/gist", "name": "gist-name" }
#   NOTE:  gist-name corresponds to name from ListGists results
#
#   mygist.getGistText(name)
#   --> return ["line1","line2","line3",....] containing each line of the Gist
#   NOTE: to output the text content to the console use something like this:
#              print "\n".join(mygist.GetGistText("gist-name")) 
#
#   mygist.DownloadGist(name)
#   --> downloads gist to current directory
#
#   Alternate:
#     mygist.DownloadGist(name,txt="win|mac|lin")
#     --> specify text format to download (default is lin)
##########################################

import requests
import re

class Gister:
  def __init__(self,username):
    self.USERNAME = username
    self.GISTROOT = "http://gist.github.com/" + self.USERNAME
    self.GISTS = []
    
    requests.packages.urllib3.disable_warnings()
    self.__populategist()

  def __parsegist(self, url):
    returndata = { "nexturl" : "", "gists" : []}
    html = requests.get(url)
    for thisline in html.iter_lines():
      if re.search("css-truncate-target",thisline):
        if not re.search(">" + self.USERNAME + "<",thisline):
          gistline = str(re.sub("^","https://gist.github.com",re.sub("<.*$","",re.sub("\".*css-truncate-target\">","|",re.sub("^.*href=\"","",thisline))))).split("|")
          returndata["gists"].append({ "url":gistline[0], "name":gistline[1]})
      if re.search(">Newer<.*href.*>Older<",thisline):
        returndata["nexturl"] = re.sub("\".*$","",re.sub("^.*href=\"","",thisline))
    
    return returndata

  def __populategist(self):
    gisturl = self.GISTROOT
    while True:
      gistdata = self.__parsegist(gisturl)
      for thisgist in gistdata["gists"]:
        self.GISTS.append({"url":thisgist["url"], "name":thisgist["name"]})
      if len(gistdata["nexturl"]) > 0:
        gisturl = gistdata["nexturl"]
      else:
        break;
  
  def ListGists(self):
    return [a["name"] for a in self.GISTS if a["name"]]

  def GetGist(self,name):
    return [a for a in self.GISTS if a["name"] == name][0]

  def GetGistText(self, name):
    gisttext = []
    html = requests.get([a["url"] for a in self.GISTS if a["name"] == name][0])
    for thisline in html.iter_lines():
      if re.search(">Raw<",thisline):
       rawurl = str(re.sub("^","https://gist.githubusercontent.com",re.sub("\".*$","",re.sub("^.*href=\"","",thisline))))
       rawgist = requests.get(rawurl)
       for thisline in rawgist.iter_lines():
         gisttext.append(thisline)
    
    return gisttext

  def DownloadGist(self, name,txt="lin"):
    if txt == "lin":
      eol = "\n"
    elif txt == "win":
      eol = "\r\n"
    elif txt == "mac":
      eol = "\r"

    if self.GetGist(name):
      html = requests.get([a["url"] for a in self.GISTS if a["name"] == name][0])
      for thisline in html.iter_lines():
        if re.search(">Raw<",thisline):
         rawurl = str(re.sub("^","https://gist.githubusercontent.com",re.sub("\".*$","",re.sub("^.*href=\"","",thisline))))
         rawgist = requests.get(rawurl)
         f = open("./" + name,"w")
         for thisline in rawgist.iter_lines():
           f.write(thisline + eol)
         f.close()