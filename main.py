#qpy:webapp:GistClientAndroid
#qpy://127.0.0.1:8080/

from flask import Flask, render_template, redirect, url_for, request, send_file
from ezdb import DatabaseDef, TableDef
from gister import Gister
import os
import sys

def GetRecentGithubUser(db):
  return [a["gituser"] for a in db.Select("gistrecent")][0:5]

def ExistGitUser(db,gituser):
 return [a["gituser"] for a in db.Select("gistrecent") if a["gituser"] == gituser]

# Environment Setup
ROOT = os.path.dirname(os.path.abspath(__file__))
activegist = None

# Database Def
recenttab = TableDef("gistrecent")
recenttab.AddField("gituser","text")
gistdb = DatabaseDef("./gistclient.db")
gistdb.AddTable(recenttab)

if not gistdb.Initialize():
  print "Error Initializing Database"
  sys.exit()

app = Flask(__name__)

@app.route("/")
def GetRoot():
  global activegist
  activegist = None
  recentlist = GetRecentGithubUser(gistdb)
  return render_template("root.html", recentlist = recentlist)

@app.route("/assets/js/jquery-3.1.1.min.js")
def GetJqueryJs():
  return render_template("jquery-3.1.1.min.js")

@app.route("/assets/img/progress.gif")
def GetProgressBar():
  return send_file("templates/progress.gif")
  
@app.route("/getgistlist/", methods = ["POST"])
def ListGists():
  global activegist
  gituser = str(request.form["gituserfield"])
  if not ExistGitUser(gistdb, gituser):
    gistdb.Insert("gistrecent",[gituser])
  
  if len(gituser) < 1:
    return render_template("error.html", errortext="Please specify user")
  else:
    activegist = Gister(gituser)
    return render_template("user.html", gistlist = activegist.ListGists(), gituser = gituser)

@app.route("/viewgist/", methods = ["POST"])
def GetGistValue():
  global activegist
  gistname = str(request.form["gistname"])
  return render_template("gist.html", gisttext = activegist.GetGistText(gistname), gistuser = activegist.USERNAME)
   
@app.errorhandler(500)
def internal_error(exception):
  app.logger.error(exception)
  return render_template('error.html', errortext = exception), 500

@app.route("/__exit", methods = ['GET','HEAD'])
def __exit():
  StopFlask()

@app.route("/__ping", methods=['GET','HEAD'])
def __ping():
  return "ok"

app.run("0.0.0.0",8080)
