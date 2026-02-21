import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
import google.generativeai as genai
from PIL import Image
import time
import random

API_KEY = "AIzaSyClRtASL4zQkbsLsDe4lXsyo2BwSvuMxCw" 

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Setup Error: {e}")
    model = None

st.set_page_config(page_title="Help For Diabetic People", page_icon="💙", layout="wide")

if 'diabet_logs' not in st.session_state:
    st.session_state.diabet_logs = []
if 'user_steps' not in st.session_state:
    st.session_state.user_steps = 0
if 'user_water' not in st.session_state:
    st.session_state.user_water = 0.0

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');
    
    .stApp { 
        background-color: rgb(248, 249, 250); 
        color: rgb(45, 55, 72); 
        font-family: 'Segoe UI', sans-serif; 
    }
    
    [data-testid="stSidebar"] {
        background-color: rgb(44, 82, 130) !important;
        border-right: none;
    }
    
    [data-testid="stSidebarNav"] span, 
    [data-testid="stSidebar"] label p, 
    .stRadio label p {
        color: rgb(255, 255, 255) !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }

    label, .stMarkdown, [data-testid="stWidgetLabel"] p, h1, h2, h3 {
        color: rgb(44, 82, 130) !important;
        font-weight: 700 !important;
    }

    [data-testid="stTable"] {
        background-color: rgb(255, 255, 255) !important;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        padding: 5px;
        border: 1px solid rgb(226, 232, 240);
    }
    [data-testid="stTable"] td, [data-testid="stTable"] th, .dataframe td, .dataframe th {
        color: rgb(45, 55, 72) !important;
    }

    .stButton>button {
        background-color: rgb(56, 178, 172) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 0.5rem 2rem !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: rgb(49, 151, 149) !important;
        box-shadow: 0 4px 12px rgba(56, 178, 172, 0.3);
        transform: translateY(-1px);
    }
    .stButton>button p { color: rgb(255, 255, 255) !important; }

    [data-testid="stForm"] button {
        background-color: rgb(56, 178, 172) !important;
        border: none !important;
    }

    input, textarea, [data-baseweb="select"] span {
        background-color: rgb(255, 255, 255) !important;
        color: rgb(45, 55, 72) !important;
        border-radius: 6px !important;
        border: 1px solid rgb(226, 232, 240) !important;
    }
    
    .brand-container {
        padding: 20px 10px; text-align: center;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); 
        margin-bottom: 25px;
    }
    .brand-name {
        color: rgb(255, 255, 255) !important; font-size: 22px !important;
        font-weight: 800 !important; text-transform: uppercase;
    }
    
    .glass-card {
        background: rgb(255, 255, 255); 
        border-radius: 12px;
        padding: 30px; margin-bottom: 25px; 
        border: 1px solid rgb(226, 232, 240);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .recipe-card {
        background: rgb(255, 255, 255); padding: 20px; border-radius: 12px;
        border-left: 4px solid rgb(56, 178, 172); margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid rgb(226, 232, 240);
    }
    
    .benefit-tag { 
        background: rgb(230, 255, 250); color: rgb(40, 94, 97); padding: 4px 12px; 
        border-radius: 15px; font-size: 12px; font-weight: bold; margin-bottom: 5px; display: inline-block; 
        border: 1px solid rgb(178, 245, 234);
    }
    
    .verdict-box {
        background: rgb(230, 255, 250); 
        border-left: 5px solid rgb(56, 178, 172);
        padding: 20px; margin-top: 15px; border-radius: 4px;
        color: rgb(35, 78, 82);
    }
    </style>
    """, unsafe_allow_html=True)

def color_sugar(val):
    try:
        f_val = float(val)
        if f_val > 7.2: return 'background-color: rgb(254, 215, 215); color: rgb(155, 44, 44); font-weight: bold;' 
        if 4.0 <= f_val <= 7.2: return 'background-color: rgb(198, 246, 213); color: rgb(34, 84, 61); font-weight: bold;' 
        return 'background-color: rgb(190, 227, 248); color: rgb(42, 67, 101); font-weight: bold;' 
    except: return ''

def play_save_sound():
    sound_url = "https://www.orangefreesounds.com/wp-content/uploads/2014/10/Ding-sound.mp3"
    st.components.v1.html(f'<audio autoplay><source src="{sound_url}" type="audio/mp3"></audio>', height=0)

def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="report.csv" style="color: rgb(56, 178, 172); font-weight:bold;">📥 Download Report (CSV)</a>'

with st.sidebar:
    st.markdown("""<div class='brand-container'><div class='brand-name'>💙 Help For<br>Diabetic People</div></div>""", unsafe_allow_html=True)
    page = st.radio("NAVIGATION:", ["🏠 Home", "🏃 Activities", "🥗 Global Kitchen", "🩺 Personal Log", "🎓 Knowledge Base"])

if page == "🏠 Home":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<div class='glass-card'><h1>Help For Diabetic People</h1><p>Your reliable ecosystem for diabetes management.</p></div>", unsafe_allow_html=True)
        
        st.subheader("🍞 Bread Units (BU) Calculator")
        carb_col, xe_col = st.columns(2)
        with carb_col: carbs = st.number_input("Carbs per serving (g):", 0, 100, 12)
        with xe_col: xe_val = st.selectbox("1 BU equals:", [10, 12], index=1)
        st.info(f"Result: **{carbs/xe_val:.1f} BU**")

        st.subheader("📊 My Metrics")
        v_col1, v_col2, v_col3 = st.columns(3)
        with v_col1: steps = st.number_input("Enter steps:", 0, 50000, st.session_state.user_steps)
        with v_col2: water = st.number_input("Water (liters):", 0.0, 10.0, st.session_state.user_water)
        with v_col3: mood = st.select_slider("Your mood:", options=["🚀 Excellent", "🙂 Good", "😐 Average", "😟 Tired", "🆘 Stress"])
        
        st.session_state.user_steps = steps
        st.session_state.user_water = water

        st.markdown("<div class='verdict-box'><b>🤖 AI Verdict:</b>", unsafe_allow_html=True)
        verdicts = []
        if steps < 5000: verdicts.append("🏃 Low activity. Try walking to reduce the risk of a sugar spike.")
        elif steps >= 10000: verdicts.append("✅ Great activity! This improves insulin sensitivity.")
        if water < 1.5: verdicts.append("💧 Drink more water to normalize blood viscosity.")
        if mood in ["😟 Tired", "🆘 Stress"]: verdicts.append("🧘 Stress raises sugar. Find 5 minutes for relaxation.")
        if not verdicts: verdicts.append("🌟 You are doing great!")
        st.write(" ".join(verdicts))
        st.markdown("</div>", unsafe_allow_html=True)

        age = st.slider("Your age category", 1, 100, 25)
        st.info(f"Recommended target range: 4.4 - 7.2 mmol/L")
    with col2:
        st.image("https://images.unsplash.com/photo-1505751172876-fa1923c5c528?q=80&w=400")

elif page == "🏃 Activities":
    st.markdown("<div class='glass-card'><h1>🏃‍♂️ Activities and Sport</h1><p>Regular exercise helps control glucose levels.</p></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("<h3>📉 Sport Calculator</h3>", unsafe_allow_html=True)
        sports_db = {
            "Walking (easy)": 0.03, "Walking (fast)": 0.05, "Running": 0.09, 
            "Swimming": 0.07, "Cycling": 0.06, "Yoga": 0.02, "Tennis": 0.08, 
            "Football": 0.1, "Dancing": 0.05, "Strength training": 0.04
        }
        sport_type = st.selectbox("Sport type:", list(sports_db.keys()))
        duration = st.slider("Duration (min):", 10, 180, 30)
        total_burn = duration * sports_db[sport_type]
        st.markdown(f"<div class='verdict-box' style='border-left-color: rgb(56, 178, 172);'>🤖 Expected sugar drop: <b>-{total_burn:.1f} mmol/L</b></div>", unsafe_allow_html=True)
        
        st.write("---")
        user_goal = st.number_input("Step goal:", 1000, 50000, 10000)
        st.progress(min(st.session_state.user_steps / user_goal, 1.0))
        st.write(f"Completed today: {st.session_state.user_steps} steps")

    with col_b:
        st.image("https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=500")

elif page == "🥗 Global Kitchen":
    st.header("🌎 Gourmet Menu: 15 Recipes for Health")
    st.info("All recipes are adapted for people with diabetes: low GI and maximum benefit.")
    
    t_rec, t_ai = st.tabs(["🥘 Step-by-Step Recipes", "🤖 AI Ingredient Scanner"])
    
    with t_rec:
        recipes_database = [
            {
                "country": "Greece", "title": "Horiatiki Salad", "benefit": "Healthy Fats",
                "ing": "Cucumbers, tomatoes, peppers, feta, Kalamata olives, olive oil, oregano.",
                "steps": ["Cut vegetables into large cubes (village style).", "Add whole olives and a whole block of feta on top.", "Sprinkle with dried oregano.", "Drizzle with oil. Do not mix until serving!"]
            },
            {
                "country": "Japan", "title": "Miso Soup", "benefit": "Probiotics",
                "ing": "Miso paste, tofu, dried wakame seaweed, green onions.",
                "steps": ["Soak seaweed in water for 5 minutes.", "Bring water to a boil, add diced tofu.", "Dissolve miso paste in a separate cup with warm water and pour into the pot.", "Remove from heat (do not boil miso!), sprinkle with onions."]
            },
            {
                "country": "Italy", "title": "Zucchini Pasta (Zoodles)", "benefit": "Low GI",
                "ing": "Young zucchini, garlic, olive oil, parmesan, basil.",
                "steps": ["Using a peeler or special grater, cut zucchini into long thin strips.", "Sauté garlic in oil for 1 minute.", "Add zucchini and fry for only 2-3 minutes (Al Dente).", "Sprinkle with cheese and basil."]
            },
            {
                "country": "India", "title": "Red Dal (Lentil Soup)", "benefit": "Fiber+",
                "ing": "Red lentils, turmeric, ginger, garlic, tomatoes in their own juice.",
                "steps": ["Rinse lentils and boil with turmeric for 15 minutes.", "In a pan, sauté grated ginger, garlic, and tomatoes.", "Mix the sauté base with the lentils.", "Cook for another 5 minutes until creamy."]
            },
            {
                "country": "Mexico", "title": "Guacamole", "benefit": "Omega-9",
                "ing": "Ripe avocado, lime juice, cilantro, red onion, chili pepper.",
                "steps": ["Mash avocado with a fork (leave some small chunks).", "Finely chop onion, cilantro, and chili.", "Mix everything with lime juice (it prevents browning).", "Serve with celery sticks instead of chips."]
            },
            {
                "country": "Lebanon", "title": "Quinoa Tabbouleh", "benefit": "Superfood",
                "ing": "Quinoa, a large bunch of parsley, mint, tomatoes, lemon juice.",
                "steps": ["Cook quinoa and let it cool.", "Finely chop parsley and mint (there should be more greens than grain).", "Dice tomatoes into small cubes.", "Season with lemon juice and oil."]
            },
            {
                "country": "Norway", "title": "Salmon with Asparagus", "benefit": "Protein",
                "ing": "Salmon fillet, asparagus, lemon, rosemary.",
                "steps": ["Place fillet on parchment, salt, and add rosemary.", "Place peeled asparagus next to it.", "Bake for 15 minutes at 180°C.", "Drizzle with fresh lemon juice before eating."]
            },
            {
                "country": "France", "title": "Ratatouille", "benefit": "Vitamins",
                "ing": "Eggplant, zucchini, pepper, sugar-free tomato sauce.",
                "steps": ["Cut all vegetables into identical thin circles.", "Arrange them in a dish 'accordion style', alternating colors.", "Pour tomato sauce with spices over it.", "Cover with foil and bake for 40 minutes."]
            },
            {
                "country": "Thailand", "title": "Tom Yum with Shrimp", "benefit": "Metabolism",
                "ing": "Shrimp, oyster mushrooms, a little coconut milk, lemongrass.",
                "steps": ["Boil a light broth with shrimp shells and lemongrass.", "Add mushrooms and cook for 5 minutes.", "Add a bit of coconut milk and cleaned shrimp.", "As soon as the shrimp turn pink, the soup is ready."]
            },
            {
                "country": "Georgia", "title": "Ajapsandali", "benefit": "Fiber",
                "ing": "Eggplants, bell peppers, tomatoes, lots of cilantro, garlic.",
                "steps": ["Bake whole vegetables in the oven until soft.", "Remove skins and cut into large strips.", "Mix with crushed garlic and chopped cilantro.", "Let it sit for 2 hours."]
            },
            {
                "country": "Turkey", "title": "Baba Ganoush", "benefit": "Low Sugar",
                "ing": "Eggplants, tahini (sesame paste), garlic, olive oil.",
                "steps": ["Prick eggplants with a fork and bake until the skin turns black.", "Remove the pulp and blend with tahini and garlic.", "Add a drop of oil and paprika.", "Use as a spread for whole-grain crackers."]
            },
            {
                "country": "Spain", "title": "Gazpacho", "benefit": "Antioxidants",
                "ing": "Ripe tomatoes, cucumber, bell pepper, some stale whole-grain bread.",
                "steps": ["Peel the tomatoes.", "Blend all vegetables until smooth.", "Add a drop of wine vinegar and olive oil.", "Serve very cold."]
            },
            {
                "country": "Vietnam", "title": "Pho-Bo with Shirataki Noodles", "benefit": "Zero Calories",
                "ing": "Beef fillet, bone broth, shirataki noodles, star anise, cinnamon.",
                "steps": ["Cook the broth with spices for a long time (at least 3 hours).", "Rinse the shirataki (it has 0 calories and carbs!).", "Thinly slice raw beef.", "Pour boiling broth over the noodles and meat (the meat cooks in the bowl)."]
            },
            {
                "country": "Russia", "title": "Kefir Okroshka", "benefit": "Probiotics",
                "ing": "Boiled chicken breast, radish, cucumber, egg, low-fat kefir.",
                "steps": ["Cut all ingredients into small cubes.", "Chop lots of dill and green onions.", "Mix and pour cold kefir.", "Add a drop of mustard for taste."]
            },
            {
                "country": "USA", "title": "Cobb Salad", "benefit": "Satiety",
                "ing": "Turkey fillet, avocado, egg, iceberg lettuce, tomatoes.",
                "steps": ["Grill the turkey.", "Cut all ingredients into large cubes.", "Arrange on a platter in rows: meat, avocado, eggs.", "Season with lemon and mustard dressing."]
            }
        ]

        c1, c2 = st.columns(2)
        for i, r in enumerate(recipes_database):
            with (c1 if i % 2 == 0 else c2):
                with st.expander(f"📍 {r['country']} | {r['title']}"):
                    st.markdown(f"<span class='benefit-tag'>{r['benefit']}</span>", unsafe_allow_html=True)
                    st.write(f"**🛒 Ingredients:** {r['ing']}")
                    st.write("**👨‍🍳 Preparation Steps:**")
                    for j, step in enumerate(r['steps'], 1):
                        st.write(f"{j}. {step}")

    with t_ai:
        st.markdown("<div class='glass-card'><h3>📸 Virtual Analysis by Photo</h3><p>Upload a photo of your dish for Gemini AI analysis.</p></div>", unsafe_allow_html=True)
        file_img = st.file_uploader("Upload plate photo", type=["jpg", "png", "jpeg"], key="food_scanner")
        if file_img:
            image = Image.open(file_img)
            st.image(image, width=400)
            if st.button("🚀 Start AI Analysis"):
                if model:
                    with st.spinner("Analyzing..."):
                        response = model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(...)
                        
if response and hasattr(response, 'text'):
    st.markdown(f"<div class='verdict-box'>{response.text}</div>", unsafe_allow_html=True)
else:
    st.error("Ошибка: Модель не смогла сгенерировать текст. Проверьте настройки или API ключ.")
elif page == "🩺 Personal Log":
    st.markdown("<div class='glass-card'><h3>🩺 Measurement Log</h3></div>", unsafe_allow_html=True)
    with st.form("log"):
        d, s, n = st.date_input("Date"), st.number_input("Sugar (mmol/L)", 2.0, 30.0, 5.5), st.text_area("Notes")
        if st.form_submit_button("Save Data"):
            st.session_state.diabet_logs.append({"Date": d, "Sugar": s, "Notes": n})
            play_save_sound() 
    
    if st.session_state.diabet_logs:
        df = pd.DataFrame(st.session_state.diabet_logs)
        st.subheader("📈 Trend Visualization")
        chart_df = df.copy()
        chart_df['Date'] = pd.to_datetime(chart_df['Date'])
        chart_df = chart_df.sort_values('Date').set_index('Date')
        st.line_chart(chart_df['Sugar'])
        st.subheader("📋 Entry History")
        st.table(df.style.applymap(color_sugar, subset=['Sugar'])) 
        st.markdown(get_table_download_link(df), unsafe_allow_html=True)

elif page == "🎓 Knowledge Base":
    st.markdown("<div class='glass-card'><h1>Information Center</h1></div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📜 Articles and Charts", "🌟 20 Heroes"])
    
    with t1:
        st.markdown("<h3>📚 10 Key Facts and Control Rules</h3>", unsafe_allow_html=True)
        facts = [
            {"title": "1. Metabolic Mechanics", "text": "Diabetes is not just 'high sugar' but a metabolic disorder where cells lack energy because glucose stays in the blood, damaging vessels."},
            {"title": "2. Fiber Magic", "text": "Eating vegetables before the main dish creates a 'mesh' in the gut that slows sugar absorption, reducing postprandial peaks by 30%."},
            {"title": "3. Hidden Sugars", "text": "Beware of 'sugar-free' products. Maltodextrin or starch can raise sugar faster than white sugar."},
            {"title": "4. Muscles as Pumps", "text": "Physical activity opens cell channels without insulin. A simple 15-minute walk after dinner works as natural medicine."},
            {"title": "5. Hypoglycemia Danger", "text": "A sharp drop (below 3.9) is more dangerous than high levels here and now. Always carry 15g of fast carbs (juice or 3 sugar cubes)."},
            {"title": "6. HbA1c", "text": "This is the 'lie detector' for diabetics. It shows average sugar for the last 3 months. The target for most is below 7.0%."},
            {"title": "7. Stress Impact", "text": "Cortisol forces the liver to release glucose stores. Sometimes 5 minutes of meditation lowers sugar better than a diet."},
            {"title": "8. Dawn Phenomenon", "text": "Sugar rise between 4-7 AM is caused by growth hormones. If you wake up high without eating at night, it's your hormonal system at work."},
            {"title": "9. Vascular & Foot Health", "text": "High sugar damages small nerves (neuropathy). Daily foot inspection is a critical ritual to prevent serious injuries."},
            {"title": "10. Plate Rule", "text": "Use the visual method: 1/2 vegetables, 1/4 protein (meat/fish), 1/4 complex carbs (buckwheat/barley). Perfect balance."}
        ]
        for f in facts:
            with st.expander(f["title"]): st.write(f["text"])
        
        st.write("---")
        st.subheader("📊 Morbidity Statistics (2000 - 2026)")
        years = list(range(2000, 2027))
        aktobe_vals = [2.2 + (i * 0.48) + (i**1.5) * 0.02 for i in range(len(years))]
        world_vals = [171 + (i * 14.5) + (i**1.6) * 0.4 for i in range(len(years))]

        st_col1, st_col2 = st.columns(2)
        with st_col1:
            st.write("**📍 Aktobe (thousands)**")
            st.area_chart(pd.DataFrame({"Year": years, "Patients": aktobe_vals}).set_index("Year"), color="rgb(56, 178, 172)")
        with st_col2:
            st.write("**🌍 World (millions)**")
            st.line_chart(pd.DataFrame({"Year": years, "Patients": world_vals}).set_index("Year"), color="rgb(44, 82, 130)")

    with t2:
        st.markdown("<h3>🌟 Celebrities with Diabetes</h3>", unsafe_allow_html=True)
        categories = {
            "🎬 Cinema and Show Business": [
                ("George Lucas", "Creator of Star Wars. Found out about Type 2 at age 23. It helped him avoid the draft and focus on cinema. He has lived with it for over 50 years!"),
                ("Sylvester Stallone", "The legendary Rocky lives with Type 1. His physical form proves that discipline and sugar control can make you a superstar."),
                ("Lila Moss", "Daughter of Kate Moss. She made waves by walking the runway with her Omnipod insulin pump visible on her thigh, becoming an icon for T1D teens."),
                ("Mikhail Boyarsky", "Russia's main 'D'Artagnan' has lived with diabetes for many years. He strictly follows his diet and medication, proving age is no barrier."),
                ("Eldar Dzharakhov", "Popular musician. Openly talks about his life with T1D, helping millions of followers stay positive through humor."),
                ("Salma Hayek", "Faced gestational diabetes during pregnancy. It taught her to value healthy eating and listen to her body's signals."),
                ("James Norton", "British actor. Calls diabetes his 'superpower' because it developed incredible empathy in him. He sometimes hides glucose tabs in his costumes.")
            ],
            "🏆 Sports Legends": [
                ("Pele", "The King of Football. Diagnosed with Type 1 at age 17 at the start of his path. It didn't stop him from becoming a 3-time World Champion."),
                ("Alexander Zverev", "Olympic tennis champion. Hid his T1D for a long time, but now openly injects insulin on court during breaks."),
                ("Bobby Clarke", "NHL legend. At 13, he was told he'd never play pro. He became captain of the Flyers and won two Stanley Cups."),
                ("Nacho Fernandez", "Real Madrid defender. Doctors predicted the end of his career at 12. He won 6 Champions Leagues with perfect control."),
                ("Nikita Kucherov", "NHL star. Handles colossal loads, serving as an example of iron will for all athletes with diabetes.")
            ],
            "🎤 Music and Art": [
                ("Nick Jonas", "Member of Jonas Brothers. Diagnosed at 13. Founded 'Beyond Type 1'. His song 'A Little Bit Longer' is dedicated to the struggle."),
                ("Ella Fitzgerald", "The First Lady of Song. Fought Type 2 most of her life while recording world hits until old age."),
                ("Sharon Stone", "Movie star with T1D. Combines yoga and meditation to control sugar through stress management."),
                ("Halle Berry", "First Black actress to win an Oscar. Fell into a coma on set at 19, then changed her life entirely using a keto diet."),
                ("Vanessa Williams", "Singer and actress. Actively supports T1D communities for many years.")
            ],
            "📖 Historical Figures": [
                ("Ernest Hemingway", "The great writer lived with 'bronze diabetes'. Despite this, he created masterpieces and led an extreme lifestyle."),
                ("Paul Cezanne", "Father of modern art. Created his great canvases despite severe diabetes in the pre-insulin era."),
                ("Tom Hanks", "Diagnosed with Type 2 in 2013. Believes it resulted from a lazy lifestyle in his youth and is now a weight control advocate.")
            ]
        }
        for cat_name, members in categories.items():
            st.subheader(cat_name)
            for name, bio in members:
                with st.expander(f"👤 {name}"): st.write(bio)
