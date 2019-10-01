from flask import Flask, request, jsonify
import pyodbc
import json
import requests
import os

app = Flask(__name__)
port = '443'

#This fuction is use to connect with database which stored on Azure
def dataconn():
    server = 'cyclo.database.windows.net'
    database = 'CYCLO'
    username = 'cycloadmin'
    password = 'Cyclosummer2019'
    driver= '{ODBC Driver 17 for SQL Server}'
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    return cursor

# This functione return customer information to chatbot.
# If there is valid information stored in database, this API will handle it and return to the bot.
# The bot answer "Hi, customer name"
# In contrast, cannot find information, the bot answer customer and ask them input again
@app.route('/customer',methods=['POST'])
def customer():
    cursor = dataconn()                                                 #connect with database
    
    #Fetch the ID
    data = json.loads(request.get_data().decode('utf-8'))               #load customerid from user's chat
    customerid = data['nlp']['entities']['number'][0]['raw']
    
    #Query database to find information
    try:
        cursor.execute("SELECT * FROM customers WHERE CustomerID ="+customerid+";") 
        row = cursor.fetchone()
        while row:
            x = {"id":str(row[0]),"firstname":str(row[1]),"lastname":str(row[2]),"address":str(row[3]),"phone":str(row[4]),"email":str(row[5])}
            row = cursor.fetchone()
        j = json.dumps(x)
        r = json.loads(j)

        #Put information to chatbot
        return jsonify(
            status=200,
            replies=[{
                'type':'text',
                'content': 'Hi, %s.' % (r['firstname'])                 #This is the answer of chatbot
            }]    
        )
    except:                                                             #Through exception if information is invalid
        return jsonify(
                status=200,
                replies=[{
                    'type':'text',
                    'content': 'Sorry, the information provided is not sufficient. Or your customer ID is not correct, please try again!'
                }]    
            )

# This function check user identity.
# Each of user will have different authentication code.
# The bot will ask and then pass the code to API then, API check on database either correct or not.
@app.route('/authentication',methods=['POST'])
def authentication():
    cursor = dataconn()                                                 #Connect to database
    
    #Fetch the customer ID and authentication
    data = json.loads(request.get_data().decode('utf-8'))
    customerid = data['conversation']['memory']['completed']['raw']
    authentication = data['nlp']['source']
    
    #Query database to find information
    try:
        cursor.execute("SELECT Authentication FROM customers WHERE CustomerID ="+customerid+";") 
        row = cursor.fetchone()
        while row:
            x = {"authentication":str(row[0])}
            row = cursor.fetchone()
        j = json.dumps(x)
        r = json.loads(j)
        check = r['authentication']
        
        #Put infor to chatbot
        if authentication == check:                                     #authentication code correct
            result = purchasehistory() 
            return jsonify(
                status=200,
                replies=[{
                    'type':'text',
                    'sentiment':'positive',
                    'content': 'Sucessful authentication.\n %s' % (result)
                }]    
            )
        
        else:                                                           #chatbot answer wrong if authentication failed
            return jsonify(
                status=200,
                replies=[{
                    'type':'text',
                    'sentiment':'negative',
                    'content': 'Your authentication is wrong.'
                }]    
            )
    except:                                                             #through exception in case invalid information
        return jsonify(
                status=200,
                replies=[{
                    'type':'text',
                    'content': 'Sorry, the information provided is not sufficient. Please try again!'
                }]    
            )

# This function check order detail by orderid.
# If user require check order, the bot will response by request orderid, then get it and sent to API to check in datasbase.
@app.route('/orderbycode',methods=['POST'])
def orderbycode():
    cursor = dataconn()                                                 #connect database                         
    
    #Fetch the ID
    data = json.loads(request.get_data().decode('utf-8'))
    orderid = data['nlp']['entities']['number'][0]['raw']
    
    #Query database to find information
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
    except:                                                     #exception in case not valid form of orderid/ invalid information
        return jsonify(
            status=200,
            replies=[{
                'type':'text',
                'content': 'Sorry, the information provided is not sufficient. Or your order ID is not valid, please try again!'
            }]    
        )

# This function will list all available products to customer.
# If the bot regconizes that users are looking for products, it will list available categories to user.
# After user selection, the bot call API by this function and find all products in database belong to input categories.
# Then, API return information to chatbot to display for customer.
@app.route('/product',methods=['POST'])
def product():
    cursor = dataconn()                                             #connect database
    
    #Fetch the input category
    data = json.loads(request.get_data().decode('utf-8'))
    category = data['nlp']['entities']['productname'][0]['raw']
    
    #Query
    try:
        if category in ('Touring Bike','Road Bike', 'Off Road Bike','Acessories','Electronic Bike'):
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
        else:                                               #return this if user input not valid category
            return jsonify(
                status=200,
                replies=[{
                    'type':'text',
                    'content': 'Sorry, the information provided is not sufficient. Please choose one of our categories!'
                }]
            )
    except:                                                 #return this if user input not valid category
        return jsonify(
            status=200,
            replies=[{
                'type':'text',
                'content': 'Sorry, the information provided is not sufficient. Please choose one of our categories!'
            }]    
        )

# This function will get weather information from open source -  openweathermap by call its API.
# If the bot regconize that customer asking about weather information, it will ask user which city/location.
# Then, is call this function and pass location into it, this function then call Openweather API get weather information.
# Finally, put weather information back to chatbot and displays to user.
@app.route('/weather',methods=['POST'])
def weather():
    #Fetch the location from chatbot conversation
    data = json.loads(request.get_data().decode('utf-8'))
    location = data['nlp']['entities']['location'][0]['raw']
    
    #Fect the weather information from Openweather API
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
    except:                                             #Exception incase openweather can not find information.
        return jsonify(
            status=200,
            replies=[{
                'type': 'text',
                'content': 'Sorry, I can not recognize the city provided.'
        }]
    )


@app.route('/errors', methods=['POST']) 
def errors(): 
  print(json.loads(request.get_data())) 
  return jsonify(status=200)

if __name__ == "__main__":
    app.run(port=port, host = '0.0.0.0')