import pymysql

HOST = "localhost"
DB = "scrapnet"
PASSWORD = ""
USER = "root"
PORT = 3308

def iud(qry,val):
    con=pymysql.connect(host=HOST,port=PORT,user=USER,password=PASSWORD,db=DB)
    cmd=con.cursor()
    cmd.execute(qry,val)
    id=cmd.lastrowid
    con.commit()
    con.close()
    return id

def selectone(qry,val):
    con=pymysql.connect(host=HOST,port=PORT,user=USER,password=PASSWORD,db=DB,cursorclass=pymysql.cursors.DictCursor)
    cmd=con.cursor()
    cmd.execute(qry,val)
    res=cmd.fetchone()
    return res

def selectall(qry):
    con=pymysql.connect(host=HOST,port=PORT,user=USER,password=PASSWORD,db=DB,cursorclass=pymysql.cursors.DictCursor)
    cmd=con.cursor()
    cmd.execute(qry)
    res=cmd.fetchall()
    return res

def selectall2(qry,val):
    con=pymysql.connect(host=HOST,port=PORT,user=USER,password=PASSWORD,db=DB,cursorclass=pymysql.cursors.DictCursor)
    cmd=con.cursor()
    cmd.execute(qry,val)
    res=cmd.fetchall()
    return res