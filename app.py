import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. הגדרות דף ועיצוב CSS מקצועי
st.set_page_config(page_title="HelpMe | אבחון תקלות חכם", page_icon="🛠️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; text-align: right; direction: rtl; }
    .main { background-color: #fcfcfc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #1e293b; color: white; font-weight: bold; border: none; transition: 0.3s; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .stButton>button:hover { background-color: #334155; transform: translateY(-2px); }
    .confidence-container { background: #f1f5f9; padding: 15px; border-radius: 15px; border: 1px solid #e2e8f0; margin: 20px 0; }
    .confidence-bar-bg { height: 12px; width: 100%; background: #e2e8f0; border-radius: 6px; overflow: hidden; }
    .safety-box { background-color: #fef2f2; border: 1px solid #ef4444; color: #b91c1c; padding: 15px; border-radius: 10px; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. סרגל צד (Sidebar) להגדרות
with st.sidebar:
    st.title("⚙️ הגדרות מערכת")
    user_api_key = st.text_input("הכנס מפתח API (מ-Google AI Studio):", type="password")
    st.markdown("---")
    skill_level = st.select_slider("רמת מיומנות טכנית (1-10):", options=list(range(1, 11)), value=2)
    st.caption("רמה 1: הסבר פשוט ללא מושגים טכניים | רמה 10: הסבר למומחים")
    if st.button("🗑️ איפוס שיחה"):
        st.session_state.messages = []
        st.session_state.confidence = 0
        st.rerun()

st.title("🛠️ HelpMe")
st.markdown("### אבחון תקלות חכם ומדריך לתיקון ביתי")

# 3. בדיקת מפתח API וחיבור ל-Gemini
if not user_api_key:
    st.info("אנא הכנס את מפתח ה-API שלך בסרגל הצד כדי להתחיל באבחון.")
else:
    try:
        genai.configure(api_key=user_api_key)
        # שימוש בשם המודל המדויק למניעת שגיאת NotFound
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if "messages" not in st.session_state: st.session_state.messages = []
        if "confidence" not in st.session_state: st.session_state.confidence = 0

        # הצגת היסטוריית האבחון
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        # העלאת תמונה לאבחון ויזואלי (שואב, מכונת קפה, לוח חשמל)
        uploaded_file = st.file_uploader("📷 צרף תמונה של התקלה (אופציונלי):", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.image(uploaded_file, caption="התמונה שהועלתה לאבחון", use_container_width=True)

        # קלט משתמש
        if prompt := st.chat_input("תאר את הבעיה שלך כאן..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                # הנחיה קשיחה ל-AI: לא לנחש, לשאול שאלות מנחות
                sys_instruction = f"""
                תפקיד: מומחה אבחון תקלות סבלני.
                רמת מיומנות משתמש: {skill_level} מתוך 10.
                חוקים: 
                1. אל תסיק מסקנה סופית עד שרמת הביטחון מעל 80%.
                2. שאל שאלה מנחה אחת בכל פעם.
                3. אם רמת המיומנות נמוכה (1-3), הסבר מושגים בעזרת תיאור ויזואלי (למשל: "החלק האדום בצד" במקום "שסתום פריקה").
                4. אם מדובר בחשמל או גז, הצג אזהרת בטיחות בולטת.
                5. בסוף כל תשובה כתוב בדיוק: CONFIDENCE: X (כאשר X הוא מספר 0-100).
                """
                
                inputs = [sys_instruction] + [m["content"] for m in st.session_state.messages]
                if uploaded_file:
                    inputs.append(Image.open(uploaded_file))
                    inputs.append("נתח את התמונה המצורפת כחלק מהאבחון.")

                with st.spinner("מנתח את הנתונים..."):
                    response = model.generate_content(inputs)
                    full_text = response.text
                
                # חילוץ רמת הביטחון ועדכון הסרגל
                if "CONFIDENCE:" in full_text:
                    try:
                        conf_part = full_text.split("CONFIDENCE:")[-1].strip()
                        st.session_state.confidence = int(''.join(filter(str.isdigit, conf_part)))
                        full_text = full_text.split("CONFIDENCE:")[0]
                    except: pass
                
                st.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})

        # 4. סרגל ביטחון ויזואלי בתחתית
        st.markdown("---")
        conf = st.session_state.confidence
        # חישוב צבע דינמי (אדום -> כתום -> ירוק)
        color = f"rgb({255 * (1 - conf/100)}, {255 * (conf/100)}, 0)"
        
        st.markdown(f"""
            <div class="confidence-container">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="font-weight: bold; font-size: 0.9em;">רמת ביטחון בזיהוי התקלה:</span>
                    <span style="font-weight: bold; color: {color};">{conf}%</span>
                </div>
                <div class="confidence-bar-bg">
                    <div style="width: {conf}%; background-color: {color}; height: 100%; transition: width 0.8s ease-in-out;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # כפתור הפקת דוח לשיתוף (למשל עם הנכד או עם טכנאי)
        if st.button("📄 הפק דוח סיכום לשיתוף"):
            history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            summary = f"--- דוח אבחון HelpMe ---\nסטטוס: {conf}% ביטחון בתקלה\nרמת מיומנות: {skill_level}\n\nהיסטוריית אבחון:\n{history_text}"
            st.text_area("העתק את הדוח ושלח אותו למסייע החיצוני:", value=summary, height=200)

    except Exception as e:
        st.error(f"שגיאה בחיבור ל-AI: {str(e)}")
        st.info("טיפ: וודא שמפתח ה-API שהכנסת תקין ופעיל ב-Google AI Studio.")
