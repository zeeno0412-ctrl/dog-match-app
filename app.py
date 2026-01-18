import streamlit as st
import google.generativeai as genai
import json
import time
import os

# ==========================================
# 1. 기본 설정 및 데이터 로드
# ==========================================

# 모델명 설정
MODEL_NAME = 'models/gemini-2.5-flash'

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception as e:
    # Secrets에 없으면 환경변수에서 시도
    api_key = os.environ.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("⚠️ API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인해주세요.")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_data
def load_dogs():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    paths = [
        os.path.join(base_dir, 'data', 'dogs.json'),
        os.path.join(base_dir, 'dogs.json')
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
    return []

dogs_data = load_dogs()

all_dog_tags = []
for dog in dogs_data:
    all_dog_tags.extend(dog.get("personality_tags", []))
all_dog_tags = list(set(all_dog_tags))

# ==========================================
# 2. 스타일링 (CSS) - 다크모드 완벽 대응
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
        
        /* [핵심 1] 배경색 강제 고정 */
        .stApp {
            background: linear-gradient(180deg, #F1F8E9 0%, #DCEDC8 100%) !important;
        }

        /* [핵심 2] 모든 글자색을 진한색으로 강제 고정 (다크모드에서도 흰색 글씨 금지) */
        * { 
            font-family: 'Jua', sans-serif !important; 
            color: #333333 !important; /* 기본 글자: 진한 회색 */
        }
        
        /* 제목 및 강조 글씨 색상 고정 */
        h1, h2, h3, .main-title {
            color: #2E7D32 !important; /* 진한 녹색 */
            text-shadow: 2px 2px 0px #fff;
        }
        
        /* 본문, 라벨, 리스트 등 모든 텍스트 강제 녹색/검정 */
        p, div, span, label, li, [data-testid="stMarkdownContainer"] p {
            color: #1B5E20 !important; /* 진한 쑥색 */
        }

        /* ------------------------------------------------ */
        /* [기존 유지] 불필요한 텍스트 숨기기 및 UI 정리 */
        /* ------------------------------------------------ */
        
        /* 이상한 key 텍스트 숨기기 */
        div[data-testid="stMarkdownContainer"] p[style*="key="] {
            display: none !important;
        }
        
        /* placeholder 텍스트 숨기기 */
        input::placeholder {
            color: transparent !important;
        }
        
        /* file uploader 내부 텍스트 정리 */
        [data-testid="stFileUploader"] label {
            font-size: 0 !important;
        }
        [data-testid="stFileUploader"] label::after {
            content: "파일 선택";
            font-size: 1rem !important;
            color: #1B5E20 !important;
        }
        
        /* ------------------------------------------------ */
        /* 박스 및 버튼 스타일 */
        /* ------------------------------------------------ */

        /* 박스 스타일 (배경을 더 불투명하게 해서 가독성 확보) */
        .content-box {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        /* 소개글 스타일 */
        .intro-text-main { 
            font-size: 1.4em; 
            color: #1B5E20 !important; 
            font-weight: bold; 
            margin-bottom: 10px; 
            text-align: center; 
        }
        .intro-text-sub { 
            font-size: 1.1em; 
            color: #333333 !important; 
            line-height: 1.6; 
            text-align: center; 
        }
        
        /* 프로세스 안내 스타일 */
        .process-container {
            display: flex; justify-content: space-around; align-items: center;
            background-color: #E8F5E9 !important; 
            border-radius: 10px; padding: 15px; margin: 20px 0;
        }
        .process-item { text-align: center; font-size: 1.1em; color: #33691E !important; }
        .process-arrow { font-size: 1.5em; color: #ccc !important; }

        /* 비구협 소개 박스 */
        .org-box {
            border-left: 5px solid #FF9800;
            background-color: #FFF3E0 !important;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            font-size: 1.0em;
            color: #E65100 !important;
        }

        /* 버튼 스타일 */
        .stButton>button {
            width: 100%; border-radius: 20px; height: 55px;
            background-color: #EF6C00 !important; 
            color: white !important; /* 버튼 글씨는 흰색 유지 */
            font-size: 1.2em; border: none;
            box-shadow: 0 4px 0 #E65100; margin-top: 10px;
        }
        .stButton>button:active { transform: translateY(4px); box-shadow: none; }
        
        .step-indicator {
            text-align: center; color: white !important; 
            background-color: #558B2F; padding: 8px 15px; border-radius: 20px; display: inline-block;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 앱 로직 & 상태 관리
# ==========================================
if 'step' not in st.session_state: st.session_state.step = 1
if 'user_tags' not in st.session_state: st.session_state.user_tags = []
if 'analysis_summary' not in st.session_state: st.session_state.analysis_summary = ""
if 'size_pref' not in st.session_state: st.session_state.size_pref = "medium"  # 추가
if 'care_ok' not in st.session_state: st.session_state.care_ok = False  # 추가

def analyze_image_with_gemini(image_file):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = f"""
        당신은 따뜻한 마음을 가진 '댕댕이 운명 매칭사'입니다! 🐾
        
        이 사진 속 사람의 얼굴을 보고, 그 사람의 **분위기, 인상, 눈빛**을 읽어주세요.
        
        중요한 것은:
        - 외모 평가가 아닌, 그 사람이 풍기는 **따뜻함, 에너지, 성향**을 파악하는 것!
        - 마치 오래된 친구처럼 편안하고 공감하는 톤으로 이야기해주세요
        - "이런 분이시네요!" 하고 긍정적으로 해석해주세요
        
        예시:
        - "부드러운 미소를 가지셨네요. 차분하고 온화한 분위기가 느껴져요."
        - "눈빛에 에너지가 넘치시네요! 활발하고 긍정적인 성격이실 것 같아요."
        - "조용하지만 깊이 있는 눈빛이에요. 세심하고 따뜻한 마음을 가지신 것 같아요."
        
        그리고 이 사람과 **가장 찰떡궁합**인 강아지 성향 태그를 아래 목록에서 3~5개 골라주세요:
        [태그 목록] {", ".join(all_dog_tags)}
        
        반드시 아래 JSON 형식으로만 답변해주세요 (다른 텍스트는 절대 포함하지 마세요):
        {{
            "summary": "2-3문장으로 따뜻하고 긍정적인 톤으로 분석",
            "matched_tags": ["태그1", "태그2", "태그3"]
        }}
        """
        
        image_parts = [{"mime_type": image_file.type, "data": image_file.getvalue()}]
        response = model.generate_content([prompt, image_parts[0]])
        
        # JSON 파싱
        result_text = response.text.replace("```json", "").replace("```", "").strip()
        parsed_result = json.loads(result_text)
        
        # 결과 검증
        if not parsed_result.get("summary") or not parsed_result.get("matched_tags"):
            raise ValueError("분석 결과가 올바르지 않습니다")
        
        return parsed_result
        
    except json.JSONDecodeError as e:
        # JSON 파싱 실패
        print(f"JSON 파싱 오류: {e}")
        return None
    except Exception as e:
        # 기타 오류
        print(f"분석 오류: {e}")
        return None

# [UI] 배너
base_dir = os.path.dirname(os.path.abspath(__file__))
banner_path = os.path.join(base_dir, "banner.jpg")
if os.path.exists(banner_path):
    st.image(banner_path, use_container_width=True)

st.markdown("<h1 class='main-title'>🎨 댕칼코마니</h1>", unsafe_allow_html=True)

# =========================================================
# Step 1. 댕칼코마니 소개 (인트로)
# =========================================================
if st.session_state.step == 1:
    # with st.container(border=False):
        st.markdown("<div style='text-align: center;'><div class='step-indicator'>Step 1 / 4</div></div>", unsafe_allow_html=True)
        
        # 1. 앱 소개 문구
        st.markdown("""
            <div class='content-box'>
                <div class='intro-text-main'>"당신의 얼굴 속에 숨겨진 댕댕이를 찾아드립니다."</div>
                <div class='intro-text-sub'>
                    댕칼코마니는 단순한 닮은꼴 찾기가 아닙니다.<br>
                    나와 닮은 눈망울을 가진 아이에게, <b>평생의 가족이 되어주는 기적의 시작</b>입니다.
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 2. 프로세스 안내
        st.markdown("""
            <div class='content-box'>
                <h3 style='text-align:center; color:#2E7D32;'>🚀 댕칼코마니 여정</h3>
                <div class='process-container'>
                    <div class='process-item'>📸<br>관상 분석</div>
                    <div class='process-arrow'>▶</div>
                    <div class='process-item'>🧠<br>성향 테스트</div>
                    <div class='process-arrow'>▶</div>
                    <div class='process-item'>💝<br>운명 매칭</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 3. 비구협 소개
        st.markdown("""
            <div class='content-box'>
                <h4 style='color:#EF6C00;'>🐾 비글구조네트워크(Beagle Rescue Network)</h4>
                <div style='color:#555; line-height:1.5;'>
                    우리는 실험동물로 가장 많이 희생되는 견종인 '비글'을 중심으로,
                    갈 곳 없는 동물들을 구조하고 보호하며 새로운 가족을 찾아주는 동물보호 단체입니다.<br>
                    단순한 구조를 넘어, 동물이 행복한 세상을 만들기 위해 노력합니다.
                </div>
                <div class='org-box'>
                    📢 <b>사지 말고 입양하세요!</b> 당신의 작은 관심이 한 생명의 세상을 바꿉니다.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 비구협 SNS 채널
        st.markdown("""
            <div class='content-box' style='text-align:center;'>
                <h4 style='color:#2E7D32; margin-bottom:15px;'>🌟 더 많은 아이들을 만나보세요</h4>
                <div style='display:flex; justify-content:center; gap:15px; flex-wrap:wrap;'>
                    <a href='https://www.youtube.com/@비글구조네트워크협회' target='_blank' 
                       style='text-decoration:none; background:#FF0000; color:white; padding:12px 24px; 
                              border-radius:10px; font-weight:bold; display:inline-block;'>
                        🎬 유튜브
                    </a>
                    <a href='https://www.instagram.com/brn_boeun/' target='_blank' 
                       style='text-decoration:none; background:linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%); 
                              color:white; padding:12px 24px; border-radius:10px; font-weight:bold; display:inline-block;'>
                        📸 인스타그램
                    </a>
                    <a href='https://cafe.naver.com/thebeagle' target='_blank' 
                       style='text-decoration:none; background:#03C75A; color:white; padding:12px 24px; 
                              border-radius:10px; font-weight:bold; display:inline-block;'>
                        ☕ 네이버 카페
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("나의 댕칼코마니 찾으러 가기 👉"):
            st.session_state.step = 2
            st.rerun()

# =========================================================
# Step 2. 이미지 분석 (관상 분석 결과 확인)
# =========================================================
elif st.session_state.step == 2:
    st.markdown("<div style='text-align: center;'><div class='step-indicator'>Step 2 / 4</div></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    st.subheader("📸 관상 분석")
    
    st.info("본인 사진을 올려주세요. AI가 당신의 분위기를 읽어냅니다.")
    
    uploaded_file = st.file_uploader("사진 업로드", type=["jpg", "png", "jpeg"])
    
    # 파일이 업로드 되면 분석 버튼 활성화
    if uploaded_file:
        st.image(uploaded_file, caption="분석할 사진", width=300)
        
        # 아직 분석 안 했으면 분석 버튼 표시
        if not st.session_state.analysis_summary:
            if st.button("내 관상 분석하기 🔍"):
                with st.spinner("🎨 당신의 얼굴을 분석하고 있습니다..."):
                    result = analyze_image_with_gemini(uploaded_file)
                    
                    if result:
                        st.session_state.analysis_summary = result.get("summary", "")
                        st.session_state.user_tags = result.get("matched_tags", [])
                        st.rerun()

        # 분석 결과가 있으면(분석 완료 시) 결과 화면 표시
        else:
            st.success("✨ 분석이 완료되었습니다!")
            st.markdown(f"""
                <div style='background-color:#E3F2FD; padding:20px; border-radius:10px; margin:15px 0;'>
                    <h4 style='color:#1565C0;'>🤖 AI 관상 리포트</h4>
                    <p style='font-size:1.1em; color:#333;'>{st.session_state.analysis_summary}</p>
                    <p style='color:#555;'><b>추출된 키워드:</b> {', '.join(st.session_state.user_tags)}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("관상이 아주 좋으시네요! 이 결과를 바탕으로 성향 테스트를 진행합니다.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("다음: 성향 테스트로 이동 👉"):
                    st.session_state.step = 3
                    st.rerun()
            with col2:
                if st.button("🔄 다른 사진으로 다시 분석"):
                    st.session_state.analysis_summary = ""
                    st.session_state.user_tags = []
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Step 3. 성향 테스트 (심리테스트 스타일)
# =========================================================
elif st.session_state.step == 3:
    st.markdown("<div style='text-align: center;'><div class='step-indicator'>Step 3 / 4</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    st.header("🧠 나는 어떤 사람일까?")
    st.write("5가지 질문으로 나의 성향을 알아볼게요!")
    st.write("---")
    
    # Q1. 주말 스타일
    q1 = st.radio(
        "Q1. 당신의 주말은?", 
        ["집콕하며 넷플릭스 정주행 🛋️", "카페 투어하며 힐링 산책 ☕", "등산이나 러닝으로 땀 흘리기 🏃"],
        key="q1"
    )
    st.write("")
    
    # Q2. 친구들이 보는 나
    q2 = st.radio(
        "Q2. 친구들이 말하는 나는?", 
        ["차분하고 조용한 편 🤫", "활발하고 에너지 넘쳐 🎉", "중간? 때에 따라 달라 😌"],
        key="q2"
    )
    st.write("")
    
    # Q3. 새로운 사람 만날 때
    q3 = st.radio(
        "Q3. 새로운 사람을 만나면?",
        ["낯을 좀 가리는 편, 천천히 친해져요 🙈", "금방 친해지는 스타일! 😄", "상대에 따라 다르게 반응해요 🤔"],
        key="q3"
    )
    st.write("")
    
    # Q4. 선호하는 공간
    q4 = st.radio(
        "Q4. 내가 좋아하는 분위기는?",
        ["아늑하고 포근한 공간 🕯️", "적당히 아담한 공간 🏠", "넓고 여유로운 공간 🏡"],
        key="q4"
    )
    st.write("")
    
    # Q5. 관계 스타일
    q5 = st.radio(
        "Q5. 누군가 나에게 의지한다면?",
        ["천천히 기다려주며 함께 성장할게요 🌱", "서로 편안하게 있고 싶어요 🌙", "밝은 에너지로 함께 즐기고 싶어요 ☀️"],
        key="q5"
    )
    
    if st.button("최종 댕칼코마니 결과 보기 💌"):
        # Q1. 활동성
        if "집콕" in q1:
            st.session_state.user_tags.extend(["#실내정적", "#조용한_가족추천", "#분리불안없음"])
        elif "카페" in q1:
            st.session_state.user_tags.extend(["#산책잘함", "#순둥이"])
        else:  # 등산
            st.session_state.user_tags.extend(["#산책러버", "#산책마스터", "#실외배변_선호"])
        
        # Q2. 에너지
        if "차분" in q2:
            st.session_state.user_tags.extend(["#조용한_가족추천", "#순둥이", "#실내정적"])
        elif "활발" in q2:
            st.session_state.user_tags.extend(["#사람좋아", "#산책잘함"])
        else:  # 중간
            st.session_state.user_tags.extend(["#순둥이"])
        
        # Q3. 사교성 (→ 강아지 겁 많은지 여부)
        if "낯을" in q3:
            st.session_state.user_tags.extend(["#겁쟁이", "#소심함", "#인내심필요", "#사회성기르는중", "#겁이많음"])
        elif "금방" in q3:
            st.session_state.user_tags.extend(["#사람좋아", "#사람손길_좋아함", "#순둥이"])
        else:  # 상대에 따라
            st.session_state.user_tags.extend(["#순둥이", "#손길허용"])
        
        # Q4. 공간 (→ 크기 선호)
        if "아늑" in q4:
            st.session_state.size_pref = "small"
            st.session_state.user_tags.append("#소형견")
        elif "아담" in q4:
            st.session_state.size_pref = "medium"
        else:  # 넓고
            st.session_state.size_pref = "large"
            st.session_state.user_tags.append("#대형견")
        
        # Q5. 관계 스타일 (→ 케어 의지)
        if "천천히" in q5:
            st.session_state.user_tags.extend(["#인내심필요", "#기다림이_필요해요", "#적응기간_필요"])
            st.session_state.care_ok = True  # 케어 의지 있음
        elif "편안" in q5:
            st.session_state.user_tags.extend(["#순둥이", "#조용한_가족추천"])
            st.session_state.care_ok = False
        else:  # 밝은
            st.session_state.user_tags.extend(["#사람좋아", "#산책잘함"])
            st.session_state.care_ok = False
        
        st.session_state.step = 4
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Step 4. 유기견 매칭 결과 (가중치 시스템)
# =========================================================
# =========================================================
# Step 4. 유기견 매칭 결과 (2~3순위 추가)
# =========================================================
elif st.session_state.step == 4:
    # with st.container(border=False):
        st.markdown("<div style='text-align: center;'><div class='step-indicator'>Step 4 / 4</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.balloons()
        st.header("🎉 당신의 댕칼코마니는?")
        
        # 가중치 매칭 로직
        user_set = set(st.session_state.user_tags)
        
        def calculate_match_score(dog):
            score = 0
            dog_tags = set(dog["personality_tags"])
            
            # 1. 기본 태그 매칭 (각 1점)
            basic_match = user_set.intersection(dog_tags)
            score += len(basic_match)
            
            # 2. 핵심 태그 가중치 (+2점 추가)
            priority_tags = ["#임보급구", "#평생가족_급구", "#겁쟁이", "#소심함", "#인내심필요"]
            for tag in priority_tags:
                if tag in basic_match:
                    score += 2
            
            # 3. 크기 매칭 보너스 (+3점)
            weight_str = dog["basic_info"].get("weight", "0kg")
            weight = int(''.join(filter(str.isdigit, weight_str))) if weight_str else 0
            
            size_pref = st.session_state.get("size_pref", "medium")
            if size_pref == "small" and weight <= 10:
                score += 3
            elif size_pref == "medium" and 10 < weight <= 20:
                score += 3
            elif size_pref == "large" and weight > 20:
                score += 3
            
            # 4. 케어 의지 매칭 (+2점)
            care_ok = st.session_state.get("care_ok", False)
            if care_ok and ("#노견케어" in dog_tags or "#살찌우기프로젝트" in dog_tags):
                score += 2
            
            # 5. 긴급도 보너스 (+1점)
            health_issue = dog["basic_info"].get("health_issue", "")
            if "🚨" in health_issue or "임박" in health_issue or "시급" in health_issue:
                score += 1
            
            return score, basic_match
        
        # 모든 강아지 점수 계산
        dog_scores = []
        for dog in dogs_data:
            score, matched_tags = calculate_match_score(dog)
            dog_scores.append({
                "dog": dog,
                "score": score,
                "matched_tags": matched_tags
            })
        
        # 점수 순으로 정렬
        dog_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # 1순위 강아지 (크게 표시)
        if dog_scores:
            best_match = dog_scores[0]
            best_dog = best_match["dog"]
            max_score = best_match["score"]
            matched = list(best_match["matched_tags"])
            
            st.markdown("### 💝 최고의 매칭!")
            
            col1, col2 = st.columns([1, 1.2])
            with col1:
                # 이미지 경로 처리
                img_path = best_dog["basic_info"]["image_path"]
                base_dir = os.path.dirname(os.path.abspath(__file__))
                full_path = os.path.join(base_dir, img_path)
                
                if os.path.exists(full_path):
                    st.image(full_path, use_container_width=True)
                else:
                    # images/ 경로도 시도
                    alt_path = os.path.join(base_dir, "images", os.path.basename(img_path))
                    if os.path.exists(alt_path):
                        st.image(alt_path, use_container_width=True)
                    else:
                        st.warning("이미지를 찾을 수 없습니다")
                    
            with col2:
                st.markdown(f"### 🐾 {best_dog['basic_info']['name']}")
                st.caption(f"{best_dog['basic_info']['breed']} | {best_dog['basic_info']['age']}")
                st.write(f"**❤️ 궁합 점수:** {max_score}점")
                
                # 교집합 태그 표시
                if matched:
                    st.info(f"💕 통하는 점: {', '.join(matched[:4])}")  # 최대 4개만
                
                st.markdown(f"""
                <div style='background-color:#FFF3E0; padding:15px; border-radius:10px; margin-top:10px;'>
                    💡 <b>{best_dog['basic_info']['name']} 이야기</b><br>
                    {best_dog['story']}
                </div>
                """, unsafe_allow_html=True)
            
            # 2~3순위 추천
            if len(dog_scores) > 1:
                st.write("---")
                st.markdown("### 🌟 이 아이들도 잘 맞아요!")
                
                # 2~3순위 (최대 3개까지)
                runner_ups = dog_scores[1:4] if len(dog_scores) > 3 else dog_scores[1:]
                
                cols = st.columns(len(runner_ups))
                
                for idx, match_info in enumerate(runner_ups):
                    dog = match_info["dog"]
                    score = match_info["score"]
                    tags = list(match_info["matched_tags"])
                    
                    with cols[idx]:
                        # 이미지
                        img_path = dog["basic_info"]["image_path"]
                        full_path = os.path.join(base_dir, img_path)
                        
                        if os.path.exists(full_path):
                            st.image(full_path, use_container_width=True)
                        else:
                            alt_path = os.path.join(base_dir, "images", os.path.basename(img_path))
                            if os.path.exists(alt_path):
                                st.image(alt_path, use_container_width=True)
                        
                        # 정보 카드
                        st.markdown(f"""
                        <div style='background-color:#F1F8E9; padding:12px; border-radius:10px; margin-top:5px;'>
                            <h4 style='margin:0; color:#2E7D32;'>🐾 {dog['basic_info']['name']}</h4>
                            <p style='font-size:0.9em; color:#666; margin:5px 0;'>
                                {dog['basic_info']['breed']}<br>
                                {dog['basic_info']['age']}
                            </p>
                            <p style='font-size:0.9em; margin:5px 0;'>
                                <b>궁합:</b> {score}점
                            </p>
                            <p style='font-size:0.85em; color:#555; margin:5px 0;'>
                                {', '.join(tags[:3]) if tags else ''}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

            st.write("---")
            st.markdown("""
                <div style='text-align:center; color:#2E7D32;'>
                    <b>이 아이들의 가족이 되어주세요.</b><br>
                    입양 문의: 비글구조네트워크 (Instagram @beagle_rescue_network)
                </div>
            """, unsafe_allow_html=True)

                        # 추가: SNS 채널 링크
            st.write("")
            st.markdown("""
                <div style='background-color:#E8F5E9; padding:20px; border-radius:15px; margin-top:20px; text-align:center;'>
                    <h4 style='color:#2E7D32; margin-bottom:15px;'>🌟 더 많은 아이들을 만나보세요!</h4>
                    <p style='color:#555; margin-bottom:20px;'>
                        비글구조네트워크의 다양한 채널에서 더 많은 아이들의 이야기를 만나보실 수 있어요.
                    </p>
                    <div style='display:flex; justify-content:center; gap:15px; flex-wrap:wrap;'>
                        <a href='https://www.youtube.com/@비글구조네트워크협회' target='_blank' 
                           style='text-decoration:none; background:#FF0000; color:white; padding:12px 24px; 
                                  border-radius:10px; font-weight:bold; display:inline-block; box-shadow: 0 2px 5px rgba(0,0,0,0.1);'>
                            🎬 유튜브
                        </a>
                        <a href='https://www.instagram.com/brn_boeun/' target='_blank' 
                           style='text-decoration:none; background:linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%); 
                                  color:white; padding:12px 24px; border-radius:10px; font-weight:bold; display:inline-block; box-shadow: 0 2px 5px rgba(0,0,0,0.1);'>
                            📸 인스타그램
                        </a>
                        <a href='https://cafe.naver.com/thebeagle' target='_blank' 
                           style='text-decoration:none; background:#03C75A; color:white; padding:12px 24px; 
                                  border-radius:10px; font-weight:bold; display:inline-block; box-shadow: 0 2px 5px rgba(0,0,0,0.1);'>
                            ☕ 네이버 카페
                        </a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            st.error("매칭된 강아지를 찾지 못했어요.")
        
        st.write("")
        if st.button("처음부터 다시 하기 🔄"):
            st.session_state.step = 1
            st.session_state.user_tags = []
            st.session_state.analysis_summary = ""
            if 'size_pref' in st.session_state:
                del st.session_state.size_pref
            if 'care_ok' in st.session_state:
                del st.session_state.care_ok
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 하단 푸터
# ==========================================
st.markdown("""
<div style='text-align: center; margin-top: 50px; padding: 20px; color: #555; border-top: 1px solid #ddd;'>
    <span style='font-size: 1.1em; font-weight: bold;'>© 2025 비글구조네트워크 | 사지말고 입양하세요 💚</span>
</div>

""", unsafe_allow_html=True)
