from connect import connect 
import csv 

def insert_contact(name, phone):
    try:
        conn=connect() # connects python to PostgreSQL/Database
        cur=conn.cursor() # a tool that sends commands to the PostgreSQL/Python through the connection

        cur.execute(
            "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
            (name, phone)
        )

        conn.commit() # saving changes that were maid --> (if INSERT/UPDATE/DELETE)
        cur.close()
        conn.close()

    except Exception as e:
        print("Error:", e)

def csv_reader(filename):
    try:
        conn=connect()
        cur=conn.cursor()

        with open(filename, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                cur.execute(
                    "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
                    (row[0], row[1])
                )
        conn.commit()
        cur.close()
        conn.close()
        print("CSV imported")

    except Exception as e:
        print("Error:", e)

def get_all():
    try:
        conn=connect()
        cur=conn.cursor()

        cur.execute("SELECT * FROM contacts")
        rows=cur.fetchall()

        for row in rows:
            print(row)

        cur.close()
        conn.close()
    except Exception as e:
        print("Error:", e)

def find_by_name(name):
    try:
        conn=connect()
        cur=conn.cursor()
        cur.execute(
            "SELECT * FROM contacts WHERE name ILIKE %s", # ILIKE --> case-insensitive (PostgreSQL only)
            (f"%{name}%",)
            )
        
        print(cur.fetchall())

        cur.close()
        conn.close()
    except Exception as e:
        print("Error:", e)

def find_by_number(prefix):
    try:
        conn=connect()
        cur=conn.cursor()
        cur.execute("SELECT * FROM contacts WHERE phone LIKE %s", 
                    (prefix + "%",))
        print(cur.fetchall())
        
        cur.close()
        conn.close()
    except Exception as e:
        print("Error:", e)

def Update_contact(old_name, new_name, new_phone):
    try:
        con=connect()
        cur=con.cursor()

        cur.execute("UPDATE contacts SET name=%s, phone=%s WHERE name=%s",
                    (new_name, new_phone, old_name)
                    )
        con.commit()
        cur.close()
        con.close()
        print("Contact Updated")

    except Exception as e:
        print("Error:", e)

def delete_by_name(name):
    try:
        conn=connect()
        cur=conn.cursor()

        cur.execute("DELETE FROM contacts WHERE name LIKE %s",
                    (name,))
        
        conn.commit()
        cur.close()
        conn.close()
    
    except Exception as e:
        print("Erroe:", e)

def menu():
    while True:
        print("1. Insert Contact")
        print("2. CSV reader")
        print("3. Gett all")
        print("4. Find by name")
        print("5. Find by phone")
        print("6. Update")
        print("7. Delete by name")
        print("0. Exit")

        choice=input("Choose:")

        if choice=='1':
            name=input("name:")
            phone=input("phone:")
            insert_contact(name, phone)

        elif choice=='2':
            csv_reader("contacts.csv")

        elif choice=='3':
            get_all()
        
        elif choice=='4':
            name=input("Name:")
            find_by_name(name)
        
        elif choice=='5':
            prenumber=input("Pre-number:")
            find_by_number(prenumber)

        elif choice=='6':
            old_name=input("Old name:")
            new_name=input("New name:")
            new_phone=input("New phone:")
            Update_contact(old_name, new_name, new_phone)

        elif choice=='7':
            name=input("Name:")
            delete_by_name(name)

        elif choice=='0':
            break

if __name__ == "__main__":
    menu()