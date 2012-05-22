# -*- coding: utf-8 -*-

#
#	LastPy - a simple Audioscrobbler Realtime Submission Protocol implementation in python 2.6	
#	protocol v1.2: http://www.audioscrobbler.net/development/protocol/
#	author: Krzysztof Rosinski
#	licence: GNU GPL 3 http://www.gnu.org/licenses/gpl-3.0.txt
#
#
import urllib2 
import re
import hashlib
import urllib
import time


class BadAuthException(Exception):
    def __init__(self):
	    self.msg ="Invalid username or password"
	
class LastPy:

    def __init__(self, uname, pword):

        #session parameters
        self.__now_playingURI = ""
        self.__submitURI = ""
        self.__sessionKey = ""


        self.__tm = int(time.time())#gmt

        #user data
        self.user = uname
        self.__password = pword

        self.__nowForm = {
            "s" : "",
            "a" : "",   
            "t" : "",
            "b" : "",
            "l" : "240",#now playing length
            "n" : "",
            "m" : ""
        }

        self.__submitForm = {
            "s":  "",
            "a[0]" :"ARTIST",
            "t[0]" :"TITLE",
            "i[0]" : "TIME",
            "o[0]" : "R", #radio
            "r[0]" : "",
            "l[0]" : "",
            "b[0]" : "ALBUM",
            "n[0]" : "",
            "m[0]" :""
        }

        self.__getSession()


    def __getSession(self):
        t = int(time.time())
        m = hashlib.md5()
        m.update(self.__password)
        elem = m.hexdigest()
        elem = elem + str(t)
        m = hashlib.md5()
        m.update(elem)
        token = m.hexdigest()
        req = urllib2.Request("http://post.audioscrobbler.com/?hs=True&p=1.2.1&c=tst&v=1.0&u=" \
                + self.user + "&t=" + str(t) + "&a=" + token)
        res = urllib2.urlopen(req).read().split("\n")
        ''' 
        1 -> sessionKey
        2 -> now playing URI
        3 -> submit URI
        ''' 
        if res[0]=="OK":
            self.__sessionKey = res[1]
            self.__now_playingURI = res[2]
            self.__submitURI = res[3]
        elif (res[0]=="BADAUTH"):
            raise BadAuthException

	    # 0 -> OK/BADAUTH/....
	    return res[0]



    #update rest of file
    def now_playing(self,title, artist, album):
	    # updates 'now playing'
        while(True):
            self.__nowForm["s"] = self.__sessionKey
            self.__nowForm["a"] = artist
            self.__nowForm["t"] = title
            self.__nowForm["b"] = album
            self.__tm = int(time.time())

            post_form = urllib.urlencode(self.__nowForm)
            req = urllib2.Request(self.__now_playingURI, post_form)
            res = urllib2.urlopen(req).read().split("\n")
            if res[0] == "OK":
                break
            else:
                time.sleep(3)
                self.__getSession()

    def submit_last_track(self):
	    # submits current track
	    self.submit_track(self.__nowForm["t"], self.__nowForm["a"], self.__nowForm["b"], self.__tm)


    def submit_track(self, title, artist, album, tm):
	    # submits track
        while(True):
            self.__submitForm["s"] = self.__sessionKey
            self.__submitForm["t[0]"] = title
            self.__submitForm["a[0]"] = artist
            self.__submitForm["b[0]"] = album
            self.__submitForm["i[0]"] = str(tm)

            post_form = urllib.urlencode(self.__submitForm)
            req = urllib2.Request(self.__submitURI, post_form)
            res = urllib2.urlopen(req).read().split("\n")

            if res[0] == "OK":
                break
            else:
                #wait 3 seconds, and request new session
                time.sleep(3)
                self.__getSession()



if __name__ == '__main__':
    '''
        Example usage
    '''
    last = LastPy("lastfm-username","lastfm-password")
    last.now_playing("Tornado of Souls", "Megadeth","Rust in Peace")
    time.sleep(30)
    last.submit_last_track()
