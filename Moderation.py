import datetime
import json
import random
from Utils import *
def ModQueue(Permissions):
    "Get moderation queue based on staff rank"
    ActionQueue = json.load(open("Moderation/Action.json")) #Posts marked as needs action
    ReviewQueue = json.load(open("Moderation/Review.json")) #Posts reported by users/marked as needs reviewing by staff
    CombinedQueues = ActionQueue
    CombinedQueues.update(ReviewQueue) #Combine queues
    ModQueue = []
    CombinedQueues = list(CombinedQueues.values())
    ActionQueue = list(ActionQueue.values())
    ReviewQueue = list(ReviewQueue.values())
    if Permissions == "ADMIN" or Permissions == "HIGHLEVEL" or Permissions == "OWNER":
        while len(ModQueue) <= 50 and len(CombinedQueues) > 0:
            Post = random.choice(CombinedQueues)
            ModQueue.append(Post)
            CombinedQueues.remove(Post)
    if Permissions == "MANAGER":
        while len(ModQueue) <= 50 and len(ActionQueue) > 0:
            ModQueue.append(ActionQueue[0])
            del ActionQueue[0]
    if Permissions == "MODERATOR":
        while len(ModQueue) <= 50 and len(ReviewQueue) > 0:
            ModQueue.append(ReviewQueue[0])
            del ReviewQueue[0]
    return ModQueue
def Report(Id,UserMetaData):
    "Report post by ID"
    if UserMetaData[4] == 0: #Code 0 means they have nothing affecting their reporting
        ReviewQueue = json.load(open("Moderation/Review.json"))
        Post = GetPost(Id)
        Post["Reporter"] = UserMetaData[1]
        Post["ReportPhase"] = "PendingReview"
        ReviewQueue[Id] = Post #Store post, AND reporter
        json.dump(ReviewQueue,open("Moderation/Review.json","w"))
        return "Added Report"
    if UserMetaData[4] == 1: #Code 1 means they have a time-based restriction on their reporting
        dtime = datetime.datetime().now()
        effectiveuntildate = datetime.datetime.strptime(UserMetaData[5],"%d %B %Y").time() + datetime.timedelta(days=7)
        if dtime > effectiveuntildate: #If report restriction has passed, remove block, then add report
            UserMetaData[5] = GetDate()
            UserMetaData[4] = 0
            SaveAccountData(UserMetaData)
            ReviewQueue = json.load(open("Moderation/Review.json"))
            Post = GetPost(Id)
            Post["Reporter"] = UserMetaData[1]
            Post["ReportPhase"] = "PendingReview"
            ReviewQueue[Id] = Post #Store post, AND reporter
            json.dump(ReviewQueue,open("Moderation/Review.json","w"))
            return "Added Report"
        if effectiveuntildate > dtime:
            return "Reporting is restricted on this account"
    if UserMetaData[4] == 2: #Code 2 means they are permanently blocked from reporting
        return "User is blocked from reporting"
    if UserMetaData[4] == 3: #Code 3 means they have been terminated
        return "User has been terminated"
def ApproveReport(ID):
    ReviewQueue = json.load(open('Moderation/Review.json'))
    ActionQueue = json.load(open('Moderation/Review.json'))
    ActionQueue[ID] = ReviewQueue[ID]
    ActionQueue[ID]["ReportPhase"] = "PendingAction"
    del ReviewQueue[ID]
    json.dump(ReviewQueue,open("Moderation/Review.json","w"))
    json.dump(ActionQueue,open("Moderation/Action.json","w"))
    return "Report with ID " + ID + " has been approved, and sent to next phase of moderation."
def RestrictUserReports(Handle):
    accounts = Accounts()
    for account in accounts:
        if accounts[account][1] == Handle and accounts[account][4] != 3:
            accounts[account][4] = 1 #Restrict user's reporting
            accounts[account][5] = GetDate() #Mark when user was restricted  (for unrestricting after a week)
            SaveAccountData(accounts)
            return Handle + "'s reporting has been restricted."
        if accounts[account][4] == 3:
            return Handle + " has been terminated already."
def BlockUserReports(Handle):
    accounts = Accounts()
    for account in accounts:
        if accounts[account][1] == Handle and accounts[account][4] != 3:
            accounts[account][4] = 2 #Block user reporting
            accounts[account][5] = GetDate() #Mark when user was blocked (Not Needed)
            SaveAccountData(accounts)
            return Handle + "'s reporting has been blocked."
        if accounts[account][4] == 3:
            return Handle + " has been terminated already."
def TerminateUser(Handle,Reason):
    "Terminate a user for a reason, sets status to 3 in database"
    accounts = Accounts()
    for account in accounts:
        if accounts[account][1] == Handle:
            if accounts[account][4] != 3:
                accounts[account][4] = 3 #USER IS TERMINATED
                accounts[account][5] = Reason # Reason for termination
            else:
                return "User has already been terminated"
    SaveAccountData(accounts)
    Posts = json.load(open("Users/{Handle}.json")) #Hide user page posts
    for Post in Posts:
        Posts[Post]["Available"] = False
    json.dump(Posts,open("Users/{Handle}.json"))
    Posts = json.load(open("Content/Posts.json")) #Hide posts in general storage
    for Post in Posts:
        Posts[Post]["Available"] = False
    json.dump(Posts,open("Content/Posts.json"))
    return "Terminated " + Handle
def HidePost(ID,Handle):
    "Set post as unavailable"
    Posts = json.load(open("Content/Posts.json"))
    Posts[ID]["Available"] = False
    json.dump(Posts,open("Content/Posts.json","w"))
    Posts = json.load(open("Users/{Handle}.json"))
    Posts[ID]["Available"] = False
    json.dump(Posts,open("Users/{Handle}.json","w"))
    return "Post Hidden"
def RemoveFromAQueue(ID):
    "Removes a report from the action queue"
    ActionQueue = json.load(open("Moderation/Action.json"))
    del ActionQueue[ID]
    json.dump(ActionQueue,open("Moderation/Action.json","w"))
def RemoveFromRQueue(ID):
    "Removes a report from the review queue"
    ReviewQueue = json.load(open("Moderation/Review.json"))
    del ReviewQueue[ID]
    json.dump(ReviewQueue,open("Moderation/Review.json","w"))