# coding=utf-8
import sys
import urllib, urllib2
import json

class GeocodeQuery:
    def __init__(self, language=None, region=None):
        self.url = 'https://maps.googleapis.com/maps/api/geocode/json?language={0}&region={1}&sensor=false'.format(language, region)
        self.jsonResponse = {}
        self.addr = None
            
    def get_geocode(self, addr):

        if '桃園' != addr[:2]:
            addr = '桃園' + addr
        if '，' in addr:
            addr = addr[:addr.index('，')]
        if '號' in addr:
            addr = addr[:addr.index('號')+3]
        elif '弄' in addr:
            addr = addr[:addr.index('弄')+3]
        elif '巷' in addr:
            addr = addr[:addr.index('巷')+3]
        elif '段' in addr:
            addr = addr[:addr.index('段')+3]
        elif '街' in addr:
            addr = addr[:addr.index('街')+3]
        elif '路' in addr:
            addr = addr[:addr.index('路')+3]
        self.addr = addr
        addr = urllib.quote(addr)
        url = self.url + '&address={}'.format(addr)
        response = urllib2.urlopen(url)
        self.jsonResponse = json.loads(response.read())
        return self.jsonResponse

    def get_lat(self):
        if len(self.jsonResponse["results"]) is not 0:
            return str( self.jsonResponse["results"][0]["geometry"]["location"]["lat"] )

    def get_lng(self):
        if len(self.jsonResponse["results"]) is not 0:
            return str( self.jsonResponse["results"][0]["geometry"]["location"]["lng"] )
    
    def get_cuntry(self):
        if len(self.jsonResponse["results"]) is not 0:
            return self.jsonResponse["results"][0]["address_components"][4]["long_name"]

    def get_area(self):
        if len(self.jsonResponse["results"]) is not 0:
            return self.jsonResponse["results"][0]["address_components"][3]["long_name"]

