import json
import os 
from groq import Groq 
from app.models.user import Requirement
from app import db
from dotenv import load_dotenv

load_dotenv()
# creating the client for GROK
GROQ_MODEL = "llama-3.3-70b-versatile"
client = Groq(
    api_key = os.getenv('GROQ_API_KEY')
)
class LLMService:
    @staticmethod
    def agent_extractor(raw_text):
        """AGENT 1: Sole job is to extract features and descriptions"""
        print("\n[AGENT 1] Extracting Base Requirements....")
        prompt = """
            Extract the core feature requested in this text. 
            Output ONLY Json with a 'requirements' key containing a list of objects.
            Each object must have: "feature" (string), "description" (string), and "priority" (string: High/Medium/Low).
        """
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {'role':'system','content':prompt},
                {'role':'user','content':raw_text}
            ],
            response_format = {'type':'json_object'}
        )
        return json.loads(response.choices[0].message.content).get('requirements',[])
    
    @staticmethod
    def agent_clarifier(feature_list):
        """AGENT 2: Sole job is to find vagueness in extracted features"""
        print("[AGENT 2] Analyzing clarity and missing info...")
        prompt = """
        Review this JSON list of features. For each feature, output ONLY JSON with a "clarifications" key containing a list of objects.
        Each object must have: 
        - "feature" (exact name from input)
        - "clarity_score" (float 0.1 to 1.0)
        - "ambiguous_terms" (list of strings)
        - "missing_info" (list of strings)
        - "clarification_questions" (list of 1-2 questions to ask the client)
        """
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': json.dumps(feature_list)}
            ],
            response_format = {'type':'json_object'}
        )
        return json.loads(response.choices[0].message.content).get('clarifications', [])
    
    @staticmethod
    def agent_feasibility(feature_list):
        """AGENT 3: Sole job is technical evaluation"""
        print("[AGENT 3]Evaluating Technical feasibility...")
        prompt = """ Review the JSON list of features. For each feature, output ONLY Json with "feasibility_report" key containing a list of objects.
            Each object must have:
            -"feature" (exact name from input)
            -"feasibility"(string:High/Medium/Low)
            -"constraints"(string)
            -"dependencies"(string)
            -"risks"(string)
         """
        response = client.chat.completions.create(
            model = GROQ_MODEL,
            messages = [
                {"role":"system","content":prompt},
                {"role":"user","content":json.dumps(feature_list)}
            ],
            response_format = {'type':'json_object'}
         )
        return json.loads(response.choices[0].message.content).get('feasibility_report',[])
    
    @classmethod
    def process_requirements_pipeline(cls,document_id,raw_text):
        """THE ORCHESTRATION: Manages the flow of agents."""
        try:
            base_features = cls.agent_extractor(raw_text)
            if not base_features:
                return None
            
            clarifications = cls.agent_clarifier(base_features)
            feasibilities = cls.agent_feasibility(base_features)

            extracted_reqs = []

            for base in base_features:
                feature_name = base.get('feature')

                clarity_data = next((item for item in clarifications if item.get('feature') == feature_name),{})
                feasibility_data = next((item for item in feasibilities if item.get('feature') == feature_name),{})

                new_req = Requirement(
                    document_id = document_id,
                    feature=feature_name,
                    description=base.get('description'),
                    priority=base.get('priority','Medium'),

                    # from feasibility agent 
                    constraints=feasibility_data.get('constraints',''),
                    dependencies = feasibility_data.get('dependencies',''),
                    feasibility=feasibility_data.get('feasibility',''),
                    risks=feasibility_data.get('risks',''),

                    # from clarifier agent
                    clarity_score=float(clarity_data.get('clarity_score',0.5)),
                    ambiguous_terms = json.dumps(clarity_data.get('ambiguous_terms', [])),
                    missing_info = json.dumps(clarity_data.get("missing_info",[])),
                    clarification_questions=json.dumps(clarity_data.get('clarification_questions',[]))

                )
                db.session.add(new_req)
                extracted_reqs.append(new_req)
            
            db.session.commit()
            print(f"[Orchestrator] Successfully saved {len(extracted_reqs)} requirements.")
            return extracted_reqs
        except Exception as e:
            print(f"[Pipeline Error]{e}")
            db.session.rollback()
            return None 