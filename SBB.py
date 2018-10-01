#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '0.03'
__author__  = 'Julien G. (@bfishadow)'

'''
This script will download all artcles from a specific Sina Blog.
Based on the XML file, you might importing into blogger.
Or simply save them anywhere as archives.
'''

import sys, urllib.request 
from time import strftime

def getBetween(str, str1, str2):
  strOutput = str[str.find(str1)+len(str1):str.find(str2)]
  return strOutput

strUsage =  "Usage: SBB.py <Sina blog URL> [asc]\n\nExample:\nSBB.py http://blog.sina.com.cn/gongmin desc\nSBB.py http://blog.sina.com.cn/u/1239657051\n"

#Step 0: get target blog homepage URL
try :
  strUserInput =sys.argv[1]
except :
  print (strUsage)
  sys.exit(0)

try :
  strUserOrder = sys.argv[2]
except :
  strUserOrder = ""

#The URL *must* start with http://blog.sina.com.cn/, otherwise the universe will be destroied XD
if strUserInput.find("http://blog.sina.com.cn/") == -1 or len(strUserInput) <= 24 :
  print(strUsage)
  print(strUserInput)
  sys.exit(0)

#Get UID for the blog, UID is critical.
objResponse = urllib.request.urlopen(strUserInput)
strResponse = objResponse.read().decode('utf-8')
objResponse.close()

strUID = getBetween(getBetween(strResponse, "format=html5;", "format=wml;"), "/blog/u/", '">')
print('用户ID '+strUID)
 
if len(strUID) > 10 :
  print(strUsage)
  sys.exit(0)

#Here's the UID. Most of the UID is a string of ten digits.
strTargetUID = strUID


#Step 1: get list for first page and article count
strTargetBlogListURL = "http://blog.sina.com.cn/s/articlelist_" + strTargetUID + "_0_1.html"

objResponse = urllib.request.urlopen(strTargetBlogListURL)
strResponse = objResponse.read().decode('utf-8')
objResponse.close()

strBlogPostList = getBetween(getBetween(strResponse,"$blogArticleSortArticleids","$blogArticleCategoryids"), " : [", "],")
strBlogPostID = strBlogPostList

strBlogPageCount = getBetween(getBetween(strResponse, "全部博文", "<!--第一列end-->"),"<em>(", ")</em>")
intBlogPostCount = int(strBlogPageCount)  #article count
intPageCount = int(intBlogPostCount/50)+1 #page count, default page size is 50

strBlogName = getBetween(getBetween(strResponse, "<title>", "</title>"), "博文_", "_新浪博客")


#Step 2: get list for the rest of pages
for intCurrentPage in range(intPageCount - 1) :
  strTargetBlogListURL = "http://blog.sina.com.cn/s/articlelist_" + strTargetUID + "_0_" + str(intCurrentPage + 2) + ".html"
  objResponse = urllib.request.urlopen(strTargetBlogListURL)
  strResponse = objResponse.read().decode('utf-8')
  strBlogPostList = getBetween(getBetween(strResponse,"$blogArticleSortArticleids","$blogArticleCategoryids"), " : [", "],")
  strBlogPostID = strBlogPostID + "," + strBlogPostList
  objResponse.close()

strBlogPostID = strBlogPostID.replace('"','')
#strBlogPostID <- this string has all article IDs for current blog


#Step 3: get all articles one by one

arrBlogPost = strBlogPostID.split(',')
if strUserOrder != "desc" :
  arrBlogPost.reverse()

intCounter    = 0
strHTML4Index = ""


#new a XML file
strLocalFilename = "BLog_sina_user" + str(strUID) +"_2018.xml" 
objFile = open(strLocalFilename, "wb+")
strXML4Post = '<?xml version="1.0" encoding="UTF-8"?> \n<root>'
objFile.write(strXML4Post.encode('utf-8'));
objFile.close()




for strCurrentBlogPostID in arrBlogPost :
  intCounter  = intCounter + 1
  strTargetBlogPostURL = "http://blog.sina.com.cn/s/blog_" + strCurrentBlogPostID + ".html"
  objResponse = urllib.request.urlopen(strTargetBlogPostURL)
  strPageCode = objResponse.read().decode('utf-8')
  objResponse.close

  #Parse blog title
  strBlogPostTitle = getBetween(strPageCode, "<title>", "</title>")
  strBlogPostTitle = strBlogPostTitle.replace("_新浪博客", "")
  strBlogPostTitle = strBlogPostTitle.replace("_" + strBlogName, "")

  #Parse blog post
  strBlogPostBody  = getBetween(strPageCode, "<!-- 正文开始 -->", "<!-- 正文结束 -->")
  strBlogPostBody  = strBlogPostBody.replace("http://simg.sinajs.cn/blog7style/images/common/sg_trans.gif", "")
  strBlogPostBody  = strBlogPostBody.replace('src=""', "")
  strBlogPostBody  = strBlogPostBody.replace("real_src =", "src =")

  #Parse blog timestamp
  strBlogPostTime  = getBetween(strPageCode, '<span class="time SG_txtc">(', ')</span><div class="turnBoxzz">')
  
  #Parse blog class
  strBlogPostClass  = getBetween(getBetween(getBetween(strPageCode, '<td class="blog_class', 'class="articalContent') ,'\n									','</td>'),'html">','</a>')
  
  #Parse blog tag
  strBlogPostTag  = getBetween(getBetween(getBetween(strPageCode, 'class="blog_tag"', 'td class="blog_class') ,'</script>\n			','</td>') ,'target="_blank">','</a>')
 
  
  #Write into local XML file
  strXML4Post = "\n <PostItem>\n <title>" + strBlogPostTitle + "</title>\n <BlogName>" + strBlogName +'</BlogName>\n <BlogClass>' + strBlogPostClass + '</BlogClass>\n<BlogTag>' + strBlogPostTag + '</BlogTag>\n<content><![CDATA[' + "\n<p>By: <em>" + strBlogName + "</em> 原文发布于：<em>" + strBlogPostTime + "</em></p>\n" + strBlogPostBody + ']]></content>\n</PostItem>\n'
   
  objFileArticle = open(strLocalFilename, "ab+")
  objFileArticle.write(strXML4Post.encode('utf-8'));
  objFileArticle.close()


  strHTML4Index = strHTML4Index + '<li><a href="' + strLocalFilename + '">' + strBlogPostTitle + '</a></li>\n'

  print (intCounter , "/", intBlogPostCount)
  


strXML4Post = '</root>\n'
objFile = open(strLocalFilename, "ab")
objFile.write(strXML4Post.encode('utf-8'));  
objFile.close()
  


strCurrentTimestamp = str(strftime("%Y-%m-%d %H:%M:%S"))
strHTML4Index = '<html>\n<head>\n<meta charset="utf-8" />\n<title>' + strBlogName + "博客文章汇总</title>\n</head>\n<body>\n<h2>新浪博客：" + strBlogName + "</h2>\n<p>共" + str(intBlogPostCount) + "篇文章，最后更新：<em>" + strCurrentTimestamp + "</em></p>\n<ol>\n" + strHTML4Index + "\n</ol>\n</body>\n</html>\n"
objFileIndex = open( "BLog_sina_user" + strUID + "_index.html", "wb")
objFileIndex.write(strHTML4Index.encode('utf-8'));
objFileIndex.close
