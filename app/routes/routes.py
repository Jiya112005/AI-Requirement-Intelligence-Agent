import os
from flask import request,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token,jwt_required,get_jwt_identity
from app.services.file_services import extract_text_from_file,clean_text
#importing app binded and db 
from app import app,db
from app.tasks import process_document_task
# importing the user model created
from app.models.user import User,Document
from app.services.llm_service import LLMService
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

@app.route('/api/process/<int:doc_id>', methods=['POST'])
@jwt_required()
def process_document(doc_id):
    """
    Dedicated endpoint to trigger the AI pipeline on a previously uploaded document.
    """
    current_user_id = get_jwt_identity()

    # 1. Fetch the document and ensure it belongs to the logged-in user
    doc = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()

    if not doc:
        return jsonify({"error": "Document not found or access denied"}), 404

    if not doc.raw_text:
        return jsonify({"error": "Document has no extractable text to process"}), 422

    # Prevent re-processing already completed documents
    if doc.status == 'CLARIFIED':
        return jsonify({"message": "Document has already been processed."}), 200
    if doc.status == 'PROCESSING':
        return jsonify({"message":"Document is currently being processed."})

    print(f"[API] Dispatching Document ID:{doc.id} to Celery Worker...")

    process_document_task.delay(doc.id)

    doc.status = 'PROCESSING'
    db.session.commit()

    return jsonify({
        "message": "AI processing started in background",
        "document_id": doc.id,
        "status": doc.status
    }),202

@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_user_history():
    """STEP 3A: Fetches a high-level list of all past documents."""
    current_user_id = get_jwt_identity()
    
    documents = Document.query.filter_by(user_id=current_user_id).order_by(Document.created_at.desc()).all()
    
    history = []
    for doc in documents:
        history.append({
            "id": doc.id,
            "filename": doc.file_path.split('/')[-1] if doc.file_path != 'pasted_email_text' else 'Pasted Text',
            "status": doc.status,
            "created_at": doc.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    return jsonify({"history": history}), 200


@app.route('/api/document/<int:doc_id>', methods=['GET'])
@jwt_required()
def get_document_details(doc_id):
    """STEP 3B: Fetches the deep AI-evaluated details of a specific document."""
    current_user_id = get_jwt_identity()
    
    doc = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    
    if not doc:
        return jsonify({"error": "Document not found or access denied"}), 404
        
    reqs_data = []
    for req in doc.requirements:
        reqs_data.append({
            "id": req.id,
            "feature": req.feature,
            "description": req.description,
            "priority": req.priority,
            "feasibility": req.feasibility,
            "risks": req.risks,
            "clarity_score": req.clarity_score,
            # Safely parse JSON strings back to lists
            "ambiguous_terms": json.loads(req.ambiguous_terms) if req.ambiguous_terms else [],
            "missing_info": json.loads(req.missing_info) if req.missing_info else [],
            "clarification_questions": json.loads(req.clarification_questions) if req.clarification_questions else []
        })
        
    return jsonify({
        "document_id": doc.id,
        "status": doc.status,
        "raw_text_snippet": doc.raw_text[:200] + "..." if doc.raw_text else None,
        "requirements": reqs_data
    }), 200