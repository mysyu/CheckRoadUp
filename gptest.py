from geocodequery import GeocodeQuery
import csv

with open('hole.csv') as csvfile:
    readcsv = csv.reader(csvfile, delimiter=',')
    readdata = []
    for row in readcsv:
        readdata.append(row)
address=[]
coor=[]
gq = GeocodeQuery("zh-tw", "tw")
for i in range(1,len(readdata)):
    print (readdata[i][4])
    gq.get_geocode(readdata[i][4])
    print(gq.get_lat())
    print(gq.get_lng())

