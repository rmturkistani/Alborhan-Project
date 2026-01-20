# razan.m.alturkistany@gmail.com

import streamlit as st
from huggingface_hub import InferenceClient
import pandas as pd
import io
import random
import math
import json

RAW_TOKEN = st.secrets["RAW_TOKEN"]
HF_TOKEN = RAW_TOKEN.strip()
client = InferenceClient(api_key=HF_TOKEN)

# إعداد الصفحة (العنوان الذي يظهر في المتصفح)
st.set_page_config(page_title="مَورِد | خدمة المساعد الذكي", layout="wide")

# CSS مخصص لجعل الواجهة احترافية
st.markdown("""
    <style>
    
    /* تنسيق العنوان الرئيسي بالأسود */
    .main-title {
        font-size: 36px;
        font-weight: bold;
        color: #000000;
        text-align: center;
        margin-bottom: 30px;
    }
    
    h3 {
        text-align: center;
    }
    
    /* اسم المنصة في الزاوية */
    .platform-name {
        position: absolute;
        top: -50px;
        left: 10px;
        font-size: 20px;
        font-weight: bold;
        color: #4A4A4A;
    }
    
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
        transition: transform 0.2s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }       

    .card:hover {
        transform: scale(1.01);
        border-color: #1E3A8A;
    }
    
    .match-score {
        font-weight: bold;
        color: #059669; /* أخضر */
        font-size: 1.1em;
    }
    
    .dist-score {
        color: #DC2626; /* أحمر */
        font-size: 0.9em;
    }
    
    </style>
    """, unsafe_allow_html=True)

# قاعدة بيانات المراكز
@st.cache_data
def get_centers_data():
    cities = {
        "الرياض": {"lat": 24.7136, "lon": 46.6753},
        "جدة": {"lat": 21.5433, "lon": 39.1728},
        "مكة": {"lat": 21.3891, "lon": 39.8579},
        "المدينة": {"lat": 24.5247, "lon": 39.5692},
        "الدمام": {"lat": 26.4207, "lon": 50.0888}
    }
    names = ["البيان", "الهدى", "النور", "الفرقان", "التقوى", "الإيمان"]
    specials = ["لا يوجد", "ذوي الإعاقة السمعية", "ذوي الإعاقة البصرية"]
    data = []
    for i in range(100):
        city_name = random.choice(list(cities.keys()))
        base_coords = cities[city_name]
        
        # محاكاة الانحراف في الموقع (ضمن نطاق 15 كم من وسط المدينة)
        # 0.1 درجة تعادل تقريباً 11 كم
        lat_dev = random.uniform(-0.15, 0.15)
        lon_dev = random.uniform(-0.15, 0.15)

        data.append({
            "id": i,
            "name": f"جمعية {random.choice(names)} ({i+1}) لتحفيظ القرآن",
            "city": city_name,
            "lat": base_coords["lat"] + lat_dev,
            "lon": base_coords["lon"] + lon_dev,
            "level": random.choice([["مبتدئ"], ["متوسط", "متقدم"], ["مبتدئ", "متوسط", "متقدم"]]),
            "target_age_min": random.randint(5, 18),
            "target_age_max": random.randint(20, 80),
            "special": random.choice(specials),
            "gender": random.choice(["ذكر", "أنثى"]),
            "mode": random.choice(["حضوري", "عن بعد"]),
        })
    return data

CENTERS = get_centers_data()

surahs = [
    {"id": 1, "name": "الفاتحة", "ayahs": 7},
    {"id": 2, "name": "البقرة", "ayahs": 286},
    {"id": 3, "name": "آل عمران", "ayahs": 200},
    {"id": 4, "name": "النساء", "ayahs": 176},
    {"id": 5, "name": "المائدة", "ayahs": 120},
    {"id": 6, "name": "الأنعام", "ayahs": 165},
    {"id": 7, "name": "الأعراف", "ayahs": 206},
    {"id": 8, "name": "الأنفال", "ayahs": 75},
    {"id": 9, "name": "التوبة", "ayahs": 129},
    {"id": 10, "name": "يونس", "ayahs": 109},
    {"id": 11, "name": "هود", "ayahs": 123},
    {"id": 12, "name": "يوسف", "ayahs": 111},
    {"id": 13, "name": "الرعد", "ayahs": 43},
    {"id": 14, "name": "إبراهيم", "ayahs": 52},
    {"id": 15, "name": "الحجر", "ayahs": 99},
    {"id": 16, "name": "النحل", "ayahs": 128},
    {"id": 17, "name": "الإسراء", "ayahs": 111},
    {"id": 18, "name": "الكهف", "ayahs": 110},
    {"id": 19, "name": "مريم", "ayahs": 98},
    {"id": 20, "name": "طه", "ayahs": 135},
    {"id": 21, "name": "الأنبياء", "ayahs": 112},
    {"id": 22, "name": "الحج", "ayahs": 78},
    {"id": 23, "name": "المؤمنون", "ayahs": 118},
    {"id": 24, "name": "النور", "ayahs": 64},
    {"id": 25, "name": "الفرقان", "ayahs": 77},
    {"id": 26, "name": "الشعراء", "ayahs": 227},
    {"id": 27, "name": "النمل", "ayahs": 93},
    {"id": 28, "name": "القصص", "ayahs": 88},
    {"id": 29, "name": "العنكبوت", "ayahs": 69},
    {"id": 30, "name": "الروم", "ayahs": 60},
    {"id": 31, "name": "لقمان", "ayahs": 34},
    {"id": 32, "name": "السجدة", "ayahs": 30},
    {"id": 33, "name": "الأحزاب", "ayahs": 73},
    {"id": 34, "name": "سبإ", "ayahs": 54},
    {"id": 35, "name": "فاطر", "ayahs": 45},
    {"id": 36, "name": "يس", "ayahs": 83},
    {"id": 37, "name": "الصافات", "ayahs": 182},
    {"id": 38, "name": "ص", "ayahs": 88},
    {"id": 39, "name": "الزمر", "ayahs": 75},
    {"id": 40, "name": "غافر", "ayahs": 85},
    {"id": 41, "name": "فصلت", "ayahs": 54},
    {"id": 42, "name": "الشورى", "ayahs": 53},
    {"id": 43, "name": "الزخرف", "ayahs": 89},
    {"id": 44, "name": "الدخان", "ayahs": 59},
    {"id": 45, "name": "الجاثية", "ayahs": 37},
    {"id": 46, "name": "الأحقاف", "ayahs": 35},
    {"id": 47, "name": "محمد", "ayahs": 38},
    {"id": 48, "name": "الفتح", "ayahs": 29},
    {"id": 49, "name": "الحجرات", "ayahs": 18},
    {"id": 50, "name": "ق", "ayahs": 45},
    {"id": 51, "name": "الذاريات", "ayahs": 60},
    {"id": 52, "name": "الطور", "ayahs": 49},
    {"id": 53, "name": "النجم", "ayahs": 62},
    {"id": 54, "name": "القمر", "ayahs": 55},
    {"id": 55, "name": "الرحمن", "ayahs": 78},
    {"id": 56, "name": "الواقعة", "ayahs": 96},
    {"id": 57, "name": "الحديد", "ayahs": 29},
    {"id": 58, "name": "المجادلة", "ayahs": 22},
    {"id": 59, "name": "الحشر", "ayahs": 24},
    {"id": 60, "name": "الممتحنة", "ayahs": 13},
    {"id": 61, "name": "الصف", "ayahs": 14},
    {"id": 62, "name": "الجمعة", "ayahs": 11},
    {"id": 63, "name": "المنافقون", "ayahs": 11},
    {"id": 64, "name": "التغابن", "ayahs": 18},
    {"id": 65, "name": "الطلاق", "ayahs": 12},
    {"id": 66, "name": "التحريم", "ayahs": 12},
    {"id": 67, "name": "الملك", "ayahs": 30},
    {"id": 68, "name": "القلم", "ayahs": 52},
    {"id": 69, "name": "الحاقة", "ayahs": 52},
    {"id": 70, "name": "المعارج", "ayahs": 44},
    {"id": 71, "name": "نوح", "ayahs": 28},
    {"id": 72, "name": "الجن", "ayahs": 28},
    {"id": 73, "name": "المزمل", "ayahs": 20},
    {"id": 74, "name": "المدثر", "ayahs": 56},
    {"id": 75, "name": "القيامة", "ayahs": 40},
    {"id": 76, "name": "الإنسان", "ayahs": 31},
    {"id": 77, "name": "المرسلات", "ayahs": 50},
    {"id": 78, "name": "النبإ", "ayahs": 40},
    {"id": 79, "name": "النازعات", "ayahs": 46},
    {"id": 80, "name": "عبس", "ayahs": 42},
    {"id": 81, "name": "التكوير", "ayahs": 29},
    {"id": 82, "name": "الانفطار", "ayahs": 19},
    {"id": 83, "name": "المطففين", "ayahs": 36},
    {"id": 84, "name": "الانشقاق", "ayahs": 25},
    {"id": 85, "name": "البروج", "ayahs": 22},
    {"id": 86, "name": "الطارق", "ayahs": 17},
    {"id": 87, "name": "الأعلى", "ayahs": 19},
    {"id": 88, "name": "الغاشية", "ayahs": 26},
    {"id": 89, "name": "الفجر", "ayahs": 30},
    {"id": 90, "name": "البلد", "ayahs": 20},
    {"id": 91, "name": "الشمس", "ayahs": 15},
    {"id": 92, "name": "الليل", "ayahs": 21},
    {"id": 93, "name": "الضحى", "ayahs": 11},
    {"id": 94, "name": "الشرح", "ayahs": 8},
    {"id": 95, "name": "التين", "ayahs": 8},
    {"id": 96, "name": "العلق", "ayahs": 19},
    {"id": 97, "name": "القدر", "ayahs": 5},
    {"id": 98, "name": "البينة", "ayahs": 8},
    {"id": 99, "name": "الزلزلة", "ayahs": 8},
    {"id": 100, "name": "العاديات", "ayahs": 11},
    {"id": 101, "name": "القارعة", "ayahs": 11},
    {"id": 102, "name": "التكاثر", "ayahs": 8},
    {"id": 103, "name": "العصر", "ayahs": 3},
    {"id": 104, "name": "الهمزة", "ayahs": 9},
    {"id": 105, "name": "الفيل", "ayahs": 5},
    {"id": 106, "name": "قريش", "ayahs": 4},
    {"id": 107, "name": "الماعون", "ayahs": 7},
    {"id": 108, "name": "الكوثر", "ayahs": 3},
    {"id": 109, "name": "الكافرون", "ayahs": 6},
    {"id": 110, "name": "النصر", "ayahs": 3},
    {"id": 111, "name": "المسد", "ayahs": 5},
    {"id": 112, "name": "الإخلاص", "ayahs": 4},
    {"id": 113, "name": "الفلق", "ayahs": 5},
    {"id": 114, "name": "الناس", "ayahs": 6},
]

# دالة مساعدة لحساب المسافة لتوفير بيانات واقعية للذكاء الاصطناعي للفرز بناءً عليها
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # نصف قطر الأرض بالكيلومتر
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return round(R * c, 2)

def parse_markdown_tables(text):
    # تحليل مخرجات النموذج اللغوي لاستخراج الجداول المنسقة بدقة
    tables = []
    lines = text.strip().split('\n')
    current_table = []
    
    for line in lines:
        if "|" in line:
            current_table.append(line)
        else:
            if len(current_table) > 2: # على الأقل العنوان والفاصل
                try:
                    df = pd.read_csv(io.StringIO('\n'.join(current_table)), sep="|", encoding='utf-8')
                    # تنظيف الأعمدة
                    df = df.dropna(axis=1, how='all')
                    df.columns = [c.strip() for c in df.columns]
                    # إزالة خط الفاصل الخاص بماركداون
                    df = df[~df.iloc[:, 0].str.contains('---', na=False)]
                    tables.append(df)
                except:
                    pass
            current_table = []
            
    # التقاط الجدول الأخير
    if len(current_table) > 2:
        try:
            df = pd.read_csv(io.StringIO('\n'.join(current_table)), sep="|", encoding='utf-8')
            df = df.dropna(axis=1, how='all')
            df.columns = [c.strip() for c in df.columns]
            df = df[~df.iloc[:, 0].str.contains('---', na=False)]
            tables.append(df)
        except: pass
        
    return tables

# واجهة المستخدم

# اسم المنصة في الزاوية
st.markdown('<div class="platform-name">منصة مَورِد</div>', unsafe_allow_html=True)

# عنوان الخدمة 
st.markdown('<div class="main-title">مساعد مَورِد الذكي</div>', unsafe_allow_html=True)
st.subheader("قم بتوليد خطة مخصصة عن طريق الذكاء الاصطناعي واعثر على أقرب الدور القرآنية إليك")
st.markdown("---")

# تصميم المدخلات
st.markdown('<div style="text-align: center; font-size: 28px; margin-bottom: 30px">بيانات الطالب المتقدم</div>', unsafe_allow_html=True)
st.info("يرجى تعبئة جميع الحقول المطلوبة")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
        age = st.number_input("العمر", 5, 100, 20)
        city = st.selectbox("المدينة", ["الرياض", "جدة", "مكة", "المدينة", "الدمام"])
        # محاكاة مدخلات موقع المستخدم (الحي) لحساب المسافة
        neighborhood = st.text_input("الحي", placeholder="مثال: النرجس")
        mode = st.radio("نوع التعليم", ["حضوري", "عن بعد"], horizontal=True)

    with col2:
        goal = st.selectbox("الهدف من الانضمام", ["حفظ", "مراجعة", "تقوية", "تثبيت"])
        level = st.selectbox("مستوى القراءة والحفظ", ["مبتدئ", "متوسط", "متقدم"])
        special = st.selectbox("الاحتياجات الخاصة", ["لا يوجد", "ذوي الإعاقة السمعية", "ذوي الإعاقة البصرية"])
        commitment = st.select_slider("مستوى الالتزام المتوقع", options=["منخفض", "متوسط", "عالي"])
        time_available = st.multiselect("الوقت المتاح", ["صباحي", "مسائي"])
        
    generate_btn = st.button("إنشاء الخطة وترشيح الدور ⚙️", use_container_width=True)

# النتائج والخطة
if generate_btn:
    tab1, tab2 = st.tabs(["الخطة المخصصة لك 📆", "أفضل الدور القرآنية لك 🏫"])
    
    with tab1:
        with st.spinner("...جارٍ تصميم خطتك باستخدام الذكاء الاصطناعي"):
            # هندسة الأوامر بدقة لضمان تناسق الأعمدة
            prompt = f"""
            You are an expert Quranic educational curriculum designer. Create a structured Quran study plan for a student with these details:
            - Age: {age}, Level: {level}
            - Goal: {goal}, Commitment: {commitment}, Special Needs: {special}

            **Requirements:**
            1. Output exactly **TWO Markdown tables**.
            2. First table: "الفصل الأول".
            3. Second table: "الفصل الثاني".
            4. **STRICT COLUMN STRUCTURE**: You must use exactly these 3 Arabic headers in this order:
            | الأسبوع | السورة والآيات | 
            5. **CRITICAL DATA ACCURACY**:
            - {surahs} table is the **single authoritative source** for surahs order and ayahs ranges.
            - You MUST strictly follow the exact Quranic surahs order and use the precise ayahs start–end ranges exactly as provided in the table.
            - It is strictly forbidden to invent, modify, extend, reduce, or combine ayahs in any way not explicitly allowed by the table.
            - Any error in surahs order or ayahs ranges is considered a **critical failure** and renders the output invalid.
    
            **Content Rules:**
            - "الأسبوع": Week 1 to Week 12.
            - "السورة والآيات": Specific range based on {surahs} AND level {level}.
            - Must align with goal ({goal}) and commitment ({commitment}) and {surahs}.
            - The weekly workload MUST be realistically achievable for a human learner of the given age and level. For young learners (children), prioritize short surahs or very small ayah ranges.
            
            Do not include any introduction or conclusion text. Only the two tables.
            """
            try:
                response = client.chat.completions.create(
                    model="Qwen/Qwen2.5-72B-Instruct",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1500, temperature=0.2
                )
                res_text = response.choices[0].message.content
                dfs = parse_markdown_tables(res_text)
                
                if len(dfs) >= 2:
                    st.subheader("الفصل الأول")
                    st.dataframe(dfs[0], use_container_width=True, hide_index=True)
                    
                    st.subheader("الفصل الثاني")
                    st.dataframe(dfs[1], use_container_width=True, hide_index=True)
                else:
                    st.warning(".عذرًا، لم يتم توليد الجداول بالشكل الصحيح. حاول مرة أخرى")
                    st.markdown(res_text) # إجراء احتياطي
            except Exception as e:
                st.error(f"{e} :حدث خطأ في الاتصال بالنموذج الذكي")
    
    with tab2:
        with st.spinner("...جارٍ ترشيح الدور القرآنية باستخدام الذكاء الاصطناعي"):

            # المعالجة المسبقة: حساب المسافة للذكاء الاصطناعي
            # محاكاة موقع المستخدم (إذا لم يتوفر GPS حقيقي)
            # نفترض أن المستخدم في مركز إحداثيات المدينة المحدد في قاعدة البيانات + إزاحة عشوائية بسيطة بناءً على الحي
            city_coords = {"الرياض": [24.7136, 46.6753], "جدة": [21.5433, 39.1728], "مكة": [21.3891, 39.8579], "المدينة": [24.5247, 39.5692], "الدمام": [26.4207, 50.0888]}
            user_lat, user_lon = city_coords.get(city, [24.0, 45.0])
            
            # إضافة عشوائية بسيطة لمحاكاة الحي إذا تم توفيره
            # محاكاة بسيطة: تشفير اسم الحي لتعديل خطي الطول والعرض قليلًا لمحاكاة الموقع
            if neighborhood:
                val = sum(ord(c) for c in neighborhood)
                user_lat += (val % 50) / 1000
                user_lon += (val % 50) / 1000

            # تصفية المرشحين حسب المدينة فقط لتناسب سياق البيانات
            candidates = []
            for c in CENTERS:
                if c['city'] == city:
                    # حساب المسافة
                    dist = calculate_distance(user_lat, user_lon, c['lat'], c['lon'])
                    c_copy = c.copy()
                    c_copy['distance_km'] = dist
                    # إزالة الإحداثيات الخام لتوفير التوكنز
                    del c_copy['lat']
                    del c_copy['lon']
                    candidates.append(c_copy)
            
            # أمر التوجيه لنظام التوصيات بالذكاء الاصطناعي
            # نقوم بتزويد القائمة بصيغة JSON للذكاء الاصطناعي ونطلب منه الفرز والاختيار
            rec_prompt = f"""
            You are an AI Recommendation Engine.
            
            **User Profile:**
            - Gender: {gender}
            - Age: {age}
            - Mode Preference: {mode}
            - Special Needs: {special}
            - Level: {level}
            
            **Candidates Data (JSON):**
            {json.dumps(candidates, ensure_ascii=False)}
            
            **Your Task:**
            1. Analyze the candidates against the User Profile.
            2. Filter out candidates that DO NOT match the user's Gender (Strict) or Special Needs (if user has any) or Level.
            3. **Sorting Rule:** You MUST sort the remaining valid candidates strictly by 'distance_km' (smallest to largest).
            4. Select the top 10 best matches.
            5. Return the result as a strictly valid JSON list.
            
            **JSON Output Format:**
            [
              {{
                "id": 1,
                "name": "Center Name",
                "distance_km": 1.2,
                "match_reason": "Why this is good (arabic)",
                "compatibility_percent": 95,
                "mode": "حضوري",
                "levels_accepted": "مبتدئ",
                "special_needs_support": "لا يوجد"
              }}
            ]
            
            Return ONLY the JSON.
            """
            
            try:
                response = client.chat.completions.create(
                    model="Qwen/Qwen2.5-72B-Instruct",
                    messages=[{"role": "user", "content": rec_prompt}],
                    max_tokens=2000, temperature=0.1
                )
                
                content = response.choices[0].message.content
                # تنظيف كتل الأكواد إذا قام الذكاء الاصطناعي بإضافتها
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                results = json.loads(content)
                results.sort(key=lambda x: x.get('distance_km'))

                if results:
                    st.subheader(f"أفضل 10 دور قرآنية في {city} مرتبة حسب القرب")
                    for res in results:
                        # تحديد اللون بناءً على نسبة التوافق
                        compatibility = res.get("compatibility_percent")
                        color = "green" if compatibility > 80 else "orange" if compatibility > 50 else "red"
                        with st.container():
                            st.markdown(f"""
                            <div class="card">
                                    <div style="display:flex; justify-content:space-between; align-items:center;">
                                     <h3 style="margin:0;">{res['name']}</h3>
                                     <span style="background-color:{color}; color:white; padding:5px 10px; border-radius:15px; font-size:0.9em;">تطابق %{compatibility}</span>
                                    </div>
                                <div style="margin-top:10px; color:#555;">
                                    <p>📍 <b>المسافة:</b> {res.get('distance_km')} كم</p>
                                    <p>👤 <b>نوع التعليم:</b> {res['mode']}</p>
                                    <p>🔠 <b>مستويات القراءة والكتابة:</b> {res['levels_accepted']}</p>
                                    <p>♿ <b>دعم الاحتياجات الخاصة:</b> {res['special_needs_support']}</p>
                                    <p>💡 <b>سبب الترشيح:</b> {res.get('match_reason')}</p>
                              </div>
                            """, unsafe_allow_html=True) 
                            
                            st.button(f"اختيار هذه الجمعية", key=f"join_{res.get('id')}", use_container_width=True)
                else:
                    st.warning(".لم يجد الذكاء الاصطناعي مراكز مطابقة في هذه المنطقة")
                    
            except json.JSONDecodeError:
                st.error(".حاول مرة أخرى .(JSON Format Error) خطأ في معالجة استجابة الذكاء الاصطناعي")
            except Exception as e:

                st.error(f"{e} :حدث خطأ غير متوقع")








