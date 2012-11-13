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
# version 0.4.1
# License: CC-BY-NC-SA v. 3.0
# Author:
# Rocco De Marco (rocco_demarco(a)an_ismar_cnr_it) -> s/_/\./g
# November 2012
#
###############################################################
''' CHANGELOG 
v. 0.4.1
1) Splitted source in two files

v. 0.4.0
1) Rewritten in class style

v. 0.3.2: 
1) choosed "NMEA UTC (Time)" as date/time parameter instead than start_date

'''


import re


class cnvParser:
   def parser(self):
      # General info: line that start with single "*"
      g_info=re.findall(r"^\* (.*) = (.*)",self.cnv[0:self.cnv.find("**")],re.MULTILINE)
		# Note: I splitted the buffer at the first "**" occurrence to avoid
		# a parsing problem with non-standard information in some cnv file.
 		# In this case I didn't used a regex due lacking performances
      # notes: these lines start with "**"
      notes=re.findall(r"^\*\* (.*): \s*(.*)",self.cnv,re.MULTILINE)
      # Measure info
      m_info=re.findall(r"^\# (.*) = (.*)",self.cnv,re.MULTILINE)
      # Data
	        # raw_data=re.findall(r"^\*END\*\r\n(.*)",cnv,re.MULTILINE|re.DOTALL)
      raw_data=self.cnv[self.cnv.find("*END*")+7:]
		# Also in this case I prefered to partition the buffer without regex
		# to reduce the excecution time
      for element in m_info+g_info+notes:
         self.parameters[element[0]]=element[1].rstrip("\r\n")
         self.n_parameters+=1
      if self.n_parameters==0:		# If no data read
	 return 0			# abort
      vector=[]
      value=""
      previous=" "
      for char in raw_data:
         if char=="\n":
            vector.append(float(value))               # add the last value in the array
	    self.data_matrix.append(vector)           # append the values to the data matrix
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

   def __init__(self,ctd_file_content):
      self.cnv=ctd_file_content
      self.parameters={}
      self.data_matrix=[]
      self.n_parameters=0
      self.n_sensors=0
      self.parser()
      if self.n_parameters>0:
         self.nquan = int(self.parameters["nquan"])  	# Number of sensors/data columns
	 self.filetype = self.parameters["file_type"] 	# CNV data type: must be "ascii"
	 self.cruise = self.parameters.get("Cruise","")
	 self.date=self.parameters.get("NMEA UTC (Time)","")
	 self.longitude=self.parameters.get("NMEA Longitude","")
	 self.latitude=self.parameters.get("NMEA Latitude","")
	 self.station=self.parameters.get("Station","")
	 self.depth=float(self.parameters.get("Bottom",""))












