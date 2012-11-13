#!/usr/bin/python
##############################################################
#
# cnv2db 
# 
# A simple Seabird cnv file parser that stores the data
# into a mysql db 
#
# For the sql structure, see below, at the end of the code 
#
# Requisites: python-mysqldb library
# version 0.4
# License: CC-BY-NC-SA v. 3.0
# Author:
# Rocco De Marco (rocco_demarco(a)an_ismar_cnr_it) -> s/_/\./g
# November 2012
#
###############################################################
''' CHANGELOG 
v. 0.4.0
1) Rewritten in class style

v. 0.3.2: 
1) choosed "NMEA UTC (Time)" as date/time parameter instead than start_date

'''


import sys
import MySQLdb
import os
from cnv2db_class import *

# Database mysql access
host = "localhost"
user = "ctd"
passwd = "DPYbLSE8eW8pEHFx"
db = "acustica"

# Dummy function called in case of error
def die(message):
   sys.stderr.write("\n*** Execution terminated ***\nError: %s\n\n" % message)
   sys.exit(-1)

if len(sys.argv) < 2:
   die("Missing CNV file")

if not os.path.exists(sys.argv[1]):
   die("Input file not found: %s" % sys.argv[1])

f=open (sys.argv[1],"r")
cnv=f.read()
f.close()

mycnv=cnvParser(cnv)


# Some integrity/compatibility check
if mycnv.filetype != "ascii":
   die("Only ascii file format supported, at the moment!")
if len(mycnv.data_matrix[0])!=mycnv.nquan:
   die("Incongruent number of columns")
        

# Let's try to read most important infos, using the get method to avoid
# the KeyError exception in case of missness


if mycnv.longitude=="" and mycnv.latitude=="":
   die ("Unable to continue without longitude and latitude values.\nParser problem or missing information?")

conn = MySQLdb.connect (host,user,passwd,db)
cursor = conn.cursor ()

#check if the data have been already saved
sql_check="SELECT * FROM CTD_STATION WHERE LONGITUDE='%s' AND LATITUDE='%s' AND DATE='%s'" \
        % (mycnv.longitude, mycnv.latitude, mycnv.date)
cursor.execute (sql_check)
if cursor.rowcount!=0:
   die("Record already stored in db");

# Store general information into db
sql_station="INSERT INTO CTD_STATION \
	  (CRUISE,DATE,LONGITUDE,LATITUDE,STATION_NAME,DEPTH) \
	  VALUES \
          ('%s','%s','%s','%s','%s','%f');" \
          % (mycnv.cruise,mycnv.date,mycnv.longitude,mycnv.latitude,mycnv.station,mycnv.depth)
cursor.execute (sql_station)
conn.commit()
ctd_station_id=cursor.lastrowid

for key in mycnv.parameters:
   sql_info="INSERT INTO CTD_INFO (CTD_STATION_ID,PARAMETER,VALUE) VALUES (%d,'%s','%s')" \
	% (ctd_station_id,MySQLdb.escape_string(key),MySQLdb.escape_string(mycnv.parameters[key]))
   cursor.execute (sql_info)
conn.commit()
   
for row in mycnv.data_matrix:
   sensor_n=0
   for element in row:
      sql_data="INSERT INTO CTD_DATA (CTD_STATION_ID,SENSOR,VALUE) VALUES (%d,%d,'%f')" \
 	 % (ctd_station_id,sensor_n,float(element))
      cursor.execute (sql_data)
      sensor_n+=1
conn.commit()

conn.close()





