import datetime
import json
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
import random
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
def SummarizeUser(Handle: str):
    "Finds, and cleans up a list of frequent subjects, or topics that a user liked, also saves to User Algorithm Data"
    text = ""
    LikedPosts = json.load(open("UserAlgorithm/{}.json".format(Handle),"r"))["Liked"]
    Posts = json.load(open("Content/Posts.json"))
    for PostID in LikedPosts:
        text += " " + Posts[PostID]["Content"]
    tokens = word_tokenize(text)
    lowercase_tokens = [t.lower() for t in tokens]
    bagofwords_1 = Counter(lowercase_tokens)
    alphabets = [t for t in lowercase_tokens if t.isalpha()]

    words = stopwords.words("english")
    stopwords_removed = [t for t in alphabets if t not in words]

    lemmatizer = WordNetLemmatizer()

    lem_tokens = [lemmatizer.lemmatize(t) for t in stopwords_removed]

    bag_words = Counter(lem_tokens)
    Topics = bag_words.most_common(6)
    TotalTopics = 0
    TopicsBalanced = {}
    for Topic in Topics:
        TotalTopics += Topic[1]
    for Topic in Topics:
        TopicsBalanced[Topic[0]] = Topic[1]/TotalTopics
    UserAlgorithm = json.load(open("UserAlgorithm/{}.json".format(Handle)))
    UserAlgorithm["LastSummarizationResult"] = TopicsBalanced
    UserAlgorithm["LastSummarizationDate"] = GetDate()
    json.dump(UserAlgorithm,open("UserAlgorithm/{}.json".format(Handle),"w"))
    return TopicsBalanced
def SummarizePost(Post: str):
    "Finds, and cleans up a list of frequent subjects, or topics in a Post"
    text = Post
    tokens = word_tokenize(text)
    lowercase_tokens = [t.lower() for t in tokens]
    bagofwords_1 = Counter(lowercase_tokens)
    alphabets = [t for t in lowercase_tokens if t.isalpha()]

    words = stopwords.words("english")
    stopwords_removed = [t for t in alphabets if t not in words]

    lemmatizer = WordNetLemmatizer()

    lem_tokens = [lemmatizer.lemmatize(t) for t in stopwords_removed]

    bag_words = Counter(lem_tokens)
    Topics = bag_words.most_common(6)
    TotalTopics = 0
    TopicsBalanced = {}
    for Topic in Topics:
        TotalTopics += Topic[1]
    for Topic in Topics:
        TopicsBalanced[Topic[0]] = Topic[1]/TotalTopics
    return TopicsBalanced
def PercentMatch(PostId,Handle):
    UserSummary = json.load(open("UserAlgorithm/{}.json".format(Handle)))
    Posts = json.load(open("Content/Posts.json","r"))
    if UserSummary["LastSummarizationDate"] != GetDate():
        SummarizeUser(Handle)
    UserSummary = json.load(open("UserAlgorithm/{}.json".format(Handle)))["LastSummarizationResult"]
    PostSummary = Posts[str(PostId)]["AlgorithmSummarization"]
    Matches = {}
    for PTopic in PostSummary:
        for UTopic in UserSummary:
            if PTopic == UTopic:
                Matches[UTopic] = PostSummary[PTopic]
    MatchP = 0 #Percentage of Post that matches User's interest e.g. 1 = Post matches User 100%
    for M in Matches:
        MatchP += Matches[M] #Add the percentage of each topic up
    #return str((UserSummary,PostSummary,Matches,MatchP)) 
    #MatchP should be around .7 - .9 to allow for posts with new keywords to appear in feed
    #If MatchP gets too high, posts will contain around the same terms, in different orders #BORING
    return MatchP
def PostFeed(Handle):
    "Recommends post using Algorithm"
    #Load posts, pick random ones, check for relevancy, if match; add to feed, repeat until feed is full
    Posts = json.load(open("Content/Posts.json"))
    Posts = Posts.values() #To simplify using the random function with the posts dictionary
    Posts = list(Posts)
    PostFeed = {}
    Matched = 0
    Filled = 0
    for x in range(500):
        if len(Posts) > 0:
            PPost = random.choice(Posts)
            if .9 >= PercentMatch(PPost["ID"],Handle) >= .7:
                PostFeed[PPost["ID"]] = PPost
                Matched += 1
                Posts.remove(PPost)
        else:
            break
    if 20 > len(PostFeed):
        for x in range(20 - len(PostFeed)):
            if len(Posts) > 0:
                Post = random.choice(Posts)
                PostFeed[Post["ID"]] = Post
                Filled += 1
                Posts.remove(Post)
            else:
                break
    return PostFeed
def GetDate():
    "Gets date in Greenwich Meridian Time (to keep things standard)"
    CDate = datetime.datetime.now()
    Date = ""
    Date += str(CDate.day) + " "
    Date += str(CDate.month) + " "
    Date += str(CDate.year) + " "
    return Date