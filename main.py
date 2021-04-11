import flask
import datetime
from flask import request,redirect
from replit import db
from collections import namedtuple
from flask import make_response
import hashlib
import string
import random
from flask import jsonify

"""
https://realpython.com/python-memcache-efficient-caching/

from pymemcache.client import base
Trebalo bi zameniti rucno napisani cache sa bibliotekom
"""
cache={}

def set(key,value):
    cache[key]=value
    return True

def delete(key):
    if key in cache:
      del cache[key]

def flush():
    cache.clear() 


def age_set(key,val):
   save_time=datetime.datetime.utcnow
   set(key,(val,save_time))

def age_get(key):
    r=cache[key]
    if r:
      val,save_time=r
      age=(datetime.datetime.utcnow()-save_time).total_seconds()
    else: 
      val,age=None,0
    return val,age
       
def add_post(ip,post):
    "Uzmi argument ip adresu koji je nacin da prevaris korisnika koji"
    "zadaje spam, post je kalasa neka"
    post.put() # nznm sta je ovo 
    get_posts(update=True)
    return str(post.key().id())
             
    
def get_posts(update="False"):
  q=db["arts"]
  mc_key="arts"
  posts,age=age_get(mc_key)
  if update or posts is None:
    posts =list(q)
    age_set(mc_key,posts)
  return posts,age  

  

def age_str(age):  
  s="queried %s seconds ago"
  age=int(age)
  if age==1:
     s=s.replace("seconds","second")
  return s%age
  


app = flask.Flask(__name__)
artt = namedtuple('artt', ['title', 'content',"created","last_modified"])

def renderfront(title="",art="",error="",arts="",timing=""):
  "Render our front page"
  return flask.render_template('blog.html', title=title,art=art,error=error,arts=arts,timing=timing)
def renderfront1(title="",art="",error="",arts=""):
  "Render our front page but on a different page"
  return flask.render_template('newpost.html', title=title,art=art,error=error,arts=arts)

def Reverse(lst): return list(reversed(lst))

def blogpost(title,art,created,last_modified):
   "Put a blog post into a database"
   try:
     db["arts"]=db["arts"]+[(artt(title,art,created,last_modified))]
   except KeyError:
     db["arts"]=[]  
     db["arts"]=db["arts"]+[(artt(title,art,created,last_modified))]   

#del db["arts"]
#print(db["arts"])   
@app.route('/<int:number>', methods=['GET', 'POST'])
def postpage(number):
  print(number)
  try:
    key="stranica"+str(number)
    if key in cache:
      set("datetime_end"+key,datetime.datetime.now() )
      minutes_diff = (cache["datetime_end"+key] - cache["datetime_start"+key]).total_seconds()   
      return renderfront("","","",Reverse(([(cache[key])[number-1]])),"stranica otvorena pre "+str(minutes_diff)+" sekundi")  
    else:  
      key="stranica"+str(number)
      set("datetime_start"+key,datetime.datetime.now())
      set(key,db["arts"])
    return renderfront("","","",Reverse(([(cache[key])[number-1]])))
  except IndexError:
    return "mmmm bebo 404"

@app.route("/<int:number>.json/?", methods=['GET', 'POST'])
def jsonmainnumber(number):
   #return jsonify({ "namebroj":"John", "age":30, "car":False})
   try:
    return jsonify(
      {'key1':db["arts"][number-1][0],"key2":db["arts"][number-1][1]} )
   except IndexError:
    return "mmmm bebo 404"

@app.route("/json", methods=['GET', 'POST'])
def jsonmain():

   return jsonify({ "name":"John", "age":30, "car":False})

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
  if flask.request.method == "POST":
     title = request.form.get("title")    
     art = request.form.get("content").replace("\n","<br>")
     created = str(datetime.date.today())
     last_modified = str(datetime.date.today())
     blogpost(title,art,created,last_modified)
     key="stranica"
     if art.strip(" ") and title.strip(" "):
       #return 'Thanks'
       set(key,db["arts"])
       #cache[key]=(db["arts"])
       return  redirect('/'+str(len(cache[key])))
     else:
       error="we need both a title and some artwork"  
     return renderfront1(title,art,error,cache[key])
  else:
	   return renderfront1("","","",Reverse(db["arts"]))  

def modify():
  "Ovo treba da modifikuje funkciju."
  return 0

alphabet=string.ascii_letters
def make_salt():
     "Return a string of 5 random characters"
     a=""
     for i in range(5):
      a+=random.choice(alphabet) 
     return a

def make_pw_hash(name,pw,salt=None):     
        if not salt:
          salt=make_salt()          
        return "{},{}".format( hash_str(name+pw+salt),salt)
    
def valid_pw(name,pw,h):
    salt=h.split(",")[1] 
    return h==make_pw_hash(name,pw,salt)


import hmac
SECRET=b"imsosecret"
def hash_str(s):
  "Hashuj string s md5 enkripcijom"
  #return hashlib.md5(s.encode("utf-8")).hexdigest()
  return hmac.new(SECRET,s.encode("utf-8"),hashlib.sha256).hexdigest()
     
def make_secure_val(s):
  "Take string s, and return s,hash(s)"
  return "{},{}".format(s,hash_str(s))
  
def check_secureval(h):
  "Uzima h par s,hash(s) i proverava jeli ispravan"  
  val=h.split(",")[0] 
  if h==make_secure_val(val):
    return val

@app.route('/.json', methods=['GET', 'POST'])
def mudo():
	   return "mudo"

cache={}

@app.route('/', methods=['GET', 'POST'])
def main():
     key="stranica"
     if key in cache: 
      set("datetime_start",datetime.datetime.now())
      minutes_diff = (cache["datetime_end"] - cache["datetime_start"]).total_seconds()   
      return renderfront("","","",Reverse(cache[key]),"stranica otvorena pre "+str(minutes_diff)+" sekundi")  
     else:  
       set("datetime_start",datetime.datetime.now())
       set(key,db["arts"])
       return renderfront("","","",Reverse(cache[key]))

@app.route('/bilbija', methods=['GET', 'POST'])
def bakci():
  visits_cookie_str=request.cookies.get("visits")
  print(visits_cookie_str)
  visits=0
  if visits_cookie_str:
    cookie_val=check_secureval(visits_cookie_str)
    print(cookie_val)
    if cookie_val:
      visits=int(cookie_val)  
  visits=visits+1
  new_cookie_val=make_secure_val(str(visits))
  print(new_cookie_val)
  if visits>10000:
    resp = make_response(flask.render_template("bilbija.html",n=visits,poruka="Najjaci si"))
  else:
    resp = make_response(flask.render_template("bilbija.html",n=visits,poruka=""))  
  resp.set_cookie('visits', str(new_cookie_val))
  return resp    

app.run('0.0.0.0')