#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
bbscrawler.py - a simple multithreaded KBS crawler
Copyright (c) 2009, J.
"""

import collections
import hashlib
import re
import os, sys
import threading, Queue
import urllib, urllib2


class Saver:
        def __init__(self):
            self.mode_, self.encoding_ = 'w', 'utf-8-sig'

        def filename(self, filename):
            self.filename_ = filename
            return self

        def mode(self, mode):
            self.mode_ = mode
            return self

        def encoding(self, encoding):
            self.encoding_ = encoding
            return self

        def save(self, text):
            file = open(self.filename_, self.mode_)
            file.write(text.encode(self.encoding_))
            file.close()


class BBSCrawler:

    def __init__(self, site, board, num_threads=10):
        self.site, self.board = site, board
        conn = urllib.urlopen(
            'http://%s/bbsdoc.php?board=%s' % (self.site, self.board))
        text = conn.read().decode('gb2312','ignore')
        conn.close()
        
        res = re.search(
            r'''
            docWriter\('[^']*',(\d+),\d+,\d+,\d+,(\d+),\d+,'[^']*',\d+,\d+\)
            ''',
            text, re.VERBOSE)
        self.bid, self.num_pages = res.group(1), res.group(2)
        self.pageQueue, self.pidQueue = Queue.Queue(), Queue.Queue()
        self.num_threads = num_threads

    def crawl_pid(self):
        while True:
            my_pages = self.pageQueue.get()
            if my_pages:
                if not isinstance(my_pages, collections.Iterable) or \
                   isinstance(my_pages, basestring):
                    my_pages = [my_pages]
                my_pids = []
                for pp in my_pages:
                    conn = urllib.urlopen(
                        'http://%s/bbsdoc.php?board=%s&page=%s' % \
                        (self.site, self.board, pp))

                    """
                    raw = conn.read()
                    re.sub('\x1b\[[0-9]*((?<=[0-9]);[0-9]+)*m',
                           '',
                           raw)
                    """

                    text = conn.read().decode('gb2312','ignore')
                    conn.close()
        
                    cell = re.findall(
                        r'''
                        \.o\(
                        (\d+),\d+,('[^']*'),'[^']*',\d+,('[^']*'),\d+,\d+,\d+
                        \)
                        ''',
                        text, re.VERBOSE)
                    pids, userids, titles = zip(*cell)
                    my_pids.extend(pids)
                self.pidQueue.put(my_pids)
                self.pageQueue.task_done()

    def crawl_keyword(self, key):                    
        saver = Saver()
        while True:
            my_pids = self.pidQueue.get()
            if my_pids:
                if not isinstance(my_pids, collections.Iterable) or \
                   isinstance(my_pids, basestring):
                    my_pids = [my_pids]
                my_posts = []
                for pid in my_pids:
                    conn = urllib.urlopen(
                        'http://%s/bbscon.php?bid=%s&id=%s' % \
                        (self.site, self.bid, pid))
                    text = conn.read().decode('gb2312','ignore')
                    conn.close()
                    res = re.search(
                        "prints\('(.*)'\);o\.h\(0\);o\.t\(\);", text)
                    if res:
                        post = res.group(1)
                        post.replace('\\r','').replace('\\n','\n')
                        if key in post:
                            saver.filename(
                                os.path.sep.join([self.outpath, pid + '.txt'])
                                ).mode('w').save(post)
                self.pidQueue.task_done()

    def crawl(self, key='', pages=[]):  # normal mode
        if not pages:
            pages = range(1, int(self.num_pages) + 1)
        else:
            pages = sorted(pages)

        digest = hashlib.md5('|'.join(map(str,pages))).hexdigest()
        outpath = os.path.sep.join(
            [ os.path.dirname(os.path.abspath(sys.argv[0])),
             self.site, self.board, key + '_' + digest ]
            )
        if os.path.exists(outpath):
            if os.path.isdir(outpath):
                print 'the job was done already.'
                sys.exit(0)
            else:
                print 'error: a file named %s exists!' % outpath
                sys.exit(1)
        else:
            L = outpath.split(os.path.sep)
            for i in range(1, len(L) + 1):
                dirname = os.path.sep.join(L[:i])
                if os.path.exists(dirname):
                    if not os.path.isdir(dirname):
                        print 'error: a file named %s exists!' % dirname
                        sys.exit(1)
                else:
                    os.mkdir(dirname)
            self.outpath = outpath

        num, pieces, upper = len(pages), len(pages)>>4, 0
        for k in range(pieces):
            lower, upper = upper, upper + (num + k) // pieces
            self.pageQueue.put(pages[lower:upper])

        for i in range(self.num_threads):
            t = threading.Thread(target=self.crawl_pid)
            t.setDaemon(True)
            t.start()

        # wait till done with pageQueue
        self.pageQueue.join()

        for i in range(self.num_threads):
            t = threading.Thread(target=self.crawl_keyword, args=(key,))
            t.setDaemon(True)
            t.start()

        # wait till done with pidQueue
        self.pidQueue.join()


if __name__=='__main__':
    crawler = BBSCrawler('www.newsmth.net','FuncProgramm', 10)
    crawler.crawl('Haskell')

