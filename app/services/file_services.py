import fitz
import re 

def clean_text(text):
    """
    Preprocessing Layer: Cleans noise from the extracted text or pasted emails.
    Prevents token-wastage before sending it to LLMs.
    """

    if not text:
        return ""
    
    text = re.sub(r'[ \t]+',' ',text) 
    text = re.sub(r'\n{3,}','\n\n',text)

    return text.strip()

def extract_text_from_file(file_path,filename):
    """
    Detects file type, extracts raw text, and passess it through the Preprocessing Layer...
    """
    ext = filename.rsplit('.',1)[1].lower()
    raw_text = ""

    if ext == 'txt':
        try:
            with open(file_path,'r',encoding='utf-8') as f:
                raw_text = f.read()
        except Exception as e:
            return None,f"Error reading TXT file: {str(e)}"
    elif ext == 'pdf':
        try:
            doc = fitz.open(file_path)
            for page in doc:
                raw_text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"Error reading PDF file: {str(e)}")
            return None,f"Error reading PDF file: {str(e)}"
    
    if raw_text:
        return clean_text(raw_text)
    return None