/**
 * GRAMSEHAT - Voice-First Rural AI Healthcare Web App Prototype
 * Core Application Logic, State Management, Multilingual System & Voice Simulation
 */

// Application State
const appState = {
  currentScreen: 'screen-login',
  language: 'en', // 'en' or 'hi'
  voiceLang: 'hi-IN', // 'hi-IN' (default) or 'en-IN'
  viewMode: 'mobile', // 'mobile' or 'desktop'
  selectedScenario: 'dizziness',
  selectedScreening: 'eye',
  selectedHospital: 'District Care Hospital',
  isRecording: false,
  etaMinutes: 11,
  doctorAcknowledged: false,
  conversationHistory: [],
  hasAskedQuestion: false
};

// Multilingual Dictionary (English and Hindi)
const translations = {
  en: {
    patientName: "Ramlal Sharma",
    patientLocation: "Uttar Pradesh, 226010",
    taglineMicro: "Rural AI Health",
    navHome: "Home",
    navSymptoms: "Symptoms",
    navReports: "Reports",
    navScreening: "Screening",
    navHospitals: "Hospitals",
    navEmergency: "Emergency",
    tabHome: "Home",
    tabSymptoms: "Symptoms",
    tabReports: "Reports",
    tabScreening: "Screening",
    tabHospitals: "Hospitals",
    tabEmergency: "Emergency",
    exploreTabsLabel: "Health Service Tabs",
    quickTabsSub: "Tap to open any tab directly",
    heroPill: "Village Health Companion • ग्राम सेवा",
    heroTitle: "Tell us what’s wrong.",
    heroSubtext: "Speak in your language. We’ll guide you to the right care.",
    tapToSpeak: "Tap to speak",
    clickToSpeak: "Click to speak",
    tapOrbHint: "Tap orb to speak symptoms",
    supportedLanguages: "Hindi • English • + more languages",
    servicesBadge: "Rural AI Healthcare",
    mainFeaturesTitle: "Health Services",
    mainFeaturesSub: "Select a service to start care in your language",
    tagVoice: "Voice AI",
    tagRx: "Lab & Rx",
    tagVisual: "Visual AI",
    tagBeds: "Live Beds",
    linkStartTriage: "Speak & Check",
    linkDecode: "Decode Report",
    linkCameraCheck: "Photo Check",
    linkViewBeds: "Check Beds",
    quickActionsTitle: "Guided Health Services",
    cardSymptomsTitle: "Check Symptoms",
    cardSymptomsDesc: "Tell us how you feel in your own words",
    cardReportTitle: "Explain Report",
    cardReportDesc: "Understand blood tests & prescriptions in plain words",
    cardScanTitle: "Scan / Screen",
    cardScanDesc: "Quick photo check for eye pallor, skin rash, or nails",
    cardHospitalTitle: "Find Hospital",
    cardHospitalDesc: "Nearby clinics, verified bed availability & doctors",
    urgentHelpTitle: "Need urgent help?",
    urgentHelpDesc: "Direct ambulance dispatch & emergency doctor alert",
    emergencyCareBtn: "Emergency Care",
    trustFooter: "Ayushman Bharat (PM-JAY) Supported • Free Government Health Guidance",
    
    // Voice Triage
    voiceScreenTitle: "Tell us your symptoms",
    voiceScreenSubtitle: "Describe how you’re feeling, and we’ll help you find the right care.",
    sampleScenarios: "Try sample voice input",
    voiceListening: "Listening to your voice in Hindi / English...",
    tapToPause: "Tap mic to speak or pause",
    youLabel: "Patient (You)",
    aiCompanionLabel: "GRAMSEHAT AI",
    listenBtn: "Listen",
    careLevelLabel: "Care level:",
    careLevelVal: "Clinic visit recommended",
    whyMattersTitle: "Why this matters",
    whyMattersDesc: "Persistent weakness with dizziness can happen from low red blood cells (anemia), dehydration, or low blood pressure. A medical check is advisable within 24 hours.",
    whatToDoTitle: "What to do now",
    whatToDoDesc: "Sit or lie down in a cool spot. Drink clean water or ORS. Avoid sudden standing. Do not ride a bicycle or operate machinery.",
    nearestCareTitle: "Nearest care option",
    findCareBtn: "Find Care Near Me",
    talkAgainBtn: "Talk Again",
    voiceLangPrompt: "Speech Language:",
    voiceNotSupportedTitle: "Microphone access unavailable or denied",
    voiceNotSupportedDesc: "Please allow microphone access in your browser to speak with Sarvam AI, or type your symptoms below.",
    typeSymptomsOption: "Or type symptoms directly:",
    typeSymptomsPlaceholder: "e.g., severe fever for 3 days, headache, weakness...",
    checkSymptomsBtn: "Check",

    // Report
    reportScreenTitle: "Understand your report",
    uploadHeadline: "Take a photo or upload a report",
    uploadSubtext: "Supports blood reports, clinic discharge slips, or handwritten doctor prescriptions",
    takePhotoBtn: "Take Photo",
    uploadFileBtn: "Upload File",
    demoReportsLabel: "Demo sample reports:",
    hereFoundTitle: "Here’s what we found",
    explainedInSimple: "Explained in clear, everyday language for you and your family",
    listenInHindi: "Listen in Voice",
    normalTitle: "What looks normal",
    attentionTitle: "What needs attention",
    askDoctorTitle: "What to ask your doctor",
    disclaimerText: "This is an AI explanation to assist your understanding, not an official medical diagnosis. Always consult a licensed physician.",
    consultDoctorBtn: "Consult Doctor for Prescription",

    // Screening
    screeningTitle: "Quick Health Check",
    screeningExplain: "Take a clear photo. GRAMSEHAT will look for visible warning signs.",
    screeningEye: "Eye",
    screeningSkin: "Skin",
    screeningNail: "Nail",
    takePhotoCamera: "Take Photo",
    warningSignDetected: "Possible warning sign detected",
    considerCheckup: "Please consider a clinical check-up.",
    screeningNotice: "This is visual SCREENING only. It cannot confirm exact blood levels. Please get a confirmatory fingerprick or lab test at your health center.",
    findPHCBtn: "Find Nearby Health Centre",

    // Hospital
    hospitalsTitle: "Finding the right care",
    gpsLoc: "GPS: Village Shivpur, Ward 4",
    recommendedTag: "Best Match for Anemia & Weakness",
    specSpecialist: "Specialist available:",
    specBeds: "Bed availability:",
    chooseHospitalBtn: "Choose Hospital",
    viewDetailsBtn: "View Details",

    // Emergency
    emergencyScreenTitle: "Get help on the way",
    transportRequested: "Transport requested",
    driverAssignedSub: "Paramedic notified • Doctor alert sent",
    stepRequested: "Requested",
    stepAssigned: "Driver assigned",
    stepOnWay: "On the way",
    stepHospital: "Hospital",
    ambulanceVehicle: "Ambulance:",
    driverName: "Driver / Paramedic:",
    patientLocation: "Patient location:",
    destinationHospital: "Destination hospital:",
    callForHelpBtn: "Call for Help (108)",

    // Bottom Nav
    bottomHome: "Home",
    bottomCare: "Care",
    bottomReports: "Reports",
    bottomProfile: "Profile",

    // Help
    helpTitle: "How to use GRAMSEHAT",
    helpStep1Title: "Tap the Blue Microphone",
    helpStep1Desc: "Speak simply in Hindi or your own local language. Explain what feels wrong.",
    helpStep2Title: "Understand your health",
    helpStep2Desc: "AI explains whether you need home rest, a local clinic visit, or immediate urgent care.",
    helpStep3Title: "Hospital & Transport",
    helpStep3Desc: "Get connected to nearest verified hospital with beds and alert the doctor before you arrive.",
    gotItBtn: "Got it, thanks!"
  },

  hi: {
    patientName: "रामलाल शर्मा",
    patientLocation: "उत्तर प्रदेश, 226010",
    taglineMicro: "ग्रामीण एआई स्वास्थ्य",
    navHome: "मुख्य पृष्ठ",
    navSymptoms: "लक्षण",
    navReports: "रिपोर्ट्स",
    navScreening: "जांच",
    navHospitals: "अस्पताल",
    navEmergency: "आपातकालीन",
    tabHome: "होम",
    tabSymptoms: "लक्षण",
    tabReports: "रिपोर्ट्स",
    tabScreening: "जांच",
    tabHospitals: "अस्पताल",
    tabEmergency: "आपातकालीन",
    exploreTabsLabel: "स्वास्थ्य सेवा टैब",
    quickTabsSub: "सीधे किसी भी टैब पर जाएं",
    heroPill: "ग्रामीण स्वास्थ्य साथी • ग्राम सेवा",
    heroTitle: "बताएं, आपको क्या परेशानी है?",
    heroSubtext: "अपनी भाषा में बोलें। हम आपको सही इलाज का रास्ता बताएंगे।",
    tapToSpeak: "बोलने के लिए दबाएं",
    clickToSpeak: "बोलने के लिए दबाएं",
    tapOrbHint: "बोलने के लिए ओर्ब दबाएं",
    supportedLanguages: "हिंदी • English • और भी भाषाएँ",
    servicesBadge: "ग्रामीण एआई स्वास्थ्य सेवा",
    mainFeaturesTitle: "मुख्य स्वास्थ्य सेवाएं",
    mainFeaturesSub: "अपनी भाषा में स्वास्थ्य सहायता पाने के लिए चुनें",
    tagVoice: "आवाज़ से",
    tagRx: "पर्चा व जांच",
    tagVisual: "कैमरा जांच",
    tagBeds: "उपलब्ध बिस्तर",
    linkStartTriage: "बोलकर जांचें",
    linkDecode: "रिपोर्ट समझें",
    linkCameraCheck: "फोटो जांचें",
    linkViewBeds: "अस्पताल देखें",
    quickActionsTitle: "स्वास्थ्य सेवाएं",
    cardSymptomsTitle: "लक्षण जांचें",
    cardSymptomsDesc: "अपनी भाषा में बोलकर या लिखकर परेशानी बताएं",
    cardReportTitle: "रिपोर्ट समझें",
    cardReportDesc: "खून की जांच और पर्चे को आसान भाषा में समझें",
    cardScanTitle: "फोटो जांच",
    cardScanDesc: "आंख, त्वचा या नाखून की फोटो से लक्षण पहचानें",
    cardHospitalTitle: "नज़दीकी अस्पताल",
    cardHospitalDesc: "नज़दीकी सरकारी क्लिनिक, उपलब्ध बिस्तर और डॉक्टर",
    urgentHelpTitle: "तुरंत मदद चाहिए?",
    urgentHelpDesc: "सीधी एम्बुलेंस सेवा और डॉक्टर को तत्काल पूर्व-सूचना",
    emergencyCareBtn: "आपातकालीन सेवा",
    trustFooter: "आयुष्मान भारत (PM-JAY) समर्थित • निःशुल्क सरकारी स्वास्थ्य मार्गदर्शन",

    // Voice Triage
    voiceScreenTitle: "अपने लक्षण बताएं",
    voiceScreenSubtitle: "बताएं कि आप कैसा महसूस कर रहे हैं, हम सही देखभाल खोजने में मदद करेंगे।",
    sampleScenarios: "उदाहरण लक्षण चुनें",
    voiceListening: "आपकी आवाज़ सुनी जा रही है (हिंदी / English)...",
    tapToPause: "बोलने या रोकने के लिए ओर्ब दबाएं",
    youLabel: "मरीज़ (आप)",
    aiCompanionLabel: "ग्रामसेहत एआई",
    listenBtn: "सुनें",
    careLevelLabel: "देखभाल स्तर:",
    careLevelVal: "क्लिनिक जांच की सलाह",
    whyMattersTitle: "यह क्यों ज़रूरी है",
    whyMattersDesc: "कमज़ोरी और चक्कर खून की कमी (एनीमिया), डिहाइड्रेशन या लो ब्लड प्रेशर के कारण हो सकते हैं। 24 घंटे के अंदर क्लिनिक में डॉक्टर को दिखाना उचित रहेगा।",
    whatToDoTitle: "अभी क्या करें",
    whatToDoDesc: "ठंडी और छायादार जगह पर बैठें या लेट जाएं। ओआरएस (ORS) या साफ पानी पिएं। अचानक उठने से बचें। कोई भारी काम या साइकिल न चलाएं।",
    nearestCareTitle: "नज़दीकी स्वास्थ्य केंद्र",
    findCareBtn: "नज़दीकी अस्पताल देखें",
    talkAgainBtn: "फिर से बोलें",
    voiceLangPrompt: "बोलने की भाषा:",
    voiceNotSupportedTitle: "माइक्रोफ़ोन अनुपलब्ध या अनुमति अस्वीकृत",
    voiceNotSupportedDesc: "सार्वम एआई से बात करने के लिए कृपया माइक की अनुमति दें, या नीचे लक्षण लिखकर बताएं।",
    typeSymptomsOption: "या सीधे लक्षण लिखकर बताएं:",
    typeSymptomsPlaceholder: "उदा. 3 दिन से तेज़ बुखार, सिरदर्द, कमजोरी...",
    checkSymptomsBtn: "जांचें",

    // Report
    reportScreenTitle: "अपनी मेडिकल रिपोर्ट समझें",
    uploadHeadline: "फोटो खींचें या रिपोर्ट अपलोड करें",
    uploadSubtext: "खून की जांच की पर्ची, डिस्चार्ज स्लिप या डॉक्टर का लिखा पर्चा",
    takePhotoBtn: "फोटो लें",
    uploadFileBtn: "फाइल चुनें",
    demoReportsLabel: "नमूना रिपोर्ट्स देखें:",
    hereFoundTitle: "रिपोर्ट में क्या आया है",
    explainedInSimple: "आपके और आपके परिवार के लिए बिल्कुल सरल शब्दों में",
    listenInHindi: "आवाज़ में सुनें",
    normalTitle: "जो सामान्य (ठीक) है",
    attentionTitle: "जिस पर ध्यान देना ज़रूरी है",
    askDoctorTitle: "डॉक्टर से क्या पूछें",
    disclaimerText: "यह एआई द्वारा आपकी समझ के लिए सरल व्याख्या है, यह डॉक्टर का औपचारिक निदान नहीं है। डॉक्टर से अवश्य सलाह लें।",
    consultDoctorBtn: "इलाज व दवा हेतु डॉक्टर से मिलें",

    // Screening
    screeningTitle: "त्वरित स्वास्थ्य जांच",
    screeningExplain: "साफ रोशनी में फोटो लें। ग्रामसेहत चेतावनी के संकेत जांचेगा।",
    screeningEye: "आंख",
    screeningSkin: "त्वचा",
    screeningNail: "नाखून",
    takePhotoCamera: "फोटो खींचें",
    warningSignDetected: "संभावित चेतावनी संकेत पाया गया",
    considerCheckup: "कृपया नजदीकी स्वास्थ्य केंद्र में जांच करवाएं।",
    screeningNotice: "यह केवल प्राथमिक स्क्रीनिंग है। सटीक खून की मात्रा जानने हेतु प्राथमिक स्वास्थ्य केंद्र में जांच कराएं।",
    findPHCBtn: "नज़दीकी स्वास्थ्य केंद्र खोजें",

    // Hospital
    hospitalsTitle: "सही अस्पताल का चुनाव",
    gpsLoc: "जीपीएस: ग्राम शिवपुर, वार्ड 4",
    recommendedTag: "कमजोरी व एनीमिया के लिए सर्वश्रेष्ठ",
    specSpecialist: "उपलब्ध डॉक्टर:",
    specBeds: "बिस्तर उपलब्धता:",
    chooseHospitalBtn: "अस्पताल चुनें",
    viewDetailsBtn: "विवरण देखें",

    // Emergency
    emergencyScreenTitle: "मदद रास्ते में है",
    transportRequested: "एम्बुलेंस बुलाई गई",
    driverAssignedSub: "पैरामेडिक को सूचना • डॉक्टर को अलर्ट भेजा गया",
    stepRequested: "अनुरोध प्राप्त",
    stepAssigned: "ड्राइवर निर्धारित",
    stepOnWay: "रास्ते में है",
    stepHospital: "अस्पताल",
    ambulanceVehicle: "एम्बुलेंस:",
    driverName: "ड्राइवर / पैरामेडिक:",
    patientLocation: "मरीज़ का स्थान:",
    destinationHospital: "गंतव्य अस्पताल:",
    callForHelpBtn: "मदद के लिए कॉल करें (108)",

    // Bottom Nav
    bottomHome: "होम",
    bottomCare: "देखभाल",
    bottomReports: "रिपोर्ट्स",
    bottomProfile: "प्रोफ़ाइल",

    // Help
    helpTitle: "ग्रामसेहत का उपयोग कैसे करें",
    helpStep1Title: "नीला माइक बटन दबाएं",
    helpStep1Desc: "अपनी भाषा में बोलें और बताएं कि क्या तकलीफ हो रही है।",
    helpStep2Title: "अपनी सेहत को समझें",
    helpStep2Desc: "एआई बताएगा कि आराम करना है, क्लिनिक जाना है या आपातकालीन मदद चाहिए।",
    helpStep3Title: "अस्पताल और गाड़ी",
    helpStep3Desc: "उपलब्ध बिस्तर वाले नजदीकी अस्पताल और एम्बुलेंस की सीधी सुविधा।",
    gotItBtn: "समझ गया, धन्यवाद!"
  }
};

// Scenario Database for Voice Triage
const scenarios = {
  dizziness: {
    patientSpeechEn: "“I have been feeling weak and dizzy since yesterday.”",
    patientSpeechHi: "कल से बहुत कमजोरी और चक्कर महसूस हो रहे हैं।",
    aiSpeechEn: "“Thank you. I’ll check how urgent this may be.”",
    aiSpeechHi: "“धन्यवाद। मैं जांच रहा हूँ कि यह कितना गंभीर हो सकता है।”",
    careLevelSubEn: "Care Level",
    careLevelSubHi: "देखभाल स्तर",
    urgencyTitleEn: "Clinic visit recommended",
    urgencyTitleHi: "क्लिनिक जांच की सलाह",
    urgencyLevelClass: "border-moderate",
    urgencyStatusEn: "Non-emergency",
    urgencyStatusHi: "गैर-आपातकालीन",
    whyMattersEn: "Weakness with dizziness can happen from low red blood cells (anemia), dehydration, or low blood pressure. A medical check is advisable within 24 hours.",
    whyMattersHi: "कमज़ोरी और चक्कर खून की कमी (एनीमिया), डिहाइड्रेशन या लो ब्लड प्रेशर के कारण हो सकते हैं। 24 घंटे के अंदर क्लिनिक में डॉक्टर को दिखाना उचित रहेगा।",
    whatToDoEn: "Sit or lie down in a cool spot. Drink clean water or ORS. Avoid sudden standing. Do not ride a bicycle or operate machinery.",
    whatToDoHi: "ठंडी और छायादार जगह पर बैठें या लेट जाएं। ओआरएस (ORS) या साफ पानी पिएं। अचानक उठने से बचें। कोई भारी काम या साइकिल न चलाएं।",
    nearestCareEn: "District Care Hospital • 4.2 km away",
    nearestCareSubEn: "(Doctor on duty now)",
    nearestCareHi: "जिला केयर अस्पताल • 4.2 किमी दूर",
    nearestCareSubHi: "(डॉक्टर ऑन ड्यूटी उपलब्ध)"
  },
  fever: {
    patientSpeechEn: "“I have had high fever with chills for 3 days and headache.”",
    patientSpeechHi: "मुझे 3 दिन से ठंड लगकर तेज बुखार आ रहा है और सिर में दर्द है।",
    aiSpeechEn: "“Thank you. A continuous fever warrants malaria or viral testing at your local Primary Health Centre.”",
    aiSpeechHi: "“धन्यवाद। 3 दिन का लगातार बुखार मलेरिया या वायरल जांच मांगता है। कृपया प्राथमिक स्वास्थ्य केंद्र जाएं।”",
    careLevelSubEn: "Care Level",
    careLevelSubHi: "देखभाल स्तर",
    urgencyTitleEn: "PHC Health Check recommended",
    urgencyTitleHi: "प्राथमिक स्वास्थ्य केंद्र जांच की सलाह",
    urgencyLevelClass: "border-mild",
    urgencyStatusEn: "Routine Clinic",
    urgencyStatusHi: "सामान्य क्लिनिक",
    whyMattersEn: "Fever exceeding 48 hours requires a rapid blood smear to rule out seasonal vector-borne diseases.",
    whyMattersHi: "48 घंटे से अधिक का बुखार मलेरिया या अन्य मौसमी बीमारियों की पुष्टि के लिए खून की जांच मांगता है।",
    whatToDoEn: "Rest adequately, take sponge baths with lukewarm water, drink coconut water and fluids. Avoid self-medicating with antibiotics.",
    whatToDoHi: "पूरा आराम करें, माथे पर गीली पट्टी रखें, नारियल पानी या तरल पदार्थ लें। बिना डॉक्टर के परामर्श के एंटीबायोटिक न लें।",
    nearestCareEn: "Rampur Community Health Centre (CHC) • 2.1 km away",
    nearestCareSubEn: "(OPD open till 4 PM)",
    nearestCareHi: "रामपुर सामुदायिक स्वास्थ्य केंद्र (CHC) • 2.1 किमी दूर",
    nearestCareSubHi: "(ओपीडी शाम 4 बजे तक खुली है)"
  },
  chest: {
    patientSpeechEn: "“I have sudden heavy pressure on my chest and trouble breathing.”",
    patientSpeechHi: "मेरी छाती में अचानक भारी दबाव और सांस लेने में तकलीफ हो रही है।",
    aiSpeechEn: "“URGENT ALERT: Heavy chest pressure with breathlessness requires immediate emergency attention.”",
    aiSpeechHi: "“आपातकालीन चेतावनी: सीने में भारी दबाव और सांस फूलना तत्काल आपातकालीन जांच मांगता है।”",
    careLevelSubEn: "Emergency Level",
    careLevelSubHi: "आपातकालीन स्तर",
    urgencyTitleEn: "URGENT EMERGENCY CARE",
    urgencyTitleHi: "तत्काल आपातकालीन सहायता",
    urgencyLevelClass: "border-urgent",
    urgencyStatusEn: "Emergency Alert",
    urgencyStatusHi: "आपातकालीन चेतावनी",
    whyMattersEn: "Acute chest pain can be a sign of cardiac distress or pulmonary emergency requiring oxygen and ECG.",
    whyMattersHi: "सीने में तेज दर्द दिल की बीमारी या फेफड़ों की गंभीर समस्या हो सकती है जिसके लिए तुरंत ईसीजी की आवश्यकता है।",
    whatToDoEn: "Sit upright, loosen collar or tight clothes, remain calm, take slow deep breaths. Ambulance is being alerted.",
    whatToDoHi: "सीधे बैठें, कपड़े ढीले करें, शांत रहें और गहरी सांस लें। एम्बुलेंस को तुरंत सूचना भेजी जा रही है।",
    nearestCareEn: "District Care Hospital Emergency Ward • 4.2 km",
    nearestCareSubEn: "(Cardiac ICU on standby • 108 Dispatched)",
    nearestCareHi: "जिला अस्पताल आपातकालीन वार्ड • 4.2 किमी",
    nearestCareSubHi: "(कार्डियक आईसीयू तैयार है • 108 रवाना)"
  }
};

// Sample Reports Database
const sampleReports = {
  cbc: {
    badge: "Diagnostic Lab Slip",
    title: "Complete Blood Count (CBC)",
    date: "Shivpur Primary Health Centre • Oct 2, 2026",
    metrics: [
      { name: "Hemoglobin (Hb)", val: "8.2 g/dL", ref: "Normal: 13.0 - 17.0 (Low)", alert: true },
      { name: "Total WBC Count", val: "6,800 /µL", ref: "Normal: 4,000 - 11,000", alert: false },
      { name: "Platelet Count", val: "2.20 Lakh /µL", ref: "Normal: 1.5 - 4.5 Lakh", alert: false }
    ],
    normalEn: [
      "Your infection-fighting cells (WBC) are at 6,800 — meaning there is no major acute bacterial infection.",
      "Your platelet count is healthy at 2.2 Lakh — your blood can clot normally if you get a scratch."
    ],
    normalHi: [
      "संक्रमण से लड़ने वाली श्वेत रक्त कोशिकाएं (WBC) 6,800 हैं — अर्थात कोई गंभीर बैक्टीरिया संक्रमण नहीं है।",
      "प्लेटलेट 2.2 लाख हैं जो सामान्य हैं — चोट लगने पर खून का थक्का सामान्य रूप से जमेगा।"
    ],
    attentionEn: "Hemoglobin is 8.2 g/dL (Lower than normal range 13–17). Hemoglobin carries oxygen to your brain and body. When it is low, you feel tired, dizzy, and short of breath after minimal exertion (commonly known as Anemia / खून की कमी).",
    attentionHi: "हीमोग्लोबिन 8.2 g/dL है (सामान्य 13–17 से कम)। हीमोग्लोबिन शरीर व मस्तिष्क तक ऑक्सीजन पहुंचाता है। कम होने पर जल्दी थकान, चक्कर और सांस फूलना (एनीमिया / खून की कमी) होता है।",
    questionsEn: [
      "“Do I need iron supplements (like IFA tablets) or an injection?”",
      "“What local vegetables and grains should I eat to improve my blood (spinach, drumstick leaves, jaggery, chana)?”",
      "“When should I repeat this blood test to check my improvement?”"
    ],
    questionsHi: [
      "“क्या मुझे आयरन की गोलियां (IFA) या इंजेक्शन की आवश्यकता है?”",
      "“खून बढ़ाने के लिए कौन सा स्थानीय खान-पान उपयोगी रहेगा (पालक, सहजन के पत्ते, गुड़, चना)?”",
      "“कितने हफ्ते बाद दोबारा खून की जांच करानी होगी?”"
    ]
  },
  rx: {
    badge: "Doctor Prescription Slip",
    title: "Primary Health Centre OPD Prescription",
    date: "Dr. Anjali Patel • Rampur CHC",
    metrics: [
      { name: "Diagnosis", val: "Nutritional Anemia", ref: "Acuity: Moderate", alert: true },
      { name: "Blood Pressure", val: "105 / 70 mmHg", ref: "Normal: 120/80", alert: false },
      { name: "Pulse Rate", val: "84 bpm", ref: "Normal: 60 - 100", alert: false }
    ],
    normalEn: [
      "Blood pressure is stable at 105/70 mmHg — resting normally.",
      "Pulse rate of 84 bpm indicates heart rhythm is within normal limits."
    ],
    normalHi: [
      "ब्लड प्रेशर 105/70 mmHg स्थिर है।",
      "नाड़ी की गति (पल्स) 84 bpm सामान्य सीमा में है।"
    ],
    attentionEn: "Prescription prescribes: 1) Tab Iron & Folic Acid (IFA) once daily after meals; 2) Deworming tablet Albendazole 400mg single dose; 3) Dietary counsel for iron-rich greens.",
    attentionHi: "पर्चे में लिखा है: 1) आयरन एवं फोलिक एसिड (IFA) गोली भोजन के बाद दिन में 1 बार; 2) पेट के कीड़े खत्म करने हेतु एल्बेंडाजोल 400mg एक खुराक; 3) हरी पत्तेदार सब्जियां खाने की सलाह।",
    questionsEn: [
      "“Should I take the iron tablet with water or lemon water for better absorption?”",
      "“Are there any side effects like dark stool or mild nausea that I shouldn’t worry about?”"
    ],
    questionsHi: [
      "“क्या आयरन की गोली नींबू पानी के साथ लेने से बेहतर असर होता है?”",
      "“क्या मल का रंग काला होना सामान्य बात है?”"
    ]
  }
};

// Screening Types Data
const screeningData = {
  eye: {
    title: "Eye (Conjunctival Pallor)",
    instructionEn: "Gently pull down lower eyelid in natural light",
    instructionHi: "प्राकृतिक रोशनी में निचली पलक को हल्के से नीचे खींचें",
    artSvg: `<svg width="120" height="90" viewBox="0 0 140 100" fill="none">
      <path d="M10 50 Q 70 5 130 50 Q 70 95 10 50 Z" fill="#FFF1EB" stroke="#C88E75" stroke-width="3"/>
      <circle cx="70" cy="50" r="24" fill="#3D2B1F"/>
      <circle cx="70" cy="50" r="12" fill="#111318"/>
      <circle cx="75" cy="45" r="4" fill="#FFFFFF"/>
      <path d="M25 62 Q 70 85 115 62 Q 70 74 25 62 Z" fill="#FFC9C9" stroke="#E57373" stroke-width="1.8" stroke-dasharray="2 2"/>
    </svg>`,
    score: "Visual Pallor Score: High (0.78)",
    resultFocus: "Lower Palpebral Conjunctiva",
    explanationEn: "The lower inner eyelid tissue appears significantly paler than typical healthy vascular pink. This is a common visible sign associated with iron deficiency anemia.",
    explanationHi: "निचली भीतरी पलक का रंग सामान्य गुलाबी के बजाय काफी पीला दिखाई दे रहा है। यह खून की कमी (आयरन डेफिशियेंसी एनीमिया) का प्रमुख दृश्य लक्षण है।"
  },
  skin: {
    title: "Skin (Rashes & Marks)",
    instructionEn: "Hold camera 15 cm from skin lesion in steady light",
    instructionHi: "त्वचा के दाद या चकत्ते से कैमरा 15 सेमी दूर रखें",
    artSvg: `<svg width="120" height="90" viewBox="0 0 140 100" fill="none">
      <rect x="20" y="15" width="100" height="70" rx="16" fill="#FCECE6" stroke="#D1A796" stroke-width="2"/>
      <circle cx="65" cy="48" r="18" fill="#F87171" fill-opacity="0.3" stroke="#DC2626" stroke-width="2" stroke-dasharray="3 3"/>
      <circle cx="65" cy="48" r="8" fill="#DC2626" fill-opacity="0.5"/>
    </svg>`,
    score: "Erythema Density: Moderate",
    resultFocus: "Dermal Lesion & Ring Border",
    explanationEn: "Circular erythematous margin detected, commonly indicative of fungal tinea infection (ringworm) or contact dermatitis. Topical anti-fungal consultation recommended.",
    explanationHi: "त्वचा पर गोलाकार लाल चकत्ता पाया गया है जो दाद (फंगल इन्फेक्शन) का संकेत हो सकता है। प्राथमिक स्वास्थ्य केंद्र पर मलहम हेतु परामर्श लें।"
  },
  nail: {
    title: "Nail (Pallor & Spooning)",
    instructionEn: "Keep fingernails flat against a plain background",
    instructionHi: "नाखूनों को सादे धरातल पर सीधा रखकर फोटो लें",
    artSvg: `<svg width="120" height="90" viewBox="0 0 140 100" fill="none">
      <rect x="45" y="20" width="50" height="65" rx="12" fill="#E8D5CE" stroke="#BA9F94" stroke-width="2"/>
      <path d="M52 28 Q 70 20 88 28 L 88 56 Q 70 52 52 56 Z" fill="#FBEFE9" stroke="#E5B7A5" stroke-width="2"/>
      <line x1="56" y1="42" x2="84" y2="42" stroke="#D4A18E" stroke-dasharray="2 2"/>
    </svg>`,
    score: "Koilonychia / Pallor Index: Mild",
    resultFocus: "Nail Bed Vascularity",
    explanationEn: "Nail beds demonstrate reduced pink capillary refill and early flattening (spoon nail tendency), supporting clinical suspicion of chronic low iron.",
    explanationHi: "नाखूनों की लाली कम पाई गई है तथा नाखून चपटे दिख रहे हैं, जो शरीर में आयरन की पुरानी कमी का संकेत करते हैं।"
  }
};

// Hospital Database
const hospitalDirectory = {
  district: {
    name: "District Care Hospital",
    dist: "4.2 km",
    time: "18 min",
    type: "Govt Sub-District • Free Ayushman",
    specialist: "General Medicine, Obstetrics, Pediatrics",
    doctor: "Dr. S. K. Verma (MD)",
    beds: "14 General Beds, 2 ICU Beds Available",
    phone: "0522-298-108",
    facilities: "24x7 Blood Bank, Emergency OT, Diagnostic Lab, Ultrasound, PMJAY Free Pharmacy"
  },
  chc: {
    name: "Rampur Community Health Centre (CHC)",
    dist: "2.1 km",
    time: "9 min",
    type: "Community Health Centre (Government)",
    specialist: "General Physician, Staff Nurse 24/7",
    doctor: "Dr. Anjali Patel (MBBS)",
    beds: "6 Daycare Beds Available",
    phone: "0522-241-102",
    facilities: "Free Routine Blood Tests, Delivery Ward, Free IFA Supplements, Ambulance Bay"
  },
  trust: {
    name: "Jeevan Jyoti Charitable Hospital",
    dist: "6.8 km",
    time: "24 min",
    type: "Trust Non-Profit Subsidized",
    specialist: "Internal Medicine & Eye Care",
    doctor: "Dr. R. Raman (Physician)",
    beds: "8 General Beds Available",
    phone: "0522-266-900",
    facilities: "Subsidized Diagnostics, Pharmacy, Cataract Surgery Camp"
  }
};


/* ==========================================================================
   THEME SYSTEM (Dark / Light Mode)
   ========================================================================== */
function initTheme() {
  const savedTheme = localStorage.getItem('gramsehat_theme');
  const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const activeTheme = savedTheme ? savedTheme : (systemPrefersDark ? 'dark' : 'light');
  applyTheme(activeTheme);

  // Sync when OS color scheme changes if user hasn't manually chosen a preference
  if (window.matchMedia) {
    try {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('gramsehat_theme')) {
          applyTheme(e.matches ? 'dark' : 'light');
        }
      });
    } catch(err) {}
  }
}

function applyTheme(theme) {
  const isDark = theme === 'dark';
  document.documentElement.setAttribute('data-theme', theme);
  if (isDark) {
    document.documentElement.classList.add('dark-theme');
    if (document.body) document.body.classList.add('dark-theme');
  } else {
    document.documentElement.classList.remove('dark-theme');
    if (document.body) document.body.classList.remove('dark-theme');
  }
  appState.theme = theme;

  const toggleBtn = document.getElementById('headerThemeToggleBtn');
  if (toggleBtn) {
    const isHindi = appState && appState.language === 'hi';
    const label = isDark 
      ? (isHindi ? 'लाइट मोड चालू करें' : 'Switch to Light Mode')
      : (isHindi ? 'डार्क मोड चालू करें' : 'Switch to Dark Mode');
    toggleBtn.setAttribute('title', label);
    toggleBtn.setAttribute('aria-label', label);
    toggleBtn.setAttribute('data-current-theme', theme);
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const newTheme = current === 'dark' ? 'light' : 'dark';
  try {
    localStorage.setItem('gramsehat_theme', newTheme);
  } catch(e) {}
  applyTheme(newTheme);

  const isHindi = appState && appState.language === 'hi';
  const msg = isHindi 
    ? (newTheme === 'dark' ? 'डार्क मोड सक्रिय किया गया' : 'लाइट मोड सक्रिय किया गया')
    : (newTheme === 'dark' ? 'Dark mode enabled' : 'Light mode enabled');
  showToast(msg);
}

// Make accessible to window
window.initTheme = initTheme;
window.applyTheme = applyTheme;
window.toggleTheme = toggleTheme;

// Run initial check immediately
try {
  initTheme();
} catch(e) {}

/* ==========================================================================
   INITIALIZATION & EVENT BINDINGS
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupNavigation();
  setupLanguageSystem();
  setupDeviceSwitcher();
  setupSampleScenarios();
  startEtaCountdown();
  initVoiceOrb();
  navigateTo('screen-login');
  showToast("Welcome to GRAMSEHAT • Please log in to continue");
});


/* ==========================================================================
   NAVIGATION ENGINE
   ========================================================================== */
function setupNavigation() {
  // Screen dropdown in prototype bar
  const screenSelect = document.getElementById('screenSelect');
  if (screenSelect) {
    screenSelect.addEventListener('change', (e) => {
      navigateTo(e.target.value);
    });
  }
}

function navigateTo(screenId) {
  // Hide all screens
  const allScreens = document.querySelectorAll('.screen-view');
  allScreens.forEach(screen => {
    screen.classList.remove('active');
  });

  // Activate selected screen
  const target = document.getElementById(screenId);
  if (target) {
    target.classList.add('active');
    appState.currentScreen = screenId;
    window.scrollTo(0, 0);

    // Scroll viewport inside app container
    const viewport = document.querySelector('.screens-viewport');
    if (viewport) viewport.scrollTop = 0;

    // Ensure symptoms checking results are hidden until a question is asked
    if (screenId === 'screen-voice' && !appState.hasAskedQuestion) {
      const chatFlow = document.getElementById('symptomsChatFlow');
      if (chatFlow) chatFlow.style.display = 'none';
      const urgencyCard = document.getElementById('urgencyCard');
      if (urgencyCard) urgencyCard.style.display = 'none';
      const patientHi = document.getElementById('patientSpeechHindi');
      if (patientHi) patientHi.textContent = '';
    }
  }

  // Update Prototype Dropdown
  const screenSelect = document.getElementById('screenSelect');
  if (screenSelect) {
    screenSelect.value = screenId;
  }

  // Handle Login Screen full-bleed immersion
  const appContainer = document.getElementById('appContainer');
  const appViewport = document.querySelector('.app-viewport');
  const screensViewport = document.querySelector('.screens-viewport');
  if (screenId === 'screen-login') {
    if (appContainer) appContainer.classList.add('login-active');
    if (appViewport) appViewport.classList.add('login-active');
    if (screensViewport) screensViewport.classList.add('login-active');
  } else {
    if (appContainer) appContainer.classList.remove('login-active');
    if (appViewport) appViewport.classList.remove('login-active');
    if (screensViewport) screensViewport.classList.remove('login-active');
  }

  // Update Desktop Menu Active States
  document.querySelectorAll('.desktop-nav-menu .nav-link').forEach(btn => {
    if (btn.getAttribute('data-screen') === screenId) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Update Mobile Floating Dock Active States (5 Tabs from Uiverse cf2-exe)
  const dockMap = {
    'screen-home': 'cf2-tab-home',
    'screen-voice': 'cf2-tab-voice',
    'screen-reports': 'cf2-tab-reports',
    'screen-hospitals': 'cf2-tab-hospitals',
    'screen-emergency': 'cf2-tab-emergency'
  };
  Object.keys(dockMap).forEach(sId => {
    const radio = document.getElementById(dockMap[sId]);
    if (radio) {
      const isMatch = (sId === screenId);
      radio.checked = isMatch;
      const label = radio.closest('.cf2-dock-label');
      if (label) label.classList.toggle('active', isMatch);
    }
  });

  // OpenStreetMap + Leaflet Map Lifecycle in Hospitals Screen
  if (screenId === 'screen-hospitals') {
    setTimeout(() => {
      initHospitalMap();
      if (hospitalMap) {
        hospitalMap.invalidateSize();
      }
    }, 150);
  }
}


/* ==========================================================================
   DEVICE VIEWPORT SWITCHER (Mobile Frame vs Desktop)
   ========================================================================== */
function setupDeviceSwitcher() {
  const viewMobileBtn = document.getElementById('viewMobileBtn');
  const viewDesktopBtn = document.getElementById('viewDesktopBtn');
  const appContainer = document.getElementById('appContainer');

  if (viewMobileBtn && viewDesktopBtn && appContainer) {
    viewMobileBtn.addEventListener('click', () => {
      viewMobileBtn.classList.add('active');
      viewDesktopBtn.classList.remove('active');
      appContainer.classList.remove('mode-desktop');
      appContainer.classList.add('mode-mobile');
      appState.viewMode = 'mobile';
      showToast("Switched to Mobile Smartphone View (390px)");
    });

    viewDesktopBtn.addEventListener('click', () => {
      viewDesktopBtn.classList.add('active');
      viewMobileBtn.classList.remove('active');
      appContainer.classList.remove('mode-mobile');
      appContainer.classList.add('mode-desktop');
      appState.viewMode = 'desktop';
      showToast("Switched to Desktop / Tablet Full Screen View");
    });
  }
}


/* ==========================================================================
   LANGUAGE & LOCALIZATION ENGINE
   ========================================================================== */
function setupLanguageSystem() {
  const langToggleBtn = document.getElementById('langToggleBtn');
  const langMenu = document.getElementById('langMenu');

  if (langToggleBtn && langMenu) {
    langToggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      langMenu.classList.toggle('show');
    });

    document.addEventListener('click', () => {
      langMenu.classList.remove('show');
    });
  }
}

function setLanguage(lang) {
  appState.language = lang;
  const currentLangLabel = document.getElementById('currentLangLabel');
  if (currentLangLabel) {
    currentLangLabel.textContent = lang === 'hi' ? 'हिंदी' : 'English';
  }

  // Update checkmarks in dropdown
  const dropdownItems = document.querySelectorAll('#langMenu .dropdown-item');
  dropdownItems.forEach((item, index) => {
    if ((lang === 'en' && index === 0) || (lang === 'hi' && index === 1)) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Apply translations to all DOM elements with data-i18n attribute
  const elements = document.querySelectorAll('[data-i18n]');
  elements.forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (translations[lang] && translations[lang][key]) {
      el.textContent = translations[lang][key];
    }
  });

  // Re-render current scenario in active language only if a question has been asked
  if (appState.hasAskedQuestion) {
    loadVoiceScenario(appState.selectedScenario);
  }
  updateOrbDisplay(orbVoiceState.isListening);
  setVoiceLanguage(lang === 'hi' ? 'hi-IN' : 'en-IN', false);

  // Close dropdown
  const langMenu = document.getElementById('langMenu');
  if (langMenu) langMenu.classList.remove('show');

  const toastMsg = lang === 'hi' ? "भाषा बदलकर हिंदी कर दी गई है" : "Language set to English";
  showToast(toastMsg);
}


/* ==========================================================================
   SARVAM AI: SPEECH-TO-TEXT (STT: Saaras v3) & TEXT-TO-SPEECH (TTS: Bulbul v3)
   ========================================================================== */

/**
 * Resolves the appropriate backend or proxy URL dynamically.
 * Works seamlessly across local development (port 8080/5500 to port 8000)
 * and Vercel serverless deployments (/api/stt and /api/tts).
 */
function getApiEndpoint(endpointPath) {
  const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  if (isLocal && window.location.port !== '8000' && window.location.port !== '') {
    return `http://127.0.0.1:8000${endpointPath}`;
  }
  return endpointPath;
}

const orbVoiceState = {
  isListening: false,
  isTranscribing: false,
  time: 0,
  maxDuration: 25, // Auto-stop recording at 25 seconds (Sarvam 30s limit)
  timerInterval: null,
  activeContext: null,
  mediaRecorder: null,
  mediaStream: null,
  audioChunks: [],
  recordingMimeType: 'audio/webm',
  lastLiveTranscript: ''
};

function initVoiceOrb() {
  updateOrbDisplay(false);
  checkMicrophoneSupport();
}

function checkMicrophoneSupport() {
  const hasMediaDevices = Boolean(
    navigator.mediaDevices && 
    typeof navigator.mediaDevices.getUserMedia === 'function' && 
    window.MediaRecorder
  );
  const notice = document.getElementById('voiceUnsupportedNotice');
  const fallbackCard = document.getElementById('voiceFallbackInputCard');

  if (!hasMediaDevices) {
    if (notice) notice.style.display = 'flex';
    if (fallbackCard) fallbackCard.style.display = 'block';
  } else {
    if (notice) notice.style.display = 'none';
    if (fallbackCard) fallbackCard.style.display = 'block';
  }
  return hasMediaDevices;
}

function setVoiceLanguage(langCode, notify = true) {
  appState.voiceLang = langCode; // 'hi-IN' or 'en-IN'

  const enPill = document.getElementById('voiceLangEn');
  const hiPill = document.getElementById('voiceLangHi');
  if (enPill && hiPill) {
    enPill.classList.toggle('active', langCode === 'en-IN');
    hiPill.classList.toggle('active', langCode === 'hi-IN');
  }

  if (notify) {
    const isHindi = langCode.startsWith('hi');
    showToast(isHindi ? "सार्वम एआई भाषा: हिंदी (hi-IN)" : "Sarvam AI Language: English (en-IN)");
  }
}

function toggleVoiceOrb(context) {
  if (orbVoiceState.isTranscribing) {
    showToast(appState.language === 'hi' ? "आवाज़ पहचानी जा रही है, कृपया प्रतीक्षा करें..." : "Transcribing audio, please wait...");
    return;
  }

  if (orbVoiceState.isListening) {
    stopVoiceOrbListening(context, true);
  } else {
    startVoiceOrbListening(context);
  }
}

// Real-time audio frequency visualizer state
let audioVisualizerCtx = null;
let audioVisualizerAnalyser = null;
let audioVisualizerFrameId = null;

function startAudioLevelVisualizer(stream) {
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;
    audioVisualizerCtx = new AudioContextClass();
    const source = audioVisualizerCtx.createMediaStreamSource(stream);
    audioVisualizerAnalyser = audioVisualizerCtx.createAnalyser();
    audioVisualizerAnalyser.fftSize = 64;
    source.connect(audioVisualizerAnalyser);

    const dataArray = new Uint8Array(audioVisualizerAnalyser.frequencyBinCount);
    const waveMeter = document.getElementById('voiceWaveMeter');
    if (waveMeter) waveMeter.style.display = 'inline-flex';
    const waveBars = document.querySelectorAll('.voice-wave-bar');

    function updateBars() {
      if (!orbVoiceState.isListening) return;
      audioVisualizerAnalyser.getByteFrequencyData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      const avg = sum / dataArray.length;

      waveBars.forEach((bar, index) => {
        const val = dataArray[index % dataArray.length] || avg;
        const scale = Math.max(0.2, (val / 128) * 1.8);
        bar.style.transform = `scaleY(${scale.toFixed(2)})`;
      });

      // Micro-reactivity on the glowing gradient sphere
      const sphere = document.querySelector('.orb-gradient-sphere');
      if (sphere) {
        const sphereScale = 1 + Math.min(0.16, (avg / 255) * 0.25);
        sphere.style.transform = `scale(${sphereScale.toFixed(2)})`;
      }

      audioVisualizerFrameId = requestAnimationFrame(updateBars);
    }
    updateBars();
  } catch (err) {
    console.warn("Could not start audio visualizer:", err);
  }
}

function stopAudioLevelVisualizer() {
  if (audioVisualizerFrameId) {
    cancelAnimationFrame(audioVisualizerFrameId);
    audioVisualizerFrameId = null;
  }
  if (audioVisualizerCtx && audioVisualizerCtx.state !== 'closed') {
    try { audioVisualizerCtx.close(); } catch (e) {}
    audioVisualizerCtx = null;
  }
  const waveMeter = document.getElementById('voiceWaveMeter');
  if (waveMeter) waveMeter.style.display = 'none';
  const sphere = document.querySelector('.orb-gradient-sphere');
  if (sphere) sphere.style.transform = 'scale(1)';
}

/* ==========================================================================
   REAL-TIME WORD-BY-WORD SPEECH TRANSCRIPTION ENGINE
   ========================================================================== */
let liveSpeechRecognizer = null;

function startLiveSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.info("Web SpeechRecognition is not available on this browser.");
    return;
  }

  stopLiveSpeechRecognition();

  try {
    const recognizer = new SpeechRecognition();
    recognizer.continuous = true;
    recognizer.interimResults = true;
    recognizer.maxAlternatives = 1;
    recognizer.lang = appState.voiceLang || (appState.language === 'hi' ? 'hi-IN' : 'en-IN');

    recognizer.onresult = (event) => {
      let interim = '';
      let finalized = '';
      for (let i = 0; i < event.results.length; ++i) {
        const item = event.results[i][0];
        if (item && item.transcript) {
          if (event.results[i].isFinal) {
            finalized += item.transcript + ' ';
          } else {
            interim += item.transcript;
          }
        }
      }

      const fullText = (finalized + interim).trim();
      if (fullText) {
        orbVoiceState.lastLiveTranscript = fullText;
        displayLiveTranscribedWords(fullText);
      }
    };

    recognizer.onerror = (e) => {
      if (e.error !== 'no-speech' && e.error !== 'aborted') {
        console.warn("Live SpeechRecognition notice:", e.error);
      }
    };

    recognizer.onend = () => {
      // Re-arm recognizer if voice input is still ongoing
      if (orbVoiceState.isListening && liveSpeechRecognizer) {
        try {
          recognizer.start();
        } catch (e) {}
      }
    };

    liveSpeechRecognizer = recognizer;
    recognizer.start();
  } catch (err) {
    console.warn("Could not start live SpeechRecognition:", err);
  }
}

function stopLiveSpeechRecognition() {
  if (liveSpeechRecognizer) {
    try {
      liveSpeechRecognizer.stop();
    } catch (e) {}
    liveSpeechRecognizer = null;
  }
}

function displayLiveTranscribedWords(text) {
  if (!text) return;
  const isHindi = appState.voiceLang === 'hi-IN' || appState.language === 'hi';

  const liveCard = document.getElementById('liveTranscribeCard');
  const streamEl = document.getElementById('liveWordsStream');
  const badgeEl = document.getElementById('liveTranscribeBadge');

  if (liveCard) liveCard.style.display = 'block';
  if (badgeEl) {
    badgeEl.textContent = isHindi 
      ? "🔴 बोलते रहें • लाइव ट्रांसक्रिप्शन (Live)" 
      : "🔴 Keep speaking • Live Transcribing";
  }
  if (streamEl) {
    streamEl.textContent = `“${text}”`;
  }

  // Also reflect speech directly in the patient bubble
  const hiEl = document.getElementById('patientSpeechHindi');
  if (hiEl) {
    hiEl.textContent = `“${text}”`;
    hiEl.style.display = 'block';
  }
}

function resetLiveTranscriptionDisplay() {
  const liveCard = document.getElementById('liveTranscribeCard');
  if (liveCard) liveCard.style.display = 'none';

  const streamEl = document.getElementById('liveWordsStream');
  if (streamEl) streamEl.textContent = '';
}

async function startVoiceOrbListening(context) {
  // If called on home screen, navigate to voice triage screen first
  if (context === 'home') {
    navigateTo('screen-voice');
    startVoiceOrbListening('triage');
    return;
  }

  // Stop any ongoing TTS audio before opening microphone
  if (typeof stopSarvamTTS === 'function') {
    stopSarvamTTS();
  }

  const isSupported = checkMicrophoneSupport();
  const isHindi = appState.voiceLang === 'hi-IN' || appState.language === 'hi';

  if (!isSupported) {
    showToast(isHindi 
      ? "इस ब्राउज़र में माइक्रोफ़ोन रिकॉर्डिंग उपलब्ध नहीं है। कृपया नीचे लक्षण लिखकर बताएं।" 
      : "Microphone recording is not supported in this browser. Please type your symptoms below."
    );
    const manualInput = document.getElementById('manualSymptomInput');
    if (manualInput) manualInput.focus();
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    });

    orbVoiceState.mediaStream = stream;
    orbVoiceState.isListening = true;
    orbVoiceState.isTranscribing = false;
    orbVoiceState.activeContext = context;
    orbVoiceState.time = 0;
    orbVoiceState.audioChunks = [];

    // Start live audio wave visualizer
    startAudioLevelVisualizer(stream);

    // Show prominent Stop & Transcribe button
    const stopBtn = document.getElementById('voiceStopCheckBtn');
    if (stopBtn) {
      stopBtn.style.display = 'inline-flex';
      const stopText = document.getElementById('voiceStopBtnText');
      if (stopText) {
        stopText.textContent = isHindi ? "बोलना पूरा हुआ • जांच करें (Done • Check)" : "Done Speaking • Check Symptoms";
      }
    }

    // Select the best supported audio MIME type for Sarvam STT
    const supportedTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/ogg;codecs=opus',
      'audio/ogg',
      'audio/wav'
    ];
    let selectedMime = '';
    for (const mime of supportedTypes) {
      if (window.MediaRecorder.isTypeSupported && window.MediaRecorder.isTypeSupported(mime)) {
        selectedMime = mime;
        break;
      }
    }
    orbVoiceState.recordingMimeType = selectedMime || 'audio/webm';

    const recorder = selectedMime 
      ? new MediaRecorder(stream, { mimeType: selectedMime })
      : new MediaRecorder(stream);
    
    orbVoiceState.mediaRecorder = recorder;

    recorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        orbVoiceState.audioChunks.push(event.data);
      }
    };

    recorder.onstop = () => {
      processRecordedAudio(context);
    };

    recorder.onerror = (e) => {
      console.warn("MediaRecorder error:", e);
      resetVoiceOrbDisplay();
    };

    // Collect audio slices every 250ms
    recorder.start(250);

    updateOrbDisplay(true);

    orbVoiceState.lastLiveTranscript = '';
    resetLiveTranscriptionDisplay();

    showToast(isHindi ? "माइक चालू है • अपने लक्षण बोलें..." : "Microphone active • Speak your symptoms clearly");

    // Start real-time streaming speech recognition to display each word as spoken
    startLiveSpeechRecognition();

    // Background safety timer (auto-stops at 25s to stay under Sarvam 30s limit)
    clearInterval(orbVoiceState.timerInterval);
    orbVoiceState.timerInterval = setInterval(() => {
      orbVoiceState.time += 1;
      const remaining = orbVoiceState.maxDuration - orbVoiceState.time;
      if (remaining <= 0) {
        clearInterval(orbVoiceState.timerInterval);
        const currentHindi = appState.voiceLang === 'hi-IN' || appState.language === 'hi';
        showToast(currentHindi 
          ? "समय पूरा हुआ • सार्वम एआई से जांच की जा रही है..." 
          : "25s limit reached • Checking symptoms with Sarvam AI..."
        );
        stopVoiceOrbListening(context, true);
      }
    }, 1000);

  } catch (err) {
    console.error("Microphone getUserMedia error:", err);
    resetVoiceOrbDisplay();

    const isDenied = err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError';
    const notice = document.getElementById('voiceUnsupportedNotice');
    if (notice) notice.style.display = 'flex';

    showToast(isHindi 
      ? (isDenied 
          ? "माइक्रोफ़ोन की अनुमति अस्वीकृत। कृपया ब्राउज़र सेटिंग्स में अनुमति दें या नीचे लिखें।" 
          : "माइक्रोफ़ोन शुरू नहीं हो पाया। कृपया नीचे लक्षण लिखकर बताएं।")
      : (isDenied 
          ? "Microphone permission denied. Please allow microphone access or type symptoms below." 
          : "Could not access microphone. Please type your symptoms below.")
    );

    const manualInput = document.getElementById('manualSymptomInput');
    if (manualInput) manualInput.focus();
  }
}

function stopVoiceOrbListening(context, shouldProcess = true) {
  if (!orbVoiceState.isListening && !orbVoiceState.mediaRecorder) return;

  orbVoiceState.isListening = false;
  clearInterval(orbVoiceState.timerInterval);
  stopAudioLevelVisualizer();
  stopLiveSpeechRecognition();

  const stopBtn = document.getElementById('voiceStopCheckBtn');
  if (stopBtn) stopBtn.style.display = 'none';

  // Stop recording if active
  if (orbVoiceState.mediaRecorder && orbVoiceState.mediaRecorder.state !== 'inactive') {
    try {
      orbVoiceState.mediaRecorder.stop();
    } catch (e) {
      console.warn("Error stopping MediaRecorder:", e);
    }
  }

  // Release mic hardware tracks immediately
  if (orbVoiceState.mediaStream) {
    try {
      orbVoiceState.mediaStream.getTracks().forEach(track => track.stop());
    } catch (e) {}
    orbVoiceState.mediaStream = null;
  }

  if (!shouldProcess) {
    orbVoiceState.audioChunks = [];
    resetVoiceOrbDisplay();
  }
}

function resetVoiceOrbDisplay() {
  orbVoiceState.isListening = false;
  orbVoiceState.isTranscribing = false;
  clearInterval(orbVoiceState.timerInterval);
  stopAudioLevelVisualizer();
  stopLiveSpeechRecognition();
  resetLiveTranscriptionDisplay();

  const stopBtn = document.getElementById('voiceStopCheckBtn');
  if (stopBtn) stopBtn.style.display = 'none';

  updateOrbDisplay(false);

  const triageSub = document.getElementById('triageOrbSub');
  if (triageSub) {
    triageSub.innerHTML = `<span class="orb-caption-text" data-i18n="tapToPause">${appState.voiceLang === 'hi-IN' || appState.language === 'hi' ? 'बोलने के लिए ओर्ब दबाएं' : 'Tap orb to speak'}</span>`;
  }
}

async function processRecordedAudio(context) {
  const isHindi = appState.voiceLang === 'hi-IN' || appState.language === 'hi';

  if (!orbVoiceState.audioChunks || orbVoiceState.audioChunks.length === 0) {
    if (orbVoiceState.lastLiveTranscript) {
      handleFinalTranscript(orbVoiceState.lastLiveTranscript);
      return;
    }
    resetVoiceOrbDisplay();
    return;
  }

  const cleanMime = (orbVoiceState.recordingMimeType || 'audio/webm').split(';')[0].trim().toLowerCase();
  const audioBlob = new Blob(orbVoiceState.audioChunks, {
    type: cleanMime
  });
  orbVoiceState.audioChunks = [];

  // Validation: Check for empty / silent audio (< 800 bytes)
  if (audioBlob.size < 800) {
    if (orbVoiceState.lastLiveTranscript) {
      handleFinalTranscript(orbVoiceState.lastLiveTranscript);
      return;
    }
    resetVoiceOrbDisplay();
    showToast(isHindi 
      ? "कोई आवाज़ रिकॉर्ड नहीं हुई। कृपया माइक दबाकर साफ़ आवाज़ में बोलें।" 
      : "No clear speech recorded. Please tap the mic and speak clearly."
    );
    return;
  }

  // Enter UI Loading State
  orbVoiceState.isTranscribing = true;
  updateOrbDisplay(false);

  // If live words were transcribed, show status in live card
  const liveCard = document.getElementById('liveTranscribeCard');
  const badgeEl = document.getElementById('liveTranscribeBadge');
  if (orbVoiceState.lastLiveTranscript) {
    if (liveCard) liveCard.style.display = 'block';
    if (badgeEl) {
      badgeEl.textContent = isHindi 
        ? "✓ आवाज़ प्राप्त • सार्वम एआई द्वारा जांच जारी..." 
        : "✓ Speech captured • Checking with Sarvam AI...";
    }
  }

  const triageSub = document.getElementById('triageOrbSub');
  if (triageSub) {
    triageSub.innerHTML = `<span class="orb-caption-text" style="color: #2b787a; font-weight: 600;">${isHindi ? "सार्वम एआई (Saaras v3) पहचान रहा है..." : "Transcribing (Sarvam Saaras v3)..."}</span>`;
  }

  showToast(isHindi ? "आवाज़ पहचानी जा रही है (Saaras v3)..." : "Transcribing with Sarvam AI...");

  // Match filename extension to clean MIME type
  let fileExt = 'webm';
  if (cleanMime.includes('mp4') || cleanMime.includes('m4a')) fileExt = 'mp4';
  else if (cleanMime.includes('wav')) fileExt = 'wav';
  else if (cleanMime.includes('ogg') || cleanMime.includes('opus')) fileExt = 'ogg';
  else if (cleanMime.includes('mp3') || cleanMime.includes('mpeg')) fileExt = 'mp3';

  const formData = new FormData();
  formData.append('file', audioBlob, `patient_symptoms.${fileExt}`);
  formData.append('language_code', appState.voiceLang || (isHindi ? 'hi-IN' : 'en-IN'));
  formData.append('model', 'saaras:v3');

  try {
    const res = await fetch(getApiEndpoint('/api/stt'), {
      method: 'POST',
      body: formData
    });

    if (res.status === 401) {
      showToast("Sarvam AI Error: Invalid API Key. Check SARVAM_API_KEY.");
      throw new Error("Sarvam 401 Unauthorized");
    } else if (res.status === 429) {
      showToast(isHindi 
        ? "सार्वम सर्वर व्यस्त है (दर सीमा)। कृपया कुछ क्षण बाद पुनः बोलें।" 
        : "Sarvam AI rate limit exceeded. Please wait a moment and try speaking again."
      );
      throw new Error("Sarvam 429 Rate Limit");
    } else if (!res.ok) {
      const errText = await res.text();
      showToast(isHindi 
        ? "आवाज़ पहचान में समस्या आई। कृपया पुनः बोलें।" 
        : "Voice recognition service error. Please try speaking again."
      );
      throw new Error(`Sarvam STT failed: ${res.status} ${errText}`);
    }

    const data = await res.json();
    let transcript = (data.transcript || '').trim();

    // Use live captured transcript as fallback if Sarvam returned empty
    if (!transcript && orbVoiceState.lastLiveTranscript) {
      transcript = orbVoiceState.lastLiveTranscript;
    }

    if (!transcript) {
      showToast(isHindi 
        ? "कोई स्पष्ट आवाज़ नहीं मिली। कृपया माइक के पास आकर पुनः बोलें।" 
        : "No speech recognized. Please speak closer to the mic."
      );
      resetLiveTranscriptionDisplay();
    } else {
      resetLiveTranscriptionDisplay();
      handleFinalTranscript(transcript);
    }

  } catch (err) {
    console.error("Sarvam STT proxy error:", err);
    if (orbVoiceState.lastLiveTranscript) {
      resetLiveTranscriptionDisplay();
      handleFinalTranscript(orbVoiceState.lastLiveTranscript);
      return;
    }
    if (!err.message.includes("401") && !err.message.includes("429")) {
      showToast(isHindi 
        ? "नेटवर्क त्रुटि: आवाज़ सर्वर से नहीं जुड़ सके। कृपया पुनः प्रयास करें।" 
        : "Network error connecting to Sarvam STT. Please try again."
      );
    }
  } finally {
    resetVoiceOrbDisplay();
  }
}

function updateLivePatientSpeech(text, isInterim) {
  if (!text) return;
  const hiEl = document.getElementById('patientSpeechHindi');
  const enEl = document.getElementById('patientSpeechEnglish');

  if (isInterim) {
    if (hiEl) {
      hiEl.innerHTML = `<em>${text}...</em>`;
      hiEl.style.display = 'block';
    }
    if (enEl) enEl.style.display = 'none';
  } else {
    if (hiEl) {
      hiEl.textContent = text;
      hiEl.style.display = 'block';
    }
    if (enEl) enEl.style.display = 'none';
  }
}

function handleFinalTranscript(transcriptText) {
  if (!transcriptText || !transcriptText.trim()) return;

  const cleanText = transcriptText.trim();
  const isHindi = appState.voiceLang === 'hi-IN' || appState.language === 'hi';

  resetLiveTranscriptionDisplay();

  // 1. Mark that user has asked a question
  appState.hasAskedQuestion = true;

  // 2. Append this patient message to cumulative conversation chat stream
  const isFirstTurn = !appState.conversationHistory || appState.conversationHistory.length === 0;
  appendPatientChatTurn(cleanText, isFirstTurn);

  // 3. Show AI analyzing bubble below patient's message
  showAiAnalyzingBubble();

  // 4. Keep urgency card hidden until analysis arrives
  const urgencyCard = document.getElementById('urgencyCard');
  if (urgencyCard && isFirstTurn) {
    urgencyCard.style.display = 'none';
  }

  showToast(isHindi ? `✓ प्रश्न दर्ज: "${cleanText.slice(0, 32)}..."` : `✓ Received: "${cleanText.slice(0, 32)}..."`);

  // 5. Send transcript to backend with full conversation history
  sendTranscriptToBackend(cleanText);
}

/**
 * Safely escapes HTML in chat message text.
 */
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Appends a patient message bubble to the cumulative conversation chat stream.
 * Preserves all previous turns in the chat view.
 */
function appendPatientChatTurn(text, isInitial = false) {
  const isHindi = appState.voiceLang === 'hi-IN' || appState.language === 'hi';
  const chatFlow = document.getElementById('symptomsChatFlow');
  if (!chatFlow) return null;

  chatFlow.style.display = 'flex';

  if (!appState.chatHistory) appState.chatHistory = [];

  const turnIndex = appState.chatHistory.filter(m => m.role === 'user').length + 1;
  const msgId = `patient-msg-${Date.now()}-${turnIndex}`;
  const isFirst = isInitial || turnIndex === 1;

  const badgeText = isFirst
    ? (isHindi ? "शुरुआती लक्षण • Initial Symptoms" : "Initial Symptoms")
    : (isHindi ? `आपका उत्तर (चरण ${turnIndex}) • Your Answer` : `Your Answer (Turn ${turnIndex})`);

  const msg = {
    id: msgId,
    role: 'user',
    text: text,
    turnIndex: turnIndex,
    isFirst: isFirst,
    badgeText: badgeText,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };

  appState.chatHistory.push(msg);

  // Remove patientSpeechHindi ID from any older element so IDs stay unique
  const prevHi = document.getElementById('patientSpeechHindi');
  if (prevHi) prevHi.removeAttribute('id');

  // Create DOM Element
  const bubbleDiv = document.createElement('div');
  bubbleDiv.className = 'patient-speech-glass-bubble chat-bubble-animate';
  bubbleDiv.id = msgId;
  bubbleDiv.innerHTML = `
    <div class="patient-bubble-header">
      <span class="patient-bubble-badge ${isFirst ? 'badge-initial' : 'badge-answer'}">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        <span>${escapeHtml(badgeText)}</span>
      </span>
      <span class="chat-turn-timestamp">${msg.timestamp}</span>
    </div>
    <p class="patient-quote-hi" id="patientSpeechHindi">“${escapeHtml(text)}”</p>
  `;

  chatFlow.appendChild(bubbleDiv);

  try {
    bubbleDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (e) {}

  return msg;
}

/**
 * Displays a typing / analyzing indicator bubble while the AI evaluates the response.
 */
function showAiAnalyzingBubble() {
  removeAiAnalyzingBubble();
  const chatFlow = document.getElementById('symptomsChatFlow');
  if (!chatFlow) return;

  const isHindi = appState.voiceLang === 'hi-IN' || appState.language === 'hi';
  const analyzingDiv = document.createElement('div');
  analyzingDiv.id = 'aiAnalyzingBubble';
  analyzingDiv.className = 'ai-speech-glass-card ai-analyzing-card chat-bubble-animate';
  analyzingDiv.innerHTML = `
    <div class="ai-speech-header">
      <div class="ai-author-branding">
        <span class="ai-clover-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <circle cx="8" cy="8" r="5" fill="#1463FF"/>
            <circle cx="16" cy="8" r="5" fill="#2563EB"/>
            <circle cx="8" cy="16" r="5" fill="#3B82F6"/>
            <circle cx="16" cy="16" r="5" fill="#60A5FA"/>
          </svg>
        </span>
        <span class="ai-brand-title">Gramsehat AI</span>
      </div>
      <div class="ai-analyzing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>
    <p class="ai-speech-body ai-analyzing-text">
      ${isHindi ? "ग्रामसेहत एआई उत्तर का विश्लेषण कर रहा है..." : "GramSehat AI is evaluating your response..."}
    </p>
  `;

  chatFlow.appendChild(analyzingDiv);
  try {
    analyzingDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (e) {}
}

/**
 * Removes the analyzing indicator bubble once the response arrives.
 */
function removeAiAnalyzingBubble() {
  const el = document.getElementById('aiAnalyzingBubble');
  if (el) el.remove();
}

/**
 * Appends an AI message bubble to the cumulative conversation chat stream.
 * Preserves all previous turns in the chat view.
 */
function appendAiChatTurn(speechText, data = {}) {
  removeAiAnalyzingBubble();
  const chatFlow = document.getElementById('symptomsChatFlow');
  if (!chatFlow) return null;

  chatFlow.style.display = 'flex';

  if (!appState.chatHistory) appState.chatHistory = [];

  const isHindi = appState.voiceLang === 'hi-IN' || appState.language === 'hi';
  const turnIndex = appState.chatHistory.filter(m => m.role === 'assistant').length + 1;
  const msgId = `ai-msg-${Date.now()}-${turnIndex}`;
  const isCompleted = data.risk_assessment_status === 'completed';

  const msg = {
    id: msgId,
    role: 'assistant',
    text: speechText,
    turnIndex: turnIndex,
    isCompleted: isCompleted,
    urgencyLevel: data.urgency_level || 'border-moderate',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };

  appState.chatHistory.push(msg);

  // Remove aiSpeechText ID from any older element so IDs stay unique
  const prevAi = document.getElementById('aiSpeechText');
  if (prevAi) prevAi.removeAttribute('id');

  const cardDiv = document.createElement('div');
  cardDiv.className = 'ai-speech-glass-card chat-bubble-animate';
  cardDiv.id = msgId;

  const statusBadge = isCompleted
    ? `<span class="ai-turn-badge badge-assessed">${isHindi ? "मूल्यांकन पूर्ण • Assessed" : "Assessed"}</span>`
    : `<span class="ai-turn-badge badge-eval">${isHindi ? "जोखिम जांच • Questioning" : "Risk Question"}</span>`;

  cardDiv.innerHTML = `
    <div class="ai-speech-header">
      <div class="ai-author-branding">
        <span class="ai-clover-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <circle cx="8" cy="8" r="5" fill="#1463FF"/>
            <circle cx="16" cy="8" r="5" fill="#2563EB"/>
            <circle cx="8" cy="16" r="5" fill="#3B82F6"/>
            <circle cx="16" cy="16" r="5" fill="#60A5FA"/>
          </svg>
        </span>
        <span class="ai-brand-title">Gramsehat AI</span>
        ${statusBadge}
      </div>
      <div class="ai-header-actions">
        <button class="ai-listen-glass-pill" onclick="speakChatMessage('${msgId}')" title="Listen to this message">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
          <span>${isHindi ? "सुनें" : "Listen"}</span>
        </button>
        <button type="button" class="ai-new-query-pill" onclick="resetTriageConversation()" title="Start new question">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
          <span>${isHindi ? "नया सवाल" : "New"}</span>
        </button>
      </div>
    </div>
    <p class="ai-speech-body" id="aiSpeechText">“${escapeHtml(speechText)}”</p>
  `;

  chatFlow.appendChild(cardDiv);

  try {
    cardDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (e) {}

  return msg;
}

/**
 * Plays a specific AI message from the chat history aloud.
 */
function speakChatMessage(msgId) {
  if (sarvamTtsState.isPlaying || sarvamTtsState.isGenerating) {
    stopSarvamTTS();
    return;
  }
  const msg = (appState.chatHistory || []).find(m => m.id === msgId);
  if (!msg || !msg.text) return;
  const isHindi = appState.language === 'hi' || appState.voiceLang === 'hi-IN';
  speakWithSarvamTTS(msg.text, isHindi ? 'hi-IN' : 'en-IN');
}

function sendTranscriptToBackend(transcriptText) {
  const isHindi = appState.voiceLang === 'hi-IN' || appState.language === 'hi';
  const backendUrl = getApiEndpoint('/process-transcript');

  fetch(backendUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      transcript: transcriptText,
      language: appState.voiceLang || (isHindi ? "hi-IN" : "en-IN"),
      history: appState.conversationHistory || []
    })
  })
  .then(res => {
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return res.json();
  })
  .then(data => {
    applyClinicalAssessment(data);
  })
  .catch(err => {
    console.warn("Backend /process-transcript unreachable, applying client-side clinical triage:", err);
    applyClientSideClinicalTriage(transcriptText);
  });
}

function applyClinicalAssessment(data) {
  const isHindi = appState.language === 'hi' || appState.voiceLang === 'hi-IN';

  // Mark that a question has been asked
  appState.hasAskedQuestion = true;

  // Update conversation history for multi-turn risk stratification
  if (!appState.conversationHistory) appState.conversationHistory = [];
  appState.conversationHistory.push({ role: 'user', content: data.transcript });
  if (data.ai_response_speech) {
    appState.conversationHistory.push({ role: 'assistant', content: data.ai_response_speech });
  }

  // Append AI response bubble to the cumulative conversation chat stream
  appendAiChatTurn(data.ai_response_speech, data);

  // Update Urgency Card styling and reveal
  const urgencyCard = document.getElementById('urgencyCard');
  const isRiskInProgress = data.risk_assessment_status === 'in_progress';
  const isCriticalEmergency = data.urgency_level === 'border-urgent';

  // If risk assessment is in progress and not a critical emergency, keep urgency card hidden
  // The clarifying questions are asked purely through voice!
  if (urgencyCard) {
    if (isRiskInProgress && !isCriticalEmergency) {
      urgencyCard.style.display = 'none';
    } else {
      urgencyCard.style.display = 'block';
      urgencyCard.classList.remove('border-moderate', 'border-mild', 'border-urgent');
      urgencyCard.classList.add(data.urgency_level);
    }
  }

  // Update Severity Badge Icon
  const severityBadge = document.getElementById('severityCircleBadge');
  if (severityBadge) {
    if (data.scenario_match === 'chest' || data.urgency_level === 'border-urgent') {
      severityBadge.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
    } else if (data.scenario_match === 'fever' || data.urgency_level === 'border-mild') {
      severityBadge.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;
    } else {
      severityBadge.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>`;
    }
  }

  // Update Care Level Subtitle and Headline
  const careLevelSub = document.getElementById('careLevelSubLabel');
  if (careLevelSub) careLevelSub.textContent = data.care_level;

  const urgencyTitle = document.getElementById('urgencyTitle');
  if (urgencyTitle) urgencyTitle.textContent = data.urgency_title;

  const urgencyStatus = document.getElementById('urgencyStatusPill');
  if (urgencyStatus) {
    if (isRiskInProgress && !isCriticalEmergency) {
      urgencyStatus.textContent = isHindi ? 'जांच जारी' : 'Assessing';
    } else {
      urgencyStatus.textContent = data.urgency_level === 'border-urgent' 
        ? (isHindi ? 'अति आवश्यक' : 'Emergency') 
        : (data.urgency_level === 'border-mild' ? (isHindi ? 'सामान्य' : 'Non-emergency') : (isHindi ? 'मध्यम' : 'Moderate'));
    }
  }

  // Detail rows
  const whyMatters = document.getElementById('whyMattersText');
  if (whyMatters) whyMatters.textContent = data.why_matters;

  const whatToDo = document.getElementById('whatToDoText');
  if (whatToDo) whatToDo.textContent = data.what_to_do;

  const nearestCare = document.getElementById('nearestCareText');
  if (nearestCare) nearestCare.innerHTML = data.nearest_care;

  // Update Voice Orb Subtitle to guide the user to speak their answer into the mic
  const triageSub = document.getElementById('triageOrbSub');
  if (triageSub) {
    if (isRiskInProgress && !isCriticalEmergency) {
      triageSub.innerHTML = `<span class="orb-caption-text" style="color: #2b787a; font-weight: 700;">${
        isHindi ? '🎙️ उत्तर देने के लिए ओर्ब दबाएं (Tap Orb to Answer)' : '🎙️ Tap Orb to Answer by Voice'
      }</span>`;
      showToast(isHindi ? "माइक दबाकर सवाल का जवाब दें 🎙️" : "Please tap mic to answer by voice 🎙️");
    } else {
      triageSub.innerHTML = `<span class="orb-caption-text">${
        isHindi ? 'नया सवाल पूछने के लिए ओर्ब दबाएं' : 'Tap orb to ask another question'
      }</span>`;
    }
  }

  // Speak AI explanation or clarifying question aloud via Sarvam AI TTS (Bulbul v3)
  speakWithSarvamTTS(data.ai_response_speech, data.language);
}

function resetTriageConversation() {
  appState.conversationHistory = [];
  appState.chatHistory = [];
  appState.hasAskedQuestion = false;

  stopLiveSpeechRecognition();
  stopSarvamTTS();
  resetLiveTranscriptionDisplay();

  const chatFlow = document.getElementById('symptomsChatFlow');
  if (chatFlow) {
    chatFlow.innerHTML = '';
    chatFlow.style.display = 'none';
  }

  const urgencyCard = document.getElementById('urgencyCard');
  if (urgencyCard) urgencyCard.style.display = 'none';

  const isHindi = appState.language === 'hi' || appState.voiceLang === 'hi-IN';
  const triageSub = document.getElementById('triageOrbSub');
  if (triageSub) {
    triageSub.innerHTML = `<span class="orb-caption-text" data-i18n="tapToPause">${
      isHindi ? 'बोलने के लिए ओर्ब दबाएं (Tap to Speak)' : 'Tap orb to speak'
    }</span>`;
  }

  showToast(isHindi ? "नया सवाल पूछने के लिए तैयार" : "Ready for new question");
}

function applyClientSideClinicalTriage(transcriptText) {
  const cleanText = (transcriptText || "").trim();
  const lower = cleanText.toLowerCase();
  const isHindi = appState.language === 'hi' || appState.voiceLang === 'hi-IN';

  updateLivePatientSpeech(cleanText, false);

  let triageData = null;

  if (lower.includes('chest') || lower.includes('heart') || lower.includes('breath') || lower.includes('सीना') || lower.includes('छाती') || lower.includes('सांस')) {
    triageData = {
      scenario_match: "chest",
      urgency_level: "border-urgent",
      urgency_title: isHindi ? "आपातकालीन चिकित्सा परामर्श आवश्यक" : "Emergency Medical Care Needed",
      care_level: isHindi ? "तत्काल एम्बुलेंस 108 / नजदीकी अस्पताल" : "Immediate Emergency Care (Call 108)",
      why_matters: isHindi ? "सीने में तेज दर्द या सांस फूलना आपातकालीन स्थिति का संकेत हो सकता है।" : "Chest pressure or breathlessness requires immediate medical evaluation.",
      what_to_do: isHindi ? "मरीज को आराम से बैठाएं। तुरंत 108 पर कॉल करें।" : "Keep patient seated comfortably. Call 108 emergency ambulance now.",
      nearest_care: isHindi ? "जिला संयुक्त चिकित्सालय (DH) — 4.2 किमी" : "District Combined Hospital (DH) — 4.2 km",
      ai_response_speech: isHindi ? "कृपया तुरंत बैठ जाएं और आराम करें। सीने के लक्षणों के लिए तुरंत 108 एम्बुलेंस से संपर्क करें।" : "Please remain seated and rest. Call 108 emergency ambulance immediately for chest symptoms."
    };
  } else if (lower.includes('stomach') || lower.includes('vomit') || lower.includes('diarrhea') || lower.includes('पेट') || lower.includes('उल्टी') || lower.includes('दस्त')) {
    triageData = {
      scenario_match: "stomach_pain",
      urgency_level: "border-moderate",
      urgency_title: isHindi ? "पेट दर्द व पाचन परामर्श" : "Digestive Care Guidance",
      care_level: isHindi ? "24 घंटे में क्लिनिक परामर्श" : "Clinic Check-up within 24 Hours",
      why_matters: isHindi ? "पेट दर्द व उल्टी से शरीर में पानी की कमी और संक्रमण का खतरा रहता है।" : "Abdominal pain with vomiting can cause rapid dehydration.",
      what_to_do: isHindi ? "ओआरएस (ORS) या साफ पानी थोड़ा-थोड़ा पिएं। हल्का भोजन लें।" : "Sip ORS solution or clean fluids frequently. Eat light foods.",
      nearest_care: isHindi ? "सामुदायिक स्वास्थ्य केंद्र (CHC) मोहनलालगंज — 3.1 किमी" : "Community Health Centre (CHC) Mohanlalganj — 3.1 km",
      ai_response_speech: isHindi ? "पेट दर्द और उल्टी में शरीर में पानी की कमी न होने दें। थोड़ा-थोड़ा ओआरएस पिएं और दर्द बने रहने पर डॉक्टर को दिखाएं।" : "For stomach pain and vomiting, maintain hydration with ORS and see a doctor if pain continues."
    };
  } else if (lower.includes('headache') || lower.includes('head') || lower.includes('सिर') || lower.includes('सर दर्द')) {
    triageData = {
      scenario_match: "headache",
      urgency_level: "border-mild",
      urgency_title: isHindi ? "सिरदर्द देखभाल परामर्श" : "Headache Care Guidance",
      care_level: isHindi ? "घरेलू देखभाल व सामान्य क्लिनिक" : "Home Care & Routine Clinic",
      why_matters: isHindi ? "सिरदर्द तनाव, थकान, धूप या पानी की कमी से हो सकता है।" : "Headaches are often linked to dehydration, fatigue, or stress.",
      what_to_do: isHindi ? "शांत जगह पर आराम करें, माथे पर ठंडी पट्टी रखें और पानी पिएं।" : "Rest in a quiet room, apply a cool compress, and drink water.",
      nearest_care: isHindi ? "प्राथमिक स्वास्थ्य केंद्र (PHC) शिवपुर — 1.8 किमी" : "Primary Health Centre (PHC) Shivpur — 1.8 km",
      ai_response_speech: isHindi ? "सिरदर्द के लिए ठंडी व शांत जगह पर थोड़ा आराम करें और पानी पिएं। अगर दर्द असहनीय हो तो डॉक्टर को दिखाएं।" : "For your headache, please rest in a quiet space and drink plenty of water."
    };
  } else if (lower.includes('fever') || lower.includes('temperature') || lower.includes('बुखार') || lower.includes('ताप')) {
    triageData = {
      scenario_match: "fever",
      urgency_level: "border-mild",
      urgency_title: isHindi ? "प्राथमिक स्वास्थ्य केंद्र परामर्श" : "Primary Care Consultation Advised",
      care_level: isHindi ? "24-48 घंटे में डॉक्टर से मिलें" : "Routine Clinic Visit (Within 24-48h)",
      why_matters: isHindi ? "लगातार बुखार मौसमी संक्रमण या वायरल का संकेत हो सकता है।" : "Persistent fever indicates viral illness or seasonal infection.",
      what_to_do: isHindi ? "पर्याप्त पानी व ओआरएस पिएं, माथे पर गीली पट्टी रखें।" : "Rest well and stay hydrated with fluids and ORS.",
      nearest_care: isHindi ? "प्राथमिक स्वास्थ्य केंद्र (PHC) शिवपुर — 1.8 किमी" : "Primary Health Centre (PHC) Shivpur — 1.8 km",
      ai_response_speech: isHindi ? "बुखार के लिए पर्याप्त आराम करें और ओआरएस पिएं। यदि 48 घंटे में न उतरे तो स्वास्थ्य केंद्र जाएं।" : "For fever, rest adequately and stay hydrated. Consult a doctor if it persists beyond 48 hours."
    };
  } else if (lower.includes('cough') || lower.includes('throat') || lower.includes('cold') || lower.includes('खांसी') || lower.includes('गला') || lower.includes('जुकाम')) {
    triageData = {
      scenario_match: "cough_cold",
      urgency_level: "border-mild",
      urgency_title: isHindi ? "खांसी व जुकाम परामर्श" : "Respiratory & Cold Guidance",
      care_level: isHindi ? "सामान्य क्लिनिक परामर्श" : "Routine Clinic Consultation",
      why_matters: isHindi ? "मौसम में बदलाव से गले में खराश और खांसी आम संक्रमण है।" : "Cough and throat irritation are common during weather changes.",
      what_to_do: isHindi ? "गुनगुने नमक के पानी से गरारे करें और गर्म तरल पदार्थ पिएं।" : "Gargle with warm salt water and drink warm fluids.",
      nearest_care: isHindi ? "प्राथमिक स्वास्थ्य केंद्र (PHC) शिवपुर — 1.8 किमी" : "Primary Health Centre (PHC) Shivpur — 1.8 km",
      ai_response_speech: isHindi ? "खांसी और गले की खराश के लिए गुनगुने पानी से गरारे करें और गर्म पानी पिएं। आराम न मिलने पर डॉक्टर को दिखाएं।" : "For cough and sore throat, try warm salt-water gargles and drink warm fluids."
    };
  } else if (lower.includes('dizziness') || lower.includes('weakness') || lower.includes('चक्कर') || lower.includes('कमजोरी')) {
    triageData = {
      scenario_match: "dizziness",
      urgency_level: "border-moderate",
      urgency_title: isHindi ? "क्लिनिक जांच की सलाह" : "Clinic Visit Recommended",
      care_level: isHindi ? "24 घंटे के अंदर क्लिनिक परामर्श" : "Clinic Check-up within 24 Hours",
      why_matters: isHindi ? "कमजोरी और चक्कर खून की कमी (एनीमिया) या डिहाइड्रेशन से हो सकते हैं।" : "Weakness and dizziness can stem from low hemoglobin or dehydration.",
      what_to_do: isHindi ? "आराम से बैठें या लेटें। ओआरएस या साफ पानी पिएं। अचानक न उठें।" : "Rest in a cool spot. Drink clean water or ORS. Avoid sudden standing.",
      nearest_care: isHindi ? "सामुदायिक स्वास्थ्य केंद्र (CHC) मोहनलालगंज — 3.1 किमी" : "Community Health Centre (CHC) Mohanlalganj — 3.1 km",
      ai_response_speech: isHindi ? "आपकी कमजोरी और चक्कर के लिए पर्याप्त आराम और ओआरएस लेना जरूरी है। स्वास्थ्य केंद्र में जांच करवाएं।" : "For dizziness and weakness, please rest and drink plenty of fluids."
    };
  } else {
    triageData = {
      scenario_match: "general_health",
      urgency_level: "border-mild",
      urgency_title: isHindi ? "स्वास्थ्य मार्गदर्शन" : "General Health Guidance",
      care_level: isHindi ? "सामान्य क्लिनिक परामर्श" : "Routine Clinic Consultation",
      why_matters: isHindi ? "आपके द्वारा पूछे गए सवाल के संबंध में उचित स्वास्थ्य सावधानी आवश्यक है।" : "Your question has been noted for clinical evaluation.",
      what_to_do: isHindi ? "पर्याप्त आराम करें, पानी पिएं और आवश्यक होने पर स्वास्थ्य केंद्र में डॉक्टर से संपर्क करें।" : "Rest well, stay hydrated, and consult a doctor at your local health centre if needed.",
      nearest_care: isHindi ? "प्राथमिक स्वास्थ्य केंद्र (PHC) शिवपुर — 1.8 किमी" : "Primary Health Centre (PHC) Shivpur — 1.8 km",
      ai_response_speech: isHindi ? `नमस्ते। आपके प्रश्न के संबंध में हमने विवरण दर्ज कर लिया है। कृपया पर्याप्त आराम करें और जरूरत पड़ने पर स्वास्थ्य केंद्र पर संपर्क करें।` : `Hello. Regarding your query, please rest and contact your local health clinic if needed.`
    };
  }

  triageData.transcript = cleanText;
  triageData.language = isHindi ? 'hi-IN' : 'en-IN';
  applyClinicalAssessment(triageData);
}

function submitManualSymptom() {
  const input = document.getElementById('manualSymptomInput');
  if (!input) return;
  const val = input.value.trim();
  if (!val) {
    showToast(appState.language === 'hi' ? "कृपया लक्षण दर्ज करें" : "Please enter your symptoms");
    return;
  }
  handleFinalTranscript(val);
  input.value = '';
}

function updateOrbDisplay(isListening) {
  const isHindi = appState.language === 'hi';
  
  // Exact user requirement: SPEAK when not clicked, LISTENING when clicked
  const speakLetters = ['S', 'P', 'E', 'A', 'K'];
  const listeningLetters = ['L', 'I', 'S', 'T', 'E', 'N', 'I', 'N', 'G'];
  
  const currentLetters = isListening ? listeningLetters : speakLetters;
  const lettersHtml = currentLetters.map((letter, idx) => 
    `<span class="loader-letter" style="animation-delay: ${(idx * 0.1).toFixed(1)}s">${letter}</span>`
  ).join('');

  // Update both home and triage orbs
  ['homeVoiceOrb', 'triageVoiceOrb'].forEach(orbId => {
    const orb = document.getElementById(orbId);
    if (orb) {
      orb.classList.toggle('listening', isListening);
      orb.setAttribute('aria-label', isListening ? 'Listening. Tap to stop' : 'Tap to speak');
    }
  });

  ['homeOrbLetters', 'triageOrbLetters'].forEach(boxId => {
    const box = document.getElementById(boxId);
    if (box) {
      box.innerHTML = lettersHtml;
    }
  });

  // Update subtitle hints below orbs
  const homeSub = document.getElementById('homeOrbSub');
  if (homeSub) {
    homeSub.innerHTML = `<span class="orb-hint">${
      isListening 
        ? (isHindi ? "सुना जा रहा है... (रोकने के लिए दबाएं)" : "Listening... (Tap to finish)") 
        : (isHindi ? "बोलने के लिए ओर्ब दबाएं" : "Tap orb to speak symptoms")
    }</span>`;
  }

  const triageSub = document.getElementById('triageOrbSub');
  if (triageSub) {
    triageSub.innerHTML = `<span class="orb-caption-text">${
      isListening 
        ? (isHindi ? "आपकी आवाज़ सुनी जा रही है... (रोकने के लिए दबाएं)" : "Listening to symptoms... (Tap to finish)") 
        : (isHindi ? "बोलने या रोकने के लिए दबाएं" : "Tap to speak or pause")
    }</span>`;
  }
}

function resetVoiceTriage() {
  toggleVoiceOrb('triage');
}

function startVoiceInteraction() {
  navigateTo('screen-voice');
  startVoiceOrbListening('triage');
}

function setupSampleScenarios() {
  const pills = ['scenarioPillDizziness', 'scenarioPillFever', 'scenarioPillChest'];
  pills.forEach(id => {
    const btn = document.getElementById(id);
    if (btn) {
      btn.addEventListener('click', function() {
        pills.forEach(p => {
          const el = document.getElementById(p);
          if (el) el.classList.remove('active');
        });
        this.classList.add('active');
      });
    }
  });
}

function loadVoiceScenario(key) {
  appState.selectedScenario = key;
  const data = scenarios[key];
  if (!data) return;

  const isHindi = appState.language === 'hi';

  const liveCard = document.getElementById('liveTranscriptCard');
  if (liveCard) liveCard.style.display = 'none';

  // Toggle active segment pill
  const pillMap = {
    dizziness: 'scenarioPillDizziness',
    fever: 'scenarioPillFever',
    chest: 'scenarioPillChest'
  };
  Object.keys(pillMap).forEach(k => {
    const pill = document.getElementById(pillMap[k]);
    if (pill) {
      pill.classList.toggle('active', k === key);
    }
  });

  // Reset and populate conversation chat stream
  const chatFlow = document.getElementById('symptomsChatFlow');
  if (chatFlow) {
    chatFlow.innerHTML = '';
    chatFlow.style.display = 'flex';
  }
  appState.chatHistory = [];
  appState.conversationHistory = [];
  appendPatientChatTurn(isHindi ? data.patientSpeechHi : data.patientSpeechEn, true);
  appendAiChatTurn(isHindi ? data.aiSpeechHi : data.aiSpeechEn, {
    risk_assessment_status: 'completed',
    urgency_level: data.urgencyLevelClass
  });

  // Update Urgency Card styling class
  const urgencyCard = document.getElementById('urgencyCard');
  if (urgencyCard) {
    urgencyCard.classList.remove('border-moderate', 'border-mild', 'border-urgent');
    urgencyCard.classList.add(data.urgencyLevelClass);
  }

  // Update Severity Header Badge Icon
  const severityBadge = document.getElementById('severityCircleBadge');
  if (severityBadge) {
    if (key === 'dizziness') {
      severityBadge.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>`;
    } else if (key === 'fever') {
      severityBadge.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;
    } else if (key === 'chest') {
      severityBadge.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
    }
  }

  // Update Care Level Subtitle and Headline
  const careLevelSub = document.getElementById('careLevelSubLabel');
  if (careLevelSub) careLevelSub.textContent = isHindi ? data.careLevelSubHi : data.careLevelSubEn;

  const urgencyTitle = document.getElementById('urgencyTitle');
  if (urgencyTitle) urgencyTitle.textContent = isHindi ? data.urgencyTitleHi : data.urgencyTitleEn;

  const urgencyStatus = document.getElementById('urgencyStatusPill');
  if (urgencyStatus) urgencyStatus.textContent = isHindi ? data.urgencyStatusHi : data.urgencyStatusEn;

  // Detail rows
  const whyMatters = document.getElementById('whyMattersText');
  if (whyMatters) whyMatters.textContent = isHindi ? data.whyMattersHi : data.whyMattersEn;

  const whatToDo = document.getElementById('whatToDoText');
  if (whatToDo) whatToDo.textContent = isHindi ? data.whatToDoHi : data.whatToDoEn;

  const nearestCare = document.getElementById('nearestCareText');
  if (nearestCare) {
    const mainNear = isHindi ? data.nearestCareHi : data.nearestCareEn;
    const subNear = isHindi ? data.nearestCareSubHi : data.nearestCareSubEn;
    nearestCare.innerHTML = `${mainNear}<br><span class="duty-status-sub">${subNear}</span>`;
  }
}

// Sarvam AI Text-to-Speech (Bulbul v3) state & queue manager
const sarvamTtsState = {
  currentAudio: null,
  currentAudioUrl: null,
  isPlaying: false,
  isGenerating: false,
  queue: [],
  speaker: 'shubh' // Default voice is "shubh"; others include "priya" and "kavya"
};

/**
 * Stops any currently playing or scheduled Sarvam TTS audio immediately.
 */
function stopSarvamTTS() {
  if (sarvamTtsState.currentAudio) {
    try {
      sarvamTtsState.currentAudio.pause();
      sarvamTtsState.currentAudio.currentTime = 0;
    } catch (e) {
      console.warn("Error pausing active TTS audio:", e);
    }
    sarvamTtsState.currentAudio = null;
  }

  if (sarvamTtsState.currentAudioUrl) {
    try {
      URL.revokeObjectURL(sarvamTtsState.currentAudioUrl);
    } catch (e) {}
    sarvamTtsState.currentAudioUrl = null;
  }

  sarvamTtsState.queue = [];
  sarvamTtsState.isPlaying = false;
  sarvamTtsState.isGenerating = false;
  updateTTSPlayingUI(false);
}

function updateTTSPlayingUI(active, textLabel = null) {
  const listenBtn = document.getElementById('aiListenBtn');
  const listenText = document.getElementById('aiListenBtnText') || (listenBtn ? listenBtn.querySelector('span') : null);
  const isHindi = appState.language === 'hi' || appState.voiceLang === 'hi-IN';

  if (listenBtn) {
    listenBtn.classList.toggle('playing', active);
  }
  if (listenText) {
    if (textLabel) {
      listenText.textContent = textLabel;
    } else if (active) {
      listenText.textContent = isHindi ? "रोकें" : "Stop";
    } else {
      listenText.textContent = isHindi ? "सुनें" : "Listen";
    }
  }
}

/**
 * Splits text exceeding Sarvam's 2500 character limit at sentence boundaries
 * (supporting Hindi purna viram '।', period '.', question mark '?', exclamation '!', newlines).
 */
function splitTextIntoSentences(text, maxChars = 2400) {
  if (!text || text.length <= maxChars) {
    return text ? [text] : [];
  }

  // Regex to match complete sentences ending with Hindi purna viram (।), periods, ?, !, or newlines
  const sentencePattern = /[^।\.?!\n]+[।\.?!\n]+|\s*\n+\s*|[^।\.?!\n]+$/g;
  const rawSentences = text.match(sentencePattern) || [text];

  const chunks = [];
  let currentChunk = '';

  for (const sentence of rawSentences) {
    const trimmed = sentence.trim();
    if (!trimmed) continue;

    if (trimmed.length > maxChars) {
      // Emergency fallback for unusually long single sentences: split by words
      const words = trimmed.split(/(\s+)/);
      for (const word of words) {
        if ((currentChunk + word).length > maxChars) {
          if (currentChunk.trim()) chunks.push(currentChunk.trim());
          currentChunk = word;
        } else {
          currentChunk += word;
        }
      }
    } else if ((currentChunk + ' ' + trimmed).length > maxChars) {
      if (currentChunk.trim()) chunks.push(currentChunk.trim());
      currentChunk = trimmed;
    } else {
      currentChunk = currentChunk ? (currentChunk + ' ' + trimmed) : trimmed;
    }
  }

  if (currentChunk.trim()) {
    chunks.push(currentChunk.trim());
  }

  return chunks;
}

/**
 * Plays speech using Sarvam Bulbul v3 via the backend /api/tts proxy.
 * Handles automatic sentence chunking for long text and sequential audio playback.
 */
async function speakWithSarvamTTS(text, lang) {
  if (!text || !text.trim()) return;

  // Stop any currently playing audio before starting new audio
  stopSarvamTTS();

  const isHindi = appState.language === 'hi' || appState.voiceLang === 'hi-IN';
  const langCode = lang || (isHindi ? 'hi-IN' : 'en-IN');

  const chunks = splitTextIntoSentences(text.trim(), 2400);
  if (!chunks.length) return;

  sarvamTtsState.queue = chunks;
  await playNextTTSQueueChunk(langCode);
}

async function playNextTTSQueueChunk(langCode) {
  if (!sarvamTtsState.queue.length) {
    stopSarvamTTS();
    return;
  }

  const chunkText = sarvamTtsState.queue.shift();
  const isHindi = (langCode && langCode.startsWith('hi')) || appState.language === 'hi';

  // Loading state so UI doesn't feel frozen
  sarvamTtsState.isGenerating = true;
  updateTTSPlayingUI(true, isHindi ? "आवाज़ तैयार हो रही है..." : "Generating voice...");
  showToast(isHindi ? "सार्वम बुलबुल आवाज़ तैयार कर रहा है 🔊" : "Generating speech with Sarvam Bulbul 🔊");

  try {
    const res = await fetch(getApiEndpoint('/api/tts'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: chunkText,
        target_language_code: langCode || (isHindi ? 'hi-IN' : 'en-IN'),
        speaker: sarvamTtsState.speaker || 'shubh',
        model: 'bulbul:v3'
      })
    });

    if (res.status === 401) {
      showToast("Sarvam AI Error: Invalid API key. Check SARVAM_API_KEY.");
      stopSarvamTTS();
      return;
    } else if (res.status === 429) {
      showToast(isHindi 
        ? "सार्वम एआई व्यस्त है (दर सीमा)। कृपया कुछ क्षण बाद सुनें।" 
        : "Sarvam AI rate limit reached. Please try again shortly."
      );
      stopSarvamTTS();
      return;
    } else if (!res.ok) {
      const errText = await res.text();
      showToast(isHindi 
        ? "ऑडियो तैयार करने में समस्या आई।" 
        : "Error synthesizing speech."
      );
      console.warn("Sarvam TTS server error:", res.status, errText);
      stopSarvamTTS();
      return;
    }

    const audioBlob = await res.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    sarvamTtsState.currentAudioUrl = audioUrl;

    const audio = new Audio(audioUrl);
    sarvamTtsState.currentAudio = audio;

    audio.onplay = () => {
      sarvamTtsState.isPlaying = true;
      sarvamTtsState.isGenerating = false;
      updateTTSPlayingUI(true, isHindi ? "बोल रहा है 🔊" : "Speaking 🔊");
      showToast(isHindi ? "सार्वम बुलबुल आवाज़ चल रही है 🔊" : "Speaking (Sarvam Bulbul) 🔊");
    };

    audio.onended = () => {
      if (sarvamTtsState.currentAudioUrl) {
        URL.revokeObjectURL(sarvamTtsState.currentAudioUrl);
        sarvamTtsState.currentAudioUrl = null;
      }
      sarvamTtsState.currentAudio = null;

      // Play subsequent chunks if the original text was split (>2500 characters)
      if (sarvamTtsState.queue.length > 0) {
        playNextTTSQueueChunk(langCode);
      } else {
        stopSarvamTTS();
      }
    };

    audio.onerror = (e) => {
      console.warn("Sarvam Audio playback element error:", e);
      stopSarvamTTS();
      showToast(isHindi ? "ऑडियो चलाने में त्रुटि आई।" : "Audio playback error.");
    };

    await audio.play();
  } catch (err) {
    console.error("Sarvam TTS request failed:", err);
    stopSarvamTTS();
    showToast(isHindi ? "ऑडियो सर्वर से संपर्क नहीं हो पाया।" : "Failed to connect to audio service.");
  }
}

function playVoiceAudio() {
  // If currently speaking or generating, clicking again stops playback (tap-to-toggle)
  if (sarvamTtsState.isPlaying || sarvamTtsState.isGenerating) {
    stopSarvamTTS();
    showToast(appState.language === 'hi' ? "ऑडियो रोक दिया गया" : "Audio stopped");
    return;
  }

  const isHindi = appState.language === 'hi' || appState.voiceLang === 'hi-IN';
  let textToSpeak = "";

  if (appState.chatHistory && appState.chatHistory.length) {
    const aiMsgs = appState.chatHistory.filter(m => m.role === 'assistant');
    if (aiMsgs.length > 0) {
      textToSpeak = aiMsgs[aiMsgs.length - 1].text;
    }
  }

  if (!textToSpeak) {
    const aiText = document.getElementById('aiSpeechText');
    textToSpeak = aiText ? aiText.textContent : "";
  }

  if (!textToSpeak || textToSpeak.includes("Analyzing") || textToSpeak.includes("विश्लेषण") || textToSpeak.includes("Transcribing")) {
    const data = scenarios[appState.selectedScenario];
    if (data) {
      textToSpeak = isHindi ? data.aiSpeechHi : data.aiSpeechEn;
    }
  }

  const langCode = isHindi ? 'hi-IN' : 'en-IN';
  speakWithSarvamTTS(textToSpeak, langCode);
}

function readReportAloud() {
  if (sarvamTtsState.isPlaying || sarvamTtsState.isGenerating) {
    stopSarvamTTS();
    return;
  }
  const isHindi = appState.language === 'hi';
  const text = isHindi
    ? `रिपोर्ट निष्कर्ष: हीमोग्लोबिन 8.2 है, जो कम है। इससे आपको चक्कर और कमजोरी महसूस हो रही है। डॉक्टर से परामर्श लें।`
    : `Report Summary: Your hemoglobin is 8.2 grams per deciliter, which is below normal. This is causing fatigue and dizziness. Please consult your physician.`;
  speakWithSarvamTTS(text, isHindi ? 'hi-IN' : 'en-IN');
}

function readScreeningAloud() {
  if (sarvamTtsState.isPlaying || sarvamTtsState.isGenerating) {
    stopSarvamTTS();
    return;
  }
  const isHindi = appState.language === 'hi';
  const text = isHindi
    ? `जांच में निचली पलक में पीलापन देखा गया है। कृपया अपने नजदीकी प्राथमिक स्वास्थ्य केंद्र पर जाकर खून की जांच करवाएं।`
    : `Visual screening detected paleness in the lower eyelid. Please visit your primary health centre for confirmation.`;
  speakWithSarvamTTS(text, isHindi ? 'hi-IN' : 'en-IN');
}

function readHospitalsAloud() {
  if (sarvamTtsState.isPlaying || sarvamTtsState.isGenerating) {
    stopSarvamTTS();
    return;
  }
  const isHindi = appState.language === 'hi';
  const text = isHindi
    ? `आपके पास जिला केयर अस्पताल 4.2 किलोमीटर दूर है, जहां जनरल फिजिशियन और बिस्तर उपलब्ध हैं।`
    : `Nearest option is District Care Hospital, 4.2 kilometers away, with doctors on duty and beds available.`;
  speakWithSarvamTTS(text, isHindi ? 'hi-IN' : 'en-IN');
}


/* ==========================================================================
   SCREEN 3: REPORT EXPLAINER & UPLOAD
   ========================================================================== */
function simulateFileUpload(type) {
  const fileInput = document.getElementById('realFileInput');
  if (fileInput) {
    fileInput.click();
  }
}

function handleRealFile(event) {
  const file = event.target.files[0];
  if (file) {
    showToast(`Analyzing file: ${file.name}...`);
    setTimeout(() => {
      loadSampleReport('cbc');
      showToast("Report successfully analyzed by GRAMSEHAT AI");
    }, 1500);
  }
}

function loadSampleReport(key) {
  const pills = document.querySelectorAll('.sample-pill');
  pills.forEach((p, idx) => {
    if ((key === 'cbc' && idx === 0) || (key === 'rx' && idx === 1)) {
      p.classList.add('active');
    } else {
      p.classList.remove('active');
    }
  });

  const rep = sampleReports[key];
  if (!rep) return;

  const isHindi = appState.language === 'hi';

  document.getElementById('reportBadgeType').textContent = rep.badge;
  document.getElementById('reportDocTitle').textContent = rep.title;

  // Render Metrics
  const metricsBox = document.getElementById('reportMetricsBox');
  if (metricsBox) {
    metricsBox.innerHTML = rep.metrics.map(m => `
      <div class="metric-cell ${m.alert ? 'alert-highlight' : 'normal-highlight'}">
        <span class="metric-name">${m.name}</span>
        <span class="metric-val ${m.alert ? 'text-emergency' : 'text-success'}">${m.val}</span>
        <span class="metric-ref">${m.ref}</span>
      </div>
    `).join('');
  }

  // Render Lists
  const normalList = document.getElementById('reportNormalList');
  if (normalList) {
    const normals = isHindi ? rep.normalHi : rep.normalEn;
    normalList.innerHTML = normals.map(n => `<li>${n}</li>`).join('');
  }

  const attentionBox = document.getElementById('reportAttentionBox');
  if (attentionBox) {
    attentionBox.innerHTML = `<p class="text-sm text-dark">${isHindi ? rep.attentionHi : rep.attentionEn}</p>`;
  }

  const questionsList = document.getElementById('reportQuestionsList');
  if (questionsList) {
    const questions = isHindi ? rep.questionsHi : rep.questionsEn;
    questionsList.innerHTML = questions.map(q => `<li>${q}</li>`).join('');
  }
}

function zoomReportModal() {
  showToast("Full report laboratory scan view opened");
}


/* ==========================================================================
   SCREEN 4: IMAGE SCREENING SCREEN
   ========================================================================== */
function selectScreeningType(type) {
  appState.selectedScreening = type;

  // Toggle active class on tabs
  document.querySelectorAll('.screening-tab-btn').forEach(btn => {
    btn.classList.remove('active');
    btn.setAttribute('aria-selected', 'false');
  });

  const targetTab = document.getElementById(`tab${type.charAt(0).toUpperCase() + type.slice(1)}`);
  if (targetTab) {
    targetTab.classList.add('active');
    targetTab.setAttribute('aria-selected', 'true');
  }

  const data = screeningData[type];
  if (!data) return;

  const isHindi = appState.language === 'hi';

  // Update graphic & instruction
  const artContent = document.getElementById('artContent');
  if (artContent) {
    artContent.innerHTML = `
      ${data.artSvg}
      <span class="viewfinder-instruction-pill" id="viewfinderHint">${isHindi ? data.instructionHi : data.instructionEn}</span>
    `;
  }

  // Update Result Preview
  document.getElementById('resultTypeLabel').textContent = data.resultFocus;
  document.getElementById('resultExplanation').textContent = isHindi ? data.explanationHi : data.explanationEn;
}

function runSimulatedScreening() {
  const scanBeam = document.getElementById('scanBeam');
  const photoBtn = document.getElementById('screenPhotoBtn');

  if (scanBeam) scanBeam.classList.add('scanning');
  if (photoBtn) photoBtn.style.opacity = '0.6';

  showToast(appState.language === 'hi' ? "कैमरा स्कैन जारी है..." : "Scanning image with AI vision...");

  setTimeout(() => {
    if (scanBeam) scanBeam.classList.remove('scanning');
    if (photoBtn) photoBtn.style.opacity = '1';

    const resultCard = document.getElementById('screeningResultCard');
    if (resultCard) {
      resultCard.scrollIntoView({ behavior: 'smooth' });
    }
    showToast(appState.language === 'hi' ? "स्क्रीनिंग रिपोर्ट तैयार है" : "Screening analysis complete");
  }, 1800);
}


/* ==========================================================================
   SCREEN 5: HOSPITAL REFERRAL & LEAFLET + OPENSTREETMAP
   ========================================================================== */

const MAP_COORDINATES = {
  patient: {
    lat: 26.8520,
    lng: 80.9380,
    title: "Village Shivpur, Ward 4 (You)",
    desc: "Patient Location • GPS Live"
  },
  district: {
    lat: 26.8320,
    lng: 80.9650,
    name: "District Care Hospital",
    dist: "4.2 km • 18 min",
    type: "Govt Sub-District • Free Ayushman",
    specialist: "Dr. S. K. Verma (General Medicine)",
    beds: "14 General, 2 ICU Beds Available",
    isRecommended: true
  },
  chc: {
    lat: 26.8680,
    lng: 80.9490,
    name: "Rampur Community Health Centre (CHC)",
    dist: "2.1 km • 9 min",
    type: "Community Health Centre",
    specialist: "Dr. Anjali Patel (Medical Officer)",
    beds: "6 Daycare Beds Available",
    isRecommended: false
  },
  trust: {
    lat: 26.8850,
    lng: 80.9120,
    name: "Jeevan Jyoti Charitable Hospital",
    dist: "6.8 km • 24 min",
    type: "Trust Non-Profit Subsidized",
    specialist: "Dr. R. Raman (Internal Medicine)",
    beds: "8 General Beds Available",
    isRecommended: false
  }
};

let hospitalMap = null;
let hospitalMarkers = {};
let hospitalRouteLines = [];

function initHospitalMap() {
  const mapContainer = document.getElementById('hospitalLeafletMap');
  if (!mapContainer) return;

  if (typeof L === 'undefined') {
    setTimeout(initHospitalMap, 300);
    return;
  }

  if (hospitalMap) {
    hospitalMap.invalidateSize();
    return;
  }

  try {
    hospitalMap = L.map('hospitalLeafletMap', {
      center: [26.8520, 80.9380],
      zoom: 13,
      zoomControl: false,
      attributionControl: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'
    }).addTo(hospitalMap);

    L.control.zoom({ position: 'topright' }).addTo(hospitalMap);

    const patientIcon = L.divIcon({
      className: 'custom-patient-div-icon',
      html: `
        <div class="custom-leaflet-patient">
          <div class="patient-pin-pulse"></div>
          <div class="patient-pin-center">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="#FFFFFF"><circle cx="12" cy="8" r="4"/><path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/></svg>
          </div>
          <div class="patient-pin-label">Shivpur (You)</div>
        </div>
      `,
      iconSize: [36, 36],
      iconAnchor: [18, 18]
    });

    const createHospitalIcon = (label, dist, typeClass, isRecommended) => {
      return L.divIcon({
        className: 'custom-hospital-div-icon',
        html: `
          <div class="custom-leaflet-hospital">
            <div class="hospital-pin-bubble ${typeClass}">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            </div>
            <div class="hospital-pin-tag ${isRecommended ? 'recommended-tag' : ''}">
              <span>${label}</span>
              <span style="font-weight:800; color:${isRecommended ? '#059669' : '#1463FF'};">(${dist})</span>
            </div>
          </div>
        `,
        iconSize: [50, 52],
        iconAnchor: [25, 26]
      });
    };

    const patientCoord = [MAP_COORDINATES.patient.lat, MAP_COORDINATES.patient.lng];
    const patientMarker = L.marker(patientCoord, { icon: patientIcon }).addTo(hospitalMap);
    patientMarker.bindPopup(`
      <div class="hospital-popup-inner">
        <h4 class="hospital-popup-name">${MAP_COORDINATES.patient.title}</h4>
        <p class="hospital-popup-meta">${MAP_COORDINATES.patient.desc}</p>
      </div>
    `);
    hospitalMarkers.patient = patientMarker;

    const hospConfigs = [
      { key: 'district', label: 'District Care', dist: '4.2 km', bubble: 'district-bubble', rec: true },
      { key: 'chc', label: 'Rampur CHC', dist: '2.1 km', bubble: 'chc-bubble', rec: false },
      { key: 'trust', label: 'Jeevan Jyoti', dist: '6.8 km', bubble: 'trust-bubble', rec: false }
    ];

    hospConfigs.forEach(cfg => {
      const info = MAP_COORDINATES[cfg.key];
      const icon = createHospitalIcon(cfg.label, cfg.dist, cfg.bubble, cfg.rec);
      const marker = L.marker([info.lat, info.lng], { icon }).addTo(hospitalMap);

      const popupHtml = `
        <div class="hospital-popup-inner">
          <div class="hospital-popup-header">
            <h4 class="hospital-popup-name">${info.name}</h4>
            <span class="hospital-popup-dist">${info.dist}</span>
          </div>
          <p class="hospital-popup-meta">${info.type}</p>
          <div class="hospital-popup-beds">
            <span style="color:#059669; font-size:12px;">●</span> ${info.beds}
          </div>
          <button class="hospital-popup-btn" onclick="chooseHospitalAndAlert('${info.name}', '${cfg.dist}', '18 min')">
            Choose Hospital
          </button>
        </div>
      `;
      marker.bindPopup(popupHtml);

      marker.on('click', () => {
        highlightHospitalCard(cfg.key);
      });

      hospitalMarkers[cfg.key] = marker;
    });

    const routeToDistrict = [
      patientCoord,
      [26.8480, 80.9450],
      [26.8410, 80.9540],
      [MAP_COORDINATES.district.lat, MAP_COORDINATES.district.lng]
    ];
    const polyDistrict = L.polyline(routeToDistrict, {
      color: '#1463FF',
      weight: 3.5,
      opacity: 0.85,
      dashArray: '6, 6',
      lineJoin: 'round'
    }).addTo(hospitalMap);
    hospitalRouteLines.push(polyDistrict);

    const routeToChc = [
      patientCoord,
      [26.8590, 80.9430],
      [MAP_COORDINATES.chc.lat, MAP_COORDINATES.chc.lng]
    ];
    const polyChc = L.polyline(routeToChc, {
      color: '#64748B',
      weight: 2.5,
      opacity: 0.6,
      dashArray: '4, 4',
      lineJoin: 'round'
    }).addTo(hospitalMap);
    hospitalRouteLines.push(polyChc);

    recenterHospitalMap();

  } catch (err) {
    console.error("Error initializing Leaflet hospital map:", err);
  }
}

function recenterHospitalMap() {
  if (!hospitalMap) return;
  const bounds = L.latLngBounds([
    [MAP_COORDINATES.patient.lat, MAP_COORDINATES.patient.lng],
    [MAP_COORDINATES.district.lat, MAP_COORDINATES.district.lng],
    [MAP_COORDINATES.chc.lat, MAP_COORDINATES.chc.lng],
    [MAP_COORDINATES.trust.lat, MAP_COORDINATES.trust.lng]
  ]);
  hospitalMap.fitBounds(bounds, {
    padding: [35, 35],
    maxZoom: 14,
    animate: true
  });
}

function focusHospitalOnMap(key) {
  const coord = MAP_COORDINATES[key];
  if (!coord || !hospitalMap) return;

  highlightHospitalCard(key);

  hospitalMap.flyTo([coord.lat, coord.lng], 14, {
    duration: 0.8,
    animate: true
  });

  const marker = hospitalMarkers[key];
  if (marker) {
    marker.openPopup();
  }
}

function highlightHospitalCard(key) {
  const cardIds = ['card-district', 'card-chc', 'card-trust'];
  cardIds.forEach(id => {
    const card = document.getElementById(id);
    if (card) card.classList.remove('active-map-highlight');
  });

  const targetCard = document.getElementById(`card-${key}`);
  if (targetCard) {
    targetCard.classList.add('active-map-highlight');
    targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function filterHospitals(type) {
  const pills = document.querySelectorAll('.hospital-filter-row .filter-pill');
  pills.forEach(p => p.classList.remove('active'));
  if (window.event && window.event.target) {
    window.event.target.classList.add('active');
  }

  const cardDistrict = document.getElementById('card-district');
  const cardChc = document.getElementById('card-chc');
  const cardTrust = document.getElementById('card-trust');

  const showHosp = {
    district: true,
    chc: true,
    trust: true
  };

  if (type === 'all') {
    showHosp.district = true;
    showHosp.chc = true;
    showHosp.trust = true;
  } else if (type === 'free') {
    showHosp.district = true;
    showHosp.chc = true;
    showHosp.trust = false;
  } else if (type === 'beds') {
    showHosp.district = true;
    showHosp.chc = true;
    showHosp.trust = true;
  } else if (type === 'emergency') {
    showHosp.district = true;
    showHosp.chc = false;
    showHosp.trust = false;
  }

  // Update List Cards
  if (cardDistrict) cardDistrict.style.display = showHosp.district ? 'flex' : 'none';
  if (cardChc) cardChc.style.display = showHosp.chc ? 'flex' : 'none';
  if (cardTrust) cardTrust.style.display = showHosp.trust ? 'flex' : 'none';

  // Update Leaflet Map Markers
  if (hospitalMap) {
    ['district', 'chc', 'trust'].forEach(k => {
      const marker = hospitalMarkers[k];
      if (marker) {
        if (showHosp[k]) {
          if (!hospitalMap.hasLayer(marker)) hospitalMap.addLayer(marker);
        } else {
          if (hospitalMap.hasLayer(marker)) hospitalMap.removeLayer(marker);
        }
      }
    });
  }
}

function selectHospitalCard(key) {
  const hosp = hospitalDirectory[key];
  if (!hosp) return;
  viewHospitalModal(key);
}

function viewHospitalModal(key) {
  const hosp = hospitalDirectory[key];
  if (!hosp) return;

  const modal = document.getElementById('hospitalModal');
  const title = document.getElementById('hospitalModalTitle');
  const body = document.getElementById('hospitalModalBody');
  const chooseBtn = document.getElementById('modalChooseHospitalBtn');

  if (title) title.textContent = hosp.name;
  if (body) {
    body.innerHTML = `
      <div class="space-y-3 text-xs text-dark">
        <div class="flex justify-between border-b pb-2">
          <span class="text-muted">Distance:</span>
          <strong>${hosp.dist} (${hosp.time})</strong>
        </div>
        <div class="flex justify-between border-b pb-2">
          <span class="text-muted">Type:</span>
          <span class="text-success font-semibold">${hosp.type}</span>
        </div>
        <div class="flex justify-between border-b pb-2">
          <span class="text-muted">Specialists:</span>
          <strong>${hosp.specialist}</strong>
        </div>
        <div class="flex justify-between border-b pb-2">
          <span class="text-muted">Bed Status:</span>
          <strong class="text-success">${hosp.beds}</strong>
        </div>
        <div class="flex justify-between border-b pb-2">
          <span class="text-muted">Helpline:</span>
          <strong>${hosp.phone}</strong>
        </div>
        <div class="pt-1">
          <span class="text-muted block mb-1">Key Facilities:</span>
          <p class="bg-gray-50 p-2 rounded border border-border">${hosp.facilities}</p>
        </div>
      </div>
    `;
  }

  if (chooseBtn) {
    chooseBtn.onclick = () => {
      closeAllModals();
      chooseHospitalAndAlert(hosp.name, hosp.dist, hosp.time);
    };
  }

  if (modal) modal.classList.add('show');
}

function chooseHospitalAndAlert(hospitalName, distance, time) {
  appState.selectedHospital = hospitalName;
  const transportDest = document.getElementById('transportDestName');
  if (transportDest) transportDest.textContent = hospitalName;

  showToast(`Hospital selected: ${hospitalName}. Notifying on-duty doctor...`);

  // Move directly to Transport & Emergency Screen
  setTimeout(() => {
    navigateTo('screen-emergency');
  }, 400);
}


/* ==========================================================================
   SCREEN 6: EMERGENCY & TRANSPORT TRACKER
   ========================================================================== */
function simulateEmergencyCall(e) {
  e.preventDefault();
  showToast("Dialing Government Emergency 108 Ambulance Dispatcher...");
  setTimeout(() => {
    alert("Emergency 108 Dispatch Simulation:\n\nConnecting to District Emergency Operations Centre.\nLocation auto-shared: Shivpur Village, Ward 4.\nAmbulance #UP-32-E-1082 is assigned.");
  }, 300);
}

function alertContactFamily() {
  showToast("SMS Alert sent to Son (+91 98765-12345) & Village Health Worker (ASHA)");
}

function startEtaCountdown() {
  // Tick every 60 seconds
  setInterval(() => {
    if (appState.etaMinutes > 2) {
      appState.etaMinutes -= 1;
      const etaElem = document.getElementById('liveEtaCount');
      if (etaElem) etaElem.textContent = appState.etaMinutes;
    }
  }, 60000);
}


/* ==========================================================================
   SCREEN 7: DOCTOR PRE-ALERT PORTAL
   ========================================================================== */
function prepareDoctorArrival() {
  appState.doctorAcknowledged = true;
  const ackStatus = document.getElementById('docAckStatus');
  if (ackStatus) {
    ackStatus.innerHTML = `
      <span class="text-xs font-bold text-success flex items-center gap-1">
        ✓ Bed #04 Reserved • Triage Orders Placed
      </span>
    `;
  }
  showToast("Doctor orders generated: STAT IV Access, CBC recheck & Oxygen standby");
}

function openFullDossierModal() {
  const modal = document.getElementById('doctorModal');
  if (modal) modal.classList.add('show');
}


/* ==========================================================================
   MODAL CONTROLLERS & TOAST
   ========================================================================== */
function showHelpModal() {
  const modal = document.getElementById('helpModal');
  if (modal) modal.classList.add('show');
}

function showProfileModal() {
  const modal = document.getElementById('profileModal');
  if (modal) modal.classList.add('show');
}

function showNotificationsModal() {
  const modal = document.getElementById('notificationsModal');
  if (modal) modal.classList.add('show');
}

function clearNotificationBadge() {
  const badge = document.getElementById('headerBellBadge');
  if (badge) {
    badge.style.display = 'none';
  }
  const msg = currentLang === 'hi' ? 'सभी सूचनाएं पढ़ी गईं' : 'All notifications marked as read';
  showToast(msg);
  closeAllModals();
}

function closeAllModals(e) {
  if (e && e.target && e.target.classList.contains('modal-card')) return;
  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.classList.remove('show');
  });
}

function showToast(message) {
  const toast = document.getElementById('toastNotification');
  const content = document.getElementById('toastContent');
  if (!toast || !content) return;

  content.textContent = message;
  toast.classList.add('show');

  if (window.toastTimeout) clearTimeout(window.toastTimeout);
  window.toastTimeout = setTimeout(() => {
    toast.classList.remove('show');
  }, 3200);
}


/* ==========================================================================
   WATERMELON UI AUTH-01 LOGIN ENGINE (PATIENT & HOSPITAL)
   ========================================================================== */
let currentAuthRole = 'patient';
let isArtworkPeek = false;

function switchAuthRole(role) {
  currentAuthRole = role;
  const patientBtn = document.getElementById('rolePatientBtn');
  const hospitalBtn = document.getElementById('roleHospitalBtn');
  const title = document.getElementById('auth1Title');
  const subtitle = document.getElementById('auth1Subtitle');
  const idInput = document.getElementById('auth1Identifier');
  const idIcon = document.getElementById('auth1IdIcon');
  const passInput = document.getElementById('auth1Password');
  const submitBtn = document.getElementById('auth1SubmitBtn');
  const dividerText = document.getElementById('auth1DividerText');
  const socialGrid = document.getElementById('auth1SocialGrid');
  const footerPrompt = document.getElementById('auth1FooterPrompt');
  const footerLink = document.getElementById('auth1FooterLink');
  const forgotText = document.getElementById('authForgotText');

  if (role === 'patient') {
    if (patientBtn) {
      patientBtn.classList.add('active');
      patientBtn.setAttribute('aria-selected', 'true');
    }
    if (hospitalBtn) {
      hospitalBtn.classList.remove('active');
      hospitalBtn.setAttribute('aria-selected', 'false');
    }
    if (title) title.textContent = "Welcome to GRAMSEHAT";
    if (subtitle) subtitle.textContent = "Speak symptoms in your dialect & access village records";
    if (idIcon) {
      idIcon.innerHTML = `<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>`;
    }
    if (idInput) {
      idInput.placeholder = "Mobile Number / ABHA Health ID";
      idInput.type = "text";
      idInput.value = "98765 43210";
    }
    if (passInput) {
      passInput.placeholder = "4-Digit Health PIN / OTP";
      passInput.value = "4321";
    }
    if (forgotText) forgotText.textContent = "Forgot PIN?";
    if (submitBtn) {
      submitBtn.innerHTML = `<span>Sign in as Patient</span><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m9 18 6-6-6-6"/></svg>`;
    }
    if (dividerText) dividerText.textContent = "or instant rural health access";
    if (socialGrid) {
      socialGrid.innerHTML = `
        <button type="button" class="auth1-social-btn" onclick="quickAuthLogin('abha')" title="Ayushman Bharat Health Account">
          <div class="auth1-social-icon-box">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect width="20" height="14" x="2" y="5" rx="2"/><circle cx="8" cy="12" r="2.2"/><path d="M13 10h5M13 14h3"/></svg>
          </div>
          <div class="auth1-social-col">
            <span class="auth1-social-sub">Login with</span>
            <span class="auth1-social-main">ABHA</span>
          </div>
        </button>
        <button type="button" class="auth1-social-btn" onclick="quickAuthLogin('aadhaar')" title="Aadhaar Linked OTP">
          <div class="auth1-social-icon-box">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="7" r="3" fill="#EA580C"/>
              <path d="M5 21c0-4.5 3.5-7.5 7-7.5s7 3 7 7.5" stroke="#DC2626" stroke-width="1.8" stroke-linecap="round"/>
              <path d="M8 21c0-3 2-5 4-5s4 2 4 5" stroke="#F97316" stroke-width="1.8" stroke-linecap="round"/>
              <path d="M11 21c0-1.2.5-2.2 1-2.2s1 1 1 2.2" stroke="#EA580C" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="auth1-social-col">
            <span class="auth1-social-sub">Login with</span>
            <span class="auth1-social-main">Aadhaar</span>
          </div>
        </button>
        <button type="button" class="auth1-social-btn" onclick="quickAuthLogin('asha')" title="ASHA Worker Login Assistance">
          <div class="auth1-social-icon-box">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </div>
          <div class="auth1-social-col">
            <span class="auth1-social-sub">Identify as</span>
            <span class="auth1-social-main">ASHA</span>
          </div>
        </button>
      `;
    }
    if (footerPrompt) footerPrompt.textContent = "New to GramSehat?";
    if (footerLink) footerLink.textContent = "Create free ABHA card";

    showToast("Switched to Patient Login Mode");
  } else {
    // Hospital Role
    if (patientBtn) {
      patientBtn.classList.remove('active');
      patientBtn.setAttribute('aria-selected', 'false');
    }
    if (hospitalBtn) {
      hospitalBtn.classList.add('active');
      hospitalBtn.setAttribute('aria-selected', 'true');
    }
    if (title) title.textContent = "Hospital & Doctor Portal";
    if (subtitle) subtitle.textContent = "Pre-alert emergency triage, duty roster & verified bed coordination";
    if (idIcon) {
      idIcon.innerHTML = `<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2z"/><path d="M12 7v10M7 12h10"/>`;
    }
    if (idInput) {
      idInput.placeholder = "Hospital Email / Doctor Reg. No.";
      idInput.type = "email";
      idInput.value = "dr.priya@districthealth.gov.in";
    }
    if (passInput) {
      passInput.placeholder = "Clinical Security Password";
      passInput.value = "Hospital@2026";
    }
    if (forgotText) forgotText.textContent = "Forgot Password?";
    if (submitBtn) {
      submitBtn.innerHTML = `<span>Access Clinical Dashboard</span><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m9 18 6-6-6-6"/></svg>`;
    }
    if (dividerText) dividerText.textContent = "or hospital health federation";
    if (socialGrid) {
      socialGrid.innerHTML = `
        <button type="button" class="auth1-social-btn" onclick="quickAuthLogin('ndhm')" title="National Digital Health Mission">
          <div class="auth1-social-icon-box">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
          </div>
          <div class="auth1-social-col">
            <span class="auth1-social-sub">Access</span>
            <span class="auth1-social-main">NDHM</span>
          </div>
        </button>
        <button type="button" class="auth1-social-btn" onclick="quickAuthLogin('pmjay')" title="PM-JAY Empanelled Network">
          <div class="auth1-social-icon-box">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v8M8 12h8"/></svg>
          </div>
          <div class="auth1-social-col">
            <span class="auth1-social-sub">Verify</span>
            <span class="auth1-social-main">PM-JAY</span>
          </div>
        </button>
        <button type="button" class="auth1-social-btn" onclick="quickAuthLogin('108ems')" title="108 Emergency Medical Services">
          <div class="auth1-social-icon-box">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="16" height="10" x="1" y="7" rx="1"/><path d="M17 11l4 2v4h-4z"/></svg>
          </div>
          <div class="auth1-social-col">
            <span class="auth1-social-sub">Fleet</span>
            <span class="auth1-social-main">108 EMS</span>
          </div>
        </button>
      `;
    }
    if (footerPrompt) footerPrompt.textContent = "Facility not registered?";
    if (footerLink) footerLink.textContent = "Empanel your hospital";

    showToast("Switched to Hospital / Doctor Portal Mode");
  }
}

function handleAuthSubmit(e) {
  e.preventDefault();
  if (currentAuthRole === 'patient') {
    showToast("✓ Authenticated! Welcome Ramlal Sharma (Village Shivpur)");
    setTimeout(() => {
      navigateTo('screen-home');
    }, 450);
  } else {
    showToast("✓ Doctor Verified: Dr. Priya Sharma (District Care Hospital)");
    setTimeout(() => {
      navigateTo('screen-doctor');
    }, 450);
  }
}

function toggleAuthPasswordVisibility() {
  const passInput = document.getElementById('auth1Password');
  const eyeIcon = document.getElementById('authEyeIcon');
  if (!passInput || !eyeIcon) return;

  const isPassword = passInput.type === 'password';
  passInput.type = isPassword ? 'text' : 'password';

  if (isPassword) {
    // Show closed eye (visible now)
    eyeIcon.innerHTML = `<path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/>`;
  } else {
    // Show open eye
    eyeIcon.innerHTML = `<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>`;
  }
}

function toggleArtworkPeek() {
  isArtworkPeek = !isArtworkPeek;
  const overlay = document.getElementById('authScreenOverlay');
  const box = document.getElementById('auth1ContentBox');
  const btnText = document.getElementById('peekBtnText');
  const screenLogin = document.getElementById('screen-login');

  if (screenLogin) screenLogin.classList.toggle('peek-mode', isArtworkPeek);
  if (overlay) overlay.classList.toggle('peek-mode', isArtworkPeek);
  if (box) box.classList.toggle('hidden-for-peek', isArtworkPeek);
  if (btnText) btnText.textContent = isArtworkPeek ? "Show Login Card" : "Peek 9:16 Journey Art";
}

function quickAuthLogin(provider) {
  const providerNames = {
    abha: "Ayushman Bharat ABHA ID",
    aadhaar: "Aadhaar e-KYC Verification",
    asha: "ASHA Worker Assisted Login",
    ndhm: "National Digital Health Mission (NDHM)",
    pmjay: "PM-JAY Hospital Staff Token",
    '108ems': "108 State Ambulance Gateway"
  };

  const name = providerNames[provider] || provider;
  showToast(`Authenticating via ${name}...`);

  setTimeout(() => {
    if (currentAuthRole === 'patient') {
      showToast(`✓ Verified via ${name} • Entering Patient Health Portal`);
      navigateTo('screen-home');
    } else {
      showToast(`✓ Provider Token Approved • Entering Emergency Pre-Alert`);
      navigateTo('screen-doctor');
    }
  }, 600);
}

function handleForgotPassword() {
  if (currentAuthRole === 'patient') {
    showToast("OTP sent to registered mobile (+91 98765-XXXXX) for instant reset.");
  } else {
    showToast("Password reset link dispatched to authorized institutional email.");
  }
}

function handleNewAccountClick() {
  if (currentAuthRole === 'patient') {
    showToast("Launching free Government ABHA Health Account registration portal...");
    setTimeout(() => {
      showHelpModal();
    }, 400);
  } else {
    showToast("Facility onboarding: Connecting to District Health Authority registry...");
  }
}

function logoutUser() {
  showToast("Logged out • Returning to Login Portal");
  setTimeout(() => {
    navigateTo('screen-login');
  }, 350);
}
