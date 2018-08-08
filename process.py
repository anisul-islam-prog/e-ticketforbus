#! /usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import sqlite3
import jinja2

form = cgi.FieldStorage()
rfid=form.getvalue('id')
tk=form.getvalue('bal')


conn = sqlite3.connect("mydatabase.db")
c = conn.cursor();	
c.execute("SELECT Count(*) FROM USERS")
count=c.fetchone()[0]

if count==0:
	
	id=(rfid)
	lat=0
	long=0
	lat_end=0
	long_end=0	
	co=0
	money=(tk)
	c.executemany("INSERT INTO USERS VALUES (?, ?, ?,?,?,?,?)", [(id,lat,long,lat_end,long_end,money,co)])
	conn.commit()


c.execute("SELECT id FROM USERS")
rows=c.fetchall()
flag=False

for row in rows:
	row="""%s"""%row
	if rfid==row:
		flag=True
if flag==True:
	money=(tk)
	c.execute("UPDATE USERS SET balance=? WHERE id=?",[money,rfid])
 	conn.commit()
else:
	id=(rfid)
	lat=0
	long=0
	lat_end=0
	long_end=0	
	co=0
	money=(tk)
	c.executemany("INSERT INTO USERS VALUES (?, ?, ?,?,?,?,?)", [(id,lat,long,lat_end,long_end,money,co)])
	conn.commit()
	
uid=[]
mon=[]

global wholepage
print("Content-Type: text/html\n")
print("""<!doctype html><title>Hello</title>""")
bigtempl = """
<html>
<head>

</head>
<body style="font-size: 150%;background: #bada55;">
        <table style="width: 60%;border-collapse: separate;background: beige;margin: 3em auto;padding: 10px;font-family: Helvetica, Arial, sans-serif;border: 2px solid #499403;">
	 <caption Style="margin-bottom: 25px;font-variant: small-caps;letter-spacing: .03em;word-spacing: .05em;color: #499403;">Automated GPS Based Ticketing Service</caption> 
	<tr style="background-color: inherit;">
    <th Style="">ID</th>
    <th Style="">Balance</th>
</tr>
        {rows}
        </table>
    </body>
</html>
"""

rowtempl = """
<tr style="background-color: inherit; ">
<td Style="text-align: center;background-color: inherit; ">{number}
</td>
<td Style="text-align: center;background-color: inherit; ">{letter}
</td>
</tr>
"""
c.execute("SELECT id FROM USERS")
rows=c.fetchall()

for row in rows:
    row="""%s"""%row   	 
    uid.append(row)
    c.execute("SELECT balance FROM USERS WHERE id=?",[row])
    balan=c.fetchall()
    tu=(balan[0])
    cu=tu[0]
    mon.append(cu)  
 
    			
   	 
    #uid.append(row)
    
    
lst = zip(uid, mon)
rows_temp = [rowtempl.format(number=number, letter=letter) for number, letter in lst]
rows_temp = "".join(rows_temp)
wholepage= bigtempl.format(rows=rows_temp)
print wholepage
    #print '<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(row)]))

#print """</table>"""

#print type(result)


