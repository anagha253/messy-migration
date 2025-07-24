from flask import Flask, request, jsonify
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash
from dataclasses import dataclass, asdict
import logging 

# Flask app setup
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Database connection setup
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

#data model for user
@dataclass
class UserDTO:
    id: int
    name: str
    email: str

@app.route('/')
def home():
    return jsonify({"message": "User Management System is running"}), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    users = [UserDTO(id=user[0], name=user[1], email=user[2]) for user in users]
    return jsonify([asdict(u) for u in users])

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if user:
        user_dto = UserDTO(id=user[0], name=user[1], email=user[2])
        return jsonify(asdict(user_dto)), 200
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        name, email, password = data['name'], data['email'], data['password']
    except (TypeError, KeyError):
        return jsonify({"message": "Invalid input"}), 400
    
    check_existing_user = cursor.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    # Check if user already exists
    if check_existing_user:
        return jsonify({"message": "User with this email already exists"}), 400

    encrypted_password = generate_password_hash(password)
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, encrypted_password))
    conn.commit()

    logging.info("User created successfully! email: %s", email)
    return jsonify({"message": "User created successfully"}), 201

@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    
    if name and email:
        cursor.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, user_id))
        conn.commit()
        return jsonify({"message": "User updated successfully"}), 200
    else:
        return jsonify({"message": "Invalid data"}), 400

@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    cursor.execute("DELETE FROM users WHERE id = ?",(user_id,))
    conn.commit()

    check_deleted_user = cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not check_deleted_user:
        logging.info(f"user: {user_id} doesnt exists")
        return jsonify({"message": "User doesnt exists"}), 404
    
    logging.info(f"User {user_id} deleted")
    return jsonify({"message": "User deleted successfully"}), 200

@app.route('/search', methods=['GET'])
def search_users():
    name = request.args.get('name')
    
    if not name:
        return jsonify({"message": "Please provide a name to search"}), 400
    
    like_pattern = f"%{name}%"
    
    cursor.execute("SELECT * FROM users WHERE name LIKE ?", (like_pattern,))
    users = cursor.fetchall()

    users = [UserDTO(id=user[0], name=user[1], email=user[2]) for user in users]
    return jsonify([asdict(u) for u in users])

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    cursor.execute("SELECT * FROM users WHERE email = ?",(email,))
    user = cursor.fetchone()
    
    
    if user and check_password_hash(user[3], password):
        return jsonify({"status": "success", "user_id": user[0]})
    else:
        return jsonify({"status": "failed","message": "Invalid email or password"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)