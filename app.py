#imports
import sqlite3


#connects to db
conn = sqlite3.connect('super_store.db')
cur = conn.cursor()
TEST = True

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
    if success:
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
            print("(1) to manage your balance")
            print("(2) add or resupply items")
            print("(3) Veiw your items and history ")
            print("(4) to exit")
            choice = int(input("=> "))
            if choice == 1:
                manage_balance(username,is_supplier)
            elif choice == 2:
                resupply(username)
            elif choice == 3:
                exit()
            else:
                exit()
        else:
            print("You are logged in")
            print("(1) to manage balance")
            print("(2) purchase new items")
            print("(3 veiw your transaction history")
            print("(4) to exit")
            choice = int(input("=> "))
            if choice == 1:
                manage_balance(username,is_supplier)
            elif choice == 2:
                shop(username,is_supplier)
            elif choice == 3:
                history(username)
            else:
                exit()
       
    exit()

'''
allows user to veiw and change their balance
input: Username
Output: None
'''
def manage_balance(username, is_supplier):
    user_balance = get_user_balance(username)

    print(f"Your current balance is: {user_balance}")
    print("(1) to add new funds to your balance")
    print("(2) to withdrawl funds from balance")
    print("(3) to exit")
    choice = int(input("=>"))
    if choice == 1:
        amount = int(input("how much would you like to add: "))
        while amount <= 0:
            print("You must add more than 0")
            amount = int(input("how much would you like to add: "))
        print("Simulating Third party credit withdrawls....")
        user_balance += amount
    elif choice == 2:
        amount = int(input("how much would you like to withdraw: "))
        while amount > user_balance:
            print("You dont have enough funds")
            amount = int(input("how much would you like to withdraw: "))
        else:
            user_balance -= amount
    query = (f'''UPDATE users
                    SET credit = '{user_balance}'
                    WHERE username = '{username}'
                    ''')
    success = do_query(query,False)
    if success:
        print(f"Your balance is: {user_balance}")
        print(f"Returning you to the menue")
    else:
        print("an error has occured while changing balance amount, returning you to menue")

    


'''
allows user to veiw online inventory and purchase items
input: Username
output: None
'''
def shop(username,is_supplier):
    user_balance = get_user_balance(username)

    query = f'''SELECT * FROM Inventory;'''
    inventory = do_query(query, True)

    print("| Item number |            Item name            | price | quantity |   Supplier   |")
    print("|---------------------------------------------------------------------------------|")
    for item in inventory:
        print(f'''|{item[0]:9}    | {item[1]:^30}  | {item[2]:5} | {item[3]:4}     | {item[4]:^12} |''')
        print("|---------------------------------------------------------------------------------|")
    print("Type the item number of the item you would like to purchase")
    item = int(input("=>"))
    item -= 1
    print("How many do you want to purchase?")
    quantity = int(input("=>"))
    if float(inventory[item][3]) < quantity:
            print("there are not enough items in stock, returning to menue")
            logged_in(username,is_supplier)
    total_cost = float(inventory[item][2]) * quantity
    new_quantity = (int(inventory[item][3]) - quantity)
    print(new_quantity)
    if total_cost > user_balance:
            print("You dont have sufficient funds, returning to menue")
            logged_in(username,is_supplier)
    user_balance -= total_cost
    print(f"confirm you would like to buy {quantity} {inventory[item][1]} for a total of {total_cost}")
    print("(1) to confirm purchase")
    print("(2) to cancel purchase")
    confirmation = int(input("=>"))
    if confirmation == 1:
        print("processing purchase...")
        user_query = f'''UPDATE users SET credit = '{user_balance}' WHERE username = '{username}';'''
        history_query = f'''INSERT INTO History(item_id,date_time, user, purchased) VALUES('{item}', date('now','localtime'),'{username}','{quantity}');'''
        inventory_query = ("UPDATE Inventory SET quantity = " + str(new_quantity) + " WHERE item_id = '" + str(item+1) + "';")
        print(inventory_query)
        query_h = do_query(history_query,False)
        query_u = do_query(user_query,False)
        query_i = do_query(inventory_query, False)
        if query_h and query_u and query_i:
            print("Purchase successfull, returning to menue")
        else:
            print("Purchase fail, returning to menue")

    else:
        print("canceling purchase, returning you to main menue")
        logged_in(username,is_supplier)


    

    return 0

'''
allows suer to veiw their transaction history
input: Username
output: None
'''
def history(username):
    #TODO: implement this
    return 0


def get_user_balance(username):
    query = (f'''SELECT credit FROM users WHERE username = '{username}';''')
    balance = do_query(query, True)
    return (int(balance[0][0]))



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
            return True
    except sqlite3.Error as er:
        print("an error occured while attempting to perform a query")
        if TEST:
            print(er)
        return False

if TEST:
    print(do_query("SELECT * FROM History", True))
    print(do_query("SELECT * FROM Users WHERE username = 'a';", True))
    shop('a',True)


welcome()
