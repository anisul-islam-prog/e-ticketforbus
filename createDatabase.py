import sqlite3
 
conn = sqlite3.connect("mydatabase.db") # or use :memory: to put it in RAM
 
cursor = conn.cursor()
 
# create a table
cursor.execute("""CREATE TABLE USERS
                  (id text, lat_start real,long_start real, 
                   lat_end real, long_end real, balance real, counter integer) 
               """)
