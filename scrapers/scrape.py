#! /usr/bin/python
import sys
from selenium import webdriver
import codecs
import csv
import urllib
from time import sleep
sys.stdout=codecs.getwriter('utf-8')(sys.stdout)

SESSION_ID = '00DC0000000PxQg!AQQAQMgdSaKN2n3G2H2rZO7TIIfxjQ7xw1LDz_nA4JQYdg1SuEGr57FCxj92UD1GI5YvtbzmXyjFTHpOSMe71JeQLxEaqrfi'
HOST_URL = 'https://na8.salesforce.com/'

desired={'phantomjs.page.settings.userAgent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)'}
driver = webdriver.PhantomJS('phantomjs', desired_capabilities=desired)

class Scraper(object):
    def __init__(self, userId, emailAddy):
        self.userId = userId
        self.userEmail = urllib.quote(emailAddy)

        self.load_page()
        sleep(1)
        self.submit_page()
        # self.close()

    def load_page(self):
        result = driver.get(self.getUrl())

    def submit_page(self):
        driver.execute_script("document.getElementsByName('save')[0].click()")
        print 'UPDATED USER'

    def close(self):
        driver.close()

    def getUrl(self):
        # return self.uniqueKey
        return HOST_URL + 'secur/frontdoor.jsp?sid=' + SESSION_ID + '&retURL=%2F' + self.userId + '%2Fe%3Fnoredirect%3D1%26Email%3D' + self.userEmail + '%26new_password%3D1'


def iterate_users():
    users_file = open('users.txt', 'r')
    for user in users_file:
        userId, userEmail = user.split(',')
        print 'USERID: ', userId
        print 'USEREMAIL: ', userEmail
        a = Scraper(userId, userEmail)
        sleep(2)
