from flask import Flask, request, jsonify
import pyodbc
import json
app = Flask(__name__)

@app.route("/")
def main():
    server = 'cyclo.database.windows.net'
    database = 'TutorialDB'
    username = 'cycloadmin'
    password = 'Cyclosummer2019'
    driver= '{ODBC Driver 17 for SQL Server}'
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    #Sample select query
    cursor.execute("SELECT * FROM dbo.Customers;") 
    row = cursor.fetchone()
    thislist =[]
    while row:
        x = {"id":str(row[0]),"name":str(row[1]),"location":str(row[2]),"mail":str(row[3])}
        thislist.append(x)
        row = cursor.fetchone()
    j = json.dumps(thislist)
    return j

if __name__ == "__main__":
    app.run()

