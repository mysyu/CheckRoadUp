# coding=utf-8
import urllib2
from pykml import parser
from BeautifulSoup import BeautifulSoup
from datetime import date
from selenium import webdriver
from geocodequery import GeocodeQuery
import mysql.connector as DB

cord = GeocodeQuery("zh-tw", "tw")
db = DB.connect( host = 'mysyu.ddns.net' , user = 'road' , passwd = 'road' , db = 'road' , charset = 'utf8' )
db.autocommit = False
cursor = db.cursor()

while 1:
    try:
        cursor.execute( 'BEGIN' )
        cursor.execute( 'DELETE FROM backup WHERE 1' )
        cursor.execute( 'INSERT INTO backup SELECT * FROM road')
        cursor.execute( "UPDATE status SET status = 'OFF'")
        db.commit()
    except:
        db.rollback()
    else:
        break
cursor.execute( 'DELETE FROM  road WHERE 1' )
db.commit()

#事故accident

try:
    cursor.execute( "INSERT INTO road SELECT * FROM accident WHERE MONTH( STR_TO_DATE( SUBSTRING( description , 1, LOCATE(' ', description ) - 1 ) , '%m/%d/%Y' ) ) = MONTH( sysdate() )" )
    db.commit()
except Exception as e:
    print e
''''''

#車速speed

try:
    file = urllib2.urlopen('http://61.60.10.87/javaAndXml/xmldata/cloud/moe/pureVdMoe1.kml').read()
    root = parser.fromstring(file)

    for i in root.Document.Folder:
        for j in i.Placemark:
            if j.name.text != None and j.description.text != None and u'國道' not in j.name.text and u'快速公路' not in j.name.text and j.description.text != u'速率:無資料' and j.LineString.coordinates != None:
                print "INSERT INTO road ( event , address , type , coordinate , description ) VALUES ( 'speed' , '%s' , 'LineString' , '%s' , '%s' )" % ( j.name.text.encode('utf-8') , j.LineString.coordinates.text.encode('utf-8') , j.description.text.encode('utf-8') )
                cursor.execute( "INSERT INTO road ( event , address , type , coordinate , description ) VALUES ( 'speed' , '%s' , 'LineString' , '%s' , '%s' )" % ( j.name.text.encode('utf-8') , j.LineString.coordinates.text.encode('utf-8') , j.description.text.encode('utf-8') ))
                db.commit()
except Exception as e:
    print e
''''''

#坑洞hole

try:
    l = []
    driver = webdriver.PhantomJS(executable_path='phantomjs.exe')
    #driver = webdriver.Firefox(executable_path='geckodriver.exe')
    driver.get('http://epark1.tycg.gov.tw/rgis/HoleCaseForm.aspx')
    page = int( driver.find_elements_by_tag_name('span')[-1].get_attribute('innerHTML').encode('utf-8') )
    for i in range( 1 , page + 1):
        while 1:
            try:
                if i == int( driver.find_elements_by_tag_name('span')[-2].get_attribute('innerHTML').encode('utf-8') ):
                    break
            except:
                pass
        for tr in driver.find_element_by_id('gv').find_elements_by_tag_name('tr')[1:-2]:
            try:
                tds = tr.find_elements_by_tag_name('td')
                if tds[2].get_attribute('innerHTML').encode('utf-8').replace(',','，').replace('\n','').replace('&nbsp;','') == '已派工':
                    addr = tds[4].get_attribute('innerHTML').encode('utf-8').replace(',','，').replace('\n','').replace('&nbsp;','')
                    info = tds[8].find_element_by_tag_name('a').get_attribute('onclick').encode('utf-8').split("'")
                    if info[1] in l:
                        continue
                    else:
                        l.append(info[1])
                    print "INSERT INTO road ( event , address , type , coordinate , description ) VALUES ( 'hole' , '%s' , 'Point' , '%s,0' , 'http://epark1.tycg.gov.tw/RGIS/%s' )" % ( addr , info[1] , info[3] )
                    cursor.execute( "INSERT INTO road ( event , address , type , coordinate , description ) VALUES ( 'hole' , '%s' , 'Point' , '%s,0' , 'http://epark1.tycg.gov.tw/RGIS/%s' )" % ( addr , info[1] , info[3] ) )
                    db.commit()
            except:
                pass
        if i == page:
            break
        driver.execute_script( "script:__doPostBack('gv$ctl13$LinkButtonNextPage','')" )
    driver.quit()
except Exception as e:
    print e
''''''

#施工construction

try:
    l = []
    driver = webdriver.PhantomJS(executable_path='phantomjs.exe')
    #driver = webdriver.Firefox(executable_path='geckodriver.exe')
    driver.get('http://epark1.tycg.gov.tw/RGIS/CaveInfo.aspx?ConstTime=' + date.today().strftime( '%Y/%m/%d' ) )
    page = int( driver.find_elements_by_tag_name('span')[-1].get_attribute('innerHTML').encode('utf-8') )
    for i in range( 1 , page + 1):
        while 1:
            try:
                if i == int( driver.find_elements_by_tag_name('span')[-2].get_attribute('innerHTML').encode('utf-8') ):
                    break
            except:
                pass
        for tr in driver.find_element_by_id('gv').find_elements_by_tag_name('tr')[1:-2]:
            try:
                url = 'http://epark1.tycg.gov.tw/RGIS/DigListinfo.aspx?caseid=' + tr.find_element_by_tag_name('td').get_attribute('innerHTML').encode('utf-8')
                soup = BeautifulSoup( urllib2.urlopen( url ).read().decode('big5') )
                addr = soup.find(id='Table1').findAll('tr')[11].findAll('td')[1].text.replace(' ','')
                cord.get_geocode(addr.encode('utf-8'))
                if cord.get_lat() != None and cord.get_lng() != None:
                    if cord.get_lng() + ',' + cord.get_lat() in l:
                        continue
                    else:
                        l.append(cord.get_lng() + ',' + cord.get_lat())
                    print "INSERT INTO road ( event , address , type , coordinate , description ) VALUES ( 'construction' , '%s' , 'Point' , '%s,%s,0' , '%s' )" % ( addr , cord.get_lng(), cord.get_lat(), url )
                    cursor.execute( "INSERT INTO road ( event , address , type , coordinate , description ) VALUES ( 'construction' , '%s' , 'Point' , '%s,%s,0' , '%s' )" % ( addr , cord.get_lng(), cord.get_lat(), url ) )
                    db.commit()
            except Exception as e:
                pass
        if i == page:
            break
        driver.execute_script( "script:__doPostBack('gv$ctl13$LinkButtonNextPage','')" )
    driver.quit()
except Exception as e:
    print e
''''''

cursor.execute( "UPDATE status SET status = 'ON' , lastupdate = sysdate()")
db.commit()
try:
    cursor.execute( 'BEGIN' )
    cursor.execute( 'DELETE FROM backup WHERE 1' )
    cursor.execute( 'INSERT INTO backup SELECT * FROM road')
    db.commit()
except:
    db.rollback()

cursor.close()
db.close()