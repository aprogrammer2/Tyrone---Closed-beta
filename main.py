from flask import *
from Utils import *
from Algorithm import *
from Moderation import *
import os
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "ProfileImages/"
app.config["MAX_CONTENT-PATH"] = 5000
@app.route("/")
def index():
    if "SID" in request.cookies:
        accounts = Accounts()
        hcookie = Hash(request.cookies["SID"])
        if hcookie in accounts:
            UserMetaData = accounts[hcookie]
            Username = UserMetaData[0]
            Handle = UserMetaData[1]
            Permissions = UserMetaData[3]
            return render_template("index.html",Username=Username,Handle=Handle,Permissions=Permissions,PostFeed=PostFeed(Handle))
    return render_template("index.html")
@app.route("/post/<ID>")
def PostPage(ID):
        if "SID" in request.cookies:
            accounts = Accounts()
            hcookie = Hash(request.cookies["SID"])
            if hcookie in accounts:
                Post = GetPost(ID)
                if Post["Available"] == True:
                    return render_template("Post.html",Post=Post)
                if Post["Handle"] != accounts[hcookie][1]:
                    return make_response("Not Authorized",405)
                if Post["Handle"] == accounts[hcookie][1]:
                    return render_template("Post.html",Post=Post,showdeleted=True)
@app.route("/join",methods=["GET","POST"])
def JoinPage():
    if request.method == "GET":
        return render_template("Join.html")
    if request.method == "POST":
        Displayname = request.form["displayname"]
        Handle = request.form["handle"]
        Password = request.form["password"]
        Cookie,Success = NewAccount(Handle,Displayname,Password)
        if Cookie == "Handle Not Available":
            return "<script>alert('That handle is not available!');location=location</script>"
        else:
            if Success == True:
                r = make_response("<script>location='/'</script>")
                r.set_cookie("SID",Cookie)
                PI = request.files["ProfileImage"]
                PI.save( "ProfileImages/" + Handle + ".png")
                return r
            else:
                return "<script>alert( 'Unknown Error, that is not accounted for! Try again :(' )</script>"
@app.route("/login",methods=["GET","POST"])
def LoginPage():
    if request.method == "GET":
        if "SID" in request.cookies:
            if Hash(request.cookies["SID"]) in Accounts():
                return redirect("/")
            else:
                return render_template("Login.html")
        else:
            return render_template("Login.html")
    if request.method == "POST":
        ncookie = Login(request.form["handle"].lower(),request.form["password"])
        if ncookie:
            r = make_response(redirect("/"))
            r.set_cookie("SID",ncookie)
            return r
        else:
            return "<script>alert('Wrong Username, Or Password'); location=location</script>"
@app.route("/logout")
def LogOutPage():
    r = make_response(redirect("/"))
    r.set_cookie("SID","")
    return r
@app.route("/user/<handle>")
def UserPage(handle):
    return render_template("Profile.html",Posts=GetUserPage(handle),Handle=handle)
@app.route("/user/<handle>/image")
def UserImage(handle):
    return send_file("ProfileImages/" + handle + ".png")
@app.route("/post",methods=["GET","POST"])
def NewPostPage():
    if request.method == "GET":
        return render_template("NewPost.html")
    if request.method == "POST":
        r = NewPost(request.form["PostContent"],request.cookies["SID"])
        if r == "Success":
            return redirect("/")
        else:
            return r
        #Run post through filter, and sanitize, store in general posts folder, and in personal file. 
        # If deleted mark as deleted just in case (never gonna happen lol)
@app.route("/like/<ID>")
def LikePost(ID):
    if Hash(request.cookies["SID"]) in Accounts():
            UserMetaData = Accounts()[Hash(request.cookies["SID"])]
            Handle = UserMetaData[1]
            Like(Handle,ID)
            return "Proccessed"
    else:
        return make_response("Not Authorized",403)
@app.route("/dislike/<ID>")
def DisLikePost(ID):
    if Hash(request.cookies["SID"]) in Accounts():
            UserMetaData = Accounts()[Hash(request.cookies["SID"])]
            Handle = UserMetaData[1]
            Dislike(Handle,ID)
            return "Proccessed"
    else:
        return make_response("Not Authorized",403)
@app.route("/report/<ID>")
def ReportPost(ID):
    if Hash(request.cookies["SID"]) in Accounts():
        UserMetaData = Accounts()[Hash(request.cookies["SID"])]
        return Report(ID,UserMetaData)
    else:
        return make_response("Not Authorized",403)
@app.route("/staff/dashboard")
def StaffIndex():
    if "SID" in request.cookies:
        accounts = Accounts()
        hcookie = Hash(request.cookies["SID"])
        if hcookie in accounts:
            UserMetaData = accounts[hcookie]
            Username = UserMetaData[0]
            Handle = UserMetaData[1]
            Permissions = UserMetaData[3]
            if Permissions != "USER":
                mqueue = ModQueue(Permissions)
                return render_template("staff.html",Username=Username,Handle=Handle,Permissions=Permissions,ModQueue=mqueue)
            else:
                return make_response("Not Authorized",403)
    return make_response("Not Authorized",403)
@app.route("/staff/approvereport/<ID>")
def ApproveReportAPI(ID):
    return ApproveReport(ID)
@app.route("/staff/restrictreport/<Handle>/<ID>")
def RestrictUserReportsAPI(Handle,ID):
    RemoveFromAQueue(ID)
    return RestrictUserReports(Handle)
@app.route("/staff/blockreport/<Handle>/<ID>")
def BlockUserReportsAPI(Handle,ID):
    RemoveFromAQueue(ID)
    return BlockUserReports(Handle)
@app.route("/staff/terminate/<Handle>/<Reason>/<ID>")
def TerminateUserAPI(Handle,Reason,ID):
    TerminateUser(Handle,Reason)
    RemoveFromAQueue(ID)
    return "User Terminated"
@app.route("/staff/hidepost/<ID>")
def HidePostAPI(ID):
    HidePost(ID)
    RemoveFromAQueue(ID)
    return "Post Hidden"
@app.route("/staff/absolvepost/<ID>")
def AbsolvePostAPI(ID):
    RemoveFromAQueue(ID)
    return "Post Absolved"
@app.route("/staff/absolvereport/<ID>")
def AbsolveReportAPI(ID):
    RemoveFromRQueue(ID)
    return "Report Absolved"
app.run()