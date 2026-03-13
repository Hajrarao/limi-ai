# 🏢 Limi AI — Proactive Spatial Orchestrator

**Technical Assessment Submission**
**Candidate:** Hajra Rao
**Position:** AI & Data Analyst Intern (Generative AI & Predictive Systems)
**Company:** Limi AI

---

## 📌 Project Overview

The **Proactive Spatial Orchestrator** is a four-module AI system designed to keep Limi AI smart modules operational 24/7 across large-scale residential complexes. It combines predictive machine learning, generative AI, retrieval-augmented generation (RAG), and real-time visualization into a single integrated pipeline.

When a module is predicted to fail → the system automatically retrieves repair instructions → drafts a technician email → logs a Salesforce case → all without any human intervention.

---

## 🗂️ Project Structure

```
limi-ai/
├── predictive-engine/
│   ├── generate_data.py        # Mock sensor dataset generator
│   ├── train_model.py          # XGBoost model training + evaluation
│   ├── main.py                 # FastAPI server (prediction endpoint)
│   └── requirements.txt
│
├── generative-music/
│   ├── music_engine.py         # LSTM/Transformer note sequence generator
│   ├── music_engine_ui.py      # Streamlit UI with audio playback
│   └── requirements.txt
│
├── support-bot/
│   ├── build_vectordb.py       # FAISS vector database builder
│   ├── rag_pipeline.py         # RAG retrieval pipeline
│   ├── email_bot.py            # Automated email + Salesforce logger
│   ├── support_bot_ui.py       # Streamlit UI with live pipeline
│   └── requirements.txt
│
├── dashboard/
│   ├── app.py                  # Streamlit real-time heatmap dashboard
│   └── requirements.txt
│
└── README.md
```

---

## ⚙️ Modules

### Module 1 — Predictive Maintenance Engine

**Tech:** XGBoost · Scikit-learn · FastAPI · Pandas

Predicts module overheating or failure before it happens using real-time sensor data combined with external weather data.

**Feature Engineering:**
- `temp_diff` — internal temperature minus external temperature
- `voltage_deviation` — absolute deviation from 220V nominal
- `heat_load_index` — internal temp × load percentage

**Model:** XGBoost Classifier with `scale_pos_weight` to handle class imbalance. Handles false positives carefully by tuning the decision threshold.

**API:** FastAPI server running on port 8001. The Limi Hub queries it every 5 minutes with live sensor readings and receives a prediction, risk level, and recommended action.

```bash
cd predictive-engine
pip install -r requirements.txt
python generate_data.py
python train_model.py
uvicorn main:app --reload --port 8001
```

API docs available at: `http://localhost:8001/docs`

**Sample API Request:**
```json
POST /predict
{
  "module_id": "LM-UNIT-042",
  "voltage": 265.0,
  "internal_temp": 72.0,
  "usage_hours": 22.0,
  "external_temp": 32.0,
  "humidity": 60.0,
  "load_percentage": 85.0
}
```

**Sample Response:**
```json
{
  "module_id": "LM-UNIT-042",
  "prediction": "FAILURE",
  "failure_probability": 0.87,
  "risk_level": "HIGH",
  "alert": true,
  "recommended_action": "IMMEDIATE inspection required. Dispatch technician."
}
```

---

### Module 2 — Generative Ambient Music Engine

**Tech:** LSTM · Transformer · LangChain · MidiUtil · NumPy

Generates a 10-second ambient melody based on the current room state. Uses different architectures depending on the mood required.

| Room State | Architecture | Tempo | Character |
|------------|-------------|-------|-----------|
| Focus | LSTM (smooth transitions) | 60 BPM | Slow, low-frequency ambient loop |
| Calm | LSTM (bidirectional) | 45 BPM | Gentle, meditative arpeggios |
| Social | Transformer (fine-tuned) | 120 BPM | Groovy, mid-tempo melody |
| Energetic | Transformer (fine-tuned) | 145 BPM | High-tempo, driving rhythm |

**LangChain Integration:** Users can type natural language commands like *"Make the music more energetic, we're having a party"* and LangChain detects the intent and switches the room state automatically.

**Audio:** Pure Python + NumPy sine wave synthesis with ADSR envelopes and harmonics. Plays directly in the browser via `st.audio()` — no external tools required.

```bash
cd generative-music
pip install -r requirements.txt
streamlit run music_engine_ui.py --server.port 8503
```

---

### Module 3 — Automated Support System (RAG Pipeline)

**Tech:** FAISS · LangChain · LLaMA 3.3 · HuggingFace Embeddings · Salesforce

When Module 1 predicts a failure, this module automatically:
1. Searches the FAISS vector database for relevant repair steps from the technical manual
2. Passes the retrieved context to LLaMA 3.3 to generate a structured response
3. Drafts a complete email to the technician with fault code, risk level, and repair instructions
4. Logs the incident to Salesforce as a new support case

**RAG Pipeline:**
```
Fault Detected → Query Embedding (all-MiniLM-L6-v2) → FAISS Search (k=3)
→ Context Retrieved → LLaMA 3.3 Inference → Email Drafted → Salesforce Logged
```

**Salesforce Integration:**
Using the `simple-salesforce` Python library (from Nespon Solutions internship experience), the system creates a new Case record with:
- Subject: Module ID + fault code
- Priority: Mapped from risk level (HIGH → Critical)
- Description: Full repair instructions
- Origin: "Limi AI Auto-Detection"
- Status: New → auto-assigned to field technician queue

```bash
cd support-bot
pip install -r requirements.txt
python build_vectordb.py        # builds FAISS index from technical manual
python email_bot.py             # test the full pipeline
streamlit run support_bot_ui.py --server.port 8502
```

---

### Module 4 — Real-Time Dashboard

**Tech:** Streamlit · Plotly · Pandas · NumPy

Live building-wide health monitoring dashboard showing the status of every module across every floor.

**Features:**
- 🗺️ **Heatmap** — color-coded by failure risk (green → yellow → red)
- ⚡ **Energy Usage** — bar chart of consumption per floor
- 📈 **Live Temperature Trend** — rolling chart with critical threshold line
- 🚨 **Active Alerts Table** — sorted by highest risk, highlighted rows
- 📋 **Full Module Details** — expandable table with all sensor readings

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

---

## 🚀 Quick Start (Run Everything)

### 1. Clone the repository
```bash
git clone https://github.com/Hajrarao/limi-ai.git
cd limi-ai
```

### 2. Install dependencies for each module
```bash
cd predictive-engine && pip install -r requirements.txt && cd ..
cd generative-music  && pip install -r requirements.txt && cd ..
cd support-bot       && pip install -r requirements.txt && cd ..
cd dashboard         && pip install -r requirements.txt && cd ..
```

### 3. Train the model and build the vector DB
```bash
cd predictive-engine
python generate_data.py
python train_model.py
cd ../support-bot
python build_vectordb.py
```

### 4. Start all services (open 4 terminals)

| Terminal | Command | URL |
|----------|---------|-----|
| 1 | `cd predictive-engine && uvicorn main:app --port 8001` | localhost:8001/docs |
| 2 | `cd dashboard && streamlit run app.py --server.port 8501` | localhost:8501 |
| 3 | `cd support-bot && streamlit run support_bot_ui.py --server.port 8502` | localhost:8502 |
| 4 | `cd generative-music && streamlit run music_engine_ui.py --server.port 8503` | localhost:8503 |

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| ML Model | XGBoost, Scikit-learn |
| API | FastAPI, Uvicorn |
| Vector DB | FAISS |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| LLM | LLaMA 3.3 (via Ollama) |
| Orchestration | LangChain |
| Music | MidiUtil, NumPy (synthesis) |
| Dashboard | Streamlit, Plotly |
| CRM | Salesforce (simple-salesforce) |
| Language | Python 3.9+ |

---

## 📊 Model Performance

The XGBoost classifier is evaluated with special attention to **false positives** (predicting failure when none exists) since unnecessary technician dispatches are costly.

- `scale_pos_weight=3` used to handle class imbalance
- Decision threshold tunable via the API for precision/recall tradeoff
- Feature engineering improves accuracy by incorporating external weather context

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/predict` | Single module prediction |
| POST | `/predict/batch` | Batch prediction for multiple modules |
| GET | `/health` | Server status + timestamp |

---

## 👩‍💻 Author

**Hajra Rao**
AI & Data Analyst Intern Candidate
📧 Available on GitHub: [Hajrarao](https://github.com/Hajrarao)

---

## 📄 License

This project was built as a technical assessment for Limi AI. All rights reserved.
