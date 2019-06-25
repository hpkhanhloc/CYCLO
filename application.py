from flask import Flask, request, jsonify
import pyodbc
import json
import requests
import os

app = Flask(__name__)

@app.route('/',methods=['POST'])
def index():
    server = 'cyclo.database.windows.net'
    database = 'TutorialDB'
    username = 'cycloadmin'
    password = 'Cyclosummer2019'
    driver= '{ODBC Driver 17 for SQL Server}'
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    #Fetch the ID
    data = json.loads(request.get_data().decode('utf-8'))
    customerid = data['nlp']['entities']['number'][0]['raw']
    #Sample select query
    cursor.execute("SELECT * FROM dbo.Customers WHERE CustomerId ="+customerid+";") 
    row = cursor.fetchone()
    while row:
        x = {"id":str(row[0]),"name":str(row[1]),"location":str(row[2]),"mail":str(row[3])}
        row = cursor.fetchone()
    j = json.dumps(x)
    r = json.loads(j)
    return jsonify(
        status=200,
        replies=[{
            'type':'text',
            'content': 'CustomerID: %s,\nName: %s,\nLocation: %s,\nEmail: %s.' % (customerid, r['name'], r['location'], r['mail']),
        }]    
    )

@app.route('/errors', methods=['POST']) 
def errors(): 
  print(json.loads(request.get_data())) 
  return jsonify(status=200)

app.run(port=80,host='0.0.0.0')

