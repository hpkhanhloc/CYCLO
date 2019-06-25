from flask import Flask, request, jsonify
import pyodbc
import json
import requests
import os

app = Flask(__name__)
port = '443'

def dataconn():
    server = 'cyclo.database.windows.net'
    database = 'CYCLO'
    username = 'cycloadmin'
    password = 'Cyclosummer2019'
    driver= '{ODBC Driver 17 for SQL Server}'
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    return cursor

@app.route('/customer',methods=['POST'])
def customer():
    cursor = dataconn()
    #Fetch the ID
    data = json.loads(request.get_data().decode('utf-8'))
    customerid = data['nlp']['entities']['number'][0]['raw']
    #Query
    cursor.execute("SELECT * FROM customer WHERE CustomerID ="+customerid+";") 
    row = cursor.fetchone()
    while row:
        x = {"id":str(row[0]),"firstname":str(row[1]),"lastname":str(row[2]),"address":str(row[3]),"phone":str(row[4]),"email":str(row[5])}
        row = cursor.fetchone()
    j = json.dumps(x)
    r = json.loads(j)
    #Put infor to chatbot
    return jsonify(
        status=200,
        replies=[{
            'type':'text',
            'content': 'CustomerID: %s \nFirst Name: %s \nLast Name: %s \nAddress: %s \nPhone: %s \nEmail: %s' % (r['id'], r['firstname'], r['lastname'], r['address'],r['phone'],r['email']),
        }]    
    )

@app.route('/order',methods=['POST'])
def order():
    cursor = dataconn()
    #Fetch the ID
    data = json.loads(request.get_data().decode('utf-8'))
    orderid = data['nlp']['entities']['number'][0]['raw']
    #Query
    cursor.execute("""SELECT orders.OrderID, customers.FirstName, products.ProductDescription, orders.OrderDate, orders.OrderStatus 
    from orders,customers,products 
    where orderid = \'"""+orderid+"""\' and orders.CustomerID = customers.CustomerID 
    and orders.ProductID = products.ProductID;""") 
    row = cursor.fetchone()
    while row:
        x = {"id":str(row[0]),"name":str(row[1]),"product":str(row[2]),"date":str(row[3]),"status":str(row[4])}
        row = cursor.fetchone()
    j = json.dumps(x)
    r = json.loads(j)
    #Put infor to chatbot
    return jsonify(
        status=200,
        replies=[{
            'type':'text',
            'content': 'OrderID: %s \nName: %s \nProduct: %s \nOrder Date: %s \nStatus: %s' % (r['id'], r['name'], r['product'], r['date'],r['status']) 
        }]
    )

@app.route('/errors', methods=['POST']) 
def errors(): 
  print(json.loads(request.get_data())) 
  return jsonify(status=200)

if __name__ == "__main__":
    app.run(port=port, host = '0.0.0.0')

