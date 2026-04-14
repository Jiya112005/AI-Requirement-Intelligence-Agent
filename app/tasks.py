from app import celery,db 
from app.models.user import Document
from app.services.llm_service import LLMService

@celery.task(name="process_document_task")
def process_document_task(document_id):
    """
    This function runs entirely in the background via a Celery worker.
    Notice we only pass the id, workers fetches the heavy text from the DB.
    """
    print(f"\n[Worker] Picked up Document {document_id} from the Redis queue")
    doc = Document.query.get(document_id)

    if not doc or not doc.raw_text:
        print(f"[Worker ERROR] Document {document_id} not found or has no text")
        return "Failed"
    
    extracted_reqs = LLMService.process_requirements_pipeline(doc.id,doc.raw_text)

    if extracted_reqs:
        doc.status = 'CLARIFIED'
        print(f"[Worker] Document {document_id} successfully processed and saved")
    else:
        doc.status = 'FAILED'
        print(f"[Worker ERROR] Document {document_id} failed AI processing.")

    db.session.commit()
    
    return "Task Complete"