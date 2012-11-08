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
# version 0.3.1
# License: CC-BY-NC-SA v. 3.0
# Author:
# Rocco De Marco (rukkuntu@yahoo.it) - November 2012
#
###############################################################
import re
import sys
import MySQLdb
import os

# Some global variable
# In most cases you have to change these

# Database mysql access
host = "localhost"
user = "ctd"
passwd = "DPYbLSE8eW8pEHFx"
db = "acustica"

# Dummy function called in case of error
def die(message):
   sys.stderr.write("\n*** Execution terminated ***\nError: %s\n\n" % message)
   sys.exit(-1)


#-------------------------------------------------------------------------------------
# The parser function
def parser(filename):
        f=open (filename,"r")
        cnv=f.read()
        f.close()

        # General info: line that start with single "*"
        g_info=re.findall(r"^\* (.*) = (.*)",cnv[0:cnv.find("**")],re.MULTILINE)
		# Note: I splitted the buffer at the first "**" occurrence to avoid
		# a parsing problem with non-standard information in some cnv file.
 		# In this case I didn't used a regex due lacking performances
        # notes: these lines start with "**"
        notes=re.findall(r"^\*\* (.*): \s*(.*)",cnv,re.MULTILINE)
        # Measure info
        m_info=re.findall(r"^\# (.*) = (.*)",cnv,re.MULTILINE)
        # Data
	        # raw_data=re.findall(r"^\*END\*\r\n(.*)",cnv,re.MULTILINE|re.DOTALL)
        raw_data=cnv[cnv.find("*END*")+7:]
		# Also in this case I prefered to partition the buffer without regex
		# to reduce the excecution time
        # Descriptor is a data structure containing all the merged info
        descriptor={}     
        for element in m_info+g_info+notes:
           descriptor[element[0]]=element[1].rstrip("\r\n")
        if descriptor=={}:
	   die ("No data has been read. Are you sure you given a CNV file?")
	# Data parser
        # Ok, there is the regex way, but sometimes is better a K.I.S.S. approach
        data_matrix=[]
        vector=[]
	value=""
        previous=" "
  	for char in raw_data:
           if char=="\n":
              vector.append(float(value))               # add the last value in the array
	      data_matrix.append(vector)                # append the values to the data matrix
              vector=[]
              value=""
           elif char==" ":
              if previous!=" " and previous!="\n": 
                 vector.append(float(value))
	   else:
   	      if previous==" " or previous=="\n":
	         value=char
	      else:
		 value=value+char
           previous=char
        # Data parsing completed

        return (descriptor,data_matrix)


if len(sys.argv) < 2:
   die("Missing CNV file")

if not os.path.exists(sys.argv[1]):
   die("Input file not found")

(descriptor, data_matrix)=parser(sys.argv[1])


# Some integrity/compatibility check
nquan = int(descriptor["nquan"])  	# Number of sensors/data columns
filetype = descriptor["file_type"]    	# CNV data type: must be "ascii"
if filetype != "ascii":
   die("Only ascii file format supported, at the moment!")
if len(data_matrix[0])!=nquan:
   die("Incongruent number of columns")
        

# Let's try to read most important infos, using the get method to avoid
# the KeyError exception in case of missness
cruise=descriptor.get("Cruise","")
date=descriptor.get("start_time","")
longitude=descriptor.get("NMEA Longitude","")
latitude=descriptor.get("NMEA Latitude","")
station=descriptor.get("Station","")
depth=float(descriptor.get("Bottom",""))

if longitude=="" and latitude=="":
   die ("Unable to continue without longitude and latitude values.\nParser problem or missing information?")

conn = MySQLdb.connect (host,user,passwd,db)
cursor = conn.cursor ()

#check if the data have been already saved
sql_check="SELECT * FROM CTD_STATION WHERE LONGITUDE='%s' AND LATITUDE='%s' AND DATE='%s'" \
        % (longitude, latitude, date)
cursor.execute (sql_check)
if cursor.rowcount!=0:
   die("Record already stored in db");

# Store general information into db
sql_station="INSERT INTO CTD_STATION \
	  (CRUISE,DATE,LONGITUDE,LATITUDE,STATION_NAME,DEPTH) \
	  VALUES \
          ('%s','%s','%s','%s','%s','%f');" \
          % (cruise,date,longitude,latitude,station,depth)
cursor.execute (sql_station)
conn.commit()
ctd_station_id=cursor.lastrowid


for key in descriptor:
   sql_info="INSERT INTO CTD_INFO (CTD_STATION_ID,PARAMETER,VALUE) VALUES (%d,'%s','%s')" \
	% (ctd_station_id,MySQLdb.escape_string(key),MySQLdb.escape_string(descriptor[key]))
   cursor.execute (sql_info)
conn.commit()
   
for row in data_matrix:
   sensor_n=0
   for element in row:
      sql_data="INSERT INTO CTD_DATA (CTD_STATION_ID,SENSOR,VALUE) VALUES (%d,%d,'%f')" \
 	 % (ctd_station_id,sensor_n,float(element))
      cursor.execute (sql_data)
      sensor_n+=1
conn.commit()

conn.close()


#-------------------------------------------
# SQL for data structure
#-------------------------------------------
'''
CREATE TABLE IF NOT EXISTS `CTD_DATA` (
  `CTD_DATA_ID` int(11) NOT NULL AUTO_INCREMENT,
  `CTD_STATION_ID` int(11) NOT NULL,
  `SENSOR` int(11) NOT NULL,
  `VALUE` float NOT NULL,
  PRIMARY KEY (`CTD_DATA_ID`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `CTD_INFO` (
  `CTD_INFO_ID` int(11) NOT NULL AUTO_INCREMENT,
  `CTD_STATION_ID` int(11) NOT NULL,
  `PARAMETER` varchar(255) NOT NULL,
  `VALUE` text NOT NULL,
  PRIMARY KEY (`CTD_INFO_ID`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `CTD_STATION` (
  `STATION_ID` int(11) NOT NULL AUTO_INCREMENT,
  `CRUISE` varchar(64) NOT NULL,
  `DATE` varchar(48) NOT NULL,
  `LONGITUDE` varchar(16) NOT NULL,
  `LATITUDE` varchar(16) NOT NULL,
  `STATION_NAME` varchar(32) NOT NULL,
  `DEPTH` float NOT NULL,
  PRIMARY KEY (`STATION_ID`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1;
'''





