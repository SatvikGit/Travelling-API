from cs50 import SQL
from flask import Flask, jsonify, redirect, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash

# Configure Application
app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///travel_locations.db")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_locations.db'

db.execute(''' CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        password TEXT
                  )'''
               )


db.execute(''' CREATE TABLE IF NOT EXISTS locations (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        country TEXT,
                        description TEXT,
                        date TEXT
                  )'''
               )


@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username:
            return "must require a username"
        
        elif not password:
            return "must require a password"
        
        # Hashing users's password
        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", username, hash)
        return jsonify({'message' : 'Registered user successfully'}), 201
    
    else:
        return render_template("register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json
        username = data.get("username")
        password = data.get("password")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not rows:
            return "Invalid Credentials"
        
        if len(rows) < 1:
            return "No user found with that username"

        user = rows[0]

        if len(user) < 3:
            return "User data is incomplete"

        if not check_password_hash(user[2], password):
            return "Invalid Credentials"
        else:
            return jsonify({'message' : 'Log-In successful'}), 201

    else:
        return render_template("login.html")
    
locations_list = []
@app.route("/locations", methods = ["GET", "POST"])
def locations():
    if request.method == "POST":
        data = request.json
        db.execute("INSERT INTO locations (name, country, description, date) VALUES (?, ?, ?, ?)", data['name'], data['country'], data['description'], data['date'])
        return jsonify({'message' : 'Location added successfully'}), 201
    else:
            locations = db.execute("SELECT * FROM locations")
            return jsonify(locations)
    

@app.route("/locations/<int:id>", methods = ["GET", "POST"])
def operate_location(id):
    location = None
    location_dict = db.execute("SELECT * FROM locations WHERE id = ?", id)

    for row in location_dict:
        location = row
        break

    if not location:
        return jsonify({'message' : 'Location not found'}), 404
    
    else:
        if request.method == "POST":
            data = request.json
            action = data.get('action')

            if action == 'UPDATE':
                new_name = data.get('name', location.get('name'))
                new_country = data.get('country', location.get('country'))
                new_description = data.get('description', location.get('description'))
                new_date = data.get('date', location.get('date'))

                db.execute("UPDATE locations SET name = ?, country = ?, description = ?, date = ? WHERE id = ?", new_name, new_country, new_description, new_date, id)
                return jsonify({'message' : 'Location updated successfully'}), 201
            
            elif action == 'DELETE':
                db.execute("DELETE FROM locations WHERE id = ?", id)
                return jsonify({'message' : 'Location deleted successfully'}), 201
            
            else:
                return jsonify({'message' : 'Invalid Input'}), 400
            
        else:
            if location_dict:
                return jsonify({'id' : location_dict[0]['id'], 'name' : location_dict[0]['name'], 'country' : location_dict[0]['country'], 'description' : location_dict[0]['description'], 'date' : location_dict[0]['date']})
            else:
                return jsonify({'message' : 'Location not found'}), 404
