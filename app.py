import streamlit as st
import google.generativeai as genai
from PIL import Image

# עיצוב דף מקצועי (CSS)
st.set_page_config(page_title="HelpMe | אבחון תקלות חכם", page_icon="🛠️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; text-align: right; }
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; background-color: #2563eb; color: white; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #1e40af; transform: translateY(-2px); }
    .confidence-bar { height: 12px; border-radius: 6px; background: #e2e8f0; overflow: hidden; margin: 10px 0; border: 1px solid #cbd5e1; }
    .skill-box { background: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# סרגל צד (Sidebar) להגדרות
with st.sidebar:
    st.title("⚙️ הגדרות")
    api_key = st.text_input("מפתח API של Gemini:", type="password")
    st.markdown("---")
    skill_level = st.select_slider("רמת מיומנות טכנית", options=list(range(1, 11)), value=2)
    st.info("רמה 1: הסבר פשוט מאוד | רמה 10: הסבר טכני מקצועי")

# גוף האתר
st.title("🛠️ HelpMe")
st.subheader("אבחון תקלות חכם ומותאם אישית")

if not api_key:
    st.warning("אנא הכנס מפתח API בסרגל הצד כדי להתחיל.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    if "messages" not in st.session_state: st.session_state.messages = []
    if "confidence" not in st.session_state: st.session_state.confidence = 0

    # אזור השאלות והצ'אט
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    # העלאת תמונה (אופציונלי)
    uploaded_file = st.file_uploader("📷 צלם או העלה תמונה (למשל: לוח המקשים או החיבורים)", type=["jpg", "jpeg", "png"])

    if prompt := st.chat_input("תאר את הבעיה (למשל: המים לא מתחממים בקומקום)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            sys_msg = f"אתה עוזר אבחון. רמת משתמש: {skill_level}/10. אל תנחש, שאל שאלות מנחות. בסוף כתוב CONFIDENCE: X"
            inputs = [sys_msg] + [m["content"] for m in st.session_state.messages]
            if uploaded_file: inputs.append(Image.open(uploaded_file))
            
            response = model.generate_content(inputs)
            res_text = response.text
            
            if "CONFIDENCE:" in res_text:
                try:
                    val = res_text.split("CONFIDENCE:")[-1].strip()
                    st.session_state.confidence = int(''.join(filter(str.isdigit, val)))
                    res_text = res_text.split("CONFIDENCE:")[0]
                except: pass
            
            st.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})

    # סרגל ביטחון מעוצב (תמיד למטה)
    st.markdown("---")
    conf = st.session_state.confidence
    color = f"rgb({255 * (1 - conf/100)}, {255 * (conf/100)}, 0)"
    st.markdown(f"**רמת ביטחון באבחון:** {conf}%")
    st.markdown(f"""<div class="confidence-bar"><div style="width: {conf}%; background-color: {color}; height: 100%; transition: 0.5s;"></div></div>""", unsafe_allow_html=True)
    
    if st.button("📄 הפק דוח סיכום לאיש מקצוע"):
        summary = f"דוח HelpMe:\nבעיה: {st.session_state.messages[0]['content']}\nרמת ביטחון: {conf}%\nרמת מיומנות משתמש: {skill_level}"
        st.code(summary, language="text")
