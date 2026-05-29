"""
Lightweight language helpers for BloodConnect.

The app does not use compiled Django translation catalogs yet, so this module
provides a small request-scoped translation layer that can be expanded later.
"""

from django.utils.translation import get_language

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी",
}
LANGUAGE_SESSION_KEY = "bloodconnect_language"

TRANSLATIONS = {
    "hi": {
        "Home": "होम",
        "Hospitals": "अस्पताल",
        "Contact": "संपर्क",
        "About": "परिचय",
        "Login": "लॉगिन",
        "Register": "पंजीकरण",
        "Join Now": "अभी शामिल हों",
        "Profile": "प्रोफ़ाइल",
        "Dashboard": "डैशबोर्ड",
        "Logout": "लॉग आउट",
        "Requests": "अनुरोध",
        "Donate": "दान करें",
        "Seek Blood": "रक्त खोजें",
        "Hospital Profile": "अस्पताल प्रोफ़ाइल",
        "Hospital Dashboard": "अस्पताल डैशबोर्ड",
        "All Hospitals": "सभी अस्पताल",
        "Emergency Request": "आपातकालीन अनुरोध",
        "Find Donors": "दाता खोजें",
        "Menu": "मेनू",
        "Language": "भाषा",
        "Connecting Lives": "जीवन जोड़ते हैं",
        "Emergency Blood Network": "आपातकालीन रक्त नेटवर्क",
        "Every Drop": "हर बूंद",
        "Saves a Life": "एक जीवन बचाती है",
        "Donate Blood": "रक्तदान करें",
        "Need Blood?": "रक्त चाहिए?",
        "Donors Registered": "पंजीकृत दाता",
        "Partner Hospitals": "साझेदार अस्पताल",
        "Lives Saved": "बचाई गई जानें",
                "BloodConnect bridges the gap between blood donors, seekers, and hospitals.": "ब्लडकनेक्ट रक्त दाताओं, सहायता चाहने वालों और अस्पतालों के बीच की दूरी कम करता है।",
                "Register today and be someone's lifesaver in their most critical moment.": "आज ही पंजीकरण करें और किसी के सबसे कठिन समय में जीवनरक्षक बनें।",
        "LIVE EMERGENCY REQUESTS": "लाइव आपातकालीन अनुरोध",
        "How BloodConnect Works": "ब्लडकनेक्ट कैसे काम करता है",
                "Donors": "दाता",
        "Simple, fast, life-saving in three steps": "तीन चरणों में सरल, तेज़ और जीवनरक्षक",
        "Register": "पंजीकरण करें",
                "Requests Fulfilled": "पूर्ण हुए अनुरोध",
        "Connect": "जुड़ें",
                "Quick Links": "त्वरित लिंक",
                "For Users": "उपयोगकर्ताओं के लिए",
                "Emergency Helpline": "आपातकालीन हेल्पलाइन",
                "Available 24x7 for blood emergencies": "रक्त आपात स्थितियों के लिए 24x7 उपलब्ध",
                "All rights reserved.": "सर्वाधिकार सुरक्षित।",
                "Made with": "के साथ बनाया गया",
                "to save lives": "जान बचाने के लिए",
                "Learn More": "और जानें",
                "Ready to Make a Difference?": "क्या आप बदलाव लाने के लिए तैयार हैं?",
                "Join thousands of donors and hospitals in our life-saving network.": "हमारे जीवनरक्षक नेटवर्क में हज़ारों दाताओं और अस्पतालों से जुड़ें।",
                "Join BloodConnect": "ब्लडकनेक्ट से जुड़ें",
        "Save Lives": "जान बचाएँ",
        "Hospitals Near You": "आपके पास के अस्पताल",
        "Find verified hospitals with blood banks on the map": "मान्यताप्राप्त रक्त बैंक वाले अस्पतालों को मानचित्र पर खोजें",
                "Search a hospital by name and instantly see it on the map": "नाम से अस्पताल खोजें और उसे तुरंत मानचित्र पर देखें",
        "Be Someone's Reason to Live": "किसी के जीने की वजह बनें",
        "Register as Donor": "दाता के रूप में पंजीकरण",
        "I Need Blood": "मुझे रक्त चाहिए",
        "Register Hospital": "अस्पताल पंजीकरण",
        "View All": "सभी देखें",
        "Details": "विवरण",
        "Blood Bank Available": "रक्त बैंक उपलब्ध",
        "For Donors": "दाताओं के लिए",
        "For Seekers": "सहायता चाहने वालों के लिए",
        "Register as Donor": "दाता के रूप में पंजीकरण",
        "Donor Dashboard": "दाता डैशबोर्ड",
        "Log Donation": "दान दर्ज करें",
        "Register as Seeker": "सहायता चाहने वाले के रूप में पंजीकरण",
        "Search Donors": "दाता खोजें",
        "Create Request": "अनुरोध बनाएं",
        "Find Hospitals": "अस्पताल खोजें",
        "Contact Us": "हमसे संपर्क करें",
        "Connecting lives through the power of blood donation. Every drop counts.": "रक्तदान की शक्ति से जीवन जोड़ते हैं। हर बूंद कीमती है।",
        "1 donation saves up to 3 lives": "1 दान 3 जीवन तक बचा सकता है",
        "Emergency? Call": "आपात स्थिति? कॉल करें",
        "Blood Bank Helpline": "ब्लड बैंक हेल्पलाइन",
        "Built to save lives.": "जीवन बचाने के लिए बनाया गया।",
        "Blood Donor": "रक्त दाता",
        "Blood Seeker": "रक्त सहायता चाहने वाला",
        "Hospital": "अस्पताल",
        "Register As": "के रूप में पंजीकरण",
        "First Name": "पहला नाम",
        "Last Name": "अंतिम नाम",
        "Email": "ईमेल",
        "Phone Number": "फोन नंबर",
        "Address": "पता",
        "City": "शहर",
        "State": "राज्य",
        "Hospital Name": "अस्पताल का नाम",
        "Hospital Type": "अस्पताल का प्रकार",
        "Registration/License Number": "पंजीकरण/लाइसेंस नंबर",
        "Emergency Contact Number": "आपातकालीन संपर्क नंबर",
        "Blood Bank Available": "रक्त बैंक उपलब्ध",
        "Website URL": "वेबसाइट URL",
        "Upload Verification Document (PDF only)": "सत्यापन दस्तावेज़ अपलोड करें (केवल PDF)",
        "Username": "उपयोगकर्ता नाम",
        "Password": "पासवर्ड",
        "Confirm Password": "पासवर्ड की पुष्टि करें",
        "Welcome Back": "वापसी पर स्वागत है",
        "Login to your BloodConnect account": "अपने ब्लडकनेक्ट खाते में लॉगिन करें",
        "Don't have an account?": "क्या आपका खाता नहीं है?",
        "Register here": "यहाँ पंजीकरण करें",
        "Hospital Login": "अस्पताल लॉगिन",
        "for healthcare institutions": "स्वास्थ्य संस्थानों के लिए",
        "Be a Hero. Donate Blood.": "हीरो बनें। रक्तदान करें।",
        "One donation can save up to 3 lives. Join our network of donors across India.": "एक दान 3 जीवन तक बचा सकता है। भारत भर में हमारे दाताओं के नेटवर्क से जुड़ें।",
        "Donations": "दान",
        "Support": "सहायता",
        "Join BloodConnect": "ब्लडकनेक्ट से जुड़ें",
        "Create your account to start saving lives": "जीवन बचाना शुरू करने के लिए अपना खाता बनाएं",
        "Hospitals:": "अस्पताल:",
        "Select \"Hospital\" role for dedicated healthcare features": "समर्पित स्वास्थ्य सुविधाओं के लिए \"अस्पताल\" भूमिका चुनें",
        "Only lowercase letters and digits (no capital letters)": "केवल छोटे अक्षर और अंक (बड़े अक्षर नहीं)",
        "No spaces or special characters (except @/_/-)": "कोई स्पेस या विशेष अक्षर नहीं (केवल @/_/- को छोड़कर)",
        "Starts with a special character (recommended)": "विशेष अक्षर से शुरू होता है (अनुशंसित)",
        "40 characters or fewer": "40 वर्ण या उससे कम",
        "At least 8 characters": "कम से कम 8 वर्ण",
        "At least one lowercase letter": "कम से कम एक छोटा अक्षर",
        "At least one uppercase letter": "कम से कम एक बड़ा अक्षर",
        "At least one digit": "कम से कम एक अंक",
        "At least one special character (@$!%*?&#)": "कम से कम एक विशेष अक्षर (@$!%*?&#)",
        "Hospital Location (Click/Drag marker to pin on map)": "अस्पताल का स्थान (मानचित्र पर पिन करने के लिए मार्कर पर क्लिक/खींचें)",
        "Locate Me": "मेरा स्थान खोजें",
        "Create Account": "खाता बनाएं",
        "Already have an account?": "पहले से खाता है?",
        "Login here": "यहाँ लॉगिन करें",
        "for registered healthcare institutions": "पंजीकृत स्वास्थ्य संस्थानों के लिए",
        "Secure access for hospitals and healthcare institutions.": "अस्पतालों और स्वास्थ्य संस्थानों के लिए सुरक्षित पहुँच।",
        "Hospital access made easy.": "अस्पताल पहुँच आसान बनाई गई है।",
        "Manage hospital requests, blood stock, and patient support through a dedicated workflow.": "समर्पित वर्कफ़्लो से अस्पताल अनुरोध, रक्त स्टॉक और मरीज सहायता का प्रबंधन करें।",
        "Verified hospitals": "मान्यताप्राप्त अस्पताल",
        "Emergency support": "आपातकालीन सहायता",
        "Request dispatch": "अनुरोध प्रेषण",
        "My Profile": "मेरा प्रोफ़ाइल",
        "Personal Information": "व्यक्तिगत जानकारी",
        "Emergency Contact": "आपातकालीन संपर्क",
        "Medical Info": "चिकित्सीय जानकारी",
        "Save Changes": "परिवर्तन सहेजें",
        "Need Blood?": "रक्त चाहिए?",
        "Search by city...": "शहर के अनुसार खोजें...",
        "Search": "खोजें",
        "Quick Donor Search": "त्वरित दाता खोज",
        "Group": "समूह",
        "RH": "RH",
        "Positive": "पॉजिटिव",
        "Negative": "नेगेटिव",
        "Find on Map": "मानचित्र पर खोजें",
        "Type a hospital name, e.g. Apollo Mumbai...": "अस्पताल का नाम लिखें, जैसे Apollo Mumbai...",
        "View All Requests": "सभी अनुरोध देखें",
            "View All": "सभी देखें",
        "Search a hospital by name and instantly see it on the map": "नाम से अस्पताल खोजें और उसे तुरंत मानचित्र पर देखें",
        "Simple steps to save a life or find help": "जीवन बचाने या सहायता पाने के सरल चरण",
            "Search": "खोजें",
        "Donate Blood": "रक्तदान करें",
        "Need Blood?": "रक्त चाहिए?",
        "Blood Group": "रक्त समूह",
        "All Blood Groups": "सभी रक्त समूह",
        "All": "सभी",
        "Search by city": "शहर द्वारा खोजें",
        "Radius (km)": "त्रिज्या (किमी)",
        "Enter city": "शहर दर्ज करें",
        "Government": "सरकारी",
        "Private": "निजी",
        "Trust / NGO": "ट्रस्ट / एनजीओ",
        "Semi-Government": "अर्द्ध-सरकारी",
        "We are on a mission to eliminate blood shortages by connecting donors, seekers and hospitals in real time.": "हम दाताओं, सहायता चाहने वालों और अस्पतालों को रीयल-टाइम में जोड़कर रक्त की कमी खत्म करने के मिशन पर हैं।",
            "About BloodConnect": "ब्लडकनेक्ट के बारे में",
        "Our Mission": "हमारा मिशन",
        "Community": "समुदाय",
        "Trust & Safety": "विश्वास और सुरक्षा",
        "To ensure that no life is lost due to unavailability of blood by building a robust, real-time blood donation network.": "मजबूत, रीयल-टाइम रक्तदान नेटवर्क बनाकर यह सुनिश्चित करना कि रक्त की अनुपलब्धता के कारण कोई जान न जाए।",
        "We unite thousands of volunteer donors across India with hospitals and patients in critical need.": "हम पूरे भारत में हज़ारों स्वैच्छिक दाताओं को अस्पतालों और ज़रूरतमंद मरीजों से जोड़ते हैं।",
        "All hospitals are verified. Donor medical info is secured. Your data is private and protected.": "सभी अस्पतालों का सत्यापन किया गया है। दाताओं की चिकित्सीय जानकारी सुरक्षित है। आपका डेटा निजी और संरक्षित है।",
        "Join BloodConnect Today": "आज ही ब्लडकनेक्ट से जुड़ें",
            "Contact Us": "हमसे संपर्क करें",
        "Have questions or need help? We're here 24x7 for blood emergencies.": "क्या आपके प्रश्न हैं या सहायता चाहिए? हम रक्त आपात स्थितियों के लिए 24x7 उपलब्ध हैं।",
            "Availability": "उपलब्धता",
        "Your Name": "आपका नाम",
        "Message": "संदेश",
        "Send Message": "संदेश भेजें",
        "Availability": "उपलब्धता",
        "Profile updated successfully!": "प्रोफ़ाइल सफलतापूर्वक अपडेट हो गई!",
        "Invalid username or password.": "उपयोगकर्ता नाम या पासवर्ड अमान्य है।",
        "You have been logged out successfully.": "आप सफलतापूर्वक लॉग आउट हो गए हैं।",
        "Your message has been sent successfully! We will get back to you soon.": "आपका संदेश सफलतापूर्वक भेज दिया गया है। हम जल्द ही आपसे संपर्क करेंगे।",
        "Welcome to BloodConnect": "ब्लडकनेक्ट में आपका स्वागत है",
    }
}


def normalize_language_code(language_code):
    """Collapse browser-style codes like hi-IN to the supported base code."""

    if not language_code:
        return DEFAULT_LANGUAGE

    normalized = str(language_code).lower().replace("_", "-").split("-")[0]
    return normalized if normalized in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def get_current_language(language_code=None):
    return normalize_language_code(language_code or get_language())


def get_language_label(language_code):
    code = normalize_language_code(language_code)
    return SUPPORTED_LANGUAGES.get(code, SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE])


def translate_text(text, language_code=None):
    if text is None:
        return text

    code = get_current_language(language_code)
    return TRANSLATIONS.get(code, {}).get(str(text), text)


def translate_choices(choices, language_code=None):
    return [(value, translate_text(label, language_code)) for value, label in choices]


def apply_field_labels(fields, label_map, language_code=None):
    for field_name, label in label_map.items():
        if field_name in fields:
            fields[field_name].label = translate_text(label, language_code)
