import mysql.connector
from flask import session


class admin_operation:
    def connection(self):
        db=mysql.connector.connect(host="localhost", port="3306", user="root", password="", database="rideon")
        return db

    
    def admin_provider_report(self):
        con=self.connection()
        sq="select city,count(city) from provider group by city"
        
        mycursor = con.cursor()
        mycursor.execute(sq)
        row=mycursor.fetchall()
        mycursor.close()
        con.close()
        return row

   