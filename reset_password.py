import sys
sys.path.insert(0, 'c:\\timetide')

from app.core.security import get_password_hash
import sqlite3

# Get password from user
password = input("Enter the password for leoyfliu@gmail.com: ")

# Hash it with the new method
hashed = get_password_hash(password)

# Update the database
conn = sqlite3.connect('timetide.db')
cursor = conn.cursor()
cursor.execute("UPDATE users SET hashed_password = ? WHERE username = ?", (hashed, 'leoyfliu'))
conn.commit()
conn.close()

print("✓ Password updated successfully!")
