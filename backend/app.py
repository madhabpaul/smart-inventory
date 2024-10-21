from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import spacy
from spacy.matcher import Matcher
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from datetime import timedelta

# Instantiate the app
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///smart-inv.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-jwt-key" 

# initialize database object
db = SQLAlchemy(app)

# jwt initialize
jwt = JWTManager(app)

# load spacy 
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# Users Database Model
class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    member = db.relationship('Items', backref="user", lazy=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


    def to_dict(self):
        return dict(id=self.id, email=self.email)

# Items Database Model
class Items(db.Model):
    __tablename__="items"
    id = db.Column(db.Integer, primary_key = True)
    item_name = db.Column(db.String(50), nullable = False)
    unit = db.Column(db.String(50), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # Foreign Key

    def __init__(self, item_name, unit, quantity, user_id):
        self.item_name = item_name
        self.unit = unit
        self.quantity = quantity
        self.user_id = user_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'unit': self.unit,
            'quantity': self.quantity,
            'user_id': self.user_id
        }


# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


# User registration
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Username, email or password are required"}), 400

    email_check = Users.query.filter_by(email=email)
    if email_check:
        return jsonify({"message": 'Users already exists'}), 400

    register = Users(username=username, email=email, password=password)
    db.session.add(register)
    db.session.commit()


    return jsonify({"message": "User registered successfully"}), 201


# User login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user_login = Users.query.filter_by(email=email).first()
    if email and user_login.password == password:
        # Include user_id in the token
        additional_info = {"user_id": str(user_login.id), "email": user_login.email}
        access_token = create_access_token(
            identity=str(user_login.email),
            additional_claims=additional_info,
            expires_delta=timedelta(days=1),
        )
        return jsonify({"access_token": access_token}), 200

    return jsonify({"message": "Invalid credentials"}), 401

# get items
@app.route('/items/<userid>', methods=['GET', 'POST'])
def items(userid):
    items_data = Items.query.filter_by(user_id=userid).all()
    # Convert the list of Items objects to a JSON string
    items_json = [item.to_dict() for item in items_data] 

    return items_json


# Define patterns to match quantity, unit, and item name
item_pattern = [{"POS": "NOUN"}] 
quantity_pattern = [{"LIKE_NUM": True}] 
unit_pattern = [{"LOWER": {"IN": ["kg", "kgs", "kilograms", "kilogram", "grm", "grms", "gram", "grams", "ltr", "ltrs", "litre", "liters", "piece", "pcs", "pieces", "unit", "units"]}}]

matcher.add("QUANTITY", [quantity_pattern])
matcher.add("UNIT", [unit_pattern])
matcher.add("ITEM_NAME", [item_pattern])

# add items
@app.route('/addItems', methods=['POST'])
def addItems():
    data = request.json
    print (data)
    # Extract query and user ID
    query = data.get('insert_query')
    userid = data.get('userid')
        
    print (query, userid)

    # if not query:
    #     response_object['status'] = 'fail'
    #     response_object['message'] = 'Missing insert query'
    #     return jsonify(response_object), 400

    # Process the query with SpaCy NLP pipeline
    doc = nlp(query)

    # Initialize variables for extraction
    actions = ["add", "update", "delete"]
    item_name, unit, quantity = None, None, None

    # Extract matched entities
    for match_id, start, end in matcher(doc):
        match_span = doc[start:end]
        match_label = nlp.vocab.strings[match_id]

        if match_label == "QUANTITY":
            quantity = int(match_span.text)
        elif match_label == "UNIT":
            unit = match_span.text
        elif match_label == "ITEM_NAME":
            item_name = match_span.text

    # Ensure all values were extracted
    if not item_name:
        return ({'message': 'Could not extract item_name, unit, or quantity'}), 400

    # Extract action
    for word in query.lower().split():
        if word in actions:
            action = word
            break  # Exit the loop after the first match

    # Handle cases
    if action == "add":
        # Add the item to the database
        item = Items(item_name=item_name, unit=unit, quantity=quantity, user_id=userid)
        db.session.add(item)
        db.session.commit()
        print (item_name, unit, quantity, userid)
        return ({'message': 'Item added successfully'})
       
    elif action == "update":
        # Update the item in the database
        Items.query.filter_by(item_name=item_name).update({'quantity': quantity})
        db.session.commit()
        return ({'message': 'Item updated'})
    elif action == "delete":
        # Delete the item from the database
        Items.query.filter_by(item_name=item_name, user_id=userid).delete()
        db.session.commit()
        return ({'message': 'Item deleted'})
    else:
        return ({'message': 'Unsupported action'})

    return jsonify()




# protected route
@app.route("/", methods=["GET", "POST"])
@jwt_required()
def home():
    # current_user = get_jwt_identity() 'username' can be retrieved from the backend but it is already retrieved in the frontend (hello view).
    return jsonify({"message": "login success"}), 200


if __name__ == "__main__":
    app.run(debug=True)
