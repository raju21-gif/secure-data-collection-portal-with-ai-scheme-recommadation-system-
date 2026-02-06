from database import users_collection
import sys

def check_admin_role():
    email = "raju36@gmail.com"
    user = users_collection.find_one({"email": email})
    
    if user:
        print(f"User found: {user.get('name')}")
        print(f"Role: {user.get('role', 'MISSING')}")
        
        if user.get('role') != 'admin':
            print("Updating role to 'admin'...")
            users_collection.update_one({"email": email}, {"$set": {"role": "admin"}})
            print("Role updated.")
        else:
            print("Role is already correct.")
    else:
        print("User not found.")

if __name__ == "__main__":
    check_admin_role()
