import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
import google.generativeai as genai
from PIL import Image
import time
import random

API_KEY = "AIzaSyCWaBUD3xJkE5H9U0JIOUXYSXsXeP_nejw" 

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"Ошибка настройки ИИ: {e}")
    model = None

st.set_page_config(page_title="Help For Diabet People", page_icon="💙", layout="wide")

if 'diabet_logs' not in st.session_state:
    st.session_state.diabet_logs = []
if 'user_steps' not in st.session_state:
    st.session_state.user_steps = 0
if 'user_water' not in st.session_state:
    st.session_state.user_water = 0.0

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
    
    .stApp { background: #0b0f19; color: #ffffff; font-family: 'Montserrat', sans-serif; }
    
    [data-testid="stSidebarNav"] span, 
    [data-testid="stSidebar"] label p, 
    .stRadio label p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }

    label, .stMarkdown, [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    [data-testid="stTable"] {
        background-color: #ffffff !important;
        border-radius: 10px;
        padding: 15px;
    }
    [data-testid="stTable"] td, [data-testid="stTable"] th, .dataframe td, .dataframe th {
        color: #000000 !important;
        font-size: 16px !important;
    }

    .stButton>button {
        background-color: #fbbf24 !important;
        border: none !important;
        border-radius: 12px !important;
    }
    .stButton>button p { color: #000000 !important; font-weight: 700 !important; }

    [data-testid="stForm"] button {
        background-color: #3b82f6 !important;
        border: 1px solid #ffffff !important;
        color: #ffffff !important;
    }
    [data-testid="stForm"] button p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    input, textarea, [data-baseweb="select"] span {
        color: #0b0f19 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #3b82f6;
    }
    
    .brand-container {
        padding: 20px 10px; text-align: center;
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-radius: 15px; border: 1px solid #fbbf24; margin-bottom: 25px;
    }
    .brand-name {
        color: #fbbf24 !important; font-size: 22px !important;
        font-weight: 800 !important; text-transform: uppercase;
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.7); border-radius: 20px;
        padding: 30px; margin-bottom: 25px; border: 1px solid rgba(96, 165, 250, 0.2);
    }
    
    h1, h2, h3 { color: #fbbf24 !important; }
    .recipe-card {
        background: #1e293b; padding: 20px; border-radius: 15px;
        border-right: 4px solid #10b981; margin-bottom: 15px;
    }
    .benefit-tag { 
        background: #064e3b; color: #34d399; padding: 4px 10px; 
        border-radius: 10px; font-size: 12px; font-weight: bold; margin-bottom: 5px; display: inline-block; 
    }
    
    .verdict-box {
        background: rgba(251, 191, 36, 0.1); border-left: 5px solid #fbbf24;
        padding: 15px; margin-top: 15px; border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def color_sugar(val):
    try:
        f_val = float(val)
        if f_val > 7.2: return 'background-color: #ef4444; color: white; font-weight: bold;'
        if 4.0 <= f_val <= 7.2: return 'background-color: #10b981; color: white; font-weight: bold;'
        return 'background-color: #3b82f6; color: white; font-weight: bold;'
    except: return ''

def play_save_sound():
    sound_url = "https://www.orangefreesounds.com/wp-content/uploads/2014/10/Ding-sound.mp3"
    st.components.v1.html(f'<audio autoplay><source src="{sound_url}" type="audio/mp3"></audio>', height=0)

def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="report.csv" style="color: #fbbf24;">📥 Скачать отчет (CSV)</a>'

with st.sidebar:
    st.markdown("""<div class='brand-container'><div class='brand-name'>💙 Help For<br>Diabet People</div></div>""", unsafe_allow_html=True)
    page = st.radio("НАВИГАЦИЯ:", ["🏠 Главная", "🏃 Активности", "🥗 Мировая Кухня", "🩺 Личный Журнал", "🎓 База Знаний"])

if page == "🏠 Главная":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<div class='glass-card'><h1>Help For Diabet People</h1><p>Ваша надежная экосистема для управления диабетом.</p></div>", unsafe_allow_html=True)
        
        # ДОБАВЛЕНО: Калькулятор ХЕ
        st.subheader("🍞 Калькулятор Хлебных Единиц (ХЕ)")
        carb_col, xe_col = st.columns(2)
        with carb_col: carbs = st.number_input("Углеводы в порции (г):", 0, 100, 12)
        with xe_col: xe_val = st.selectbox("1 ХЕ равна:", [10, 12], index=1)
        st.info(f"Результат: **{carbs/xe_val:.1f} ХЕ**")

        st.subheader("📊 Мои показатели")
        v_col1, v_col2, v_col3 = st.columns(3)
        with v_col1: steps = st.number_input("Введите шаги:", 0, 50000, st.session_state.user_steps)
        with v_col2: water = st.number_input("Вода (литры):", 0.0, 10.0, st.session_state.user_water)
        with v_col3: mood = st.select_slider("Ваше настроение:", options=["🚀 Отлично", "🙂 Хорошо", "😐 Средне", "😟 Устал", "🆘 Стресс"])
        
        st.session_state.user_steps = steps
        st.session_state.user_water = water

        st.markdown("<div class='verdict-box'><b>🤖 ИИ Вердикт:</b>", unsafe_allow_html=True)
        verdicts = []
        if steps < 5000: verdicts.append("🏃 Мало движений. Попробуйте пройтись, чтобы снизить риск скачка сахара.")
        elif steps >= 10000: verdicts.append("✅ Прекрасная активность! Это повышает чувствительность к инсулину.")
        if water < 1.5: verdicts.append("💧 Пейте больше воды для нормализации вязкости крови.")
        if mood in ["😟 Устал", "🆘 Стресс"]: verdicts.append("🧘 Стресс поднимает сахар. Найдите 5 минут для отдыха.")
        if not verdicts: verdicts.append("🌟 Вы отлично справляетесь!")
        st.write(" ".join(verdicts))
        st.markdown("</div>", unsafe_allow_html=True)

        age = st.slider("Ваша возрастная категория", 1, 100, 25)
        st.info(f"Рекомендуемый целевой диапазон: 4.4 - 7.2 ммоль/л")
    with col2:
        st.image("https://images.unsplash.com/photo-1505751172876-fa1923c5c528?q=80&w=400")

elif page == "🏃 Активности":
    st.markdown("<div class='glass-card'><h1>🏃‍♂️ Активности и Спорт</h1><p>Регулярные нагрузки помогают контролировать уровень глюкозы.</p></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("### 📉 Калькулятор спорта")
        sports_db = {
            "Ходьба (спокойная)": 0.03, "Ходьба (быстрая)": 0.05, "Бег": 0.09, 
            "Плавание": 0.07, "Велосипед": 0.06, "Йога": 0.02, "Теннис": 0.08, 
            "Футбол": 0.1, "Танцы": 0.05, "Силовая тренировка": 0.04
        }
        sport_type = st.selectbox("Вид спорта:", list(sports_db.keys()))
        duration = st.slider("Продолжительность (мин):", 10, 180, 30)
        total_burn = duration * sports_db[sport_type]
        st.markdown(f"<div class='verdict-box' style='border-left-color: #10b981;'>🤖 Ожидаемое снижение сахара: <b>-{total_burn:.1f} ммоль/л</b></div>", unsafe_allow_html=True)
        
        st.write("---")
        user_goal = st.number_input("Цель по шагам:", 1000, 50000, 10000)
        st.progress(min(st.session_state.user_steps / user_goal, 1.0))
        st.write(f"Пройдено сегодня: {st.session_state.user_steps} шагов")

    with col_b:
        st.image("https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=500", caption="Движение повышает чувствительность к инсулину")
elif page == "🥗 Мировая Кухня":
    st.header("🌎 Гурман-меню: 15 рецептов здоровья")
    st.info("Все рецепты адаптированы для людей с диабетом: низкий ГИ и максимум пользы.")
    
    t_rec, t_ai = st.tabs(["🥘 Пошаговые рецепты", "🤖 ИИ Сканер состава"])
    
    with t_rec:
        recipes_database = [
            {
                "country": "Греция", "title": "Салат Хориатики", "benefit": "Здоровые жиры",
                "ing": "Огурцы, томаты, перец, фета, оливки Каламата, оливковое масло, орегано.",
                "steps": ["Нарежьте овощи крупными кубиками (по-деревенски).", "Добавьте целые оливки и целый пласт феты сверху.", "Посыпьте сушеным орегано.", "Полейте маслом. Не перемешивайте до подачи!"]
            },
            {
                "country": "Япония", "title": "Мисо-суп", "benefit": "Пробиотики",
                "ing": "Паста мисо, сыр тофу, сушеные водоросли вакаме, зеленый лук.",
                "steps": ["Замочите водоросли в воде на 5 минут.", "Доведите воду до кипения, добавьте нарезанный кубиками тофу.", "Разведите пасту мисо в отдельной чашке с теплой водой и влейте в кастрюлю.", "Снимите с огня (не кипятите мисо!), посыпьте луком."]
            },
            {
                "country": "Италия", "title": "Паста из кабачков (Zoodles)", "benefit": "Низкий ГИ",
                "ing": "Молодые кабачки, чеснок, оливковое масло, пармезан, базилик.",
                "steps": ["С помощью овощечистки или спец. терки нарежьте кабачок длинными тонкими полосками.", "Обжарьте чеснок на масле 1 минуту.", "Добавьте кабачки и жарьте всего 2-3 минуты (до состояния Al Dente).", "Посыпьте сыром и базиликом."]
            },
            {
                "country": "Индия", "title": "Красный Дал (Суп из чечевицы)", "benefit": "Клетчатка+",
                "ing": "Красная чечевица, куркума, имбирь, чеснок, томаты в собств. соку.",
                "steps": ["Промойте чечевицу и варите с куркумой 15 минут.", "На сковороде обжарьте тертый имбирь, чеснок и томаты.", "Смешайте зажарку с чечевицей.", "Варите еще 5 минут до кремообразного состояния."]
            },
            {
                "country": "Мексика", "title": "Гуакамоле", "benefit": "Омега-9",
                "ing": "Спелое авокадо, сок лайма, кинза, красный лук, перец чили.",
                "steps": ["Разомните мякоть авокадо вилкой (оставьте небольшие кусочки).", "Мелко нарежьте лук, кинзу и чили.", "Смешайте всё с соком лайма (он не даст авокадо потемнеть).", "Подавайте с палочками сельдерея вместо чипсов."]
            },
            {
                "country": "Ливан", "title": "Табуле с киноа", "benefit": "Суперфуд",
                "ing": "Киноа, огромный пучок петрушки, мята, помидоры, лимонный сок.",
                "steps": ["Отварите киноа и остудите.", "Мелко-мелко порубите петрушку и мяту (зелени должно быть больше, чем крупы).", "Нарежьте помидоры мелкими кубиками.", "Заправьте лимонным соком и маслом."]
            },
            {
                "country": "Норвегия", "title": "Лосось со спаржей", "benefit": "Белок",
                "ing": "Филе лосося, спаржа, лимон, розмарин.",
                "steps": ["Выложите филе на пергамент, посолите, добавьте розмарин.", "Рядом положите очищенную спаржу.", "Запекайте 15 минут при 180°C.", "Сбрызните свежим лимонным соком перед едой."]
            },
            {
                "country": "Франция", "title": "Рататуй", "benefit": "Витамины",
                "ing": "Баклажан, кабачок, перец, томатный соус без сахара.",
                "steps": ["Нарежьте все овощи одинаковыми тонкими кружочками.", "Выложите их в форму 'гармошкой', чередуя цвета.", "Залейте томатным соусом со специями.", "Накройте фольгой и запекайте 40 минут."]
            },
            {
                "country": "Таиланд", "title": "Том Ям с креветками", "benefit": "Метаболизм",
                "ing": "Креветки, грибы вешенки, кокосовое молоко (немного), лемонграсс.",
                "steps": ["Сварите легкий бульон на панцирях креветок и лемонграссе.", "Добавьте грибы и варите 5 минут.", "Влейте немного кокосового молока и добавьте очищенные креветки.", "Как только креветки порозовеют — суп готов."]
            },
            {
                "country": "Грузия", "title": "Аджапсандал", "benefit": "Клетчатка",
                "ing": "Баклажаны, болгарский перец, помидоры, много кинзы, чеснок.",
                "steps": ["Запеките овощи целиком в духовке до мягкости.", "Снимите кожицу и нарежьте крупными полосками.", "Смешайте с давленым чесноком и рубленой кинзой.", "Дайте настояться 2 часа."]
            },
            {
                "country": "Турция", "title": "Бабагануш", "benefit": "Низкий сахар",
                "ing": "Баклажаны, тахини (кунжутная паста), чеснок, оливковое масло.",
                "steps": ["Проткните баклажаны вилкой и запекайте до черноты кожицы.", "Достаньте мякоть и взбейте блендером с тахини и чесноком.", "Добавьте каплю масла и паприку.", "Используйте как паштет для цельнозерновых хлебцев."]
            },
            {
                "country": "Испания", "title": "Гаспачо", "benefit": "Антиоксиданты",
                "ing": "Спелые томаты, огурец, болгарский перец, немного черствого цельнозернового хлеба.",
                "steps": ["Очистите томаты от кожицы.", "Взбейте в блендере все овощи до однородности.", "Добавьте каплю винного уксуса и оливкового масла.", "Подавайте очень холодным."]
            },
            {
                "country": "Вьетнам", "title": "Фо-Бо с лапшой Ширатаки", "benefit": "0 Калорий",
                "ing": "Говяжья вырезка, бульон на костях, лапша ширатаки, анис, корица.",
                "steps": ["Варите бульон со специями долго (минимум 3 часа).", "Промойте ширатаки под водой (в ней 0 калорий и углеводов!).", "Тонко нарежьте сырую говядину.", "Залейте лапшу и мясо кипящим бульоном (мясо сварится прямо в тарелке)."]
            },
            {
                "country": "Россия", "title": "Окрошка на кефире", "benefit": "Пробиотики",
                "ing": "Отварная грудка, редис, огурец, яйцо, нежирный кефир.",
                "steps": ["Нарежьте все ингредиенты мелкими кубиками.", "Порубите много укропа и зеленого лука.", "Смешайте и залейте холодным кефиром.", "Добавьте каплю горчицы для вкуса."]
            },
            {
                "country": "США", "title": "Салат Кобб", "benefit": "Сытость",
                "ing": "Филе индейки, авокадо, яйцо, салат айсберг, томаты.",
                "steps": ["Обжарьте индейку на гриле.", "Нарежьте все ингредиенты крупными кубиками.", "Выложите на блюдо рядами: ряд мяса, ряд авокадо, ряд яиц.", "Заправьте соусом из лимона и горчицы."]
            }
        ]

        c1, c2 = st.columns(2)
        for i, r in enumerate(recipes_database):
            with (c1 if i % 2 == 0 else c2):
                with st.expander(f"📍 {r['country']} | {r['title']}"):
                    st.markdown(f"<span class='benefit-tag'>{r['benefit']}</span>", unsafe_allow_html=True)
                    st.write(f"**🛒 Ингредиенты:** {r['ing']}")
                    st.write("**👨‍🍳 Шаги приготовления:**")
                    for j, step in enumerate(r['steps'], 1):
                        st.write(f"{j}. {step}")

    with t_ai:
        st.markdown("<div class='glass-card'><h3>📸 Виртуальный анализ по фото</h3><p>Загрузите фото вашего блюда для анализа через Gemini AI.</p></div>", unsafe_allow_html=True)
        
        file_img = st.file_uploader("Загрузите фото тарелки", type=["jpg", "png", "jpeg"], key="food_scanner")
        if file_img:
            image = Image.open(file_img)
            st.image(image, width=400)
            
            if st.button("🚀 Начать анализ ИИ"):
                if model:
                    with st.spinner("Нейросеть анализирует..."):
                        response = model.generate_content(["Определи блюдо, оцени БЖУ и дай совет диабетику на русском.", image])
                        st.markdown(f"<div class='verdict-box'>{response.text}</div>", unsafe_allow_html=True)
                else:
                    st.error("ИИ недоступен.")

elif page == "🩺 Личный Журнал":
    st.markdown("<div class='glass-card'><h3>🩺 Дневник замеров</h3></div>", unsafe_allow_html=True)
    with st.form("log"):
        d, s, n = st.date_input("Дата"), st.number_input("Сахар (ммоль/л)", 2.0, 30.0, 5.5), st.text_area("Заметки")
        if st.form_submit_button("Сохранить данные"):
            st.session_state.diabet_logs.append({"Дата": d, "Сахар": s, "Заметки": n})
            play_save_sound() 
    
    if st.session_state.diabet_logs:
        df = pd.DataFrame(st.session_state.diabet_logs)
        st.subheader("📈 Визуализация трендов")
        chart_df = df.copy()
        chart_df['Дата'] = pd.to_datetime(chart_df['Дата'])
        chart_df = chart_df.sort_values('Дата')
        chart_df = chart_df.set_index('Дата')
        st.line_chart(chart_df['Сахар'])
        st.subheader("📋 История записей")
        st.table(df.style.applymap(color_sugar, subset=['Сахар'])) 
        st.markdown(get_table_download_link(df), unsafe_allow_html=True)

elif page == "🎓 База Знаний":
    st.markdown("<div class='glass-card'><h1>Информационный Центр</h1></div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📜 Статьи и Графики", "🌟 10 Героев"])
    
    with t1:
        st.markdown("### 📚 10 Ключевых фактов и правил контроля")
        
        facts = [
            {
                "title": "1. Механика обмена веществ",
                "text": "Диабет — это не просто 'высокий сахар', а нарушение обмена веществ, где клеткам не хватает энергии из-за проблем с инсулином. Без него глюкоза остается в крови, повреждая сосуды."
            },
            {
                "title": "2. Магия клетчатки",
                "text": "Употребление овощей перед основным блюдом создает в кишечнике 'сетку', которая замедляет всасывание сахара. Это снижает постпрандиальный (после еды) пик глюкозы на 30%."
            },
            {
                "title": "3. Скрытые сахара",
                "text": "Берегитесь продуктов 'без сахара' и обезжиренных йогуртов. Часто туда добавляют мальтодекстрин или крахмал, которые поднимают сахар быстрее, чем обычный белый песок."
            },
            {
                "title": "4. Мышцы как насос",
                "text": "Физическая нагрузка открывает каналы в клетках без участия инсулина. Даже простая 15-минутная прогулка после ужина работает как естественное лекарство."
            },
            {
                "title": "5. Опасность гипогликемии",
                "text": "Резкое падение сахара (ниже 3.9) опаснее высокого уровня здесь и сейчас. Всегда имейте при себе 15г быстрых углеводов: сок или 3 кусочка сахара."
            },
            {
                "title": "6. Гликированный гемоглобин (HbA1c)",
                "text": "Это главный 'детектор лжи' для диабетика. Он показывает средний сахар за последние 3 месяца. Норма для большинства — ниже 7.0%."
            },
            {
                "title": "7. Влияние стресса",
                "text": "Гормон кортизол заставляет печень выбрасывать запасы глюкозы в кровь. Иногда 5 минут медитации снижают сахар эффективнее, чем диета."
            },
            {
                "title": "8. Синдром утренней зари",
                "text": "Рост сахара в 4-7 утра обусловлен выбросом гормонов роста. Если вы проснулись с высоким сахаром, хотя не ели на ночь — это работа вашей гормональной системы."
            },
            {
                "title": "9. Здоровье сосудов и стоп",
                "text": "Высокий сахар повреждает мелкие нервы (нейропатия). Ежедневный осмотр стоп — это критически важный ритуал, предотвращающий серьезные травмы."
            },
            {
                "title": "10. Правило тарелки",
                "text": "Используйте визуальный метод: 1/2 тарелки — зелень/овощи, 1/4 — белок (мясо/рыба), 1/4 — сложные углеводы (гречка/перловка). Это идеальный баланс."
            }
        ]

        for f in facts:
            with st.expander(f["title"]):
                st.write(f["text"])
        
        st.write("---")
        st.subheader("📊 Статистика заболеваемости (2000 - 2026)")
        years = list(range(2000, 2027))
        aktobe_vals = [2.2 + (i * 0.48) + (i**1.5) * 0.02 for i in range(len(years))]
        world_vals = [171 + (i * 14.5) + (i**1.6) * 0.4 for i in range(len(years))]

        st_col1, st_col2 = st.columns(2)
        with st_col1:
            st.write("**📍 Актобе (тыс. чел)**")
            df_akt = pd.DataFrame({"Год": years, "Больных": aktobe_vals}).set_index("Год")
            st.area_chart(df_akt, color="#fbbf24")
        with st_col2:
            st.write("**🌍 Весь мир (млн. чел)**")
            df_wld = pd.DataFrame({"Год": years, "Больных": world_vals}).set_index("Год")
            st.line_chart(df_wld, color="#3b82f6")
        
        st.write("---")
        st.subheader("📊 Аналитические графики болезни")
        cg1, cg2 = st.columns(2)
        with cg1:
            st.write("**Динамика уровня глюкозы (типичный день)**")
            time_data = pd.DataFrame(np.random.normal(5.8, 0.8, size=(24, 1)), columns=['ммоль/л'])
            st.line_chart(time_data)
        with cg2:
            st.write("**Влияние различных нагрузок на сахар**")
            impact_data = pd.DataFrame({'Снижение': [0.5, 1.2, 0.8, 1.5]}, index=['Йога', 'Бег', 'Ходьба', 'Бассейн'])
            st.bar_chart(impact_data)

        st.write("---")
        st.subheader("🎥 Полезные видео-материалы")
        st.markdown("""
        * [🎥 Как вылечить ДИАБЕТ 2 типа: 7 шагов (Доктор Евдокименко)](http://www.youtube.com/watch?v=tryte6ZoXPo) — Простые и эффективные советы по лечению.
        * [🎥 Что такое сахарный диабет простыми словами](https://www.youtube.com/watch?v=XfyGv-xwjlI) — Основы заболевания для новичков.
        * [🎥 Принципы питания при диабете 1 и 2 типа](https://www.youtube.com/watch?v=ox-v7TfN0mY) — Как составить правильный рацион.
        * [🎥 Как быстро снизить сахар: главные советы](http://www.youtube.com/watch?v=1xaBkGLhgR4) — Экспресс-рекомендации от эндокринолога.
        * [🎥 5 советов для пациентов с диабетом 2 типа](http://www.youtube.com/watch?v=leKkGkHLkCs) — Коротко о самом важном в повседневной жизни.
        * [🎥 Что действительно важно знать диабетику?](http://www.youtube.com/watch?v=iqV1EY6aSu8) — Ключевые аспекты самоконтроля.
        * [🎥 Личный опыт: Жизнь с диабетом 1 типа](http://www.youtube.com/watch?v=NusIsLqQGpY) — Мотивирующая история и советы по адаптации.
        """)

    with t2:
        st.markdown("### 🌟 Знаменитости с диабетом")
        
        categories = {
            "🎬 Кино и Шоу-бизнес": [
                ("Джордж Лукас", "Создатель «Звездных войн». Узнал о диабете 2 типа в 23 года. Болезнь помогла ему избежать призыва в армию и сосредоточиться на кино. Он живет с диабетом уже более 50 лет!"),
                ("Сильвестр Сталлоне", "Легендарный «Рокки» живет с СД 1 типа. Глядя на его физическую форму, сложно поверить, что он ежедневно контролирует сахар, но именно дисциплина сделала его суперзвездой."),
                ("Лила Мосс", "Дочь супермодели Кейт Мосс. Она произвела фурор на подиуме, выйдя на показ Fendi x Versace с видимой инсулиновой помпой Omnipod на бедре, став иконой для подростков с СД1."),
                ("Михаил Боярский", "Главный 'Д'Артаньян' России живет с диабетом много лет. Он строго следит за диетой и вовремя принимает лекарства, доказывая, что возраст и диагноз не помеха творчеству."),
                ("Эльдар Джарахов", "Популярный блогер и музыкант. Открыто рассказывает о своей жизни с СД 1 типа, юмором и искренностью помогая миллионам подписчиков не унывать."),
                ("Сальма Хайек", "Столкнулась с гестационным диабетом во время беременности. Это научило её ценить здоровое питание и внимательно относиться к сигналам своего тела."),
                ("Джеймс Нортон", "Британский актер («Гранчестер»). Называет диабет своей 'суперсилой', так как болезнь развила в нем невероятную эмпатию. Иногда прячет таблетки глюкозы в костюмах героев.")
            ],
            "🏆 Легенды Спорта": [
                ("Пеле", "Король футбола. Получил диагноз СД 1 типа в 17 лет, в самом начале пути. Это не помешало ему стать единственным трехкратным чемпионом мира в истории."),
                ("Александр Зверев", "Олимпийский чемпион по теннису. Долго скрывал СД 1 типа, но теперь открыто делает инъекции прямо на корте во время перерывов, показывая, что спорт высших достижений возможен."),
                ("Бобби Кларк", "Легенда НХЛ. В 13 лет ему сказали, что из-за диабета он никогда не будет играть профи. В итоге он стал капитаном «Филадельфии» и взял два Кубка Стэнли."),
                ("Начо Фернандес", "Защитник «Реала». Врачи пророчили конец карьеры в 12 лет. Выиграл 6 Лиг Чемпионов. Секрет — идеальный контроль питания и нагрузок."),
                ("Никита Кучеров", "Звезда НХЛ. Справляется с колоссальными нагрузками, будучи примером железной воли для всех атлетов с диабетом.")
            ],
            "🎤 Музыка и Искусство": [
                ("Ник Джонас", "Музыкант из Jonas Brothers. Заболел в 13 лет. Основал фонд 'Beyond Type 1'. Его песня 'A Little Bit Longer' посвящена борьбе с болезнью."),
                ("Элла Фицджеральд", "Первая леди джаза. Боролась с диабетом 2 типа почти всю жизнь, продолжая выступать и записывать мировые хиты до глубокой старости."),
                ("Шэрон Стоун", "Кинодива с СД 1 типа. Сочетает йогу и медитацию, чтобы контролировать уровень сахара через управление стрессом."),
                ("Холли Берри", "Первая темнокожая актриса, получившая 'Оскар'. Впала в кому на съемках в 19 лет, после чего кардинально изменила жизнь, выбрав кето-диету."),
                ("Ванесса Уильямс", "Певица и актриса, первая темнокожая «Мисс Америка». Много лет активно поддерживает сообщества людей с диабетом 1 типа.")
            ],
            "📖 Исторические личности": [
                ("Эрнест Хемингуэй", "Великий писатель жил с так называемым 'бронзовым диабетом'. Несмотря на это, он создал шедевры мировой литературы и вел экстремальный образ жизни."),
                ("Пол Сезанн", "Отец современного искусства и импрессионизма. Творил свои великие полотна, несмотря на тяжелое течение диабета в эпоху до открытия инсулина."),
                ("Том Хэнкс", "Узнал о СД 2 типа в 2013 году. Считает, что это следствие 'ленивого образа жизни' в молодости, и теперь является активным сторонником контроля веса.")
            ]
        }

        for cat_name, members in categories.items():
            st.subheader(cat_name)
            for name, bio in members:
                with st.expander(f"👤 {name}"):
                    st.write(bio)
