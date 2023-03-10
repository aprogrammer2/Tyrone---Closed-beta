import datetime
import requests
import bleach
import json
import hashlib
import random
import os
from Algorithm import SummarizePost

def Accounts():
    return json.load(open("Accounts.json"))
def Hash(Data: any):
    return hashlib.sha256(Data.encode()).hexdigest()
def NewAccount(Handle: str, Displayname: str, Password, Email):
    Password = Hash(Password)
    cookie = NewCookie()
    Handle = Handle.lower()
    Handle = FilterText(Handle)
    Displayname = FilterText(Displayname)
    ReportingStatus = 0
    ReportingStatusDate = GetDate()
    if not IsHandleAvailable(Handle):
        return "Handle Not Available",False
    UserMetaData = [Displayname,Handle,Password,"USER",ReportingStatus,ReportingStatusDate]
    accountdata = Accounts()
    accountdata[cookie[1]] = UserMetaData
    SaveAccountData(accountdata)
    f = open("Users/{}.json".format(Handle),"w")
    f.write("{}")
    f = open("UserAlgorithm/{}.json".format(Handle),"w")
    f.write('{"Liked" : [], "Disliked" : [], "LastSummarizationResult" : [], "LastSummarizationDate" : []}')
    f.close()
    return cookie[0],True
def NewCookie():
    #Creates a new cookie, and a hashed version for saving
    CurrentCookies = dict.keys(Accounts())
    ncookie = Hash(str(random.randbytes(100)))
    while ncookie in CurrentCookies:
        ncookie = str(random.randbytes(100))
        hashedncookie = Hash(ncookie)
    hashedncookie = Hash(ncookie)
    return [ncookie,hashedncookie]
def IsHandleAvailable(Handle):
    accounts = Accounts()
    for account in accounts:
        if accounts[account][1] == Handle:
            return False
    return True
def SaveAccountData(AccountData: dict):
    """ WTH????????????! WILL OVERIDE EVERY ACCOUNT IF EXECUTED WTH
        ^^^^^ is my reaction when I mistakenly thought this was for saving just a single accounts data
        Don't make that mistake!
    """
    with open("Accounts.json","w+") as f: 
        AccountData = json.dumps(AccountData)
        #SAVE IT
        f.write(AccountData)
def MatchToAccount(Handle,Password):
    Password = Hash(Password)
    accounts = Accounts()
    for account in accounts:
        if accounts[account][1] == Handle and accounts[account][2] == Password:
            return [account,accounts[account]]
    return False
def GetUserPage(Handle: str):
    with open("Users/{}.json".format(Handle),"r") as f:
        return json.load(f)
def Login(Handle,Password):
    AccountData = MatchToAccount(Handle,Password)
    if AccountData:
        accounts = Accounts()
        ncookie = NewCookie()
        AccountEntry = accounts[AccountData[0]]
        del accounts[AccountData[0]]
        accounts[ncookie[1]] = AccountEntry
        with open("Accounts.json","w") as f:
            json.dump(accounts,f)
        return ncookie[0]
def FilterText(text: str):
    try:
        return requests.get("https://www.purgomalum.com/service/plain?text=" + text).text
    except:
        return text #Do not disrupt fresh content if filter does not respond
def NewPost(RawText: str,Cookie: str):
    accounts = Accounts()
    if not accounts[Hash(Cookie)]:
        return "Account Not Found"
    if 10 > len(RawText):
        return "Post too short! Must be at least 10 characters!"
    Text = bleach.clean(RawText)
    Text = FilterText(Text)
    PostID = NewID()
    PostData = {}
    PostData["Content"] = Text
    PostData["Available"] = True
    PostData["Date"] = str(datetime.datetime.now(datetime.timezone.utc))
    PostData["User"] = accounts[Hash(Cookie)][0]
    PostData["Handle"] = accounts[Hash(Cookie)][1]
    PostData["NegativeReviewers"] = []
    PostData["PositiveReviewers"] = []
    PostData["AlgorithmSummarization"] = SummarizePost(Text) 
    PostData["ID"] = PostID
    SavePost(PostData,PostID)
    return "Success"
def SavePost(PostData: dict, ID: int):
    Posts = json.load(open("Content/Posts.json","r"))
    Posts[ID] = PostData
    json.dump(Posts,open("Content/Posts.json","w+"))
    Posts = json.load(open("Users/{}.json".format(PostData["Handle"].upper()),"r"))
    Posts[ID] = PostData
    json.dump(Posts,open("Users/{}.json".format(PostData["Handle"].upper()),"w+"))
def NewID():
    return len(json.load(open("Content/Posts.json"))) + 1
def Like(Handle,ID):
    Posts = json.load(open("Content/Posts.json","r"))
    UAlgorithmData = json.load(open("UserAlgorithm/{}.json".format(Handle),"r"))
    if Posts[ID]:
        PostData = Posts[ID]
        if Handle not in PostData["PositiveReviewers"]:
            PostData["PositiveReviewers"].append(Handle)
            if Handle in PostData["NegativeReviewers"]:
                PostData["NegativeReviewers"].remove(Handle)
            if ID in UAlgorithmData["Disliked"]:
                UAlgorithmData["Disliked"].remove(ID)
            UAlgorithmData["Liked"].append(ID)
    json.dump(UAlgorithmData,open("UserAlgorithm/{}.json".format(Handle),"w"))
    SavePost(PostData,ID)
    return "Success"  
def Dislike(Handle,ID):
    Posts = json.load(open("Content/Posts.json","r"))
    UAlgorithmData = json.load(open("UserAlgorithm/{}.json".format(Handle),"r"))
    if Posts[ID]:
        PostData = Posts[ID]
        if Handle not in PostData["NegativeReviewers"]:
            PostData["NegativeReviewers"].append(Handle)
            if Handle in PostData["PositiveReviewers"]:
                PostData["PositiveReviewers"].remove(Handle)
            if ID in UAlgorithmData["Liked"]:
                UAlgorithmData["Liked"].remove(ID)
            UAlgorithmData["Disliked"].append(ID)
    json.dump(UAlgorithmData,open("UserAlgorithm/{}.json".format(Handle),"w"))
    SavePost(PostData,ID)
    return "Success"     
def CalculateScore(Post):
    "Calculate score of a post (for templating the home page)"
    return len(Post["NegativeReviewers"]) + len(Post["PositiveReviewers"])
def GetPost(ID):
    Posts = json.load(open("Content/Posts.json"))
    try:
        return Posts[ID]
    except:
        return "Post not found"
def GetDate():
    "Gets date in Greenwich Meridian Time (to keep things standard)"
    CDate = datetime.datetime.now()
    Date = ""
    Date += str(CDate.day) + " "
    Date += str(CDate.month) + " "
    Date += str(CDate.year) + " "
    return Date