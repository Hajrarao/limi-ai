from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# Mock technical manual - in production, load from PDF
TECHNICAL_MANUAL = """
LIMI AI MODULE TECHNICAL MANUAL v2.1

=== FAULT CODE: OVERHEAT_001 ===
Symptom: Module internal temperature exceeds 65°C
Diagnosis Steps:
1. Check ambient room temperature - should be below 35°C
2. Inspect cooling vents for dust blockage using compressed air
3. Verify airflow clearance - minimum 10cm on all sides
4. Check thermal paste on processor - reapply if dry/cracked
5. Test cooling fan RPM using diagnostic tool (target: 2000-3000 RPM)
Repair Steps:
- Clean cooling vents with compressed air
- Replace thermal paste (Arctic MX-4 recommended)
- If fan RPM < 1500, replace cooling fan (Part# LM-FAN-02)
- After repair, run 2-hour burn test to confirm stable temperature
Escalation: If temperature still >65°C after above steps, replace heat sink assembly

=== FAULT CODE: VOLTAGE_INSTABILITY_002 ===
Symptom: Voltage deviation >30V from 220V nominal
Diagnosis Steps:
1. Check input power supply voltage at mains connection
2. Inspect capacitors on power board for bulging/leaking
3. Test voltage regulator output (should be 220V ±5%)
4. Check for loose connections on power terminals
Repair Steps:
- Tighten all terminal connections
- Replace faulty capacitors (electrolytic, 470µF 25V)
- If voltage regulator failure confirmed, replace PSU board (Part# LM-PSU-05)
- Test with calibrated multimeter after repair
Required Tools: Multimeter, soldering iron, capacitor kit

=== FAULT CODE: HIGH_LOAD_003 ===
Symptom: Load percentage sustained >90% for >2 hours
Diagnosis Steps:
1. Check number of connected devices vs module capacity
2. Review usage logs for abnormal consumption patterns
3. Inspect current limiting circuit
Repair Steps:
- Redistribute connected devices to adjacent modules
- Update firmware to latest version (v3.1.2) for load balancing
- If hardware fault, replace load management IC (Part# LM-IC-12)

=== PREVENTIVE MAINTENANCE SCHEDULE ===
Monthly: Visual inspection, vent cleaning, connection tightening
Quarterly: Fan RPM test, thermal paste inspection, firmware update
Annually: Full component test, capacitor health check, calibration
Emergency Contacts: support@limai.ai | +92-21-1234567
"""

def build_vectordb():
    print("Building FAISS vector database from technical manual...")
    
    # Split manual into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n===", "\n\n", "\n", " "]
    )
    
    docs = [Document(page_content=TECHNICAL_MANUAL, metadata={"source": "technical_manual_v2.1"})]
    chunks = splitter.split_documents(docs)
    
    print(f"Created {len(chunks)} document chunks")
    
    # Use HuggingFace embeddings (free, no API key)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Build FAISS index
    vectordb = FAISS.from_documents(chunks, embeddings)
    vectordb.save_local("faiss_index")
    
    print("✅ FAISS index saved to ./faiss_index")
    return vectordb

if __name__ == "__main__":
    build_vectordb()