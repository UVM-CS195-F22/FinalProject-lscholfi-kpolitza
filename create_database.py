import sqlite3
from sqlite3 import Error
import pandas as pd


def to_sqllite(u_file, i_file):
    connection = None
    db = "super_store.db"

    try:
        connection = sqlite3.connect(db)
        cur = connection.cursor()
        create_u_table = "CREATE TABLE IF NOT EXISTS Users(username TEXT PRIMARY KEY, password TEXT NOT NULL, credit INTEGER NOT NULL, is_supplier BOOL NOT NULL);"
        create_i_table = "CREATE TABLE IF NOT EXISTS Inventory(item_id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT NOT NULL, cost INTEGER NOT NULL, quantity INTEGER NOT NULL, supplier TEXT NOT NULL);"
        create_h_table = "CREATE TABLE IF NOT EXISTS History(order_id INTEGER PRIMARY KEY AUTOINCREMENT, item_id INTEGER NOT NULL, date_time TEXT NOT NULL, user TEXT NOT NULL, purchased INTEGER, added INTEGER)"

        cur.execute(create_u_table)
        cur.execute(create_i_table)

        users = pd.read_csv(u_file)
        inventory = pd.read_csv(i_file)
        
        users.to_sql('Users', connection, if_exists='replace', index=False, dtype={"username": "TEXT PRIMARY KEY", "password": "TEXT NOT NULL", "credit": "INTEGER NOT NULL", "is_supplier": "BOOL NOT NULL"})
        inventory.to_sql('Inventory', connection, if_exists='replace', index=False, dtype={"item_id": "INTEGER PRIMARY KEY", "item_name": "TEXT NOT NULL", "cost": "INTEGER NOT NULL", "quantity": "INTEGER NOT NULL", "supplier": "TEXT NOT NULL"})
        print("Database loaded...")
        connection.close()

    except Error as e:
        print(e)

def main():
    to_sqllite("user_data.csv", "item_data.csv")
    print("Database saved...")
    
main()