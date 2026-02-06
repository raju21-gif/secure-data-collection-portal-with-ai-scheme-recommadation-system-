from database import users_collection
from auth import get_password_hash
import sys

def seed_admin():
    # Credentials requested
    admin_email = "admin@freedy.ai"
    admin_password = "admin123"
    admin_name = "System Admin"

    existing_user = users_collection.find_one({"email": admin_email})
    if existing_user:
        print(f"User {admin_email} already exists provided.")
        # Optional: Update password if it exists but is wrong?
        # For now, just skip to avoid overwriting data unexpectedly.
        # But if the user wants to login, maybe we SHOULD update the password?
        # Let's update the password and role to ensure they are admin.
        new_hash = get_password_hash(admin_password)
        users_collection.update_one(
            {"email": admin_email},
            {"$set": {"password": new_hash, "role": "admin", "name": admin_name}}
        )
        print(f"Updated existing user {admin_email} to Admin Role with new password.")
        return

    hashed_password = get_password_hash(admin_password)
    new_admin = {
        "name": admin_name,
        "email": admin_email,
        "password": hashed_password,
        "role": "admin",
        "image_url": ""
    }
    
    users_collection.insert_one(new_admin)
    print(f"Admin user {admin_email} created successfully.")

if __name__ == "__main__":
    seed_admin()
