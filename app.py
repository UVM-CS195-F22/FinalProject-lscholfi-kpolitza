#imports
import sqlite3


#connects to db
conn = sqlite3.connect('super_store.db')
cur = conn.cursor()

'''
welcomes user to superstore website
input: None
Output None
'''
def welcome():
    print(do_query("SELECT * FROM users", True))
    print("Welcome to the the super store")
    print("(1) to sign in")
    print("(2) to Create an acount")
    print("(3) to exit")
    choice = int(input("=> "))
    if choice == 1:
        sign_in()
    elif choice == 2:
        create_account()
    elif choice == 3:
        exit()


'''
allows user to restock existing items or add a new one
input: None
output: None
'''
def resupply(username):
    print("(1) to restock product")
    print("(2) to deliver a new item")
    choice = int(input("=> "))
    quantity = 0
    owned_products = cur.execute(f"SELECT Inventory.item_id, Inventory.item_name, Inventory.quantity FROM \
                                     (Inventory INNER JOIN Users ON Users.username = Inventory.supplier) WHERE Inventory.supplier = Users.username \
                                     AND Users.username = '{username}';").fetchall()
    print(f"--- Products supplied by '{username}' ---")
    for each in owned_products:
        print(f"ID: '{each[0]}' Name: '{each[1]}' Quantity: '{each[2]}'")
    
    if choice == 1:
        #restock existing product
        while choice == 1:
            print("Enter the ID of the item to restock")
            item = str(input("=> "))
            for each in owned_products:
                if(each[0] == item):
                    quantity = int(each[2])
            print("Enter number being restocked")
            num = input("=> ")
            total = int(quantity) + int(num)
            cur.execute("UPDATE Inventory SET quantity = " + str(total) + " WHERE item_name = '" + item + "';")
            conn.commit()
            print("Product restocked")
            print("(1) to restock another item")
            print("(2) to exit")
            choice = int(input("=> "))
    else:
        #add a new product
        while choice == 2:
            print("Enter the name of the item being added")
            name = str(input("=> "))
            print("Enter the quantity being added")
            quantity = input("=> ")
            print("Enter the price of each unit")
            cost = input("=> ")
            query = f"INSERT INTO Inventory (item_name, cost, quantity, supplier) VALUES ('" + name + "', " + str(cost) + ", " + str(quantity) + ", '" + str(username) + "');"
            cur.execute(query)
            conn.commit()
            print("Product added")
            print("(2) to add another item")
            print("(3) to exit")
            choice = int(input("=> "))


'''
alows user to sign into an already created account
input: None
Output: None
'''
def sign_in():
    username = input("Username: ")
    password = input("Password: ")
    query = (f'''SELECT is_supplier FROM users WHERE username = '{username}' AND password = '{password}';''')
    login_attempt = do_query(query, True)
    if len(login_attempt) == 1:
        print("Successfull Login")
        is_supplier = login_attempt[0][0]
        logged_in(username, is_supplier)

    else:
        print("username and/or password are incorrect, returning to menue")
        welcome()

    

'''
allows user to make a new account with super store
input: None
output: None
'''
def create_account():
    print("Create and account here")
    print("please provide the following information to creat your account")
    print("Note, your username must be identical to any other users")
    username = input("username: ")
    password = input("Password: ")
    print("\n Are you a customer or supplier?\n type 1 for customer\n type 2 for supplier")
    supplier_or_customer = int(input("=>"))
    if supplier_or_customer == 1:
        is_supplier = False
    elif supplier_or_customer == 2:
        is_supplier = True
    query = (f'''INSERT INTO users(username,password,credit,is_supplier) VALUES('{username}','{password}','0','{is_supplier}');''')
    success = do_query(query, False)
    if success == 1:
        print("account successfully created, returning you to the main menue. You may now log into your account")
        welcome()
    else:
        print("try a new username as that one could already be in use, returning you to main menue")
        welcome()


'''
welcomes user once logged in
input:username
output:
'''
def logged_in(username,is_supplier):
    choice = 0
    while choice != 4:
        if is_supplier:
            print("You are logged in")
            print("(1) to veiw / change balance")
            print("(2) add or resupply items")
            print("(3) Veiw your items and history ")
            print("(4) to exit")
            choice = int(input("=> "))
            if choice == 1:
                sign_in()
            elif choice == 2:
                resupply(username)
            elif choice == 3:
                exit()
            else:
                exit()
        else:
            print("You are logged in")
            print("(1) to veiw / change balance")
            print("(2) purchase some new stuff")
            print("(3) view your transaction history")
            choice = int(input("=> "))
            if choice == 1:
                sign_in()
            elif choice == 2:
                create_account()
            elif choice == 3:
                exit()
       
    exit()






'''
performes a query on superstore.db
input: query the query to be processed, want_output bool if query output is needed or just a success flag is needed
output:either bool for success or fail or query list or returned output
'''
def do_query(query, want_output):
    try:
        output = cur.execute(query).fetchall()
        conn.commit()
        if want_output:
            return output
        else:
            return 1
    except sqlite3.Error:
        print("an error occured while attempting to perform a query")
        return 0


welcome()
