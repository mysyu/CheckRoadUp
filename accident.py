# coding=utf-8
import urllib2
from geocodequery import GeocodeQuery
import mysql.connector as DB

cord = GeocodeQuery("zh-tw", "tw")
db = DB.connect( host = 'mysyu.ddns.net' , user = 'road' , passwd = 'road' , db = 'road' , charset = 'utf8' )
db.autocommit = False
cursor = db.cursor()

#事故accident

cursor.execute( 'DELETE FROM accident WHERE 1' )
db.commit()
try:
    file = urllib2.urlopen('http://data.tycg.gov.tw/opendata/datalist/datasetMeta/download?id=af256309-2d0f-4599-82bc-b7f7f38b6089&rid=7dce03ca-6670-420b-8527-950752d031b5')
    for lines in file.readlines()[1:]:
        lines = lines.replace('\r','').replace('\n','')
        print lines
        line = lines.split(',')
        if line[4] == 'NA' or line[5] == 'NA':
            cord.get_geocode(line[1])
            line[4] = cord.get_lat()
            line[5] = cord.get_lng()
        if line[4] != None and line[5] != None:
            print "INSERT INTO accident ( event , address , type , coordinate , description ) VALUES ( 'accident' , '%s' , 'Point' , '%s,%s,0' , '%s' )" % ( line[1] , line[5] , line[4], lines )
            cursor.execute( "INSERT INTO accident ( event , address , type , coordinate , description ) VALUES ( 'accident' , '%s' , 'Point' , '%s,%s,0' , '%s' )" % ( line[1] , line[5] , line[4], lines ) )
            db.commit()
except Exception as e:
    print e
''''''