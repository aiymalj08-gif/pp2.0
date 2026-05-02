"""
PhoneBook – Extended Contact Management (TSIS 1)
Builds on top of Practice 7 & 8.  No functionality from those
practices is re-implemented here; only new features are added.
"""

import csv
import json
from datetime import date, datetime
from connect import connect #DB connection 

# ──────────────────────────────────────────────────────────────
#  Internal helpers
# ──────────────────────────────────────────────────────────────

def _run_procedure(sql, params=()):
    """Execute a stored procedure / DML statement and commit."""
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
    """Run a SELECT / function and return all rows."""
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


def _json_serial(obj):
    """JSON serialiser for date/datetime objects."""
    if isinstance(obj, (date, datetime)): #Checks type of variable
        return obj.isoformat() # because json cannot store data objects, it converts them to string 
    raise TypeError(f"Type {type(obj)} not serialisable") # raise -- Stops program and shows error


# ──────────────────────────────────────────────────────────────
#  3.1  Extended schema helpers
# ──────────────────────────────────────────────────────────────

def upsert_contact_extended(name, email=None, birthday=None, group_name=None):
    """
    Insert or update a contact with the new fields (email, birthday, group).
    Phone numbers are added separately via add_phone().
    """
    try:
        conn = connect()
        cur  = conn.cursor()

        # Resolve group_id
        group_id = None
        if group_name:
            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
            row = cur.fetchone()
            if row:
                group_id = row[0]
            else:
                cur.execute(
                    "INSERT INTO groups (name) VALUES (%s) RETURNING id",
                    (group_name,)
                )
                group_id = cur.fetchone()[0]

        # Upsert contact
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()
        if existing:
            cur.execute(
                """UPDATE contacts
                      SET email    = COALESCE(%s, email),
                          birthday = COALESCE(%s::DATE, birthday),
                          group_id = COALESCE(%s, group_id)
                    WHERE name = %s""",
                (email, birthday, group_id, name)
            )
            print(f"Updated contact: {name}")
        else:
            cur.execute(
                """INSERT INTO contacts (name, email, birthday, group_id)
                   VALUES (%s, %s, %s::DATE, %s)""",
                (name, email, birthday, group_id)
            )
            print(f"Inserted contact: {name}")

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Error:", e)


# ──────────────────────────────────────────────────────────────
#  3.1  Stored-procedure wrappers (TSIS 1 procedures)
# ──────────────────────────────────────────────────────────────

def add_phone(contact_name, phone, phone_type):
    """Call the add_phone stored procedure."""
    _run_procedure(
        "CALL add_phone(%s, %s, %s)",
        (contact_name, phone, phone_type)
    )


def move_to_group(contact_name, group_name):
    """Call the move_to_group stored procedure."""
    _run_procedure(
        "CALL move_to_group(%s, %s)",
        (contact_name, group_name)
    )


# ──────────────────────────────────────────────────────────────
#  3.2  Advanced search / filter / sort
# ──────────────────────────────────────────────────────────────

def _print_contacts(rows, headers=None):
    """Pretty-print a list of contact rows."""
    if not rows:
        print("  No contacts found.")
        return
    if headers:
        print("  " + " | ".join(f"{h:<20}" for h in headers))
        print("  " + "-" * (23 * len(headers)))
    for row in rows:
        print("  " + " | ".join(f"{str(v or ''):<20}" for v in row))


def search_contacts_all_fields(query):
    """
    Full-text search across name, email, and all phone numbers
    using the new search_contacts() DB function.
    """
    rows = _run_query("SELECT * FROM search_contacts(%s)", (query,))
    print(f"\n--- Search results for '{query}' ---")
    _print_contacts(rows, ["ID", "Name", "Email", "Birthday", "Group", "Phones"])
    return rows

# COALESCE prevents overwriting existing values with NULL, it is related to SQL not python, If user gives new email → update it
#If user gives nothing → keep old one
def filter_by_group(group_name):
    """Show contacts belonging to a given group, sorted by name."""
    rows = _run_query(
        """SELECT c.id, c.name, c.email, c.birthday, g.name AS grp,
                  STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones 
             FROM contacts c
             LEFT JOIN groups g ON g.id = c.group_id
             LEFT JOIN phones p ON p.contact_id = c.id
            WHERE g.name ILIKE %s
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name""",
        (group_name,)
    )
    print(f"\n--- Contacts in group '{group_name}' ---")
    _print_contacts(rows, ["ID", "Name", "Email", "Birthday", "Group", "Phones"])
    return rows


def search_by_email(partial_email):
    """Find contacts whose email contains the given string."""
    rows = _run_query(
        """SELECT c.id, c.name, c.email, c.birthday, g.name,
                  STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
             FROM contacts c
             LEFT JOIN groups g ON g.id = c.group_id
             LEFT JOIN phones p ON p.contact_id = c.id
            WHERE c.email ILIKE %s
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name""",
        (f"%{partial_email}%",)
    )
    print(f"\n--- Email search: '{partial_email}' ---")
    _print_contacts(rows, ["ID", "Name", "Email", "Birthday", "Group", "Phones"])
    return rows


def get_all_sorted(sort_by="name"):
    """
    Retrieve all contacts sorted by name, birthday, or created_at.
    sort_by: 'name' | 'birthday' | 'date'
    """
    order_map = {
        "name":     "c.name",
        "birthday": "c.birthday NULLS LAST",
        "date":     "c.created_at",
    }
    order_col = order_map.get(sort_by, "c.name")
    rows = _run_query(
        f"""SELECT c.id, c.name, c.email, c.birthday, g.name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
              FROM contacts c
              LEFT JOIN groups g ON g.id = c.group_id
              LEFT JOIN phones p ON p.contact_id = c.id
             GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
             ORDER BY {order_col}"""
    )
    print(f"\n--- All contacts (sorted by {sort_by}) ---")
    _print_contacts(rows, ["ID", "Name", "Email", "Birthday", "Group", "Phones"])
    return rows


# ──────────────────────────────────────────────────────────────
#  3.2  Paginated navigation console loop
#       (uses the existing get_contacts_paginated DB function)
# ──────────────────────────────────────────────────────────────

def paginated_navigation(page_size=5):
    """Interactive next/prev/quit navigator using the Practice-8 DB function."""
    offset = 0
    while True:
        rows = _run_query(
            "SELECT * FROM get_contacts_paginated(%s, %s)",
            (page_size, offset)
        )
        print(f"\n--- Page (offset={offset}, limit={page_size}) ---")
        if rows:
            for row in rows:
                print(f"  id={row[0]}  name={row[1]}  phone={row[2]}")
        else:
            print("  (no more contacts)")

        cmd = input("\n  [n]ext  [p]rev  [q]uit: ").strip().lower()
        if cmd == "n":
            if rows:
                offset += page_size
            else:
                print("  Already at the last page.")
        elif cmd == "p":
            offset = max(0, offset - page_size)
        elif cmd == "q":
            break
        else:
            print("  Invalid command.")


# ──────────────────────────────────────────────────────────────
#  3.3  Import / Export
# ──────────────────────────────────────────────────────────────

def export_to_json(filename="contacts_export.json"):
    """Export all contacts (with phones and group) to a JSON file."""
    rows = _run_query(
        """SELECT c.id, c.name, c.email,
                  c.birthday, g.name AS grp,
                  c.created_at
             FROM contacts c
             LEFT JOIN groups g ON g.id = c.group_id
             ORDER BY c.id"""
    )
    contacts_list = []
    for row in rows:
        contact_id, name, email, birthday, grp, created_at = row
        phone_rows = _run_query(
            "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
            (contact_id,)
        )
        contacts_list.append({
            "name":       name,
            "email":      email,
            "birthday":   birthday,
            "group":      grp,
            "created_at": created_at,
            "phones": [
                {"phone": pr[0], "type": pr[1]} for pr in phone_rows
            ],
        })

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(contacts_list, f, ensure_ascii=False, indent=2, default=_json_serial)
    print(f"Exported {len(contacts_list)} contact(s) to '{filename}'.")


def import_from_json(filename="contacts_export.json"):
    """
    Import contacts from a JSON file.
    On duplicate name, ask: skip or overwrite.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            contacts_list = json.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return

    inserted = skipped = overwritten = 0

    for c in contacts_list:
        name = c.get("name", "").strip()
        if not name:
            print("  Skipping entry with no name.")
            continue

        existing = _run_query("SELECT id FROM contacts WHERE name = %s", (name,))
        if existing:
            ans = input(
                f"  '{name}' already exists. (s)kip / (o)verwrite? "
            ).strip().lower()
            if ans != "o":
                print(f"  Skipped: {name}")
                skipped += 1
                continue
            # Overwrite
            upsert_contact_extended(
                name,
                email=c.get("email"),
                birthday=c.get("birthday"),
                group_name=c.get("group"),
            )
            # Remove old phones before re-inserting
            contact_id = existing[0][0]
            _run_procedure("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
            overwritten += 1
        else:
            upsert_contact_extended(
                name,
                email=c.get("email"),
                birthday=c.get("birthday"),
                group_name=c.get("group"),
            )
            inserted += 1

        # Add phones
        for ph in c.get("phones", []):
            phone_val  = ph.get("phone", "").strip()
            phone_type = ph.get("type", "mobile").strip()
            if phone_val:
                add_phone(name, phone_val, phone_type)

    print(
        f"\nImport done – inserted: {inserted}, "
        f"overwritten: {overwritten}, skipped: {skipped}."
    )


def csv_reader_extended(filename):
    """
    Extended CSV importer that handles the new fields:
      name, email, birthday, group, phone, phone_type
    Falls back gracefully if optional columns are missing.
    """
    try:
        conn = connect()
        cur  = conn.cursor()
        imported = 0
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name       = row.get("name",       "").strip()
                email      = row.get("email",       "").strip() or None
                birthday   = row.get("birthday",    "").strip() or None
                group_name = row.get("group",       "").strip() or None
                phone      = row.get("phone",       "").strip() or None
                phone_type = row.get("phone_type",  "mobile").strip() or "mobile"

                if not name:
                    continue

                # Resolve group
                group_id = None
                if group_name:
                    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                    g = cur.fetchone()
                    if g:
                        group_id = g[0]
                    else:
                        cur.execute(
                            "INSERT INTO groups (name) VALUES (%s) RETURNING id",
                            (group_name,)
                        )
                        group_id = cur.fetchone()[0]

                # Upsert contact
                cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                existing = cur.fetchone()
                if existing:
                    cur.execute(
                        """UPDATE contacts
                              SET email    = COALESCE(%s, email),
                                  birthday = COALESCE(%s::DATE, birthday),
                                  group_id = COALESCE(%s, group_id)
                            WHERE name = %s""",
                        (email or None, birthday or None, group_id, name)
                    )
                    contact_id = existing[0]
                else:
                    cur.execute(
                        """INSERT INTO contacts (name, email, birthday, group_id)
                           VALUES (%s, %s, %s::DATE, %s) RETURNING id""",
                        (name, email or None, birthday or None, group_id)
                    )
                    contact_id = cur.fetchone()[0]

                # Insert phone
                if phone:
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (contact_id, phone, phone_type)
                    )
                imported += 1

        conn.commit()
        cur.close()
        conn.close()
        print(f"CSV imported successfully – {imported} row(s) processed.")
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    except Exception as e:
        print("Error:", e)


# ──────────────────────────────────────────────────────────────
#  Console menu
# ──────────────────────────────────────────────────────────────

def _phone_type_prompt():
    """Helper: ask user for a valid phone type."""
    while True:
        t = input("Phone type (home / work / mobile): ").strip().lower()
        if t in ("home", "work", "mobile"):
            return t
        print("  Invalid type. Choose home, work, or mobile.")


def _sort_prompt():
    """Helper: ask user for a sort field."""
    while True:
        s = input("Sort by (name / birthday / date): ").strip().lower()
        if s in ("name", "birthday", "date"):
            return s
        print("  Invalid choice.")


def menu():
    options = """
╔══════════════════════════════════════════════════╗
║           PhoneBook Extended – TSIS 1            ║
╠══════════════════════════════════════════════════╣
║  1.  Add / update contact (name + extra fields)  ║
║  2.  Add phone number to existing contact        ║
║  3.  Move contact to a group                     ║
╠══════════════════════════════════════════════════╣
║  4.  Search across all fields (name/email/phone) ║
║  5.  Filter by group                             ║
║  6.  Search by email                             ║
║  7.  Get all contacts (sorted)                   ║
║  8.  Browse contacts page by page                ║
╠══════════════════════════════════════════════════╣
║  9.  Export contacts to JSON                     ║
║ 10.  Import contacts from JSON                   ║
║ 11.  Import contacts from CSV (extended format)  ║
╠══════════════════════════════════════════════════╣
║  0.  Exit                                        ║
╚══════════════════════════════════════════════════╝
"""
    while True:
        print(options)
        choice = input("Choose: ").strip()

        # ── New / extended contact management ──────────────
        if choice == "1":
            name  = input("Name:           ").strip()
            email = input("Email (opt):    ").strip() or None
            bday  = input("Birthday YYYY-MM-DD (opt): ").strip() or None
            grp   = input("Group (opt):    ").strip() or None
            upsert_contact_extended(name, email, bday, grp)

        elif choice == "2":
            name  = input("Contact name: ").strip()
            phone = input("Phone number: ").strip()
            ptype = _phone_type_prompt()
            add_phone(name, phone, ptype)

        elif choice == "3":
            name  = input("Contact name: ").strip()
            group = input("Group name:   ").strip()
            move_to_group(name, group)

        # ── Search / filter / sort ──────────────────────────
        elif choice == "4":
            search_contacts_all_fields(input("Query: ").strip())

        elif choice == "5":
            filter_by_group(input("Group name: ").strip())

        elif choice == "6":
            search_by_email(input("Email fragment: ").strip())

        elif choice == "7":
            sort = _sort_prompt()
            get_all_sorted(sort)

        elif choice == "8":
            try:
                ps = int(input("Page size (default 5): ").strip() or "5")
            except ValueError:
                ps = 5
            paginated_navigation(ps)

        # ── Import / Export ─────────────────────────────────
        elif choice == "9":
            fname = input("Output filename (default: contacts_export.json): ").strip()
            export_to_json(fname or "contacts_export.json")

        elif choice == "10":
            fname = input("JSON filename (default: contacts_export.json): ").strip()
            import_from_json(fname or "contacts_export.json")

        elif choice == "11":
            fname = input("CSV filename (default: contacts.csv): ").strip()
            csv_reader_extended(fname or "contacts.csv")

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    menu()