# dog-match-app
AI 기반 유기견 매칭 서비스 - 댕칼코마니
# 🐾 댕칼코마니 (Dog Match App)

> AI 기반 유기견 매칭 서비스 - 당신의 얼굴 속에 숨겨진 댕댕이를 찾아드립니다

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dog-match-app-for-beagle-rescue-network.streamlit.app/)

---

## 📖 프로젝트 배경

유기견 입양을 원하지만, 까다롭고 위압적인 심사 절차 때문에 망설이는 분들이 많습니다.  
**댕칼코마니**는 복잡한 서류와 면접 같은 심사 대신, **AI가 당신의 관상과 성향을 분석**하여  
가장 잘 어울리는 보호소 아이를 추천해주는 서비스입니다.

> **"평가하지 않고, 연결합니다 (Not Judging, Just Matching)"**

<img width="515" height="792" alt="image" src="https://github.com/user-attachments/assets/10ef8ac1-71d7-4d80-96dc-f1b848c0c6ed" />
<img width="571" height="786" alt="image" src="https://github.com/user-attachments/assets/53dad18c-1dcd-4a43-909e-8a4e9a0e8293" />
<img width="671" height="807" alt="image" src="https://github.com/user-attachments/assets/09542178-1fbe-4c8e-84b9-b654a6d5b674" />

---

## ✨ 주요 기능

### 1. 📸 AI 관상 분석
- Google Gemini AI가 사용자의 얼굴 사진을 분석
- 외모가 아닌 **분위기, 인상, 에너지**를 파악
- 따뜻하고 긍정적인 톤으로 리포트 제공

### 2. 🧠 심리테스트
- 5가지 질문으로 사용자의 라이프스타일과 성향 파악
- 면접이 아닌 **가벼운 심리테스트** 형식
- 간접적으로 선호도 수집 (크기, 활동성, 케어 의지 등)

### 3. 💝 가중치 매칭 시스템
- 태그 매칭 (기본 1점)
- 핵심 태그 보너스 (임보급구, 겁쟁이 등 +2점)
- 크기 선호 일치 (+3점)
- 케어 의지 매칭 (+2점)
- 긴급도 보너스 (+1점)

### 4. 🏆 2~3순위 추천
- 최고 매칭 1마리 상세 소개
- 잘 맞는 다른 아이들 2~3마리 추가 추천

### 5. 🌐 비구협 채널 연결
- 유튜브, 인스타그램, 네이버 카페 링크
- 더 많은 유기견 정보 접근 가능

---

## 🛠️ 기술 스택

### Frontend & Backend
- **Streamlit** `1.40.2` - 웹 인터페이스 및 상호작용

### AI & ML
- **Google Gemini 2.5 Flash** - 이미지 분석 및 관상 리포트 생성
- **google-generativeai** `0.8.3` - Gemini API 클라이언트

### Data
- **JSON** - 유기견 정보 관리 (20마리)
  - 기본 정보 (이름, 견종, 나이, 성별, 체중)
  - 성격 태그 (40+ 태그)
  - 스토리 (각 아이의 배경 이야기)

### Design
- **Custom CSS** - Jua 폰트, 그라데이션 배경
- **반응형 디자인** - 모바일/데스크톱 대응

### Deployment
- **Streamlit Cloud** - 무료 호스팅
- **GitHub** - 버전 관리 및 CI/CD

---

## 🎯 프로젝트 특징

### 1. 사용자 친화적 UX
- ❌ 딱딱한 입양 심사 느낌 제거
- ✅ 재미있는 심리테스트 형식
- ✅ 따뜻하고 공감적인 AI 리포트

### 2. 정교한 매칭 알고리즘
- 단순 태그 매칭이 아닌 **가중치 시스템**
- 사용자 성향 + 강아지 특성 종합 분석
- 긴급도 높은 아이 우선 추천

### 3. 스토리텔링
- 각 유기견의 **감동적인 스토리** 제공
- 숫자가 아닌 **생명**으로 접근
- 입양 동기 부여

### 4. 접근성
- 누구나 무료로 사용 가능
- 회원가입 불필요
- 모바일 친화적

---

## 📂 프로젝트 구조
```
dog-match-app/
├── app.py              # 메인 애플리케이션
├── data/
│   └── dogs.json       # 유기견 데이터 (20마리)
├── images/             # 강아지 사진 (20장)
│   ├── dog_001.jpg
│   ├── dog_002.jpg
│   └── ...
├── logo.png            # 비구협 로고
├── requirements.txt    # 패키지 의존성
├── .gitignore
└── README.md
```

---


## 🌐 배포 URL

**👉 [댕칼코마니 바로가기](https://dog-match-app-for-beagle-rescue-network.streamlit.app/)**

---

## 🐕 협력 단체

### 비글구조네트워크 (Beagle Rescue Network)

실험동물로 희생되는 비글을 중심으로,  
갈 곳 없는 동물들을 구조하고 새로운 가족을 찾아주는 동물보호 단체

- 🎬 [유튜브](https://www.youtube.com/@비글구조네트워크협회)
- 📸 [인스타그램](https://www.instagram.com/brn_boeun/)
- ☕ [네이버 카페](https://cafe.naver.com/thebeagle)

---

## 📊 데이터 현황

- **유기견 수**: 20마리
- **성격 태그**: 40+ 종류
- **매칭 알고리즘**: 5단계 가중치 시스템
---

<div align="center">

**🐾 사지 말고 입양하세요! 🐾**

Made with ❤️ for rescue dogs

</div>
