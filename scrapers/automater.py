#! /usr/bin/python
import os
from sqlalchemy import *
import thread
import time
from ConfigParser import SafeConfigParser
import logging
import socket
from logging.handlers import SysLogHandler
from simple_salesforce import Salesforce
from booking import BookingScraper
import datetime
import amenity_mapping

hostname = socket.gethostname()

logger = logging.getLogger()
logger.setLevel(logging.INFO)
syslog = SysLogHandler(address=('logs.papertrailapp.com', 49761))
formatter = logging.Formatter('%(levelname)s - ' + hostname + ' - %(asctime)s - %(message)s')
syslog.setFormatter(formatter)
logger.addHandler(syslog)

# logging.basicConfig(format='%(levelname)s - ' + hostname + ' - %(asctime)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p %z', filename='scraping.log',level=logging.INFO)

class Automator(object):

    @staticmethod
    def scrapeHotels():
        directory = '../data/'
        count = 0
        for filename in os.listdir(directory):
            if '.txt' in filename and '.swp' not in filename:
                f = open(directory + filename)
                site = filename.replace('.txt', '')
                module = __import__(site)
                SiteScraper = getattr(module, site.title() + 'Scraper') ##dynamically instantiate class
                for uniqueKey in f:
                    count += 1
                    try: 
                        scrape = SiteScraper(uniqueKey)
                        scrape.doScrape() ## todo move try/catch block to this method
                        print '%s - %s' % (count, uniqueKey)
                    except Exception as e:
                        print 'something went wrong with: ' + uniqueKey
                        print e

    def connect_to_sf(self):
        parser = SafeConfigParser()
        parser.read('database.conf')
        user = parser.get('SF', 'USERNAME')
        pw = parser.get('SF', 'PW')
        token = parser.get('SF', 'TOKEN')
        sf = Salesforce(username=user, password=pw, security_token=token, sandbox=True)
        return sf

    def monitor_sf(self):
        if not hasattr(self, 'sf'):
            self.sf = self.connect_to_sf()
        items = self.sf.query('SELECT Id, Name, Booking_com_ID__c FROM Account WHERE Booking_com_ID__c != NULL AND (Booking_com_Last_Scrape_Date__c < TODAY OR Booking_com_Last_Scrape_Date__c = NULL) ORDER BY Booking_com_Last_Scrape_Date__c DESC NULLS FIRST LIMIT 1 OFFSET 100')
        hasMore = True
        if len(items['records']) == 0:
            hasMore = False
        while hasMore:
            print 'SCRAPING: '
            print items['records'][0]['Name']
            sf_id = items['records'][0]['Id']
            booking_url = items['records'][0]['Booking_com_ID__c']
            try:
                self.update_sf(sf_id, booking_url)
            except Exception as e: 
                print e
                self.sf.Account.update(sf_id,
                {'Booking_com_Last_Scrape_Date__c' : (datetime.date.today() + datetime.timedelta(days=10000)).isoformat()})
            items = self.sf.query('SELECT Id, Name, Booking_com_ID__c FROM Account WHERE Booking_com_ID__c != NULL AND (Booking_com_Last_Scrape_Date__c < TODAY OR Booking_com_Last_Scrape_Date__c = NULL) ORDER BY Booking_com_Last_Scrape_Date__c DESC NULLS FIRST LIMIT 1 OFFSET 100')
            if len(items['records']) == 0:
                hasMore = False
        print 'sleeping for a bit'
        time.sleep(10)
        self.monitor_sf()

    def update_sf(self, sf_id, booking_url):
        print booking_url
        scraper = BookingScraper(booking_url)
        scraper.doScrape()
        summary = scraper.getSummary()
        amenities = ';'.join(scraper.getAmenities())
        scrubbed_ameneities = ';'.join(self.scrub_amenities(scraper.getAmenities()))
        self.sf.Account.update(sf_id,
                {'Booking_com_Summary__c': summary,
                 'Booking_com_Amenities__c' : amenities,
                 'Booking_com_Last_Scrape_Date__c' : datetime.date.today().isoformat() })

    def scrub_amenities(self, amenities):
        clean = []
        for amenity in amenities:
            clean.append(amenity_mapping.amenity_dictionary.get(amenity, amenity))

        print 'clean'
        print clean
        return clean

    def monitor_queue(self):
        if not hasattr(self, 'engine'):
            self.engine = self.connect_to_db()
        query = self.engine.execute('SELECT * FROM Next_Item')
        workItem = query.fetchall()

        if len(workItem) == 0: 
            print 'Nothing in Queue'
            logging.info('Nothing in Queue')
            return

        self.update_status('Working', workItem[0])

        site = workItem[0]['Site']
        uniqueKey = workItem[0]['URL']
        module = __import__(site)
        SiteScraper = getattr(module, site.title() + 'Scraper') ##dynamically instantiate class
        try: 
            scrape = SiteScraper(uniqueKey)
            scrape.doScrape() ## todo move try/catch block to this method
            self.insert_amenities(workItem[0], scrape)
            self.insert_images(workItem[0], scrape)
            self.insert_summary(workItem[0], scrape)
            self.update_status('Complete', workItem[0])
            print '%s' % (uniqueKey)
            logging.info('Successfully scraped %s' % uniqueKey)
        except Exception as e:
            logging.warning('Something went wrong with %s' % uniqueKey)
            print 'something went wrong with: ' + uniqueKey
            self.update_status('Error', workItem[0])
            print e
        finally:
            scrape.close()
            self.monitor_queue()
    
    def connect_to_db(self):
        print 'CONNECTING'
        engine = create_engine(self.connection_string())
        return engine

    def connection_string(self):
        parser = SafeConfigParser()
        parser.read('database.conf')
        url = parser.get('database', 'HOST')
        user = parser.get('database', 'USER')
        pw = parser.get('database', 'PW')
        return 'mysql://%s:%s@%s' % (user, pw, url)

    def update_status(self, status, record):
        queueId = record['ID']
        self.engine.execute("UPDATE Scraping.Queue SET Status = '%s' WHERE ID = %i" % (status, queueId))

    def insert_amenities(self, workItem, scraper):
        site = workItem['Site']
        url = workItem['URL']
        for amenity in scraper.getAmenities():
            self.engine.execute("INSERT INTO `Scraping`.`Amenities` (`HotelKey`, `Site`, `Amenity`) VALUES ('%s', '%s', '%s')" % (url, site, amenity))

    def insert_images(self, workItem, scraper):
        site = workItem['Site']
        hotelKey = workItem['URL']
        for image in scraper.getImages():
            self.engine.execute("INSERT INTO `Scraping`.`Images` (`HotelKey`, `Site`, `URL`) VALUES ('%s', '%s', '%s')" % (hotelKey, site, image))

    def insert_summary(self, workItem, scraper):
        site = workItem['Site']
        hotelKey = workItem['URL']
        summary = unicode(scraper.getSummary()).replace("'", "") # BAD BAD BAD
        sql = "INSERT INTO `Scraping`.`Summaries` (`HotelKey`, `Site`, `Summary`) VALUES ('%s', '%s', '%s')" % (hotelKey, site, summary)
        self.engine.execute(sql)

    @staticmethod
    def run_job():
        logging.info('STARTED')
        automator = Automator()
        # automator.monitor_queue()
        automator.monitor_sf()

    @staticmethod
    def thread_scrape(count):
        for i in range(count):
            print 'starting job'
            time.sleep(1)
            thread.start_new_thread(Automator.run_job, ())
        while 1:
            pass

# automator = Automator()
# automator.monitor_queue()

# Automator.thread_scrape(1)
Automator.run_job()
