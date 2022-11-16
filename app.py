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
    print("(3 to exit")
    choice = int(input("=> "))
    if choice == 1:
        sign_in()
    elif choice == 2:
        create_account()
    elif choice == 3:
        exit()



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
                manage_balance(username)
            elif choice == 2:
                create_account()
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
                manage_balance(username)
            elif choice == 2:
                shop(username)
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
def manage_balance(username):
    query = (f'''SELECT credit FROM users WHERE username = '{username}';''')
    balance = do_query(query, True)
    balance = int(balance[0][0])
    print(f"Your current balance is: {balance}")
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
        balance += amount
    elif choice == 2:
        amount = int(input("how much would you like to withdraw: "))
        while amount > balance:
            print("You dont have enough funds")
            amount = int(input("how much would you like to withdraw: "))
        else:
            balance -= amount
    query = (f'''UPDATE users
                    SET credit = '{balance}'
                    WHERE username = '{username}'
                    ''')
    success = do_query(query,False)
    if success:
        print(f"Your balance is: {balance}")
        print(f"Returning you to the menue")
    else:
        print("an error has occured while changing balance amount, returning you to menue")


'''
allows user to veiw online inventory and purchase items
input: Username
output: None
'''
def shop(username):
    #TODO: implement this
    return 0

'''
allows suer to veiw their transaction history
input: Username
output: None
'''
def history(username):
    #TODO: implement this
    return 0






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
    except sqlite3.Error:
        print("an error occured while attempting to perform a query")
        return False



welcome()
