from flask import Markup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
from functools import wraps
from flask import Response
import os
from flask import Flask, session, render_template, request, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#if not os.getenv("DATABASE_URL"):
   # raise RuntimeError("DATABASE_URL is not set")



def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'SECRET' and password == 'SECRET'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
scope = ['SECRET']
creds = ServiceAccountCredentials.from_json_keyfile_name('data.json', scope)
client = gspread.authorize(creds)
sheet = client.open('Internship_Record').sheet1
app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("SECRET")
db = scoped_session(sessionmaker(bind=engine))
#headcode="<tr>"
#tablebody="<tr>"
@app.route("/")
def index():
    valueslist = sheet.col_values(1)
    confirmedCount=str(valueslist.count("1"))
    pendingCount=str(valueslist.count("0"))
    return render_template("index.html",
        totalStudents="91",
        confirmedStudents=confirmedCount,
        pendingStudents=pendingCount,)

@app.route("/stats", methods=["GET", "POST"])
@requires_auth
def stats():
    headcode="<table><tr>"
    tablebody="<tr>"
  #  session.clear()
    if request.method == "POST":
       # print("I am inside stats call")
        value="selected"
        try:
            cell_list = sheet.findall(value)
           
            valueslist = sheet.col_values(2)
            print(valueslist[1])
            selectedCountInt=valueslist.count("1")
            selectedCount=str(selectedCountInt)
            NotselectedCountInt=valueslist.count("0")
            NotselectedCount=str(NotselectedCountInt)
            #count=rowHarsh.len()
            headcode=headcode+''.join("<th>"+"Total Students"+"</th>")
            tablebody=tablebody+''.join("<td>"+"93"+"</td>")
            headcode=headcode+''.join("<th>"+"Confirmed Cases"+"</th>")
            tablebody=tablebody+''.join("<td>"+selectedCount+"</td>")
            headcode=headcode+''.join("<th>"+"Unplaced"+"</th>")
            tablebody=tablebody+''.join("<td>"+NotselectedCount+"</td>")
          #  headcode=headcode+''.join("<th>"+""+"</th>")
          #  tablebody=tablebody+''.join("<td>"+"93"+"</td>")
            headcode+="</tr>"
            tablebody+="</tr>"
           # Adding a comment for test 
           # print(headcode)
           # print("Hello")
            tablecode=Markup(headcode+tablebody)
        except gspread.exceptions.CellNotFound:  # or except gspread.CellNotFound:
            return render_template("error.html",message="Roll Number Not Found, Please Check Again!")
       # return headcode
       
        return render_template("login.html",sprdata=tablecode)

    return render_template("login.html") 

@app.route("/student")
def student_sec():
    return render_template("register.html")

@app.route("/stuLoginSubmit", methods=["GET", "POST"])
def loginSubmit():
    session.clear()
    if request.method == "POST":
        if not request.form.get("sapid"):
            return render_template("error.html", message="Please Provide SAPID")
        if not request.form.get("password"):
            return render_template("error.html", message="must provide password")
        rows = db.execute("SELECT * FROM data WHERE sapid = :sapid",
                            {"sapid": request.form.get("sapid")})
        result = rows.fetchone()
        if result is None or not (result[1]==request.form.get("password")):
            return render_template("error.html", message="Invalid Username or Password")                
        session["sap_id"] = result[4]
        session["roll_no"] = result[5]
        session["email_value"] = result[2]
        session["user_name"] = result[0]  
        session["github_url"] = result[6]
        session["contact_value"] = result[3]
        session["resume_url"] = result[7]
        session["linkedin_url"] = result[8]
        return render_template("dashboard.html", 
        stu_name=session["user_name"],
        sap_id=session["sap_id"],
        github_url=session["github_url"],
        linkedin_url=session["linkedin_url"],
        resume_url=session["resume_url"],
        roll_no= session["roll_no"],
        contact_value= session["contact_value"],
        email_value=session["email_value"]
        ) 

    return render_template("login.html")      

@app.route("/loginSubmit", methods=["GET", "POST"])
@requires_auth
def showData():
    valueslist = sheet.col_values(1)
    confirmedCount=str(valueslist.count("1"))
    pendingCount=str(valueslist.count("0"))
    headcode="<table><tr>"
    tablebody="<tr>"
  #  session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("error.html", message="Please Enter ROLL NUMBER")
        roll=request.form.get("username")
        try:
            cell = sheet.find(roll)
            val=cell.row
            rowHarsh=sheet.row_values(val)
            count=len(rowHarsh)
            for i in range (1,count):
                if(rowHarsh[i]!=""):
                  # print(rowHarsh[i])
                   headcode=headcode+''.join("<th>"+sheet.row_values(1)[i]+"</th>")
                   tablebody=tablebody+''.join("<td>"+rowHarsh[i]+"</td>")
            headcode+="</tr>"
            tablebody+="</tr>"
            print(headcode)
            tablecode=Markup(headcode+tablebody)
        except gspread.exceptions.CellNotFound:  # or except gspread.CellNotFound:
            return render_template("error.html",message="Roll Number Not Found, Please Check Again!")
       # return headcode
       
        return render_template("login.html",sprdata=tablecode, totalStudents="91",
        confirmedStudents=confirmedCount,
        pendingStudents=pendingCount,
        raw_link="https://docs.google.com/spreadsheets/d/1MYiPmH67D8d7c6TibFEEyslkhYmdXz8697DU3VMgnfw/edit?usp=sharing")

    return render_template("login.html") 

@app.route("/stulogin", methods=["GET", "POST"])
def stulogin():
    if 'sap_id' in session:
        return render_template("dashboard.html", 
        stu_name=session["user_name"],
        sap_id=session["sap_id"],
        github_url=session["github_url"],
        linkedin_url=session["linkedin_url"],
        resume_url=session["resume_url"],
        roll_no= session["roll_no"],
        contact_value= session["contact_value"],
        email_value=session["email_value"]
        )

    return render_template("stulogin.html")
       
@app.route("/updateProfile",methods=["GET", "POST"])
def updateProfile():
    if request.method == "POST":

        # Ensure mandatory data was submitted
        if not request.form.get("resume"):
            return render_template("error.html", message="Must provide Resume Link")
        if not request.form.get("github"):
            return render_template("error.html", message="Must provide Github URL")
        if not request.form.get("email"):
            return render_template("error.html", message="Must provide Email")
        if not request.form.get("linkedin"):
            return render_template("error.html", message="Must provide Linkedin URL")
        if not request.form.get("contact"):
            return render_template("error.html", message="Must provide Contact")

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("error.html", message="Must provide password")

        # Hash user's password to store in DB
        #hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        hashedPassword = request.form.get("password")
        rows = db.execute("SELECT * FROM data WHERE sapid = :sapid",
                            {"sapid": session["sap_id"]})
        result = rows.fetchone()
        if result is None or not (result[1]==request.form.get("password")):
            return render_template("error.html", message="Invalid Username or Password")  
        
        # Insert register into DB
        db.execute("UPDATE data set (email,contact,sapid,github,resume,linkedin)=(:email, :contact, :sapid, :github, :resume, :linkedin) where sapid= (:sapid)",
                            {
                             "email":request.form.get("email"),
                             "contact":request.form.get("contact"),
                             "sapid":session["sap_id"],
                             "github":request.form.get("github"),
                             "resume":request.form.get("resume"),
                             "linkedin":request.form.get("linkedin")
                             })

        # Commit changes to database
        db.commit()

        flash('Account created', 'info')
        session.clear()
        return render_template("success.html", message="Congratulations! Details Have been Updated")


    
@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")


@app.route("/registerSubmit", methods=["GET", "POST"])
def registerSubmit():
    """ Register user """
    
    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")

        # Query database for username
        userCheck = db.execute("SELECT * FROM data WHERE username = :username",
                          {"username":request.form.get("username")}).fetchone()

        # Check if username already exist
        if userCheck:
            return render_template("error.html", message="username already exists")

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("error.html", message="Must provide password")
        if not request.form.get("sapid"):
            return render_template("error.html", message="Must provide SAPID")
        if not request.form.get("roll"):
            return render_template("error.html", message="Must provide Roll")
        if not request.form.get("github"):
            return render_template("error.html", message="Must provide Github URL")
        if not request.form.get("resume"):
            return render_template("error.html", message="Must provide Link to Resume")

        if not request.form.get("email"):
            return render_template("error.html", message="Please Enter Email")

        if not request.form.get("contact"):
            return render_template("error.html", message="Please enter Contact")

        # Hash user's password to store in DB
        #hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        hashedPassword = request.form.get("password")
        
        # Insert register into DB
        db.execute("INSERT INTO data VALUES (:username, :password, :email, :contact, :sapid, :roll, :github, :resume, :linkedin)",
                            {"username":request.form.get("username"), 
                             "password":hashedPassword,
                             "email":request.form.get("email"),
                             "contact":request.form.get("contact"),
                             "sapid":request.form.get("sapid"),
                             "roll":request.form.get("roll"),
                             "github":request.form.get("github"),
                             "resume":request.form.get("resume"),
                             "linkedin":request.form.get("linkedin")
                             })

        # Commit changes to database
        db.commit()

        flash('Account created', 'info')
        return render_template("dashboard.html", message="Congratulations! You are Registered")

        # Redirect user to login page

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("register.html")
