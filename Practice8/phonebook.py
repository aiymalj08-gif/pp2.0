from connect import connect
import csv


def _run_procedure(sql, params=()):
    try:
        conn = connect()
        cur  = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Error:", e)


def _run_query(sql, params=()):
    try:
        conn = connect()
        cur  = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print("Error:", e)
        return []


def upsert_contact(name, phone):
    _run_procedure("CALL upsert_contact(%s, %s)", (name, phone))


def bulk_insert_contacts(names: list, phones: list):
    _run_procedure(
        "CALL bulk_insert_contacts(%s::TEXT[], %s::TEXT[])",
        (names, phones)
    )


def search_by_pattern(pattern):
    rows = _run_query("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
    print(f"\n--- Results for '{pattern}' ---")
    for row in rows:
        print(f"  id={row[0]}  name={row[1]}  phone={row[2]}")
    if not rows:
        print("  No contacts found.")
    return rows


def get_contacts_page(limit=100, offset=0):
    rows = _run_query(
        "SELECT * FROM get_contacts_paginated(%s, %s)",
        (limit, offset)
    )
    print(f"\n--- Limit {limit}, Offset {offset} ---")
    for row in rows:
        print(f"  id={row[0]}  name={row[1]}  phone={row[2]}")
    if not rows:
        print("  No contacts on this page.")
    return rows


def get_all():
    rows = _run_query("SELECT * FROM contacts ORDER BY id")
    print("\n--- All Contacts ---")
    for row in rows:
        print(f"  id={row[0]}  name={row[1]}  phone={row[2]}")


def delete_by_name(name):
    _run_procedure("CALL delete_contact(p_name := %s, p_phone := NULL)", (name,))


def delete_by_phone(phone):
    _run_procedure("CALL delete_contact(p_name := NULL, p_phone := %s)", (phone,))


def csv_reader(filename):
    try:
        conn = connect()
        cur  = conn.cursor()
        with open(filename, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    cur.execute("CALL upsert_contact(%s, %s)", (row[0].strip(), row[1].strip()))
        conn.commit()
        cur.close()
        conn.close()
        print("CSV imported successfully.")
    except Exception as e:
        print("Error:", e)


def menu():
    while True:
        print(" 1. Upsert contact")
        print(" 2. Bulk insert")
        print(" 3. Search by pattern")
        print(" 4. View page")
        print(" 5. Get all contacts")
        print(" 6. Delete by name")
        print(" 7. Delete by phone")
        print(" 8. Import CSV")
        print(" 0. Exit")


        choice = input("Choose: ").strip()

        if choice == "1":
            name  = input("Name:  ").strip()
            phone = input("Phone: ").strip()
            upsert_contact(name, phone)

        elif choice == "2":
            names  = [n.strip() for n in input("Names  (comma-separated): ").split(",")]
            phones = [p.strip() for p in input("Phones (comma-separated): ").split(",")]
            bulk_insert_contacts(names, phones)

        elif choice == "3":
            search_by_pattern(input("Pattern: ").strip())

        elif choice == "4":
            try:
                limit  = int(input("Limit  (default 100): ").strip() or "100")
                offset = int(input("Offset (default 0):   ").strip() or "0")
            except ValueError:
                limit, offset = 100, 0
            get_contacts_page(limit, offset)

        elif choice == "5":
            get_all()

        elif choice == "6":
            delete_by_name(input("Name: ").strip())

        elif choice == "7":
            delete_by_phone(input("Phone: ").strip())

        elif choice == "8":
            csv_reader(input("CSV filename: ").strip())

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()