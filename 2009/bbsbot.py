#! /usr/bin/env python 
# -*- coding: utf-8 -*- 

"""
bbsbot.py - bot to post article on KBS-based BBS (like SMTH)
Copyright (c) 2009, J.
"""

import os, sys, re
import cookielib, urllib, urllib2 

class BBSQuery:
    def __init__(self, site='www.newsmth.net'):
        self.site = site
        self.boards = self.selectall()

    def select(self, key):  # select boards containing key
        conn = urllib.urlopen(
            'http://%s/bbssel.php?board=%s' % (self.site, key))
        text = conn.read().decode('gb2312','ignore')
        conn.close()
        L = re.findall(
            r'''
            '\<a\ href="bbsdoc\.php\?board=\w+"\>(\w+)\</a\>'
            ''', text, re.VERBOSE)
        return L

    def selectall(self):
        boards = []
        if self.site=='www.newsmth.net':
            targets = [ i+j for i in 'aeiou' for j in 'abcdefghijklmnopqrstuvwxyz']
            targets.extend(['.','tv'])
        else:
            targets = ['a','e','i','o','u','.','tv']
        
        for key in targets:
            boards.extend(self.select(key))
        
        boards = sorted(set(boards))
        return boards

    def query(self, board, userid, datewithin=7):
        conn = urllib.urlopen(
            'http://%s/bbsbfind.php?q=1&board=%s&title=&title2=&title3=&userid=%s&dt=%s' % \
            (self.site, board, userid, datewithin))
        text = conn.read().decode('gb2312','ignore')
        conn.close()
        cell = re.findall(
            r'''
            \.r\(
            '\d+',      # displayed number
            '[^']*',    # mark m/g/b/etc
            '[^']*',    # link to bbsqry.php?userid=...
            '[^']*',    # date
            '\<a\ href="bbscon\.php\?bid=\d+\&id=(\d+)"\>(.+)\</a\>'
            \)
            ''', text, re.VERBOSE)
        """
        make a list of 3-tuples (board,postid,title)
        from a list of 2-tuples (postid,title)
        """
        cell = zip((board,) * len(cell), *zip(*cell))
        return cell

    def queryall(self, userid, datewithin=5000):
        cell = []
        for board in self.boards:
            cell.extend(self.query(board, userid, datewithin))
        return cell

class BBSBot:

    def __init__(self):
        cj = cookielib.CookieJar()
        cookie_handler = urllib2.HTTPCookieProcessor(cj)
        # proxies = {'http':'http://127.0.0.1:8118/'} # use TOR
        # proxy_handler = urllib2.ProxyHandler(proxies)
        # to hide IP, uncomment the above two lines, and change the following line
        self.opener = urllib2.build_opener(cookie_handler) #, proxy_handler)
        self.opener.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)')]
        self.opener.addheaders = [('Accept-Language', 'en-US')]
        self.opener.addheaders = [('Accept', 'image/jpeg, image/gif, image/pjpeg, application/xaml+xml, 
application/x-ms-application, application/x-ms-xbap, application/x-shockwave-flash, */*')]

    def __del__(self):
        self.opener.close()

    def login(self, userid, passwd, site='www.newsmth.net'):
        self.site = site
        self.userid = userid
        login_url = 'http://%s/bbslogin.php' % site
        login_data = urllib.urlencode({'id':userid, 'passwd':passwd, 'webtype':'classic', '%CC%E1%BD 
%BB':'%B5%C7%C2%BC'})
        self.opener.open(login_url, login_data)

    def post(self, board, title, text):
        post_url = 'http://%s/bbssnd.php?board=%s&reid=0' % (self.site, board)
        post_data = urllib.urlencode({'reid':'0', 'title':title, 'signature':'0', 'text':text})
        self.opener.open(post_url, post_data)

    def edit(self, board, postid, title, text):
        """
        self.opener.open('http://%s/bbsedit.php?board=%s&id=%s&ftype=0' %
                         (self.site, board, postid))
        """
        edit_url = 'http://%s/bbsedit.php?board=%s&id=%s&ftype=0&do' % \
                   (self.site, board, postid)
        edit_data = urllib.urlencode({'title':title.encode('gb2312'),'text':text.encode('gb2312')})
        self.opener.open(edit_url, edit_data)

    def delete(self, board, postid):
        del_url = 'http://%s/bbsdel.php?board=%s&id=%s' % \
                  (self.site, board, postid)
        self.opener.open(del_url)

    def purge(self):
        q = BBSQuery(self.site)
        res = q.queryall(self.userid)
        for item in res:
            board, postid, title = item
            self.edit(board, postid, title, '')
            self.delete(board, postid)

    def logout(self):
        logout_url = 'http://%s/bbslogout.php' % self.site
        self.opener.open(logout_url)

    
def test():
    cfgfile = open('.'.join(os.path.abspath(sys.argv[0]).split('.')[:-1]) + '.cfg')    
    lines = cfgfile.read().decode('utf-8-sig').split('\n')
    cfgfile.close()
    
    lines = [ line for line in lines if line and line[0]!=';' ]
    conf = dict(map(lambda _:_.split('=',1), lines))
    
    title = conf['title']
    infile = open(conf['text'], 'r')
    text, dummy = infile.read().decode('utf-8-sig'), infile.close()
    
    bot = BBSBot()
    bot.login(conf['myid'], conf['mypasswd'], conf['site'] )
    bot.post(conf['board'], title.encode('gb2312'), text.encode('gb2312'))
    bot.logout()

if __name__=='__main__':
    test()
