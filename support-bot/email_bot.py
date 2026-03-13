import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from rag_pipeline import get_repair_instructions
import json

def generate_technician_email(prediction_result: dict) -> str:
    """
    Given a prediction result from Module 1,
    use RAG to get repair instructions and draft an email.
    """
    module_id = prediction_result.get("module_id", "UNKNOWN")
    probability = prediction_result.get("failure_probability", 0)
    risk = prediction_result.get("risk_level", "HIGH")
    
    # Map failure symptoms to fault description
    fault_desc = f"Module {module_id} predicted failure. "
    if probability > 0.8:
        fault_desc += "Critical overheating and voltage instability detected. Internal temperature critical."
    elif probability > 0.6:
        fault_desc += "High temperature warning. Load percentage abnormal."
    else:
        fault_desc += "Voltage deviation detected. Monitoring required."
    
    # Get repair instructions via RAG
    rag_result = get_repair_instructions(fault_desc, use_mock=True)
    repair_instructions = rag_result["repair_instructions"]
    
    # Draft email
    email_body = f"""
Dear Limi AI Technical Team,

AUTOMATED MAINTENANCE ALERT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

MODULE DETAILS:
  • Module ID: {module_id}
  • Alert Time: {prediction_result.get('timestamp', datetime.now().isoformat())}
  • Failure Probability: {probability*100:.1f}%
  • Risk Level: {risk}
  • Predicted Status: {prediction_result.get('prediction', 'FAILURE')}

RECOMMENDED ACTION:
  {prediction_result.get('recommended_action', 'Immediate inspection required')}

RETRIEVED REPAIR INSTRUCTIONS (from Technical Manual):
{'='*60}
{repair_instructions[:800]}
{'='*60}

Please dispatch a technician immediately for HIGH risk alerts.
Update the Salesforce case upon completion.

This is an automated message from the Limi AI Predictive Maintenance System.
For support: support@limai.ai | +92-21-1234567
    """
    
    return email_body

def send_email(to_address: str, subject: str, body: str, 
               smtp_host: str = "smtp.gmail.com", 
               smtp_port: int = 587,
               sender_email: str = None,
               sender_password: str = None):
    """Send email via SMTP. For demo, just prints the email."""
    
    print("="*60)
    print(f"TO: {to_address}")
    print(f"SUBJECT: {subject}")
    print(body)
    print("="*60)
    
    # Uncomment to actually send:
    # msg = MIMEMultipart()
    # msg['From'] = sender_email
    # msg['To'] = to_address
    # msg['Subject'] = subject
    # msg.attach(MIMEText(body, 'plain'))
    # with smtplib.SMTP(smtp_host, smtp_port) as server:
    #     server.starttls()
    #     server.login(sender_email, sender_password)
    #     server.send_message(msg)
    
    return {"status": "sent", "to": to_address, "subject": subject}

def handle_maintenance_alert(prediction_result: dict):
    """Full pipeline: prediction → RAG → email."""
    if not prediction_result.get("alert", False):
        return {"status": "no_alert", "message": "No failure predicted"}
    
    email_body = generate_technician_email(prediction_result)
    
    result = send_email(
        to_address="technician@limai.ai",
        subject=f"🚨 ALERT: Module {prediction_result['module_id']} - {prediction_result['risk_level']} Risk",
        body=email_body
    )
    
    # Salesforce integration (see below)
    log_to_salesforce(prediction_result)
    
    return result

def log_to_salesforce(prediction_result: dict):
    """
    Salesforce CRM Integration.
    
    In production (from Nespon Solutions experience):
    1. Use simple-salesforce library:
       pip install simple-salesforce
    
    2. Authenticate:
       from simple_salesforce import Salesforce
       sf = Salesforce(username='user@limai.ai', 
                       password='pass', 
                       security_token='token')
    
    3. Create Case:
       sf.Case.create({
           'Subject': f'Module {module_id} Failure Alert',
           'Status': 'New',
           'Priority': 'High',
           'Description': repair_instructions,
           'Origin': 'Limi AI Auto-Detection',
           'Type': 'Hardware Failure'
       })
    
    For this demo: logging to console
    """
    print(f"\n[SALESFORCE LOG] Case created for Module: {prediction_result['module_id']}")
    print(f"  Priority: {prediction_result['risk_level']}")
    print(f"  Status: New → Assigned to field technician")

if __name__ == "__main__":
    # Test with a mock prediction result
    mock_prediction = {
        "module_id": "LM-UNIT-042",
        "timestamp": datetime.now().isoformat(),
        "prediction": "FAILURE",
        "failure_probability": 0.87,
        "risk_level": "HIGH",
        "alert": True,
        "recommended_action": "IMMEDIATE inspection required. Dispatch technician."
    }
    handle_maintenance_alert(mock_prediction)