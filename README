Print the most common amenities
```
awk -F ',' '{print $2}' amenities.csv | sort | uniq -c | sort -nr
```

EC2 Intructions
-- AN AMI has been created already, but, to do from scratch

[Spin up Ubuntu 12.04 LTS 64 bit](https://aws.amazon.com/marketplace/pp/B007Z5YWX4)

install pip
````
sudo apt-get install python-pip
```

install selenium
```
sudo pip install selenium
```

install phantomjs 
NOTE MAKE SURE TO GET THE MOST UP TO DATE VERSION
Before you start, take a look that is this a installation for x64 OS's
If you need just a x86 package, download it at phantomJS official website or on google code.
 
[http://phantomjs.googlecode.com/files/](http://phantomjs.googlecode.com/files/)
[http://phantomjs.org/](http://phantomjs.googlecode.com/files/)
 
Go to the SHARE directory
```
cd /usr/local/share
``` 
Push file from google code
```
sudo wget http://phantomjs.googlecode.com/files/phantomjs-1.8.1-linux-x86_64.tar.bz2
```

Extract the files to directory
```
sudo tar xjf phantomjs-1.8.1-linux-x86_64.tar.bz2
``` 
Move files to Phantom's directory
```
sudo ln -s /usr/local/share/phantomjs-1.8.1-linux-x86_64/bin/phantomjs /usr/local/share/phantomjs; sudo ln -s /usr/local/share/phantomjs-1.8.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs; sudo ln -s /usr/local/share/phantomjs-1.8.1-linux-x86_64/bin/phantomjs /usr/bin/phantomjs
```
install sqlalchemy
```
sudo pip install sqlalchemy
```
install mysqldb
```
sudo apt-get install python-mysqldb
```
set environmental vars
```
SCRAPER_URL
SCRAPER_USERNAME
SCRAPER_PW
```
call shell script form /etc/rc.local

LOAD DATA FROM FILE INTO MYSQL
```
LOAD DATA LOCAL INFILE '/Users/mistewart/Salesforce/selenium/example/data/booking.txt'
INTO TABLE Queue (URL)
SET Site = 'booking'
```
place script in /etc/init.d/{scriptname}
call with
```
sudo service {servicename} start
```
add to startup
```
sudo update-rc.d {scriptname} defaults
```
add papertrail monitoring [https://papertrailapp.com/systems/setup](https://papertrailapp.com/systems/setup)
As root, edit /etc/rsyslog.conf with a text editor (like pico or vi). Paste this line at the end:
```
*.*          @logs.papertrailapp.com:49761
```
Restart rsyslog to re-read the config file:
```
sudo service rsyslog restart
```
