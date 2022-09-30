import datefinder
import os
import requests
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup as bs
import re

class DatesRecognition():
    def __init__(self, url=None, lines=None, content=None):
        self.stats = {}
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.selected_date = None
        self.dates = {}
        self.DEBUG = False
        self.lines = lines
        self.content = content
        self.datepub = None
        self.url = url
        self.settime = None
        self.longread = 0
        self.htmltext = None
        self.fulltext = None
        self.alldates = []

    def getdemo(self):    
        lines = []
        input_string = "vandaag, 10:28 "
        lines.append(input_string)
        input_string = "Сегодня понедельник 27 декабря, завтра 28 декабря"
        lines.append(input_string)
        input_string = 'Publié aujourd’hui à 06h41, mis à jour à 10h35'
        lines.append(input_string)
        input_string = '<p>27 грудня 2021 14:55</p>'
        lines.append(input_string)
        return lines

    def get_publication_date(self, lines=[]):                
        today = datetime.now()
        nextday = today + timedelta(days=1)
        prevday = today - timedelta(days=3000) 
        for i in range(0,len(lines)):
            input_string = lines[i]
            matches = list(datefinder.find_dates(input_string))

            if today:
                if len(matches) > 0:
                    # date returned will be a datetime.datetime object. here we are only using the first match.
                    for date in matches:
                        fulldate = date
                        status = False
                        date = date.replace(tzinfo=None)
                        d1 = prevday
                        if d1 < date < nextday: #fulldate: # < d2:
                            dateitem = {}
                            if self.DEBUG:
                                print(matches)
                                print("%s %s" % (i, date))

                            if not '00:00' in str(fulldate):
                                if re.search(r'\d+\:\d+', str(fulldate)):
                                    if not self.settime:
                                        status = True
                                        self.settime = str(fulldate)
                                        self.selected_date = fulldate
                                        if self.DEBUG:
                                            print("\tStatus %s" % str(fulldate))

                            thisdateinfo = { 'i': i, 'original': input_string, 'date': str(fulldate), 'time': status, 'confirmed': 'true' }
                            self.alldates.append(thisdateinfo)
                            # If date not set, take first one
                            if not self.selected_date:
                                self.selected_date = fulldate

                            if status:
                                if not self.selected_date:
                                    self.selected_date = fulldate
                        else:
                            thisdateinfo = { 'i': i, 'original': input_string, 'date': str(date), 'confirmed': 'no' }
                            self.alldates.append(thisdateinfo)
                else:
                    x = 0
                    #print('No dates found')
        return self.selected_date

    def bs(self, url):
        html = requests.get(url).content
        soup = bs(html, "lxml")
        # Get the text on the html through BeautifulSoup
        text = soup.get_text().splitlines()
        self.htmltext = text
        LONGLINE = 150
        fulltext = []
        for i in range(0, len(text)):            
            if len(text[i]) >= LONGLINE:
                self.longread = self.longread + 1
            thisline = text[i].split('. ')
            if thisline:
                fulltext.append(thisline)
            if self.DEBUG: # == 'INFO':
                print("%s %s" % (i, text[i]))
        self.fulltext = fulltext
        return fulltext

    def preparecontent(self, html):        
        soup = bs(html, "lxml")
        # Get the text on the html through BeautifulSoup
        text = soup.get_text().splitlines()
        self.htmltext = text
        LONGLINE = 150
        fulltext = []
        for i in range(0, len(text)):            
            if len(text[i]) >= LONGLINE:
                self.longread = self.longread + 1
            thisline = text[i].split('. ')
            for line in thisline:
                if len(line):
                    fulltext.append(line)
            if self.DEBUG: # == 'INFO':
                print("%s %s" % (i, text[i]))
        self.fulltext = fulltext
        return fulltext

    def load(self, content=None, lines=None):
        currentDateTime = datetime.now()
        date = currentDateTime.date()
        currentyear = date.strftime("%Y")

        if self.lines:
            content = lines
        if content:
            self.lines = self.preparecontent(content)
        if lines:
            if self.DEBUG:
                print("[DEBUG] Use content")
            self.lines = lines
        #    for line in content.split('\n'):        
        firstlines = []
        for line in self.lines:
            if str(currentyear) in line:
                firstlines.append(line)

        if self.DEBUG:
            print("First %s" % len(firstlines))

        firstlines = False
        if firstlines:
            self.datepub = self.get_publication_date(firstlines)

        #self.datepub = False
        if not self.datepub or not self.settime:
            if self.DEBUG:
                print("All records: %s" % len(self.lines))
            self.datepub = self.get_publication_date(self.lines)
        if self.DEBUG:
            print(self.datepub)
        return self.datepub

