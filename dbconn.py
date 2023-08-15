
# Name of programmer: Fiorella Scarpino 
# Student ID: 21010043
# Date: 1/05/2022
# Final Version. Created with Python
# Description of program: configuration to connect to the database



import mysql.connector
from mysql.connector import errorcode
 
hostname    = "localhost"
username    = "root"
passwd  = "toshi"
db = "horizonhotelDB"

def getConnection():    
    try:
        conn = mysql.connector.connect(host=hostname,                              
                              user=username,
                              password=passwd,
                              database=db)  
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('username/pass is not working')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
        else:
            print(err)                        
    else: 
        return conn   
                
