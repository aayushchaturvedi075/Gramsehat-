# GRAMSEHAT (ग्रामसेहत)
### *“From symptoms to treatment, one guided path.”*

A modern, minimal, trustworthy healthcare web app prototype designed specifically for rural patients in India.

---

## 🌟 Vision & Design Philosophy

Rural patients in India frequently face barriers in accessing quality healthcare: digital literacy challenges, complex medical jargon, fragmented transport logistics, and delayed clinical triage. 

**GRAMSEHAT** addresses this through:
- **Voice-First Interaction:** The central blue microphone action is the primary entry point, letting patients articulate symptoms naturally in Hindi, English, and regional dialects.
- **Extreme Simplicity & Accessibility:** High-contrast color hierarchy, 48–64px touch targets, clear iconography with short labels, and zero confusing ERP tables or charts.
- **Multilingual By Design:** Instant language toggle between English and हिंदी (Hindi), with Web Speech API audio narration for non-literate patients.
- **End-to-End Continuity:** Connects home voice triage $\rightarrow$ lab report decoding $\rightarrow$ visual symptom screening $\rightarrow$ nearby hospital bed lookup $\rightarrow$ 108 ambulance transport $\rightarrow$ doctor pre-arrival notification.

---

## 🎨 Design System & Color Tokens

| Token | Hex / Spec | Purpose |
| :--- | :--- | :--- |
| **Primary Blue** | `#1463FF` | Main action buttons, voice center, brand emblem |
| **Dark Charcoal** | `#111318` | High-contrast readable typography, doctor portal |
| **Pure White** | `#FFFFFF` | Dominant card and background surface |
| **Secondary Light Blue** | `#F5F8FF` | Calming background tint, neutral surfaces |
| **Borders** | `#E6EAF0` | Subtle, thin card and container dividers |
| **Subtle Green** | `#12B76A` | Normal test metrics, verified beds, completed steps |
| **Subtle Amber** | `#F59E0B` | Moderate triage warnings, screening flags |
| **Subtle Red** | `#E02D3C` | Emergency 108 dispatch, critical alerts |

---

## 📱 The 7 Core Prototype Screens

### 1. Home / Patient Dashboard
- **Top Bar:** Brand logo, live Hindi/English language toggle, audio user guide, and patient profile avatar (`Ramlal S., 54y, Shivpur Village`).
- **Hero Voice Centerpiece:** 120px pulsing circular blue voice button (`#1463FF`), with clear labels and multilingual badge.
- **4 Guided Action Cards:**
  1. *Check Symptoms* (Stethoscope)
  2. *Explain Report* (FileText)
  3. *Scan / Screen* (Camera)
  4. *Find Hospital* (Building2 / MapPin)
- **Emergency Section:** High-contrast red-outlined *Emergency Care* button.
- **Ayushman Bharat (PM-JAY)** trust mark.

### 2. Voice Triage Screen
- Active real-time voice waveform simulation.
- Real-time conversation thread:
  - Patient: *“I have been feeling weak and dizzy since yesterday.”*
  - AI: *“Thank you. I’ll check how urgent this may be.”*
- Interactive scenario switcher (*Dizziness & Weakness*, *3-Day Fever*, *Acute Chest Pain*).
- Reassuring Urgency Result Card:
  - Care Level: *Clinic visit recommended*
  - Why this matters
  - What to do now
  - Nearest care option
- Primary action: *“Find Care Near Me”* & *“Talk Again”*.
- Text-to-Speech audio read-aloud via Web Speech API.

### 3. Report / Prescription Explainer
- Photo capture or file upload interface.
- Sample switchers for *Complete Blood Count (CBC)* and *Doctor Prescription*.
- Clean lab result preview (Hemoglobin 8.2 g/dL flagged).
- AI Plain-Language Breakdown:
  - **What looks normal:** WBC & Platelet counts explained in simple analogies.
  - **What needs attention:** Hemoglobin & iron explained in everyday terms (Anemia / खून की कमी).
  - **What to ask your doctor:** 3 ready-to-ask questions for the next visit.
- Audio read-aloud button for patients who cannot read.
- Ethical AI disclaimer banner.

### 4. Image Screening Screen
- Preliminary non-diagnostic visual triage.
- 3 Screening Modalities:
  - **Eye:** Conjunctival pallor check for anemia.
  - **Skin:** Rashes, ringworm, and dermatitis.
  - **Nail:** Spooning (koilonychia) and pale nail bed.
- Interactive camera viewfinder with guide reticle and animated laser scan.
- Result card with clear distinction between screening flag and formal clinical diagnosis.

### 5. Hospital Referral Screen
- Clean vector map view showing patient's village (*Shivpur*), nearby Community Health Centre (*Rampur CHC - 2.1 km*), and recommended Sub-District Hospital (*District Care - 4.2 km*).
- Filtering pills: *All Verified*, *Ayushman (Free)*, *Bed Available*, *24/7 Emergency*.
- Rich facility cards showing doctor on duty, verified general/ICU bed availability, and transit time.
- 1-click *“Choose Hospital”* flow that initiates transport and transmits data to the doctor.

### 6. Emergency / Transport Screen
- Stress-free emergency status interface with beacon pulse.
- Real-time 4-step progress tracker:
  $$\text{Requested} \longrightarrow \text{Driver assigned} \longrightarrow \text{On the way} \longrightarrow \text{Hospital}$$
- Live ETA countdown timer (11 min).
- Assigned vehicle details (Govt 108 Ambulance `#UP-32-E-1082`, Paramedic Rajesh Kumar).
- Large high-contrast *“Call for Help (108)”* button and family SMS alert dispatcher.

### 7. Doctor Pre-Alert Screen
- Clinician-facing intake terminal for ER / PHC Medical Officers.
- Incoming arrival banner (*“Patient arriving in approximately 18 minutes”*).
- Full clinical dossier:
  - Patient demographics (Ramlal Sharma, 54y, Shivpur).
  - Voice symptom intake transcription and SBAR clinical summary.
  - Flagged lab values (Hb 8.2 g/dL).
  - Visual screening pallor score (0.78).
  - In-transit transport and vitals status.
- Clinician action bar: *“Prepare for Arrival”* (reserves bed, prepares IV saline & iron orders) and *“View Full Summary”*.

---

## 📁 Repository Structure

```
Gramsehat/
├── frontend/             # Patient & Clinician Frontend Web Application
│   ├── assets/           # Application images & UI graphics
│   │   ├── banner_rural_health.png
│   │   ├── gramsehat_journey_bg.jpg
│   │   └── patient_avatar.jpg
│   ├── index.html        # Main HTML structure
│   ├── styles.css        # Responsive CSS & frosted glassmorphism styling
│   ├── app.js            # Frontend logic, state, and Sarvam AI voice integration
│   └── run.sh            # Local server runner (http://localhost:8080)
├── backend/              # Full FastAPI Clinical AI & OCR Backend
│   ├── app/              # FastAPI application (routers, schemas, services)
│   ├── tests/            # Test suite & mock assets
│   ├── requirements.txt  # Full backend dependencies (EasyOCR, Torch, etc.)
│   └── run.sh            # Local backend runner (http://127.0.0.1:8000)
├── api/                  # Vercel Serverless Functions
│   ├── stt.py            # Serverless Sarvam Speech-to-Text proxy
│   └── tts.py            # Serverless Sarvam Text-to-Speech proxy
├── .env                  # Environment configuration (API keys)
├── .env.example          # Sample environment variables
├── requirements.txt      # Root requirements for Vercel deployment
└── vercel.json           # Vercel deployment & rewrite configuration
```

---

## 🚀 How to Run Locally

### 1. Run Frontend (Port 8080)
```bash
./frontend/run.sh
# or:
python3 -m http.server --directory frontend 8080
# Open http://localhost:8080 in your browser
```

### 2. Run Backend API (Port 8000)
```bash
./backend/run.sh
# Interactive API Docs: http://127.0.0.1:8000/docs
```

---

## 💡 Prototype Presentation Features (For Judges & Investors)
- **Device Viewport Switcher:** Toggle between **Mobile App Frame** (390px iPhone simulator with notch and home bar) and **Desktop Full Screen View** at the top utility bar.
- **Quick Jump Menu:** Jump directly to any of the 7 screens instantly from the header.
- **Multilingual Demo:** Switch language to **हिंदी (Hindi)** to test localized text and Hindi voice synthesis.
- **Voice Playback:** Click any 🔊 icon to hear browser speech synthesis read out the AI clinical advice.
