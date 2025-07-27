import sqlite3
import re
import datetime

conn = sqlite3.connect('profile-management-system.sqlite')
cur = conn.cursor()

cur.execute('''
            CREATE TABLE IF NOT EXISTS Profile(
                name TEXT PRIMARY KEY,
                DOB TEXT,
                email TEXT,
                phone_number TEXT,
                registration TEXT
                )
''')
conn.commit()

def validate_phone_number(phone_number):
    phone_pattern = re.compile(r'^\+?[\d\s\-\(\)]{7,20}$')
    if phone_pattern.fullmatch(phone_number):
        return phone_number
    print("⚠️ Invalid phone number format.")
    return None

def validate_email(email):
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if email_pattern.fullmatch(email):
        return email
    print("⚠️ Invalid email format.")
    return None

def validate_registration_date_string_format(date_time_str):
    # This function is primarily for validating existing strings,
    # but the registration date should ideally be auto-generated.
    registration_pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
    if not registration_pattern.fullmatch(date_time_str):
        print("⚠️ Invalid format. Must be YYYY-MM-DD HH:MM:SS.")
        return None
    try:
        datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
        return date_time_str
    except ValueError:
        print("⚠️ Invalid date or time value.")
        return None
        
def get_current_registration_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def validate_dob(dob_str):
    try:
        dob_date = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()
    except ValueError:
        print("⚠️ Invalid DOB format or invalid date. Please use YYYY-MM-DD (e.g., 2000-01-15).")
        return None

    current_date = datetime.date.today()
    if dob_date > current_date:
        print("⚠️ Date of Birth cannot be in the future.")
        return None
    
    return dob_date.strftime('%Y-%m-%d')


while True:
    print('\n📇Profile Manager')
    print("1. Add Contact details")
    print("2. Search Contact")
    print("3. Edit Contact")
    print("4. Delete Contact")
    print("5. Show All Contacts")
    print("6. Exit")
    
    choice = input("Enter Your Choice:").strip()
    
    if choice == "1":
        name = input("Enter Username:").strip()
        
        cur.execute('SELECT name FROM Profile WHERE name = ? COLLATE NOCASE', (name,))
        if cur.fetchone():
            print(f"❌ Username '{name}' already exists. Please choose a different one.")
            continue

        dob_input = input("Enter Date of Birth (YYYY-MM-DD): ").strip()
        validated_dob = validate_dob(dob_input)
        if validated_dob is None:
            print("Profile creation cancelled due to invalid Date of Birth.")
            continue 
            
        email_input = input("Enter Email:").strip()
        validated_email = validate_email(email_input)
        if validated_email is None:
            print("Profile creation cancelled due to invalid Email.")
            continue 
            
        phone_number_input = input("Enter Mobile Number: ").strip()
        validated_phone_number = validate_phone_number(phone_number_input)
        if validated_phone_number is None:
            print("Profile creation cancelled due to invalid Phone Number.")
            continue 
        
        # Auto-generate registration timestamp
        registration_timestamp = get_current_registration_timestamp()
        
        try:
            cur.execute('''
                        INSERT INTO PROFILE (name, DOB, email, phone_number, registration) 
                        VALUES(?,?,?,?,?)''',
                        (name, validated_dob, validated_email,
                        validated_phone_number, registration_timestamp))
            conn.commit()
            print("✅ Profile added successfully!")
        except sqlite3.IntegrityError:
            print(f"❌ Error: A profile with the username '{name}' already exists.")
        except sqlite3.Error as e:
            print(f"❌ An unexpected database error occurred: {e}")
            conn.rollback()

    elif choice == "2":
        search_user = input("Enter Username to Search:").strip()
        # Use COLLATE NOCASE for case-insensitive search
        cur.execute('SELECT name, DOB, email, phone_number, registration FROM Profile WHERE name = ? COLLATE NOCASE', (search_user,))
        row = cur.fetchone()
        if row:
            name, dob_input, email_input, phone_number_input, registration_timestamp = row
            dob_display = dob_input if dob_input is not None else "N/A"
            email_display = email_input if email_input is not None else "N/A"
            phone_number_display = phone_number_input if phone_number_input is not None else "N/A"
            registration_timestamp_display = registration_timestamp if registration_timestamp is not None else "N/A"
            print("\nProfile Found:")
            print(f"Username: {name}")
            print(f"DOB: {dob_display}")
            print(f"Email: {email_display}")
            print(f"Phone Number: {phone_number_display}")
            print(f"Registration Date: {registration_timestamp_display}")
        else:
            print("❌ Profile not found.")
            
    elif choice == "3":
        edit_username = input("Enter username to edit details:").strip()
        
        # Fetch all profile data at once for the initial existence check
        # and to get current values. Use COLLATE NOCASE for case-insensitive search.
        cur.execute('SELECT name, DOB, email, phone_number, registration FROM Profile WHERE name = ? COLLATE NOCASE', (edit_username,))
        profile_row = cur.fetchone() # Store the fetched row in a variable. It will be None if not found.

        if profile_row:
            # Unpack all current values from the 'profile_row' found above.
            _name_from_db, current_dob, current_email, current_phone_number, _registration_from_db = profile_row

            print(f"\nEditing Profile for: {_name_from_db}") # Use _name_from_db for display consistency
            print("Leave fields blank if you want to keep the current value.")
            print(f"Current DOB: {current_dob or 'N/A'}")
            print(f"Current Email: {current_email or 'N/A'}")
            print(f"Current Phone: {current_phone_number or 'N/A'}")

            new_dob_input = input("Enter New Date of Birth (YYYY-MM-DD): ").strip()
            new_email_input = input("Enter New Email: ").strip()
            new_phone_number_input = input("Enter New Phone Number: ").strip()
            
            # --- Validate and Determine DOB to Save ---
            new_dob_to_save = current_dob # Initialize with current value
            if new_dob_input:
                validated_new_dob = validate_dob(new_dob_input)
                if validated_new_dob is not None:
                    new_dob_to_save = validated_new_dob
                else:
                    # If new input is invalid, new_dob_to_save remains current_dob (initialized value)
                    pass 
            
            # --- Validate and Determine Email to Save ---
            new_email_to_save = current_email # Initialize with current value
            if new_email_input:
                validated_new_email = validate_email(new_email_input)
                if validated_new_email is not None:
                    new_email_to_save = validated_new_email
                else:
                    # If new input is invalid, new_email_to_save remains current_email
                    pass 
            
            # --- Validate and Determine Phone Number to Save ---
            new_phone_number_to_save = current_phone_number # Initialize with current value
            if new_phone_number_input:
                validated_new_phone_number = validate_phone_number(new_phone_number_input)
                if validated_new_phone_number is not None:
                    new_phone_number_to_save = validated_new_phone_number
                else:
                    # If new input is invalid, new_phone_number_to_save remains current_phone_number
                    pass
            
            # --- Execute Update ---
            try:
                cur.execute('''
                            UPDATE Profile
                            SET DOB = ?, email = ?, phone_number = ?
                            WHERE name = ? COLLATE NOCASE
                            ''',
                            (new_dob_to_save, new_email_to_save,
                            new_phone_number_to_save, edit_username))
                conn.commit()
                print("✅ Profile updated successfully!")
            except sqlite3.Error as e:
                print(f"❌ An error occurred during update: {e}")
                conn.rollback()
        else:
            print(f"❌ Profile with username '{edit_username}' not found.")

    elif choice == "4":
        delete_contact = input("Enter contact name to delete: ").strip()
        cur.execute('SELECT*FROM Profile WHERE name = ?', (delete_contact,))
        if cur.fetchone():
            cur.execute('DELETE FROM Profile WHERE name = ?',(delete_contact,))
            conn.commit()
            print("🗑️ Username deleted successfully!")
        else:
            print("❌ Username not found.")
            
        
    elif choice == "5":
        # Removed the unnecessary "WHERE" clause to show all contacts
        cur.execute('SELECT name, DOB, email, phone_number, registration FROM Profile')
        
        rows = cur.fetchall()
        
        if not rows:
            print("No user profiles found.")
        else:
            print("\nAll Saved User Profiles:")
            # Added 'email_input' to the unpacking list to match the 5 columns selected.
            for name, dob_input, email_input, phone_number_input, registration_timestamp in rows:
                phone_number_display = phone_number_input if phone_number_input is not None else "N/A"
                dob_display = dob_input if dob_input is not None else "N/A"
                email_display = email_input if email_input is not None else "N/A"
                registration_timestamp_display = registration_timestamp if registration_timestamp is not None else "N/A"
                
                print(f"\n- Name: {name}")
                print(f"  DOB: {dob_display}")
                print(f"  Email: {email_display}")
                print(f"  Phone Number: {phone_number_display}")
                print(f"  Registration Date: {registration_timestamp_display}")

    elif choice == "6":
        print("Exiting Profile Manager. Goodbye!")
        conn.close()
        break
    else:
        print("🚫 Invalid choice. Please select a number between 1 and 6.")