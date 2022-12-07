#imports
import sqlite3
from flask import Flask, render_template, request, url_for, redirect, session
import json
import plotly
from plotly import data
import plotly.express as px
import pandas as pd

conn = sqlite3.connect('super_store.db', check_same_thread=False)
cur = conn.cursor()

app = Flask(__name__)
app.secret_key = 'verysecretkey'
#app.run()
#to run use
#python -m flask run
#connects to db


@app.route('/',methods=['GET', 'POST'])
def login():
    """This function serves as an app route for the flask app and acts as a home page for directing the user to different functionality.

    Returns:
        _type_: renders the template with a login message
    """
    failed_login_message = ""
    if request.method == 'POST':
        username = request.form.get("username_form", None)
        password = request.form.get("password_form", None)

        query = (f'''SELECT is_supplier FROM users WHERE username = '{username}' AND password = '{password}';''')
        login_attempt = do_query(query, True)
        if len(login_attempt) == 1:
            is_supplier = login_attempt[0][0]  
            session['username'] = username
            session['is_supplier'] = is_supplier
            if is_supplier:
                return redirect(url_for('supplier_logged_in', username=username, is_supplier=is_supplier))
            elif not is_supplier:
                return redirect(url_for('customer_logged_in', username=username, is_supplier=is_supplier))
        else:
            failed_login_message = "login failed, username or password are incorrect"
            return render_template('login.html',failed_login_message=failed_login_message)
    return render_template('login.html',failed_login_message=failed_login_message)

@app.route('/metrics', methods=['GET', 'POST'])
def metrics():
    """This function gets the credit from both customers and suppliers and displays it on the web page as a histogram.

    Returns:
        _type_: renders the template of the graph.
    """
    query_suppliers = "SELECT credit FROM users WHERE is_supplier = 1;"
    query_customers = "SELECT credit FROM users WHERE is_supplier = 0;"
    supp_credit = cur.execute(query_suppliers).fetchall()
    cust_credit = cur.execute(query_customers).fetchall()
    #list comprehension
    supp_out = [item for t in supp_credit for item in t]
    cust_out = [item for t in cust_credit for item in t]
    
    df = pd.DataFrame()
    df['customer_credit'] = cust_out
    
    fig = px.histogram(df, x="customer_credit", nbins=10)
    
    fig.show()
    
    return render_template('metrics.html')


@app.route('/metrics2', methods=['GET', 'POST'])
def metrics2():
    """This function gets the ids and the cost of each item by id and generates a scatter plot for it.

    Returns:
        _type_: renders the template with the graph
    """
    query_id = "SELECT item_id FROM inventory;"
    query_cost = "SELECT cost FROM inventory;"
    id_list = cur.execute(query_id).fetchall()
    cost_list = cur.execute(query_cost).fetchall()
    #list comprehension
    id_out = [item for t in id_list for item in t]
    cost_out = [item for t in cost_list for item in t]

    df = pd.DataFrame()
    df['id'] = id_out
    df['cost'] = cost_out

    fig = px.scatter(df, x="id", y="cost")

    fig.show()

    return render_template('metrics2.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    """This function creates an account by using user input obtained through the form on the web page.

    Returns:
        _type_: renders template and brings new account to the home page depending on whether they are supplier or customer.
    """
    if request.method == "POST":
        username = request.form.get("username_form", None)
        password = request.form.get("password_form", None)
        supplier_or_customer = int(request.form.get("is_supplier"))
        #RADIO BUTTON INPUT
        if supplier_or_customer == 0:
            is_supplier = 0
        elif supplier_or_customer == 1:
            is_supplier = 1
        query = (f'''INSERT INTO users(username,password,credit,is_supplier) VALUES('{username}','{password}','0','{is_supplier}');''')
        cur.execute(query)
        conn.commit()
        session['username'] = username
        session['is_supplier'] = is_supplier
        if is_supplier == 1:
            return redirect(url_for('supplier_logged_in', username=username, is_supplier=is_supplier))
        elif is_supplier == 0:
            return redirect(url_for('customer_logged_in', username=username, is_supplier=is_supplier))
    return render_template('create_account.html')


@app.route('/return_to_home',methods=['GET', 'POST'])
def return_to_home():
    """utility function for passing between functional pages and home page

    Returns:
        _type_: redirects to the home page
    """
    username = request.form.get("username_form", None)
    is_supplier = session['is_supplier']
    if is_supplier:
        return redirect(url_for('supplier_logged_in', username=username, is_supplier=is_supplier))
    else:
        return redirect(url_for('customer_logged_in', username=username, is_supplier=is_supplier))


@app.route('/supplier_profile',methods=['GET', 'POST'])
def supplier_logged_in():
    #NOTE - dont think i need the line below, saving it for a little incase
    #username = request.args['username']  # counterpart for url_for()
    username = session['username'] 
    is_supplier = session['is_supplier']
    print('username: ',username)
    print('is_supplier: ',is_supplier)
    # if request.method == 'POST':
    #     return redirect(url_for('balance', username=username, is_supplier=is_supplier))
    return render_template('supplier_profile.html', username = username)

@app.route('/customer_profile',methods=['GET', 'POST'])
def customer_logged_in():
    #NOTE - dont think i need the line below, saving it for a little incase
    #username = request.args['username']  # counterpart for url_for()
    username = session['username'] 
    is_supplier = session['is_supplier']
    print('username: ',username)
    print('is_supplier: ',is_supplier)
    if request.method == 'POST':
        return redirect(url_for('balance', username=username, is_supplier=is_supplier))
    return render_template('customer_profile.html', username = username)



@app.route('/balance',methods=['GET', 'POST'])
def balance():
    username = session['username'] 
    is_supplier = session['is_supplier']
    user_balance = int(get_user_balance(username))
    if request.method == 'POST':
        submission_message = ""
        try:
            amount = int(request.form.get("add_balance_form", None))
            if amount <= 0:
                submission_message += "You must add more than 0, try again\n"
            else:
                user_balance += amount
        except Exception:
            amount = int(request.form.get("withdrawl_balance_form", None))
            if amount > user_balance:
                submission_message += "You dont have enough funds, try again\n"
            else:
                user_balance -= amount
        print(submission_message)
        if submission_message == "":
            query = (f'''UPDATE users
                    SET credit = '{user_balance}'
                    WHERE username = '{username}'
                    ''')
            success = do_query(query,False)
            if success and submission_message == "":
                submission_message += f"Success, your balance has been updated"
            else:
                submission_message += "an error has occured while changing balance amount, no changes occured to your balance"
        return render_template('balance_submitted.html',user_balance=user_balance, submission_message=submission_message)
    return render_template('balance.html',user_balance=user_balance)



@app.route('/history',methods=['GET', 'POST'])
def history():
    username = session['username'] 
    print(do_query("SELECT * FROM HISTORY WHERE user = 'a'", True))
    is_supplier = session['is_supplier']
    submission_message = ""
    if is_supplier == 0:
        query = (f"SELECT History.date_time, Inventory.item_name, History.purchased FROM (History INNER JOIN Inventory ON Inventory.item_id = History.item_id) WHERE user = '{username}';")
        submission_message = "Purchase History"
    elif is_supplier == 1:
        query = (f"SELECT History.date_time, Inventory.item_name, History.added FROM (History INNER JOIN Inventory ON Inventory.item_id = History.item_id) WHERE user = '{username}';")
        submission_message = "Delivery History"
    hist = do_query(query, True)
    print(hist)
    return render_template('history.html', history_list=hist, submission_message=submission_message)


@app.route('/resupply', methods=['POST', 'GET'])
def resupply():
    username = session['username']
    is_supplier = session['is_supplier']
    owned_items = get_owned_items(username)
    submission_message = ""
    quantity = 0
    owned_list = cur.execute(f"SELECT Inventory.item_id, Inventory.item_name, Inventory.quantity FROM \
                                     (Inventory INNER JOIN Users ON Users.username = Inventory.supplier) WHERE Inventory.supplier = Users.username \
                                     AND Users.username = '{username}';").fetchall()
    print(owned_list)
    if request.method == "POST":
        item = int(request.form.get("item_form", None))
        for i in owned_list:
            if i[0] == item:
                amount = int(request.form.get("amount_form", None))
                for each in owned_list:
                    if (each[0] == item):
                        quantity = int(each[2])
                total = int(quantity) + int(amount)
                query = "UPDATE Inventory SET quantity = " + str(total) + " WHERE item_id = " + str(item) + ";"
                print(query)
                cur.execute(query)
                #success = do_query(query, False)
                submission_message = "Stock updated successfully."
                conn.commit()
                owned_items = get_owned_items(username)
                query = f"INSERT INTO History(item_id, date_time, user, added) VALUES('{item}', date('now','localtime'),'{username}','{amount}');"
                cur.execute(query)
                conn.commit()
                return render_template("resupply_submitted.html", owned_products=owned_items, submission_message=submission_message)
            else:
                submission_message = "Item is not in your catalogue."
    return render_template('resupply.html', owned_products=owned_items, submission_message=submission_message)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    username = session['username']
    is_supplier = session['is_supplier']
    owned_items = get_owned_items(username)
    submission_message = ""
    
    if request.method == "POST":
        name = str(request.form.get("name_form", None))
        #quantity = str(request.form.get("quantity_form", None))
        quantity = 0
        cost = str(request.form.get("price_form", None))
        query = f"INSERT INTO Inventory (item_name, cost, quantity, supplier) VALUES ('" + \
            name + "', " + str(cost) + ", " + str(quantity) + \
            ", '" + str(username) + "');"
        cur.execute(query)
        conn.commit()
        submission_message = "Product added successfully."
        owned_items = get_owned_items(username)
        return render_template("add_product_submitted.html", owned_products=owned_items, submission_message=submission_message)
    return render_template("add_product.html", owned_products=owned_items)

@app.route('/shop', methods=['GET', 'POST'])
def shop():
    '''
    allows user to veiw online inventory and purchase items
    input: Username
    output: None
    '''
    username = session['username']
    is_supplier = session['is_supplier']
    user_balance = get_user_balance(username)
    submission_message = ""
    query = f'''SELECT * FROM Inventory WHERE quantity > 0;'''
    inventory = do_query(query, True)
    
        
    owned_products = []
    for each in inventory:
        owned_products.append(f"ID: {each[0]} Name: {each[1]} Quantity: {each[3]} Price: ${each[2]}")
    
    if request.method == "POST":
        item = int(request.form.get("item", None))
        item -= 1
        quantity = int(request.form.get("quantity", None))
        try:
            if float(inventory[item][3]) < quantity:
                submission_message += "there are not enough items in stock, returning to menue\n"
            new_quantity = (int(inventory[item][3]) - quantity)
            total_cost = float(inventory[item][2]) * quantity
            if total_cost > user_balance:
                submission_message += "You dont have sufficient funds, returning to menue\n"
            else:
                user_balance -= total_cost
        except Exception:
            submission_message += "A non valid item was chosen\n"
        if submission_message == "":
            user_query = f'''UPDATE users SET credit = '{user_balance}' WHERE username = '{username}';'''
            item += 1
            history_query = f'''INSERT INTO History(item_id,date_time, user, purchased) VALUES('{item}', date('now','localtime'),'{username}','{quantity}');'''
            inventory_query = ("UPDATE Inventory SET quantity = " + str(new_quantity) + " WHERE item_id = '" + str(item) + "';")
            query_h = do_query(history_query,False)
            query_u = do_query(user_query,False)
            query_i = do_query(inventory_query, False)
            if query_h and query_u and query_i:
                submission_message +="Purchase successfull, returning to menue\n"
            else:
                submission_message +="Purchase fail, returning to menue\n"
     
        return render_template("shop_submitted.html",submission_message=submission_message)
    return render_template("shop.html", owned_products=owned_products)


def history(username):
    '''
    allows suer to veiw their transaction history
    input: Username
    output: None
    '''
    query = (f"SELECT History.order_id, History.date_time, Inventory.item_name, History.purchased FROM (History INNER JOIN Inventory ON Inventory.item_id = History.item_id) WHERE user = '{username}';")
    hist = do_query(query, True)
    print("--- Purchase History ---")
    for each in hist:
        print(each)


def get_user_balance(username):
    query = (f'''SELECT credit FROM users WHERE username = '{username}';''')
    balance = do_query(query, True)
    return (int(balance[0][0]))


def get_owned_items(username):
    owned_products = cur.execute(f"SELECT Inventory.item_id, Inventory.item_name, Inventory.quantity FROM \
                                     (Inventory INNER JOIN Users ON Users.username = Inventory.supplier) WHERE Inventory.supplier = Users.username \
                                     AND Users.username = '{username}';").fetchall()
    formatted_products = []
    for each in owned_products:
        formatted_products.append(f"ID: {each[0]} Name: {each[1]} Quantity: {each[2]}")
    
    return (formatted_products)


def do_query(query, want_output):
    '''
    performes a query on superstore.db
    input: query the query to be processed, want_output bool if query output is needed or just a success flag is needed
    output:either bool for success or fail or query list or returned output
    '''
    try:
        output = cur.execute(query).fetchall()
        conn.commit()
        if want_output:
            return output
        else:
            return True
    except sqlite3.Error as er:
        print("an error occured while attempting to perform a query")
        return False
