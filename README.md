cnv2db
======

 
 A simple Seabird cnv file parser that stores the data
 into a mysql db 

 Requisites: python-mysqldb library

 version 0.4.0
 
 License: CC-BY-NC-SA v. 3.0
  
 Author:
 Rocco De Marco - November 2012
 email: "rocco_demarco(a)an_ismar_cnr_it" | sed s/"_"/\./g | sed s/"(a)"/"@"/g

 File included:

    cnv2db_class: parser class
    cnv2db: main program
    tables.sql: table definition sql
    db.py_entry.txt: web2py db model (if you plan to use with web2py framework)


 Prerequisite:
  1) Create a mysql database
  2) update mysql access information inside cnv2db file

 Usage:
  
    python cnv2db your_cnv_file

