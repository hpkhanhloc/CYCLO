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
    try:
        cursor.execute("SELECT * FROM customers WHERE CustomerID ="+customerid+";") 
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
    except:
        return jsonify(
                status=200,
                replies=[{
                    'type':'text',
                    'content': 'Sorry, the information provided is not sufficient. Or your customer ID is not correct, please try again!'
                }]    
            )

@app.route('/orderbycode',methods=['POST'])
def orderbycode():
    cursor = dataconn()
    #Fetch the ID
    data = json.loads(request.get_data().decode('utf-8'))
    orderid = data['nlp']['entities']['number'][0]['raw']
    #Query
    try:
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
    except:
        return jsonify(
            status=200,
            replies=[{
                'type':'text',
                'content': 'Sorry, the information provided is not sufficient. Or your order ID is not valid, please try again!'
            }]    
        )

@app.route('/product',methods=['POST'])
def product():
    cursor = dataconn()
    #Fetch the category
    data = json.loads(request.get_data().decode('utf-8'))
    category = data['nlp']['entities']['productname'][0]['raw']
    #Query
    try:
        cursor.execute("SELECT ProductDescription FROM products where Category =\'"+category+"\';")
        row = cursor.fetchone()
        thislist=[]
        while row:
            x = {"descript":str(row[0])}
            thislist.append(x)
            row = cursor.fetchone()
        j = json.dumps(thislist)
        r = json.loads(j)
        content = ''
        for i in r:
            if i == r[-1]:
                content = content + (i['descript'])
            else:
                content = content + i['descript'] + '\n'
    #Put infor to chatbot
        return jsonify(
            status=200,
            replies=[{
                'type':'text',
                'content': 'We have %i products in %s category:\n%s' % (len(r), category, content) 
            }]
        )
    except:
        return jsonify(
            status=200,
            replies=[{
                'type':'text',
                'content': 'Sorry, the information provided is not sufficient. Please choose one of our categories!'
            }]    
        )

@app.route('/weather',methods=['POST'])
def weather():
    #Fetch the location
    data = json.loads(request.get_data().decode('utf-8'))
    location = data['nlp']['entities']['location'][0]['raw']
    #Fect the weather information
    try:
        r = requests.get("https://api.openweathermap.org/data/2.5/weather?q="+location+"&units=metric&appid=63879a9b19bc9fa80e75ca0adc836c7e")
        #Put infor to chatbot
        return jsonify(
            status=200,
            replies=[{
                'type': 'text',
                'content': 'The weather in %s is %s now,\nTemperature: %8.2f%s,\nPressure: %i hPa,\nHumidity: %i%%.' % (r.json()['name'], r.json()['weather'][0]['description'],r.json()['main']['temp'],chr(176)+'C', r.json()['main']['pressure'],r.json()['main']['humidity'])
        }]
    )
    except:
        return jsonify(
            status=200,
            replies=[{
                'type': 'text',
                'content': 'Sorry, I can not recognize the city provided.)
        }]
    )

@app.route('/purchasehistory',methods=['POST'])
def purchasehistory():
    cursor = dataconn()
    #Fetch the ID
    data = json.loads(request.get_data().decode('utf-8'))
    customerid = data['nlp']['entities']['number'][0]['raw']
    #Query
    try:
        cursor.execute("SELECT orderID, products.productdescription, orderdate, orderstatus FROM orders,products WHERE CustomerID ="+customerid+" and orders.productid = products.productid;") 
        row = cursor.fetchone()
        thislist=[]
        while row:
            x = {"orderid":str(row[0]),"product":str(row[1]),"orderdate":str(row[2]),"orderstatus":str(row[3])}
            thislist.append(x)
            row = cursor.fetchone()
        j = json.dumps(thislist)
        r = json.loads(j)
        content = ''
        raw = ''
        if len(r) == 0:
            content = 'You have not ordered before.'
        else:
            for i in r:
                if i == r[-1]:
                    content = content + 'OrderId: '+ i['orderid'] + '\n'+ 'Product: '+ i['product'] + '\n'+ 'Orderdate: '+ i['orderdate'] + '\n'+ 'Status: '+i['orderstatus']
                else:
                    raw = raw + 'OrderId: '+ i['orderid'] + '\n'+ 'Product: '+ i['product'] + '\n'+ 'Orderdate: '+ i['orderdate'] + '\n'+ 'Status: '+i['orderstatus'] + '\n'
                    raw = raw + '\n'
                    content = 'You have ordered %i:\n%s' % (len(r),raw)
        #Put infor to chatbot
        return jsonify(
            status=200,
            replies=[{
                'type':'text',
                'content': ('%s') % (content)
            }]
        )
    except:
        return jsonify(
            status=200,
            replies=[{
                'type':'text',
                'content': 'Sorry, the information provided is not sufficient. Or your customer ID is not correct, please try again!'
            }]
        )

@app.route('/errors', methods=['POST']) 
def errors(): 
  print(json.loads(request.get_data())) 
  return jsonify(status=200)

if __name__ == "__main__":
    app.run(port=port, host = '0.0.0.0')