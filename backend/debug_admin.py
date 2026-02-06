from database import users_collection
import sys

def debug_admin():
    email = "admin@freedy.ai"
    user = users_collection.find_one({"email": email})
    
    if user:
        print(f"User Found: {user['name']}")
        print(f"Email: {user['email']}")
        print(f"Role: {user.get('role', 'NOT SET')}")
        print(f"ID: {user.get('_id')}")
        
        # Force update if not admin
        if user.get('role') != 'admin':
            print("Role is NOT admin. Fixing now...")
            users_collection.update_one(
                {"email": email},
                {"$set": {"role": "admin"}}
            )
            print("Role updated to 'admin'.")
        else:
            print("Role is correctly set to 'admin'.")
            
    else:
        print(f"User {email} NOT FOUND in database.")

if __name__ == "__main__":
    debug_admin()
