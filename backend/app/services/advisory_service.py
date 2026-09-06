"""
Personalized Agronomic Advisory Engine & Multilingual Translation System for KrushiRakshak.
Generates localized, crop-specific, and climate-risk-connected advisories based on
farm context, soil properties, atmospheric telemetry, and AI risk prediction scores.
Supports: English (en), Marathi (mr), Hindi (hi), and Kannada (kn).
"""

from typing import Dict, Any, List, Optional
import math


SUPPORTED_LANGUAGES = ["en", "mr", "hi", "kn"]

# ---------------------------------------------------------------------------
# Controlled Translation Dictionaries for System Labels & Urgencies
# ---------------------------------------------------------------------------

URGENCY_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "CRITICAL": {
        "en": "CRITICAL",
        "mr": "अति तातडीचे",
        "hi": "अत्यंत गंभीर",
        "kn": "ಅತ್ಯಂತ ತುರ್ತು",
    },
    "HIGH": {
        "en": "HIGH",
        "mr": "उच्च",
        "hi": "उच्च",
        "kn": "ಹೆಚ್ಚಿನ",
    },
    "MEDIUM": {
        "en": "MODERATE",
        "mr": "मध्यम",
        "hi": "मध्यम",
        "kn": "ಮಧ್ಯಮ",
    },
    "LOW": {
        "en": "LOW / ROUTINE",
        "mr": "कमी / नियमित",
        "hi": "कम / सामान्य",
        "kn": "ಕಡಿಮೆ / ನಿಯಮಿತ",
    },
}

TIME_WINDOW_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "IMMEDIATE": {
        "en": "Immediate (Within 6–12 hours)",
        "mr": "तातडीने (पुढील ६ ते १२ तासांत)",
        "hi": "तत्काल (अगले ६ से १२ घंटों में)",
        "kn": "ತಕ್ಷಣ (ಮುಂದಿನ ೬-೧೨ ಗಂಟೆಗಳಲ್ಲಿ)",
    },
    "SHORT_TERM": {
        "en": "Next 24–48 hours",
        "mr": "पुढील २४ ते ४८ तासांत",
        "hi": "अगले २४ से ४८ घंटों में",
        "kn": "ಮುಂದಿನ ೨೪-೪೮ ಗಂಟೆಗಳಲ್ಲಿ",
    },
    "MEDIUM_TERM": {
        "en": "Next 2–4 days",
        "mr": "पुढील २ ते ४ दिवसांत",
        "hi": "अगले २ से ४ दिनों में",
        "kn": "ಮುಂದಿನ ೨-೪ ದಿನಗಳಲ್ಲಿ",
    },
    "ROUTINE": {
        "en": "Routine Monitoring (Next 5–7 days)",
        "mr": "नियमित निरीक्षण (पुढील ५ ते ७ दिवसांत)",
        "hi": "नियमित निगरानी (अगले ५ से ७ दिनों में)",
        "kn": "ನಿಯಮಿತ ಮೇಲ್ವಿಚಾರಣೆ (ಮುಂದಿನ ೫-೭ ದಿನಗಳಲ್ಲಿ)",
    },
}

RISK_NAMES: Dict[str, Dict[str, str]] = {
    "drought": {
        "en": "Drought & Moisture Stress",
        "mr": "दुष्काळ आणि ओलावा टंचाई",
        "hi": "सूखा और नमी की कमी",
        "kn": "ಬರ ಮತ್ತು ತೇವಾಂಶ ಕೊರತೆ",
    },
    "flood": {
        "en": "Flood & Waterlogging",
        "mr": "पूर आणि पाणी साचणे",
        "hi": "बाढ़ और जलभराव",
        "kn": "ಪ್ರವಾಹ ಮತ್ತು ನೀರು ನಿಲ್ಲುವಿಕೆ",
    },
    "heat": {
        "en": "Severe Heat Stress",
        "mr": "तीव्र उष्णतेचा ताण",
        "hi": "तीव्र ऊष्मा तनाव",
        "kn": "ತೀವ್ರ ಶಾಖದ ಒತ್ತಡ",
    },
    "extreme_rainfall": {
        "en": "Extreme Rainfall & Storm Inundation",
        "mr": "अतिवृष्टी आणि वादळी पाऊस",
        "hi": "अतिवृष्टि और मूसलाधार बारिश",
        "kn": "ಅತಿಯಾದ ಮಳೆ ಮತ್ತು ಚಂಡಮಾರುತ",
    },
}

CROP_NAMES: Dict[str, Dict[str, str]] = {
    "cotton": {"en": "Cotton", "mr": "कापूस", "hi": "कपास", "kn": "ಹತ್ತಿ"},
    "soybean": {"en": "Soybean", "mr": "सोयाबीन", "hi": "सोयाबीन", "kn": "ಸೋಯಾಬೀನ್"},
    "wheat": {"en": "Wheat", "mr": "गहू", "hi": "गेहूं", "kn": "ಗೋಧಿ"},
    "paddy": {"en": "Paddy / Rice", "mr": "भात / धान", "hi": "धान / चावल", "kn": "ಭತ್ತ"},
    "maize": {"en": "Maize / Corn", "mr": "मका", "hi": "मक्का", "kn": "ಮೆಕ್ಕೆಜೋಳ"},
    "sugarcane": {"en": "Sugarcane", "mr": "ऊस", "hi": "गन्ना", "kn": "ಕಬ್ಬು"},
    "pulses": {"en": "Pulses / Gram", "mr": "हरभरा / डाळी", "hi": "चना / दलहन", "kn": "ಬೇಳೆಕಾಳು / ಕಡಲೆ"},
    "vegetables": {"en": "Vegetables", "mr": "भाजीपाला", "hi": "सब्जियां", "kn": "ತರಕಾರಿಗಳು"},
    "general": {"en": "Standing Crop", "mr": "उभे पीक", "hi": "खड़ी फसल", "kn": "ಬೆಳೆ"},
}


def normalize_crop_key(crop: Optional[str]) -> str:
    if not crop:
        return "general"
    c = crop.lower().strip()
    if "cotton" in c or "kapas" in c:
        return "cotton"
    if "soy" in c:
        return "soybean"
    if "wheat" in c or "gehun" in c or "gahu" in c:
        return "wheat"
    if "paddy" in c or "rice" in c or "dhan" in c or "bhat" in c:
        return "paddy"
    if "maize" in c or "corn" in c or "maka" in c:
        return "maize"
    if "sugar" in c or "cane" in c or "oos" in c:
        return "sugarcane"
    if "gram" in c or "pulse" in c or "chickpea" in c or "harbhara" in c or "dal" in c:
        return "pulses"
    if "veg" in c or "tomato" in c or "onion" in c or "chilli" in c:
        return "vegetables"
    return "general"


def normalize_risk_key(risk_type: Optional[str]) -> str:
    if not risk_type:
        return "drought"
    r = risk_type.lower().strip()
    if "drought" in r:
        return "drought"
    if "extreme" in r or "storm" in r:
        return "extreme_rainfall"
    if "flood" in r or "inundat" in r or "heavy" in r:
        return "flood"
    if "heat" in r or "temp" in r or "thermal" in r:
        return "heat"
    return "drought"


# ---------------------------------------------------------------------------
# Agronomic Knowledge Base & Recommendation Templates
# ---------------------------------------------------------------------------

AGRONOMIC_KNOWLEDGE_BASE: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {
    # -----------------------------------------------------------------------
    # 1. SOYBEAN
    # -----------------------------------------------------------------------
    "soybean": {
        "drought": {
            "title": {
                "en": "Critical Drought & Moisture Deficit Advisory for Soybean",
                "mr": "सोयाबीन पिकासाठी दुष्काळ आणि ओलावा टंचाई तातडीचा सल्ला",
                "hi": "सोयाबीन फसल के लिए सूखा और गंभीर नमी संकट परामर्श",
                "kn": "ಸೋಯಾಬೀನ್ ಬೆಳೆಗೆ ಬರ ಮತ್ತು ತೇವಾಂಶ ಕೊರತೆಯ ತುರ್ತು ಸಲಹೆ",
            },
            "recommendations": {
                "en": [
                    "Apply protective micro-irrigation or sprinkler watering during critical flowering and pod-filling stages to prevent flower abortion.",
                    "Foliar spray with 2% Urea or 1% Potassium Nitrate (13:0:45) to enhance crop resilience against severe thermal and moisture stress.",
                    "Halt inter-cultivation or weeding immediately to avoid soil disturbance and prevent rapid sub-surface moisture evaporation.",
                    "Utilize organic straw mulch or crop residue (3-5 tonnes/ha) between rows to reduce root-zone evapotranspiration."
                ],
                "mr": [
                    "फुलोरा आणि शेंगा भरण्याच्या नाजूक टप्प्यावर संरक्षित ठिबक किंवा तुषार सिंचनाने पाणी द्या, जेणेकरून फुलगळ थांबेल.",
                    "उष्णता आणि पाण्याचा ताण सहन करण्यासाठी १% पोटॅशियम नायट्रेट (१३:०:४५) किंवा २% युरियाची फवारणी करा.",
                    "जमिनीतील ओलावा टिकवून ठेवण्यासाठी मशागत किंवा कोळपणी तात्पुरती थांबवा, ज्यामुळे जमिनीतील ओल उडून जाणार नाही.",
                    "दोन ओळींमधील जागेत सोयाबीनचे भुसकट किंवा गवताचे आच्छादन (मल्चिंग) करून बाष्पीभवन रोखा."
                ],
                "hi": [
                    "फूल आने और फलियां बनते समय जीवन रक्षक फव्वारा या ड्रिप सिंचाई अवश्य करें ताकि फूलों को झड़ने से रोका जा सके।",
                    "सूखे और गर्मी के प्रभाव को कम करने के लिए फसल पर १% पोटेशियम नाइट्रेट (१३:०:४५) या २% यूरिया का छिड़काव करें।",
                    "मिट्टी से नमी का वाष्पीकरण रोकने के लिए निराई-गुड़ाई का कार्य तत्काल रोक दें।",
                    "पंक्तियों के बीच पुआल या फसल अवशेषों की पलवार (मल्चिंग) बिछाकर जमीन की नमी सुरक्षित रखें।"
                ],
                "kn": [
                    "ಹೂವಾಡುವ ಮತ್ತು ಕಾಯಿ ಕಟ್ಟುವ ಸೂಕ್ಷ್ಮ ಹಂತದಲ್ಲಿ ಹನಿ ಅಥವಾ ತುಂತುರು ನೀರಾವರಿ ಮೂಲಕ ರಕ್ಷಣಾತ್ಮಕ ನೀರು ಒದಗಿಸಿ.",
                    "ಬರ ಮತ್ತು ಶಾಖದ ಒತ್ತಡ ತಡೆದುಕೊಳ್ಳಲು ಶೇ ೧ ರ ಪೊಟ್ಯಾಸಿಯಮ್ ನೈಟ್ರೇಟ್ (೧೩:೦:೪೫) ಸಿಂಪಡಣೆ ಮಾಡಿ.",
                    "ಮಣ್ಣಿನಲ್ಲಿರುವ ತೇವಾಂಶ ಆವಿಯಾಗುವುದನ್ನು ತಡೆಯಲು ಎಡೆಕುಂಟೆ ಹೊಡೆಯುವುದನ್ನು ಮತ್ತು ಕಳೆ ಕೀಳುವುದನ್ನು ತಕ್ಷಣ ನಿಲ್ಲಿಸಿ.",
                    "ಸಾಲುಗಳ ನಡುವೆ ಒಣ ಹುಲ್ಲು ಅಥವಾ ಕೃಷಿ ತ್ಯಾಜ್ಯದಿಂದ ಹೊದಿಕೆ (ಮಲ್ಚಿಂಗ್) ಮಾಡಿ ತೇವಾಂಶ ಸಂರಕ್ಷಿಸಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Construct farm contour bunds to intercept any unexpected light shower runoff.",
                    "Ensure drip irrigation lines are flushed and running at minimum 80% distribution uniformity.",
                    "Avoid high-nitrogen fertilizer top-dressing which increases leaf vegetative water demand."
                ],
                "mr": [
                    "अचानक येणाऱ्या पावसाचे पाणी शेतातच अडवण्यासाठी समपातळी बांध घाला.",
                    "ठिबक सिंचन नलिका स्वच्छ करून पाण्याचे योग्य नियोजन करा.",
                    "नत्राचा अतिवापर टाळा, ज्यामुळे पिकांची पाण्याची गरज अनावश्यक वाढत नाही."
                ],
                "hi": [
                    "वर्षा जल संचयन के लिए खेत की मेड़ों को मजबूत बनाएं।",
                    "ड्रिप या फव्वारा प्रणाली की सफाई करके पानी का समान वितरण सुनिश्चित करें।",
                    "अधिक नाइट्रोजन वाले उर्वरक न डालें, इससे पौधे की पानी की खपत बढ़ती है।"
                ],
                "kn": [
                    "ಬೀಳುವ ಅಲ್ಪ ಮಳೆಯ ನೀರನ್ನು ಸಂರಕ್ಷಿಸಲು ಜಮೀನಿನಲ್ಲಿ ಬದುಗಳನ್ನು ನಿರ್ಮಿಸಿ.",
                    "ಹನಿ ನೀರಾವರಿ ಪೈಪ್‌ಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ ಸಮರ್ಪಕ ನೀರು ಹರಿಯುವಂತೆ ನೋಡಿಕೊಳ್ಳಿ.",
                    "ಹೆಚ್ಚು ಸಾರಜನಕ ಗೊಬ್ಬರ ಹಾಕಬೇಡಿ, ಇದು ಸಸ್ಯಗಳ ನೀರಿನ ಬೇಡಿಕೆಯನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ."
                ]
            }
        },
        "flood": {
            "title": {
                "en": "Waterlogging & Inundation Drainage Advisory for Soybean",
                "mr": "सोयाबीन पिकासाठी पाणी साचणे आणि निचरा व्यवस्थापन तातडीचा सल्ला",
                "hi": "सोयाबीन फसल के लिए जलभराव और जल निकासी प्रबंधन परामर्श",
                "kn": "ಸೋಯಾಬೀನ್ ಬೆಳೆಯಲ್ಲಿ ನೀರು ನಿಲ್ಲುವಿಕೆ ಮತ್ತು ಬಸಿದು ಹೋಗುವ ವ್ಯವಸ್ಥೆಯ ತುರ್ತು ಸಲಹೆ",
            },
            "recommendations": {
                "en": [
                    "Immediately create dead furrows every 3 to 4 rows to drain stagnant surface water out within 12–24 hours.",
                    "Post-drainage, spray 1% Urea + 0.5% micronutrient mixture to counteract root hypoxia and yellowing.",
                    "Postpone all chemical spraying and top-dressing until standing water is completely evacuated."
                ],
                "mr": [
                    "शेतात साचलेले पाणी १२ ते २४ तासांत बाहेर काढण्यासाठी ३ ते ४ ओळींनंतर चर किंवा दांड काढा.",
                    "पाण्याचा निचरा झाल्यानंतर मुळांना प्राणवायू मिळण्यासाठी आणि पिवळेपणा घालवण्यासाठी १% युरिया फवारा.",
                    "शेतातील पाणी पूर्णपणे निघून जाईपर्यंत खते देणे किंवा कीटकनाशक फवारणी थांबवा."
                ],
                "hi": [
                    "खेत में रुके हुए पानी को १२ से २४ घंटे के भीतर बाहर निकालने के लिए तुरंत ३-४ पंक्तियों के बाद जल निकास नालियां बनाएं।",
                    "पानी निकलने के बाद जड़ों के दम घुटने और पत्तियों के पीलेपन से बचाव हेतु १% यूरिया का छिड़काव करें।",
                    "जब तक खेत से पानी पूरी तरह न निकल जाए, तब तक उर्वरक और कीटनाशकों का प्रयोग स्थगित रखें।"
                ],
                "kn": [
                    "ಜಮೀನಿನಲ್ಲಿ ನಿಂತ ನೀರನ್ನು ೧೨-೨೪ ಗಂಟೆಗಳೊಳಗೆ ಹೊರಹಾಕಲು ಪ್ರತಿ ೩-೪ ಸಾಲುಗಳ ನಂತರ ಬಸಿಗಾಲುವೆಗಳನ್ನು ನಿರ್ಮಿಸಿ.",
                    "ನೀರು ಬಸಿದು ಹೋದ ನಂತರ ಎಲೆಗಳು ಹಳದಿಯಾಗುವುದನ್ನು ತಡೆಯಲು ಶೇ ೧ ರ ಯೂರಿಯಾ ಸಿಂಪಡಣೆ ಮಾಡಿ.",
                    "ಜಮೀನಿನಲ್ಲಿ ನಿಂತ ನೀರು ಸಂಪೂರ್ಣ ಹೊರಹೋಗುವವರೆಗೆ ಯಾವುದೇ ರಾಸಾಯನಿಕ ಸಿಂಪಡಣೆ ಮಾಡಬೇಡಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Clear field outlet channels towards natural drains.",
                    "Monitor for collar rot (Rhizoctonia solani) and Phytophthora root rot after heavy inundation.",
                    "Prepare Broad Bed Furrow (BBF) systems for future crop cycles."
                ],
                "mr": [
                    "शेतातील पाणी नैसर्गिक नाल्याकडे वाहून जाण्यासाठी मुख्य चर स्वच्छ करा.",
                    "पाणी ओसरल्यानंतर खोडकुज आणि मूळकुज रोगांचा प्रादुर्भाव तपासण्यासाठी निरीक्षण करा.",
                    "पुढील हंगामासाठी रुंद वरंबा-सरी (BBF) पद्धतीचा अवलंब करा."
                ],
                "hi": [
                    "खेत के मुख्य निकास द्वार से खरपतवार हटाकर पानी का बहाव सुगम करें।",
                    "पानी हटने के बाद तना गलन और जड़ गलन रोगों की रोकथाम के लिए निगरानी रखें।",
                    "आगामी फसल में ब्रॉड बेड फरो (BBF) तकनीक अपनाएं।"
                ],
                "kn": [
                    "ಜಮೀನಿನಿಂದ ನೀರು ಸರಾಗವಾಗಿ ಹರಿಯುವಂತೆ ಮುಖ್ಯ ನಾಲೆಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ.",
                    "ನೀರು ಇಳಿದ ನಂತರ ಬೇರು ಕೊಳೆ ರೋಗ ಮತ್ತು ಕಾಂಡ ಕೊಳೆ ರೋಗದ ಲಕ್ಷಣಗಳನ್ನು ಪರೀಕ್ಷಿಸಿ.",
                    "ಮುಂದಿನ ಬೆಳೆಗಾಗಿ ಅಗಲವಾದ ಏರುಮಡಿ ಸಾಲು (BBF) ಪದ್ಧತಿ ಅಳವಡಿಸಿಕೊಳ್ಳಿ."
                ]
            }
        },
        "heat": {
            "title": {
                "en": "Thermal Stress & High Temperature Advisory for Soybean",
                "mr": "सोयाबीन पिकासाठी उष्णतेचा ताण आणि तापमान संरक्षण सल्ला",
                "hi": "सोयाबीन फसल के लिए उच्च तापमान और थर्मल तनाव सुरक्षा परामर्श",
                "kn": "ಸೋಯಾಬೀನ್ ಬೆಳೆಗೆ ಅತಿಯಾದ ಶಾಖದ ಒತ್ತಡ ನಿರ್ವಹಣಾ ಸಲಹೆ",
            },
            "recommendations": {
                "en": [
                    "Provide light evening sprinkler irrigation to reduce canopy microclimate temperatures by 2–4°C.",
                    "Spray 0.5% Potassium Chloride or 1% Salicylic acid solution to reduce transpirational shock.",
                    "Refrain from applying herbicides during peak daylight hours (11 AM to 4 PM)."
                ],
                "mr": [
                    "पिकांचे तापमान २ ते ४ अंशांनी कमी करण्यासाठी संध्याकाळच्या वेळी तुषार सिंचनाने हलके पाणी द्या.",
                    "पानाचा बाष्पोत्सर्जन वेग कमी करण्यासाठी ०.५% पोटॅशियम क्लोराईड किंवा सॅलिसिलिक आम्ल फवारा.",
                    "सकाळी ११ ते दुपारी ४ या वेळेत तणनाशकांची फवारणी करू नका."
                ],
                "hi": [
                    "फसल का तापमान कम करने के लिए शाम के समय हल्की फव्वारा सिंचाई करें।",
                    "पत्तियों से पानी की हानि रोकने के लिए ०.५% पोटैशियम क्लोराइड का छिड़काव करें।",
                    "दोपहर ११ से ४ बजे के बीच खरपतवारनाशी का छिड़काव बिल्कुल न करें।"
                ],
                "kn": [
                    "ಬೆಳೆಯ ತಾಪಮಾನ ಕಡಿಮೆ ಮಾಡಲು ಸಂಜೆಯ ವೇಳೆ ತುಂತುರು ನೀರಾವರಿ ಮೂಲಕ ಹಗುರ ನೀರು ಹಾಯಿಸಿ.",
                    "ಅತಿಯಾದ ನೀರು ಆವಿಯಾಗುವುದನ್ನು ತಡೆಯಲು ಶೇ ೦.೫ ರ ಪೊಟ್ಯಾಸಿಯಮ್ ಕ್ಲೋರೈಡ್ ಸಿಂಪಡಿಸಿ.",
                    "ಬೆಳಿಗ್ಗೆ ೧೧ ರಿಂದ ಮಧ್ಯಾಹ್ನ ೪ ಗಂಟೆಯವರೆಗೆ ಕಳೆನಾಶಕ ಸಿಂಪಡಣೆ ಮಾಡಬೇಡಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Maintain inter-row organic mulching to shield soil organisms from lethal surface heat.",
                    "Schedule field operations during early mornings."
                ],
                "mr": [
                    "जमिनीतील सूक्ष्मजीव वाचवण्यासाठी आणि उष्णता रोखण्यासाठी पिकांच्या ओळीत आच्छादन करा.",
                    "शेतातील सर्व कामे पहाटे किंवा सकाळी लवकर पूर्ण करा."
                ],
                "hi": [
                    "मिट्टी के सूक्ष्मजीवों की सुरक्षा के लिए पंक्तियों में पलवार (मल्च) बनाए रखें।",
                    "कृषि कार्य सुबह के ठंडे समय में ही निपटाएं।"
                ],
                "kn": [
                    "ಮಣ್ಣಿನ ತೇವಾಂಶ ಕಾಪಾಡಲು ಸಾಲುಗಳ ಮಧ್ಯೆ ಒಣ ಕಸದ ಹೊದಿಕೆ ಮುಂದುವರಿಸಿ.",
                    "ಕೃಷಿ ಕೆಲಸಗಳನ್ನು ಮುಂಜಾನೆಯ ತಂಪಾದ ವೇಳೆಯಲ್ಲಿ ಪೂರ್ಣಗೊಳಿಸಿ."
                ]
            }
        },
        "extreme_rainfall": {
            "title": {
                "en": "Extreme Rainfall Storm Protection Advisory for Soybean",
                "mr": "सोयाबीन पिकासाठी अतिवृष्टी व वादळी पाऊस संरक्षण सल्ला",
                "hi": "सोयाबीन फसल के लिए मूसलाधार बारिश और तूफान सुरक्षा परामर्श",
                "kn": "ಸೋಯಾಬೀನ್ ಬೆಳೆಗೆ ಭಾರೀ ಮಳೆ ಮತ್ತು ಚಂಡಮಾರುತ ತುರ್ತು ಮುನ್ನೆಚ್ಚರಿಕೆ",
            },
            "recommendations": {
                "en": [
                    "Open boundary drainage trenches prior to storm onset to prevent prolonged submergence.",
                    "Secure peripheral field bunds to resist sudden flash overflow from adjacent slopes.",
                    "Do not broadcast fertilizers into saturated soils as runoff will cause 100% nutrient loss."
                ],
                "mr": [
                    "पावसाचा जोर वाढण्यापूर्वी शेताच्या चारी बाजूंना पाण्याचा निचरा होण्यासाठी चर उघडा.",
                    "बाजूच्या उतारावरून येणारे पाणी शेतात घुसू नये म्हणून शेताचे बांध मजबूत करा.",
                    "ओल्या जमिनीत खते टाकू नका, अन्यथा वाहून जाऊन संपूर्ण नुकसान होईल."
                ],
                "hi": [
                    "तेज बारिश से पहले खेत के किनारों पर जल निकासी की गहरी नालियां खोलें।",
                    "खेत की मेड़ों को मजबूत करें ताकि बाहरी पानी का बहाव खेत में न घुसे।",
                    "जलभराव वाली मिट्टी में यूरिया या डीएपी न डालें, यह बहकर नष्ट हो जाएगा।"
                ],
                "kn": [
                    "ಭಾರೀ ಮಳೆ ಪ್ರಾರಂಭವಾಗುವ ಮೊದಲೇ ಜಮೀನಿನ ಅಂಚಿನಲ್ಲಿ ಬಸಿಗಾಲುವೆಗಳನ್ನು ತೆರೆಯಿರಿ.",
                    "ಪಕ್ಕದ ಜಮೀನಿನಿಂದ ಹೆಚ್ಚುವರಿ ನೀರು ನುಗ್ಗದಂತೆ ಬದುಗಳನ್ನು ಬಲಪಡಿಸಿ.",
                    "ನೀರು ನಿಂತ ಜಮೀನಿನಲ್ಲಿ ರಸಗೊಬ್ಬರ ಹಾಕಬೇಡಿ, ಮಳೆ ನೀರಿನಲ್ಲಿ ಕೊಚ್ಚಿ ಹೋಗುತ್ತದೆ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Inspect harvest-ready pods; harvest mature fields immediately if rain forecast exceeds 40mm.",
                    "Park and cover farm implements under elevated shelters."
                ],
                "mr": [
                    "पीक काढणीला आले असल्यास पाऊस सुरू होण्यापूर्वी तातडीने मळणी किंवा काढणी उरकून घ्या.",
                    "शेती अवजारे उंचावर सुरक्षित ठिकाणी झाकून ठेवा."
                ],
                "hi": [
                    "यदि फसल पक चुकी है, तो बारिश शुरू होने से पहले तुरंत कटाई पूरी करें।",
                    "कृषि यंत्रों को ऊंचे और सुरक्षित स्थान पर रखें।"
                ],
                "kn": [
                    "ಬೆಳೆ ಕಟಾವಿಗೆ ಬಂದಿದ್ದರೆ ಮಳೆ ಸುರಿಯುವ ಮೊದಲೇ ತಕ್ಷಣ ಕಟಾವು ಮುಗಿಸಿಕೊಳ್ಳಿ.",
                    "ಕೃಷಿ ಉಪಕರಣಗಳನ್ನು ಎತ್ತರದ ಸುರಕ್ಷಿತ ಜಾಗದಲ್ಲಿರಿಸಿ."
                ]
            }
        }
    },

    # -----------------------------------------------------------------------
    # 2. COTTON
    # -----------------------------------------------------------------------
    "cotton": {
        "drought": {
            "title": {
                "en": "Severe Drought Mitigation Advisory for Cotton Crop",
                "mr": "कापूस पिकासाठी तीव्र दुष्काळ व ओलावा व्यवस्थापन सल्ला",
                "hi": "कपास फसल के लिए गंभीर सूखा निवारण परामर्श",
                "kn": "ಹತ್ತಿ ಬೆಳೆಗೆ ತೀವ್ರ ಬರ ಪರಿಹಾರ ಮತ್ತು ತೇವಾಂಶ ನಿರ್ವಹಣಾ ಸಲಹೆ",
            },
            "recommendations": {
                "en": [
                    "Adopt alternate furrow irrigation to maximize water productivity across the entire acreage.",
                    "Foliar spray with 2% Potassium Nitrate (13:0:45) + 1% Magnesium Sulphate to arrest square and boll shedding.",
                    "Loosen surface soil crust with a shallow blade harrow to break soil capillaries and reduce evaporation.",
                    "Spray anti-transpirant Kaolin (5%) or PMA under prolonged dry spells to lower leaf canopy temperature."
                ],
                "mr": [
                    "उपलब्ध पाण्याचा जास्तीत जास्त फायदा घेण्यासाठी एकाआड एक सरी (एक आड सरी) सिंचन पद्धती वापरा.",
                    "पात्या आणि बोंडे गळणे थांबवण्यासाठी २% पोटॅशियम नायट्रेट (१३:०:४५) आणि १% मॅग्नेशियम सल्फेट फवारा.",
                    "जमिनीतील भेगा बुजवून बाष्पीभवन रोखण्यासाठी हलके कोळपे फिरवून जमिनीचा वरचा थर मोकळा करा.",
                    "उष्णतेचा ताण कमी करण्यासाठी ५% केओलीन किंवा योग्य बाष्पोत्सर्जन प्रतिबंधकाची फवारणी करा."
                ],
                "hi": [
                    "उपलब्ध जल का अधिकतम लाभ लेने के लिए एकान्तर नाली (एक छोड़कर एक कूंड़) सिंचाई विधि अपनाएं।",
                    "कपास के फूल और टिंडे झड़ने से रोकने हेतु २% पोटेशियम नाइट्रेट (१३:०:४५) + १% मैग्नीशियम सल्फेट का छिड़काव करें।",
                    "खेत में हलकी गुड़ाई करके मिट्टी की ऊपरी पपड़ी तोड़ें ताकि वाष्पीकरण रुक सके।",
                    "लगातार सूखे की स्थिति में पत्तियों का तापमान नियंत्रित रखने के लिए ५% काओलिन का छिड़काव करें।"
                ],
                "kn": [
                    "ನೀರಿನ ಸಮರ್ಪಕ ಬಳಕೆಗಾಗಿ ಒಂದು ಸಾಲು ಬಿಟ್ಟು ಒಂದು ಸಾಲಿಗೆ ನೀರುಣಿಸುವ ಪರ್ಯಾಯ ಸಾಲು ನೀರಾವರಿ ಪದ್ಧತಿ ಬಳಸಿ.",
                    "ಹತ್ತಿ ಮೊಗ್ಗು ಮತ್ತು ಕಾಯಿ ಉದುರುವುದನ್ನು ತಡೆಯಲು ಶೇ ೨ ರ ಪೊಟ್ಯಾಸಿಯಮ್ ನೈಟ್ರೇಟ್ + ಶೇ ೧ ರ ಮೆಗ್ನೀಸಿಯಮ್ ಸಲ್ಫೇಟ್ ಸಿಂಪಡಿಸಿ.",
                    "ಮಣ್ಣಿನಲ್ಲಿ ಬಿರುಕು ಮೂಡುವುದನ್ನು ಮತ್ತು ತೇವಾಂಶ ನಷ್ಟವಾಗುವುದನ್ನು ತಪ್ಪಿಸಲು ಹಗುರ ಎಡೆಕುಂಟೆ ಹೊಡೆಯಿರಿ.",
                    "ಎಲೆಗಳಿಂದ ನೀರು ಆವಿಯಾಗುವುದನ್ನು ತಗ್ಗಿಸಲು ಶೇ ೫ ರ ಕಯೋಲಿನ್ ಸಿಂಪಡಣೆ ಮಾಡಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Maintain drip lines at 1.2–1.5 bars operating pressure for consistent emitter discharge.",
                    "Avoid deep intercultural operations that damage shallow feeder roots."
                ],
                "mr": [
                    "ठिबक सिंचन योग्य दाबावर चालू ठेवा जेणेकरून झाडांना समप्रमाणात पाणी मिळेल.",
                    "खोल नांगरणी किंवा कोळपणी टाळा ज्यामुळे मुळांना इजा होणार नाही."
                ],
                "hi": [
                    "ड्रिप प्रणाली को सही दबाव पर चलाएं ताकि प्रत्येक पौधे को उचित नमी मिले।",
                    "गहरी निराई-गुड़ाई से बचें ताकि जड़ों को नुकसान न पहुंचे।"
                ],
                "kn": [
                    "ಹನಿ ನೀರಾವರಿಯನ್ನು ಸರಿಯಾದ ಒತ್ತಡದಲ್ಲಿ ಚಲಾಯಿಸಿ ಸಮಪ್ರಮಾಣದಲ್ಲಿ ನೀರು ತಲುಪುವಂತೆ ಮಾಡಿ.",
                    "ಬೇರುಗಳಿಗೆ ಹಾನಿಯಾಗದಂತೆ ಆಳವಾದ ಉಳುಮೆಯನ್ನು ತಪ್ಪಿಸಿ."
                ]
            }
        },
        "flood": {
            "title": {
                "en": "Waterlogging & Inundation Drainage Advisory for Cotton Crop",
                "mr": "कापूस पिकासाठी पाणी साचणे व निचरा नियंत्रण सल्ला",
                "hi": "कपास फसल के लिए जलभराव और जलनिकासी प्रबंधन परामर्श",
                "kn": "ಹತ್ತಿ ಬೆಳೆಯಲ್ಲಿ ನೀರು ನಿಲ್ಲುವಿಕೆ ಮತ್ತು ಬಸಿಗಾಲುವೆ ನಿರ್ವಹಣೆ ಸಲಹೆ",
            },
            "recommendations": {
                "en": [
                    "Immediately create evacuation furrows across slope lines; cotton cannot tolerate standing water beyond 24 hours.",
                    "Once soil drains, drench root zones with Copper Oxychloride (2.5 g/L) to prevent root rot and Parawilt.",
                    "Foliar spray with 1% Urea + 1% DAP solution to restore root nutrient uptake impaired by oxygen depletion."
                ],
                "mr": [
                    "शेतातील साचलेले पाणी तातडीने बाहेर काढा; कापसाची मुळे २४ तासांपेक्षा जास्त वेळ पाण्यात राहिल्यास झाडे कोमेजतात (पॅराविल्ट).",
                    "पाणी ओसरताच मूळकुज आणि उबळणे रोखण्यासाठी कॉपर ऑक्सिक्लोराईड (२.५ ग्रॅम प्रति लिटर) आळवणी करा.",
                    "मुळांची अन्नद्रव्ये शोषण्याची क्षमता पूर्ववत करण्यासाठी १% युरिया + १% डीएपीची फवारणी करा."
                ],
                "hi": [
                    "खेत से पानी तुरंत बाहर निकालें; २४ घंटे से अधिक समय तक पानी भरा रहने पर कपास के पौधे मुरझा जाते हैं।",
                    "पानी हटने पर जड़ गलन और विल्ट रोग से बचाव हेतु कॉपर ऑक्सीक्लोराइड (२.५ ग्राम/लीटर) से जड़ों का शोधन करें।",
                    "ऑक्सीजन की कमी से प्रभावित पौधों को सहारा देने हेतु १% यूरिया + १% डीएपी का पर्णीय छिड़काव करें।"
                ],
                "kn": [
                    "ಜಮೀನಿನಲ್ಲಿ ನಿಂತ ನೀರನ್ನು ಕೂಡಲೇ ಹೊರಹಾಕಿ; ಹತ್ತಿ ಬೆಳೆಗೆ ೨೪ ಗಂಟೆಗಿಂತ ಹೆಚ್ಚು ಕಾಲ ನೀರು ನಿಲ್ಲಲು ಬಿಡಬಾರದು.",
                    "ನೀರು ಇಳಿದ ನಂತರ ಬೇರು ಕೊಳೆ ಮತ್ತು ಒಣಗುವ ರೋಗ ತಡೆಯಲು ಕಾಪರ್ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ (೨.೫ ಗ್ರಾಂ/ಲೀಟರ್) ಮಣ್ಣಿಗೆ ಹಾಕಿ.",
                    "ಪೋಷಕಾಂಶಗಳ ಕೊರತೆ ನೀಗಿಸಲು ಶೇ ೧ ರ ಯೂರಿಯಾ + ಶೇ ೧ ರ ಡಿಎಪಿ ದ್ರಾವಣವನ್ನು ಸಿಂಪಡಿಸಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Clear boundary outlets of weed growth to facilitate unhindered runoff.",
                    "Inspect regularly for sucking pest resurgence (jassids and aphids) after rains subside."
                ],
                "mr": [
                    "शेताचे मुख्य नाले कचरामुक्त करा जेणेकरून पाणी अडकणार नाही.",
                    "पाऊस थांबल्यानंतर तुडतुडे आणि मावा यांसारख्या रसशोषक किडींचा प्रादुर्भाव बारकाईने तपासा."
                ],
                "hi": [
                    "खेत के नालों से घासफूस हटाकर पानी का निकास खुला रखें।",
                    "बारिश के बाद रस चूसक कीटों (माहू, हरा तेला) के प्रकोप की नियमित जांच करें।"
                ],
                "kn": [
                    "ನೀರು ಸರಾಗವಾಗಿ ಹರಿಯುವಂತೆ ಜಮೀನಿನ ಬಸಿಗಾಲುವೆಗಳನ್ನು ಸದಾ ಸ್ವಚ್ಛವಾಗಿಡಿ.",
                    "ಮಳೆ ನಿಂತ ನಂತರ ಹತ್ತಿಯಲ್ಲಿ ರಸಹೀರುವ ಕೀಟಗಳ ಬಾಧೆಯನ್ನು ಸೂಕ್ಷ್ಮವಾಗಿ ಗಮನಿಸಿ."
                ]
            }
        },
        "heat": {
            "title": {
                "en": "Heat Stress Mitigation Advisory for Cotton Crop",
                "mr": "कापूस पिकासाठी उष्णतेचा ताण नियंत्रण सल्ला",
                "hi": "कपास फसल के लिए अत्यधिक गर्मी व ताप तनाव प्रबंधन परामर्श",
                "kn": "ಹತ್ತಿ ಬೆಳೆಗೆ ಶಾಖದ ಒತ್ತಡ ನಿಯಂತ್ರಣ ಸಲಹೆ",
            },
            "recommendations": {
                "en": [
                    "Maintain soil moisture through short-interval light irrigations during early morning or late evening.",
                    "Spray 1% Urea + 1% Potassium Nitrate (13:0:45) to minimize pollen desiccation and boll shedding.",
                    "Ensure adequate soil covering using crop residue mulches to insulate roots from scorching soil temperatures."
                ],
                "mr": [
                    "सकाळी लवकर किंवा संध्याकाळी हलके पाणी देऊन जमिनीत सतत ओलावा राखा.",
                    "परागकण वाळणे आणि बोंडगळ रोखण्यासाठी १% युरिया + १% पोटॅशियम नायट्रेटची फवारणी करा.",
                    "जमिनीचे तापमान नियंत्रित ठेवण्यासाठी पिकांच्या ओळीत पालापाचोळ्याचे आच्छादन करा."
                ],
                "hi": [
                    "सुबह या शाम के समय हलकी सिंचाई करके खेत में लगातार नमी बनाए रखें।",
                    "परागण और टिंडे झड़ने से बचाने के लिए १% यूरिया + १% पोटेशियम नाइट्रेट का छिड़काव करें।",
                    "जड़ों को अधिक तापमान से बचाने हेतु फसल अवशेषों की पलवार का उपयोग करें।"
                ],
                "kn": [
                    "ಮುಂಜಾನೆ ಅಥವಾ ಸಂಜೆಯ ಸಮಯದಲ್ಲಿ ಹಗುರ ನೀರು ಹಾಯಿಸಿ ಮಣ್ಣಿನಲ್ಲಿ ತೇವಾಂಶ ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
                    "ಹೂ ಮತ್ತು ಕಾಯಿ ಉದುರುವುದನ್ನು ತಡೆಯಲು ಶೇ ೧ ರ ಯೂರಿಯಾ + ಶೇ ೧ ರ ಪೊಟ್ಯಾಸಿಯಮ್ ನೈಟ್ರೇಟ್ ಸಿಂಪಡಿಸಿ.",
                    "ಬೇರುಗಳಿಗೆ ಶಾಖ ತಾಗದಂತೆ ಒಣ ಕಸದಿಂದ ಮಣ್ಣನ್ನು ಮುಚ್ಚಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Avoid application of organophosphate insecticides during high thermal peaks.",
                    "Monitor soil moisture tension daily using tensiometers or soil feel tests."
                ],
                "mr": [
                    "तीव्र उन्हामध्ये जहाल कीटकनाशकांची फवारणी करू नका.",
                    "जमिनीतील ओलाव्याची नियमित पाहणी करा."
                ],
                "hi": [
                    "कड़क धूप में कीटनाशकों का छिड़काव न करें।",
                    "मिट्टी में नमी की स्थिति की प्रतिदिन जांच करें।"
                ],
                "kn": [
                    "ಕಡು ಬಿಸಿಲಿನಲ್ಲಿ ತೀವ್ರ ರಾಸಾಯನಿಕ ಕೀಟನಾಶಕಗಳನ್ನು ಸಿಂಪಡಿಸಬೇಡಿ.",
                    "ಮಣ್ಣಿನಲ್ಲಿರುವ ತೇವಾಂಶವನ್ನು ಪ್ರತಿದಿನ ಪರೀಕ್ಷಿಸಿ."
                ]
            }
        },
        "extreme_rainfall": {
            "title": {
                "en": "Extreme Storm & Wind Damage Prevention Advisory for Cotton",
                "mr": "कापूस पिकासाठी अतिवृष्टी आणि वादळी वारा पूर्वतयारी सल्ला",
                "hi": "कपास फसल के लिए भारी आंधी-बारिश सुरक्षा परामर्श",
                "kn": "ಹತ್ತಿ ಬೆಳೆಗೆ ಭಾರೀ ಮಳೆ ಮತ್ತು ಬಿರುಗಾಳಿ ರಕ್ಷಣಾ ಸಲಹೆ",
            },
            "recommendations": {
                "en": [
                    "Reinforce ridge earthing-up to prevent plant lodging from heavy gale-force winds.",
                    "Dredge interceptor ditches along farm edges to channel runoff away from the crop.",
                    "After torrential rains, stake lodged plants immediately before stem tissues harden."
                ],
                "mr": [
                    "वादळी वाऱ्यामुळे झाडे कोलमडू नयेत म्हणून झाडांना मातीचा भक्कम आधार (भर) द्या.",
                    "शेताच्या कडेने चर खोदून पावसाचे पाणी तातडीने बाहेर काढा.",
                    "झाडे वाऱ्याने पडल्यास माती ओली असतानाच त्यांना त्वरित सरळ करून आधार द्या."
                ],
                "hi": [
                    "तेज हवाओं से पौधों को गिरने से बचाने के लिए पौधों के तनों पर मिट्टी चढ़ाएं।",
                    "खेत के चारों ओर पानी के निकास के लिए गहरी नालियां बनाएं।",
                    "यदि पौधे गिर जाएं, तो मिट्टी गीली रहते ही उन्हें तुरंत सीधा करके सहारा दें।"
                ],
                "kn": [
                    "ಬಿರುಗಾಳಿಗೆ ಗಿಡಗಳು ನೆಲಕ್ಕುರುಳದಂತೆ ಬುಡಕ್ಕೆ ಮಣ್ಣು ಏರಿಸಿ ಭದ್ರಪಡಿಸಿ.",
                    "ಹೆಚ್ಚುವರಿ ನೀರು ಹರಿದು ಹೋಗಲು ಜಮೀನಿನ ಸುತ್ತಲೂ ಬಸಿಗಾಲುವೆಗಳನ್ನು ಸಜ್ಜುಗೊಳಿಸಿ.",
                    "ಗಿಡಗಳು ವಾಲಿದ್ದರೆ ಮಣ್ಣು ಹಸಿಯಾಗಿರುವಾಗಲೇ ತಕ್ಷಣ ನೆಟ್ಟಗೆ ನಿಲ್ಲಿಸಿ ಆಸರೆ ಕೊಡಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Inspect and clean field perimeter drains.",
                    "Protect opened bolls by harvesting ready cotton bolls ahead of heavy storm warnings."
                ],
                "mr": [
                    "पाण्याचा निचरा सुरळीत असल्याची खात्री करा.",
                    "उमलेली बोंडे भिजून नुकसान होऊ नये म्हणून पाऊस सुरू होण्यापूर्वी फुटलेला कापूस वेचून घ्या."
                ],
                "hi": [
                    "पानी की निकासी वाले रास्तों को साफ रखें।",
                    "खिले हुए टिंडों को भीगने से बचाने के लिए बारिश से पहले कपास की चुनाई कर लें।"
                ],
                "kn": [
                    "ಜಮೀನಿನ ಸುತ್ತಲಿನ ಚರಂಡಿಗಳನ್ನು ಸ್ವಚ್ಛವಾಗಿಡಿ.",
                    "ಅರಳಿದ ಹತ್ತಿ ಹಾಳಾಗದಂತೆ ಮಳೆ ಬರುವ ಮೊದಲೇ ಬಿಡಿಸಿಕೊಳ್ಳಿ."
                ]
            }
        }
    },

    # -----------------------------------------------------------------------
    # 3. WHEAT
    # -----------------------------------------------------------------------
    "wheat": {
        "drought": {
            "title": {
                "en": "Critical Drought & Crown Root Initiation Advisory for Wheat",
                "mr": "गहू पिकासाठी दुष्काळ आणि मुकुट मूळ टप्पा पाणी व्यवस्थापन सल्ला",
                "hi": "गेहूं फसल के लिए सूखा एवं सीआरआई अवस्था पर जल प्रबंधन परामर्श",
                "kn": "ಗೋಧಿ ಬೆಳೆಗೆ ಬರ ಮತ್ತು ಬೇರು ಬಿಡುವ ಹಂತದ ನೀರಾವರಿ ಸಲಹೆ",
            },
            "recommendations": {
                "en": [
                    "Ensure mandatory irrigation at Crown Root Initiation (CRI) stage (20–25 days after sowing) to prevent tillering collapse.",
                    "Apply 2% Potassium Nitrate (13:0:45) spray at boot and anthesis stages to preserve flag leaf greenness.",
                    "Utilize micro-sprinklers during night or dawn hours to minimize wind drift and evaporative loss."
                ],
                "mr": [
                    "पेरणीनंतर २० ते २५ दिवसांनी मुकुट मुळे फुटण्याच्या (CRI) अत्यंत महत्त्वाच्या टप्प्यावर संरक्षित पाणी अवश्य द्या.",
                    "पानाचा हिरवेगारपणा आणि ओंबीतील दाणे भरण्यासाठी २% पोटॅशियम नायट्रेट (१३:०:४५) फवारा.",
                    "बाष्पीभवन टाळण्यासाठी रात्री किंवा पहाटेच्या वेळी तुषार सिंचनाने पाणी द्या."
                ],
                "hi": [
                    "बुवाई के २०-२५ दिन बाद ताज मूल अवस्था (CRI) पर हर हाल में सिंचाई करें ताकि कल्ले उचित संख्या में निकलें।",
                    "बालियां निकलते समय पत्तियों की सेहत बनाए रखने के लिए २% पोटेशियम नाइट्रेट का छिड़काव करें।",
                    "वाष्पीकरण रोकने के लिए रात या तड़के फव्वारा सिंचाई करें।"
                ],
                "kn": [
                    "ಬಿತ್ತನೆಯ ೨೦-೨೫ ದಿನಗಳ ನಂತರ ಬೇರು ಬಿಡುವ (CRI) ಪ್ರಮುಖ ಹಂತದಲ್ಲಿ ಕಡ್ಡಾಯವಾಗಿ ನೀರು ಹಾಯಿಸಿ.",
                    "ಕಾಳುಗಳು ಉತ್ತಮವಾಗಿ ಬೆಳೆಯಲು ಶೇ ೨ ರ ಪೊಟ್ಯಾಸಿಯಮ್ ನೈಟ್ರೇಟ್ ಸಿಂಪಡಿಸಿ.",
                    "ಆವಿಯಾಗುವಿಕೆಯನ್ನು ತಗ್ಗಿಸಲು ರಾತ್ರಿ ಅಥವಾ ಮುಂಜಾನೆ ತುಂತುರು ನೀರಾವರಿ ಮೂಲಕ ನೀರು ಕೊಡಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Apply paddy straw mulch in border strips to suppress soil moisture depletion.",
                    "Monitor soil moisture tension closely before booting stage."
                ],
                "mr": [
                    "जमिनीतील ओलावा टिकवण्यासाठी पेंढ्याचे आच्छादन करा.",
                    "ओंब्या बाहेर पडण्यापूर्वी जमिनीतील ओलावा सतत तपासा."
                ],
                "hi": [
                    "नमी संरक्षण के लिए क्यारियों में पुआल का मल्च बिछाएं।",
                    "बालियां आने से पहले मिट्टी की नमी पर नजर रखें।"
                ],
                "kn": [
                    "ತೇವಾಂಶ ಕಾಪಾಡಲು ಸಾಲುಗಳಲ್ಲಿ ಬತ್ತದ ಹುಲ್ಲಿನ ಹೊದಿಕೆ ಹಾಕಿ.",
                    "ತೆನೆ ಬರುವ ಮುನ್ನ ಮಣ್ಣಿನ ತೇವಾಂಶವನ್ನು ಪರೀಕ್ಷಿಸುತ್ತಿರಿ."
                ]
            }
        },
        "heat": {
            "title": {
                "en": "Terminal Heat Stress Advisory for Wheat Grain Filling",
                "mr": "गहू पिकासाठी दाणे भरताना उष्णतेचा ताण नियंत्रण सल्ला",
                "hi": "गेहूं फसल के लिए दाना भराव अवस्था पर तापमान तनाव सुरक्षा परामर्श",
                "kn": "ಗೋಧಿ ಬೆಳೆಯಲ್ಲಿ ಕಾಳು ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ ಉಷ್ಣತೆಯ ಒತ್ತಡ ನಿರ್ವಹಣೆ",
            },
            "recommendations": {
                "en": [
                    "Give light and frequent sprinkler irrigation to lower canopy temperature during sudden thermal spikes (>32°C).",
                    "Spray 0.2% Salicylic acid or 1% Potassium Chloride to protect enzymes in the grain-filling process.",
                    "Avoid irrigation during gusty daytime winds to prevent lodging."
                ],
                "mr": [
                    "तापमान ३२ अंशांच्या पुढे गेल्यास पिकाचे तापमान कमी करण्यासाठी तुषार सिंचनाने हलके पाणी द्या.",
                    "दाणे भरण्याच्या क्रियेत मदत करण्यासाठी ०.२% सॅलिसिलिक आम्ल किंवा १% पोटॅशियम क्लोराईड फवारा.",
                    "दुपारी सोसाट्याचा वारा असताना पाणी देणे टाळा, अन्यथा गहू भुईसपाट होऊ शकतो."
                ],
                "hi": [
                    "तापमान ३२ डिग्री से ऊपर जाने पर फसल का तापमान घटाने के लिए हल्की फव्वारा सिंचाई करें।",
                    "दाना सिकुड़ने से बचाने के लिए ०.२% सैलिसिलिक एसिड या १% पोटैशियम क्लोराइड का छिड़काव करें।",
                    "तेज हवा के समय सिंचाई न करें, इससे फसल गिर सकती है।"
                ],
                "kn": [
                    "ತಾಪಮಾನ ೩೨ ಡಿಗ್ರಿಗಿಂತ ಹೆಚ್ಚಾದಾಗ ಬೆಳೆಯ ಉಷ್ಣತೆ ತಗ್ಗಿಸಲು ಹಗುರ ತುಂತುರು ನೀರಾವರಿ ನೀಡಿ.",
                    "ಕಾಳು ಸರಿಯಾಗಿ ತುಂಬಲು ಶೇ ೦.೨ ರ ಸ್ಯಾಲಿಸಿಲಿಕ್ ಆಮ್ಲ ಅಥವಾ ಶೇ ೧ ರ ಪೊಟ್ಯಾಸಿಯಮ್ ಕ್ಲೋರೈಡ್ ಸಿಂಪಡಿಸಿ.",
                    "ಜೋರಾದ ಗಾಳಿ ಬೀಸುವಾಗ ನೀರು ಹಾಯಿಸಬೇಡಿ, ಬೆಳೆ ನೆಲಕ್ಕುರುಳಬಹುದು."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Plan future sowing with heat-tolerant certified varieties (e.g. DBW series).",
                    "Maintain sprinkler readiness for sudden heatwaves."
                ],
                "mr": [
                    "पुढील हंगामात उष्णतारोधक प्रमाणित जातींचीच पेरणी करा.",
                    "अचानक वाढणाऱ्या उष्णतेसाठी तुषार सिंचन यंत्रणा सज्ज ठेवा."
                ],
                "hi": [
                    "अगली बुवाई के लिए ताप सहनशील किस्मों (जैसे DBW किस्में) का चयन करें।",
                    "अचानक लू चलने की स्थिति के लिए स्प्रिंकलर तैयार रखें।"
                ],
                "kn": [
                    "ಮುಂದಿನ ಬೆಳೆಗೆ ಶಾಖ-ನಿರೋಧಕ ಪ್ರಮಾಣಿತ ಬೀಜಗಳನ್ನು ಆಯ್ಕೆಮಾಡಿ.",
                    "ಶಾಖ ಹೆಚ್ಚಾದ ತಕ್ಷಣ ಸಿಂಪಡಿಸಲು ತುಂತುರು ಸಾಧನಗಳನ್ನು ಸಿದ್ಧವಾಗಿಟ್ಟುಕೊಳ್ಳಿ."
                ]
            }
        },
        "flood": {
            "title": {
                "en": "Water Inundation Drainage Advisory for Wheat",
                "mr": "गहू पिकासाठी पाणी साचणे व निचरा सल्ला",
                "hi": "गेहूं फसल के लिए जलभराव जलनिकासी परामर्श",
                "kn": "ಗೋಧಿ ಬೆಳೆಯಲ್ಲಿ ನೀರು ನಿಲ್ಲುವಿಕೆ ನಿವಾರಣಾ ಸಲಹೆ",
            },
            "recommendations": {
                "en": [
                    "Drain all standing water within 12 hours; wheat roots suffer irreversible chlorosis under waterlogging.",
                    "Apply foliar spray of 1% Urea + 0.2% Zinc Sulphate once water is drained.",
                    "Do not apply granular fertilizers while the soil remains slushy."
                ],
                "mr": [
                    "शेतात साचलेले पाणी १२ तासांच्या आत बाहेर काढा; मुळांमध्ये पाणी साचल्यास गहू पिवळा पडून जळतो.",
                    "पाणी निघून गेल्यानंतर पिकाला उभारी देण्यासाठी १% युरिया + ०.२% झिंक सल्फेट फवारा.",
                    "जमीन चिखलमय असताना युरिया किंवा खतांचा वापर करू नका."
                ],
                "hi": [
                    "खेत से सारा पानी १२ घंटे के भीतर बाहर निकालें; गेहूं की जड़ें जलभराव बिल्कुल सहन नहीं कर पातीं।",
                    "जल निकासी के बाद १% यूरिया + ०.२% जिंक सल्फेट का छिड़काव करें।",
                    "गीली और दलदली मिट्टी में दानेदार खाद न डालें।"
                ],
                "kn": [
                    "ನಿಂತ ನೀರನ್ನು ೧೨ ಗಂಟೆಯೊಳಗೆ ಹೊರಹಾಕಿ; ನೀರು ನಿಂತರೆ ಗೋಧಿ ಬೇರುಗಳು ಕೊಳೆತು ಗಿಡಗಳು ಹಳದಿಯಾಗುತ್ತವೆ.",
                    "ನೀರು ಸರಿದ ಮೇಲೆ ಶೇ ೧ ರ ಯೂರಿಯಾ + ಶೇ ೦.೨ ರ ಜಿಂಕ್ ಸಲ್ಫೇಟ್ ಸಿಂಪಡಿಸಿ.",
                    "ಕೆಸರು ಮಣ್ಣಿನಲ್ಲಿ ಹರಳು ಗೊಬ್ಬರಗಳನ್ನು ಹಾಕಬೇಡಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Maintain clear ditch systems bordering wheat plots.",
                    "Scout for yellow rust emergence in moist microclimates."
                ],
                "mr": [
                    "शेताभोवती पाण्याचे चर नेहमी मोकळे ठेवा.",
                    "दमट हवामानामुळे पिवळा तांबेरा रोगाचा प्रादुर्भाव होतो का ते तपासा."
                ],
                "hi": [
                    "खेत की सीमाओं पर जल निकास की नालियों को साफ रखें।",
                    "अत्यधिक नमी में पीले रतुआ रोग के लक्षणों की नियमित निगरानी करें।"
                ],
                "kn": [
                    "ಜಮೀನಿನ ಸುತ್ತಲೂ ನೀರು ಹರಿದುಹೋಗುವ ದಾರಿಗಳನ್ನು ತೆರೆದಿಡಿ.",
                    "ತೇವಾಂಶದ ವಾತಾವರಣದಲ್ಲಿ ಹಳದಿ ತುಕ್ಕು ರೋಗದ ಬಾಧೆ ತಪಾಸಣೆ ಮಾಡಿ."
                ]
            }
        },
        "extreme_rainfall": {
            "title": {
                "en": "Excess Rainfall & Storm Advisory for Wheat",
                "mr": "गहू पिकासाठी अतिवृष्टी व वादळ पूर्वतयारी सल्ला",
                "hi": "गेहूं फसल के लिए भारी बारिश एवं आंधी-तूफान परामर्श",
                "kn": "ಗೋಧಿ ಬೆಳೆಗೆ ಭಾರೀ ಮಳೆ ಮತ್ತು ಬಿರುಗಾಳಿ ಎಚ್ಚರಿಕೆ",
            },
            "recommendations": {
                "en": [
                    "Dig drainage channels at field ends to divert torrents.",
                    "Delay scheduled nitrogen top-dressings until dry weather returns.",
                    "Inspect crop for earhead mold if rains coincide with grain ripening."
                ],
                "mr": [
                    "पावसाचे पाणी शेतात न साचता निघून जाण्यासाठी कडेने चर खोदा.",
                    "पाऊस पूर्ण थांबेपर्यंत खतांचा दुसरा हप्ता पुढे ढकला.",
                    "दाणे पक्व असताना पाऊस आल्यास ओंब्यांवर बुरशी वाढू नये म्हणून लक्ष ठेवा."
                ],
                "hi": [
                    "भारी बारिश के पानी को मोड़ने के लिए खेत के सिरों पर गहरी नालियां खोदें।",
                    "मौसम साफ होने तक नाइट्रोजन की दूसरी खुराक टाल दें।",
                    "यदि बालियां पक रही हों, तो फफूंद संक्रमण की तुरंत जांच करें।"
                ],
                "kn": [
                    "ಮಳೆ ನೀರು ಹರಿದುಹೋಗಲು ಜಮೀನಿನ ತುದಿಯಲ್ಲಿ ಬಸಿಗಾಲುವೆಗಳನ್ನು ಮಾಡಿ.",
                    "ಮಳೆ ಕಡಿಮೆಯಾಗುವವರೆಗೆ ಸಾರಜನಕ ಗೊಬ್ಬರ ಕೊಡುವುದನ್ನು ಮುಂದೂಡಿ.",
                    "ತೆನೆಗಳು ಮಾಗುವ ಹಂತದಲ್ಲಿ ಮಳೆಯಾದರೆ ಬೂಷ್ಟು ರೋಗ ಬಾರದಂತೆ ನಿಗಾವಹಿಸಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Maintain natural field slope channels.",
                    "Protect harvested bundles under tarpaulins."
                ],
                "mr": [
                    "पाणी वाहून जाणाऱ्या नैसर्गिक वाटा मोकळ्या ठेवा.",
                    "काढणी केलेले गव्हाचे भारे ताडपत्रीने झाकून ठेवा."
                ],
                "hi": [
                    "खेत के स्वाभाविक ढलान वाले रास्तों को खुला रखें।",
                    "कटे हुए गेहूं के पूलों को तिरपाल से ढक कर रखें।"
                ],
                "kn": [
                    "ನೈಸರ್ಗಿಕವಾಗಿ ನೀರು ಹರಿಯುವ ಮಾರ್ಗಗಳನ್ನು ಸುಗಮವಾಗಿಡಿ.",
                    "ಕಟಾವು ಮಾಡಿದ ತೆನೆಗಳನ್ನು ಟಾರ್ಪಾಲಿನ್ ಹಾಕಿ ಸುರಕ್ಷಿತವಾಗಿ ಮುಚ್ಚಿ."
                ]
            }
        }
    },

    # -----------------------------------------------------------------------
    # 4. GENERAL / OTHER CROPS FALLBACK
    # -----------------------------------------------------------------------
    "general": {
        "drought": {
            "title": {
                "en": "Drought & Moisture Conservation Advisory for Field Crops",
                "mr": "उभ्या पिकांसाठी दुष्काळ व ओलावा संवर्धन सल्ला",
                "hi": "खड़ी फसलों के लिए सूखा एवं नमी संरक्षण परामर्श",
                "kn": "ಬೆಳೆಗಳಿಗೆ ಬರ ಮತ್ತು ತೇವಾಂಶ ಸಂರಕ್ಷಣಾ ಸಲಹೆ",
            },
            "recommendations": {
                "en": [
                    "Prioritize protective irrigation to critical growth phases (flowering and grain/fruit filling).",
                    "Apply organic or straw mulch to lower surface soil evaporation rates by up to 30%.",
                    "Foliar spray with 1% Potassium Nitrate (13:0:45) to enhance osmotic regulation.",
                    "Suspend inter-row tilling to prevent breaking the soil moisture boundary layer."
                ],
                "mr": [
                    "पिकांच्या अत्यंत संवेदनशील अवस्थेत (फुलोरा आणि दाणे/फळ भरणे) संरक्षित पाणी देण्यास प्राधान्य द्या.",
                    "जमिनीतील ओलावा टिकवण्यासाठी पालापाचोळा किंवा पेंढ्याचे आच्छादन करा, ज्यामुळे बाष्पीभवन ३०% कमी होते.",
                    "झाडांना पाण्याचा ताण सहन होण्यासाठी १% पोटॅशियम नायट्रेटची फवारणी करा.",
                    "जमिनीतील ओलावा उडून जाऊ नये म्हणून आंतरमशागत तात्पुरती थांबवा."
                ],
                "hi": [
                    "फसल की नाजुक अवस्थाओं (फूल और फल बनते समय) में जीवन रक्षक सिंचाई को प्राथमिकता दें।",
                    "खेत में पुआल या सूखी घास का मल्च बिछाएं जिससे वाष्पीकरण में ३०% तक कमी आती है।",
                    "पौधों की सहनशक्ति बढ़ाने के लिए १% पोटेशियम नाइट्रेट का छिड़काव करें।",
                    "मिट्टी की नमी को सुरक्षित रखने के लिए निराई-गुड़ाई का कार्य रोक दें।"
                ],
                "kn": [
                    "ಬೆಳೆಯ ಪ್ರಮುಖ ಹಂತಗಳಲ್ಲಿ (ಹೂವಾಡುವ ಮತ್ತು ಕಾಳು/ಕಾಯಿ ಕಟ್ಟುವ ಹಂತ) ರಕ್ಷಣಾತ್ಮಕ ನೀರಾವರಿ ನೀಡಿ.",
                    "ಮಣ್ಣಿನ ತೇವಾಂಶ ಆವಿಯಾಗುವುದನ್ನು ತಡೆಯಲು ಸಾಲುಗಳ ನಡುವೆ ಒಣ ಹುಲ್ಲಿನ ಹೊದಿಕೆ (ಮಲ್ಚಿಂಗ್) ಮಾಡಿ.",
                    "ಗಿಡಗಳು ಬರವನ್ನು ತಡೆದುಕೊಳ್ಳಲು ಶೇ ೧ ರ ಪೊಟ್ಯಾಸಿಯಮ್ ನೈಟ್ರೇಟ್ ಸಿಂಪಡಿಸಿ.",
                    "ತೇವಾಂಶ ಕಾಪಾಡಲು ಎಡೆಕುಂಟೆ ಹೊಡೆಯುವುದನ್ನು ಸದ್ಯಕ್ಕೆ ನಿಲ್ಲಿಸಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Maintain irrigation equipment and check for leakages in supply conduits.",
                    "Avoid high-nitrogen fertilizer doses under acute water shortage."
                ],
                "mr": [
                    "सिंचन उपकरणांची तपासणी करून गळती थांबवा.",
                    "पाण्याची टंचाई असताना नत्रयुक्त खतांचा अतिवापर टाळा."
                ],
                "hi": [
                    "सिंचाई प्रणाली की जांच करें और पाइप लीकेज को ठीक करें।",
                    "पानी की कमी के समय नाइट्रोजन उर्वरकों की अधिक मात्रा न दें।"
                ],
                "kn": [
                    "ನೀರಾವರಿ ಉಪಕರಣಗಳನ್ನು ಪರಿಶೀಲಿಸಿ ಪೈಪ್‌ಗಳಲ್ಲಿ ನೀರು ಪೋಲಾಗದಂತೆ ತಡೆಯಿರಿ.",
                    "ನೀರಿನ ಕೊರತೆಯಿದ್ದಾಗ ಹೆಚ್ಚಿನ ಸಾರಜನಕ ಗೊಬ್ಬರ ಹಾಕಬೇಡಿ."
                ]
            }
        },
        "flood": {
            "title": {
                "en": "Waterlogging & Excessive Moisture Drainage Advisory",
                "mr": "शेतात पाणी साचणे आणि निचरा व्यवस्थापन सल्ला",
                "hi": "जलभराव एवं जलनिकासी प्रबंधन परामर्श",
                "kn": "ಜಮೀನಿನಲ್ಲಿ ನೀರು ನಿಲ್ಲುವಿಕೆ ಮತ್ತು ಬಸಿಗಾಲುವೆ ನಿರ್ವಹಣೆ ಸಲಹೆ",
            },
            "recommendations": {
                "en": [
                    "Facilitate rapid field evacuation of standing water through perimeter drainage trenches within 24 hours.",
                    "Apply light foliar spray of water-soluble fertilizers once water recedes to restore root activity.",
                    "Postpone pesticide and fertilizer applications until soil reaches workable moisture status."
                ],
                "mr": [
                    "शेतातील साचलेले पाणी २४ तासांच्या आत बाहेर काढण्यासाठी चर खोदून निचरा करा.",
                    "पाणी ओसरल्यानंतर मुळांना उभारी देण्यासाठी विद्राव्य खतांची हलकी फवारणी करा.",
                    "जमीन वाफशावर येईपर्यंत कोणतीही खते किंवा कीटकनाशके जमिनीत टाकू नका."
                ],
                "hi": [
                    "खेत में रुके हुए पानी को २४ घंटे के भीतर नालियों द्वारा बाहर निकालें।",
                    "पानी उतरने के बाद जड़ों को सक्रिय करने के लिए घुलनशील उर्वरकों का हल्का छिड़काव करें।",
                    "जब तक मिट्टी उचित नमी (वापसा) स्थिति में न आ जाए, तब तक उर्वरक न दें।"
                ],
                "kn": [
                    "ಜಮೀನಿನಲ್ಲಿ ನಿಂತ ನೀರನ್ನು ೨೪ ಗಂಟೆಯೊಳಗೆ ಬಸಿಗಾಲುವೆಗಳ ಮೂಲಕ ಹೊರಹಾಕಿ.",
                    "ನೀರು ಇಳಿದ ಮೇಲೆ ಬೇರುಗಳು ಚೇತರಿಸಿಕೊಳ್ಳಲು ನೀರಿನಲ್ಲಿ ಕರಗುವ ರಸಗೊಬ್ಬರವನ್ನು ಹಗುರವಾಗಿ ಸಿಂಪಡಿಸಿ.",
                    "ಮಣ್ಣು ಹಸಿಯಾಗುವವರೆಗೂ ಯಾವುದೇ ರಾಸಾಯನಿಕ ಗೊಬ್ಬರಗಳನ್ನು ಹಾಕಬೇಡಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Clear blockages in waterways and roadside channels.",
                    "Scout for bacterial and fungal root infections following prolonged saturation."
                ],
                "mr": [
                    "पाणी वाहून जाणाऱ्या मुख्य वाटा व गटारे स्वच्छ ठेवा.",
                    "पाणी साचून राहिल्यामुळे मूळकुज किंवा बुरशीजन्य रोग होतात का ते तपासा."
                ],
                "hi": [
                    "खेत के चारों ओर पानी के निकास को अवरोध मुक्त रखें।",
                    "जलभराव के बाद फफूंद और जीवाणु जनित रोगों की संभावना पर नजर रखें।"
                ],
                "kn": [
                    "ನೀರು ಹರಿದುಹೋಗುವ ಚರಂಡಿಗಳಲ್ಲಿ ಅಡೆತಡೆಗಳಿದ್ದರೆ ತೆರವುಗೊಳಿಸಿ.",
                    "ನೀರು ನಿಂತ ಪರಿಣಾಮವಾಗಿ ಬೇರು ಕೊಳೆಯುವ ರೋಗಗಳ ಲಕ್ಷಣಗಳನ್ನು ಗಮನಿಸಿ."
                ]
            }
        },
        "heat": {
            "title": {
                "en": "Heatwave & Thermal Crop Protection Advisory",
                "mr": "उष्णतेची लाट आणि पीक संरक्षण सल्ला",
                "hi": "लू एवं अत्यधिक तापमान सुरक्षा परामर्श",
                "kn": "ಶಾಖದ ಅಲೆ ಮತ್ತು ಬೆಳೆ ರಕ್ಷಣಾ ಸಲಹೆ",
            },
            "recommendations": {
                "en": [
                    "Provide frequent light irrigations in early mornings to moderate root-zone temperature.",
                    "Spray canopy with anti-stress formulations or potassium nitrate solution.",
                    "Avoid spraying chemicals during high temperature hours."
                ],
                "mr": [
                    "जमिनीचे तापमान नियंत्रणात ठेवण्यासाठी सकाळी लवकर हलके पाणी द्या.",
                    "पिकांवर ताण कमी करण्यासाठी पोटॅशियम नायट्रेट द्रावण फवारा.",
                    "दुपारच्या कडक उन्हामध्ये कोणतीही फवारणी करू नका."
                ],
                "hi": [
                    "जमीन का तापमान संतुलित रखने के लिए तड़के हल्की सिंचाई करें।",
                    "फसल का तनाव दूर करने के लिए पोटेशियम नाइट्रेट का छिड़काव करें।",
                    "दोपहर के समय तेज धूप में रासायनिक छिड़काव से बचें।"
                ],
                "kn": [
                    "ಮಣ್ಣಿನ ತಾಪಮಾನ ಸಮತೋಲನದಲ್ಲಿಡಲು ಬೆಳಗಿನ ಜಾವ ಹಗುರ ನೀರುಣಿಸಿ.",
                    "ಬೆಳೆಯ ಮೇಲಿನ ಒತ್ತಡ ತಗ್ಗಿಸಲು ಪೊಟ್ಯಾಸಿಯಮ್ ನೈಟ್ರೇಟ್ ಸಿಂಪಡಿಸಿ.",
                    "ಕಡು ಬಿಸಿಲಿನ ವೇಳೆಯಲ್ಲಿ ಯಾವುದೇ ಸಿಂಪಡಣೆ ಮಾಡಬೇಡಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Use crop residue mulch to preserve soil biome from thermal damage.",
                    "Ensure windbreaks or border crops are maintained."
                ],
                "mr": [
                    "जमिनीतील उपयुक्त जीव वाचवण्यासाठी पिकांमध्ये आच्छादन करा.",
                    "शेताच्या बांधावरील पिकांची काळजी घ्या."
                ],
                "hi": [
                    "मिट्टी के जीवन को सुरक्षित रखने के लिए पलवार का प्रयोग करें।",
                    "खेत की सीमाओं पर वायु-अवरोधक बनाए रखें।"
                ],
                "kn": [
                    "ಮಣ್ಣನ್ನು ತಂಪಾಗಿರಿಸಲು ಸಾವಯವ ತ್ಯಾಜ್ಯದ ಹೊದಿಕೆ ಬಳಸಿ.",
                    "ಜಮೀನಿನ ಸುತ್ತಲೂ ಗಾಳಿ-ತಡೆ ಬೆಳೆಗಳನ್ನು ಸಂರಕ್ಷಿಸಿ."
                ]
            }
        },
        "extreme_rainfall": {
            "title": {
                "en": "Heavy Downpour & Storm Protection Advisory",
                "mr": "अतिमुसळधार पाऊस व वादळ संरक्षण सल्ला",
                "hi": "अतिवृष्टि एवं आंधी-तूफान सुरक्षा परामर्श",
                "kn": "ಭಾರೀ ಮಳೆ ಮತ್ತು ಚಂಡಮಾರುತ ಮುನ್ನೆಚ್ಚರಿಕೆ",
            },
            "recommendations": {
                "en": [
                    "Prepare perimeter trenches to steer flash runoff away from planting beds.",
                    "Suspend all intercultural operations and spraying until weather clears.",
                    "Clear drains to avoid backflow inundation."
                ],
                "mr": [
                    "जास्तीचे पावसाचे पाणी शेतातून बाहेर काढण्यासाठी बांधाशेजारी चर तयार ठेवा.",
                    "हवामान स्वच्छ होईपर्यंत कोणतीही फवारणी किंवा आंतरमशागत करू नका.",
                    "पाणी उलट फिरून शेतात घुसू नये म्हणून गटारे स्वच्छ करा."
                ],
                "hi": [
                    "खेत में पानी भरने से रोकने के लिए किनारों पर गहरी नालियां तैयार रखें।",
                    "मौसम साफ होने तक सभी कृषि कार्य और छिड़काव रोक दें।",
                    "पानी का बैकफ्लो रोकने के लिए निकास रास्तों की सफाई करें।"
                ],
                "kn": [
                    "ಹೆಚ್ಚುವರಿ ನೀರು ಸರಾಗವಾಗಿ ಹರಿಯಲು ಜಮೀನಿನ ಅಂಚಿನಲ್ಲಿ ಬಸಿಗಾಲುವೆಗಳನ್ನು ಸಿದ್ಧಪಡಿಸಿ.",
                    "ವಾತಾವರಣ ತಿಳಿಯಾಗುವವರೆಗೂ ಯಾವುದೇ ಕೃಷಿ ಕೆಲಸ ಮತ್ತು ಸಿಂಪಡಣೆ ನಿಲ್ಲಿಸಿ.",
                    "ನೀರು ಹಿಮ್ಮುಖವಾಗಿ ಜಮೀನಿಗೆ ನುಗ್ಗದಂತೆ ಚರಂಡಿಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ."
                ]
            },
            "preventive_actions": {
                "en": [
                    "Reinforce weak spots along field bunds.",
                    "Safeguard harvested produce in waterproof storage."
                ],
                "mr": [
                    "कमकुवत झालेले शेताचे बांध त्वरित दुरुस्त करा.",
                    "काढणी केलेले धान्य सुरक्षित व कोरड्या जागी झाकून ठेवा."
                ],
                "hi": [
                    "कमजोर मेड़ों को तुरंत मजबूत करें।",
                    "काटी गई फसल को सुरक्षित और सूखे गोदाम में रखें।"
                ],
                "kn": [
                    "ದುರ್ಬಲವಾಗಿರುವ ಬದುಗಳನ್ನು ಗಟ್ಟಿ ಮಾಡಿ.",
                    "ಕಟಾವು ಮಾಡಿದ ಧಾನ್ಯವನ್ನು ಸುರಕ್ಷಿತ ಒಣ ಜಾಗದಲ್ಲಿ ಶೇಖರಿಸಿ."
                ]
            }
        }
    }
}


def build_explanation_text(
    lang: str,
    crop: str,
    risk_name_translated: str,
    risk_score: int,
    risk_level: str,
    soil_type: str,
    soil_moisture: float,
    temp: float,
    fc_rain: float
) -> str:
    """
    Builds natural, explainable advisory overview paragraph tailored to the farm telemetry.
    """
    if lang == "mr":
        return (
            f"{crop} पिकासाठी {risk_name_translated} धोका पातळी '{risk_level}' (धोका निर्देशांक: {risk_score}/१००) "
            f"नोंदवली गेली आहे. सध्या जमिनीतील ओलावा {soil_moisture:.1f}% असून मातीचा प्रकार '{soil_type}' आहे. "
            f"तापमान {temp:.1f}°C आणि पुढील २४ तासांत {fc_rain:.1f} मिमी पावसाचा अंदाज असल्याने, "
            f"पिकाचे नुकसान टाळण्यासाठी खालील उपाययोजना तातडीने अंमलात आणाव्यात."
        )
    elif lang == "hi":
        return (
            f"{crop} फसल के लिए {risk_name_translated} जोखिम स्तर '{risk_level}' (जोखिम सूचकांक: {risk_score}/१००) "
            f"दर्ज किया गया है। वर्तमान में मिट्टी की नमी {soil_moisture:.1f}% तथा मिट्टी का प्रकार '{soil_type}' है। "
            f"तापमान {temp:.1f}°C और अगले २४ घंटों में {fc_rain:.1f} मिमी बारिश के पूर्वानुमान के आधार पर, "
            f"फसल की सुरक्षा हेतु निम्नलिखित अनुशंसित कदम तुरंत उठाएं।"
        )
    elif lang == "kn":
        return (
            f"{crop} ಬೆಳೆಗೆ {risk_name_translated} ಅಪಾಯದ ಮಟ್ಟವು '{risk_level}' (ಅಪಾಯ ಸೂಚ್ಯಂಕ: {risk_score}/೧೦೦) "
            f"ಎಂದು ಗುರುತಿಸಲಾಗಿದೆ. ಪ್ರಸ್ತುತ ಮಣ್ಣಿನ ತೇವಾಂಶವು ಶೇ {soil_moisture:.1f} ಆಗಿದ್ದು, ಮಣ್ಣಿನ ವಿಧ '{soil_type}' ಆಗಿದೆ. "
            f"ತಾಪಮಾನ {temp:.1f}°C ಮತ್ತು ಮುಂದಿನ ೨೪ ಗಂಟೆಗಳಲ್ಲಿ {fc_rain:.1f} ಮಿಮೀ ಮಳೆಯ ಮುನ್ಸೂಚನೆಯಿರುವುದರಿಂದ, "
            f"ಬೆಳೆಯ ರಕ್ಷಣೆಗಾಗಿ ಈ ಕೆಳಗಿನ ಕ್ರಮಗಳನ್ನು ತುರ್ತಾಗಿ ಕೈಗೊಳ್ಳಿ."
        )
    else:
        # Default English
        return (
            f"The AI Risk Engine evaluated an aggregated '{risk_level}' risk level ({risk_score}/100) for {crop} "
            f"concerning {risk_name_translated}. Present field telemetry records root-zone soil moisture at {soil_moisture:.1f}% "
            f"in '{soil_type}' soil with ambient temperature at {temp:.1f}°C and {fc_rain:.1f}mm forecast precipitation. "
            f"The following tailored recommendations and preventive interventions should be implemented."
        )


class AdvisoryService:
    """
    Core Agronomic Engine for generating personalized and multilingual crop advisories.
    """

    def generate_advisory(
        self,
        farm_id: int,
        farm_name: str,
        crop: str,
        soil_type: str,
        soil_moisture: float,
        water_availability: str,
        temperature: float,
        rainfall: float,
        forecast_rainfall: float,
        humidity: float,
        risk_type: str,
        risk_score: int,
        risk_level: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        # Validate / normalize language
        lang = language.lower() if language in SUPPORTED_LANGUAGES else "en"

        crop_key = normalize_crop_key(crop)
        risk_key = normalize_risk_key(risk_type)

        # Retrieve crop knowledge entry (fallback to general)
        crop_data = AGRONOMIC_KNOWLEDGE_BASE.get(crop_key, AGRONOMIC_KNOWLEDGE_BASE["general"])
        risk_data = crop_data.get(risk_key, crop_data.get("drought", AGRONOMIC_KNOWLEDGE_BASE["general"]["drought"]))

        # Determine Urgency based on risk level and score
        if risk_level == "HIGH" and risk_score >= 80:
            urgency_key = "CRITICAL"
            time_key = "IMMEDIATE"
        elif risk_level == "HIGH":
            urgency_key = "HIGH"
            time_key = "SHORT_TERM"
        elif risk_level == "MEDIUM":
            urgency_key = "MEDIUM"
            time_key = "MEDIUM_TERM"
        else:
            urgency_key = "LOW"
            time_key = "ROUTINE"

        urgency_text = URGENCY_TRANSLATIONS[urgency_key].get(lang, urgency_key)
        time_window_text = TIME_WINDOW_TRANSLATIONS[time_key].get(lang, "Routine Monitoring")

        # Titles & localized text
        title = risk_data["title"].get(lang, risk_data["title"]["en"])
        recommendations = risk_data["recommendations"].get(lang, risk_data["recommendations"]["en"])
        preventive_actions = risk_data["preventive_actions"].get(lang, risk_data["preventive_actions"]["en"])

        crop_localized = CROP_NAMES.get(crop_key, {}).get(lang, crop)
        risk_localized = RISK_NAMES.get(risk_key, {}).get(lang, risk_type)

        explanation = build_explanation_text(
            lang=lang,
            crop=crop_localized,
            risk_name_translated=risk_localized,
            risk_score=risk_score,
            risk_level=risk_level,
            soil_type=soil_type,
            soil_moisture=soil_moisture,
            temp=temperature,
            fc_rain=forecast_rainfall
        )

        return {
            "farm_id": farm_id,
            "farm_name": farm_name,
            "crop": crop,
            "risk_type": risk_type,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "title": title,
            "explanation": explanation,
            "recommendations": recommendations,
            "preventive_actions": preventive_actions,
            "urgency": urgency_text,
            "time_window": time_window_text,
            "language": lang
        }


advisory_service = AdvisoryService()
