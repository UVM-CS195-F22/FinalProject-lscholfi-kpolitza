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
    print("Welcome to the the super store")
    print("(1) to sign in")
    print("(2) to Create an acount")
    choice = int(input("=> "))
    if choice == 1:
        sign_in()
    elif choice == 2:
        create_account()


'''
alows user to sign into an already created account
input: None
Output: None
'''
def sign_in():
    username = input("Username: ")
    password = input("Password: ")
    query = (f'''SELECT username FROM users WHERE username = '{username}' AND password = '{password}';''')
    login_attempt = do_query(query, True)
    if len(login_attempt) == 1:
        print("Successfull Login")
        logged_in()
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
def logged_in(username):
    print("You are logged in")


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
