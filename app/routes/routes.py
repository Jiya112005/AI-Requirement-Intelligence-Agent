import os
from flask import request,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token,jwt_required,get_jwt_identity
from app.services.file_services import extract_text_from_file,clean_text
#importing app binded and db 
from app import app,db
# importing the user model created
from app.models.user import User,Document

@app.route('/')
@app.route('/index')
def index():
    return "<h1>Welcome to the AI Automation Project 1</h1>"

@app.route('/register',methods=['POST'])
def register():
    data= request.get_json()
    email=data.get('email')
    password=data.get('password')
    
    if not email or not password:
        return jsonify({'error':'Missing email and password!'}),400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error":"User Already Exist"}),400

    hashed_password=generate_password_hash(password,method='pbkdf2:sha256')
    new_user=User(email=email,password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message':'User Registered Successfully!'}),201

@app.route('/login',methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash,password):
        return jsonify({"error":"Invalid email or password"}),401
    
    #generate access token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message":"Login Successful",
        "access_token":access_token,
        "user_id":user.id
    }),200

@app.route('/api/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    # get_jwt_identity() extracts the user_id we embedded inside the token during login
    current_user_id = get_jwt_identity()
    
    return jsonify({
        "message": "Authentication successful. You have access to the vault.", 
        "your_user_id": current_user_id
    }), 200


##### Phase 2 upload endpoints ######
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload',methods=['POST'])
@jwt_required() 
def upload_document():
    current_user_id = get_jwt_identity()

    # If user pasted raw text or email
    if request.is_json:
        data = request.get_json()
        raw_text = data.get('text')

        if not raw_text:
            return jsonify({"error":"No text provided in the body"}),400

        new_doc = Document(
            user_id = current_user_id,
            file_path = "pasted_email_text",
            status="UPLOADED",
            raw_text=clean_text(raw_text)
        ) 
        db.session.add(new_doc)
        db.session.commit()

        return jsonify({
            "message":"Raw Text ingested successfully",
            "document_id":new_doc.id,
            "status":new_doc.status
        }),202

    if 'file' not in request.files:
        return jsonify({"error":"No file in the body found"}),400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error":"No selected file"}),400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER,exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER,filename)
        file.save(file_path)

        raw_text = extract_text_from_file(file_path,filename)
        if not raw_text:
            return jsonify({"error":"could not extract text from file"}),422
            
        new_doc = Document(
            user_id = current_user_id,
            file_path = file_path,
            status = "UPLOADED",
            raw_text = clean_text(raw_text)
        )
        db.session.add(new_doc)
        db.session.commit()

        return jsonify({
            "message":"File uploaded and text extracted successfully",
            "document_id":new_doc.id,
            "status":new_doc.status
        }),202
        
    return jsonify({"error":"Invalid file type, only txt and pdf are allowed"}),400
