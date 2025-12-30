# 복잡계이론 기반 AI 연구 및 서비스 개발

```python
'''
이론에서 출발해 AI 연구를 수행하고, 실험적 접근을 통해 서비스로 연결합니다.
'''
```

## 👤 About Me

- **AI 풀스택 연구자 & 개발자**
- **AI 모델링 → 배포 → 프론트엔드·백엔드·센서 HW/SW**까지 엔드투엔드 경험
- 빠른 프로토타이핑 및 실제 서비스화 경험 다수

---

## 💼 경력

- **피부질환 관리앱 개발 스타트업** (2024.10~**현재**)
    - 직무: 테크 리더 (기술 총괄 리더)
        - AI 모델 개발: 시계열 예측 및 요인 파악 AI 모델 개발 (진행 중)
        - 서버 개발: Python FastAPI 기반 서버 개발 (서비스 중)
        - LLM 엔진 개발: LLM 기반 챗봇 서버 개발 (MVP 버전)
        - 프론트엔드 개발: Flutter 앱 개발 (MVP 버전)
        - 센서 개발: 휴대용 온습도 센서 HW/SW 개발 (MVP 버전)
- **LLM 기반 자기 계발 앱 개발 스타트업 창업시도** (2023.08~2024.08)
    - 직무: AI Engineer
        - LLM 기반 질문 생성 엔진 개발 $^{[1]}$
        - SLM 기반 질문 보정 엔진 개발 $^{[2]}$
- **운수업체 ERP 솔루션 개발 스타트업** (2022.08~2023.08)
    - 직무: Data Scientist
        - 기존 로직 보완
            - 자동배차 로직$^{[3]}$, 자동휴무신청 로직
        - 핵심 로직 개발
            - 운수종사자시스템 로우데이터 기반 운행/휴게시간 계산 로직 개발 $^{[4]}$
            - 정해진 개별 노선 시간표에 맞춰 조퇴, 차량교체, 인력교체 등의 스케줄이 있을 때, 여러 시간표를 조합하는 로직 개발 $^{[5]}$
    - 직무: Web Developer
        - ERP 화면 개발$^{[6]}$
            - 차량 관리 화면: 운행 전 차량 점검, 배차 등
            - 업무상태 관리 화면: 출퇴근, 근무, 휴무 등
            - 홈 화면: 주요 알림(출퇴근, 차량 이상 여부, 공지사항 등 확인), 퀵 메뉴

---

## 👨🏻‍💻 개발 & 배포

### 🧠 AI 모델 개발 & 배포

- **시계열 예측 모델**: Temporal Convolution Network기반 요인 파악 레이어 포함된 시계열 예측 모델 개발
- **LLM 기반 챗봇 서버**: LangChain으로 사용자 질의응답 및 대화형 서비스 구축 및 배포
- **질문 생성 엔진**: 질문/키워드 그래프 + LLM 기반 자동 질문 생성 및 서비스화
- **SLM Fine-tuning**: 질문 보정 엔진 개발 및 모델을 서버에 배포

### ⚙️ 백엔드 개발 & 배포

- **ERP 전용 서버 (Python + MySQL)**
    - 핵심 알고리즘 처리 서버 개발
    - AWS ECS(Fargate) 환경에 배포 및 운영
- **피부질환 관리앱 서버**
    - 전용 API 서버 개발
    - AWS ECS에 Fargate 방식으로 배포
    - CDN + S3 조합으로 랜딩페이지 배포

### 📡 센서 소프트웨어 개발

- **블루투스 기반 휴대용 온습도계 시제품 개발**
- **올인원 환경 센서 보드** (온습도, 미세먼지, 유기화학물질)
    - 센서 데이터 수집 및 소프트웨어 개발

### 🌐 웹 개발 & 배포

- **ERP 웹 개발 (운수업체 전용)**: 데이터 관리/분석 기능 포함, 웹 앱 구축 및 배포
- **피부질환 관리앱 랜딩페이지**: 사용자 친화적 UI/UX 중심 웹 구축 및 배포

---

## 🔧 Skills

- **AI/ML**: PyTorch(🏅), Longterm Time-series Forecasting(🏅), Transformers, Fine-tuning
- **Backend**: FastAPI(🏅), MySQL, AWS(ECS, S3, RDS, CDN, Route53, …)
- **Frontend**: React(🏅), Flutter
- **Infra/DevOps**: Docker
- **Sensors(HW/SW)**: Arduino IDE, Platform.io

---

## 📚 Knowledge & Study

- *(경희대학교)* **복잡계 정보이론 연구실 석사졸업**
    - 다양한 시계열에서의 신기록경신 통계이론 연구$^{[7]}$
        - random walk
        - drifted random walk
        - drifted random walk with non-zero origin staying prob
        - Real data: KRX 한국 주식 시장 종가 데이터, 서울시 부동산 시장 거래가격 데이터
    - Network Theory(graph) 공부 / 다양한 network C 구현 / 시뮬레이션
        - 공부/구현한 networks:
            - Periodic squared lattice
            - Erdos-Renyi random network
            - Barabasi-Albert network
            - static network
        - 시뮬레이션:
            - Multi-state voter model (Potts model)
            - Axelrod Model (문화전파 모형)
    - 시뮬레이션 전용 CPU 병렬 연산용 서버 구축
        - Fedora server$^{[8]}$, OpenMPI$^{[8]}$, RAID system$^{[9]}$ 등
- *(경희대학교)* **물리학과 졸업**
    - 정보물리학(Python), 전산물리학(Ubuntu, C, OpenGL) 이수

---

## 🔖 References

[1] ‣ 

[2] ‣ 

[3] ‣

[4] ‣ 

[5] 배차시간표 수정로직

[dispatchInsertDriverComponent.py](%EB%B3%B5%EC%9E%A1%EA%B3%84%EC%9D%B4%EB%A1%A0%20%EA%B8%B0%EB%B0%98%20AI%20%EC%97%B0%EA%B5%AC%20%EB%B0%8F%20%EC%84%9C%EB%B9%84%EC%8A%A4%20%EA%B0%9C%EB%B0%9C/dispatchInsertDriverComponent.py)

[dispatchDeleteRoundComponent.py](%EB%B3%B5%EC%9E%A1%EA%B3%84%EC%9D%B4%EB%A1%A0%20%EA%B8%B0%EB%B0%98%20AI%20%EC%97%B0%EA%B5%AC%20%EB%B0%8F%20%EC%84%9C%EB%B9%84%EC%8A%A4%20%EA%B0%9C%EB%B0%9C/dispatchDeleteRoundComponent.py)

[6] ‣ 

[7] 시계열 이론 연구 정리자료

[8] CPU 병렬 연산용 Fedora Server 구축 매뉴얼 제작

[OpenMPIFedoraServerManual.md](%EB%B3%B5%EC%9E%A1%EA%B3%84%EC%9D%B4%EB%A1%A0%20%EA%B8%B0%EB%B0%98%20AI%20%EC%97%B0%EA%B5%AC%20%EB%B0%8F%20%EC%84%9C%EB%B9%84%EC%8A%A4%20%EA%B0%9C%EB%B0%9C/OpenMPIFedoraServerManual.md)

[9] RAID 시스템 구축 매뉴얼 제작

[RaidSystemFedora.md](%EB%B3%B5%EC%9E%A1%EA%B3%84%EC%9D%B4%EB%A1%A0%20%EA%B8%B0%EB%B0%98%20AI%20%EC%97%B0%EA%B5%AC%20%EB%B0%8F%20%EC%84%9C%EB%B9%84%EC%8A%A4%20%EA%B0%9C%EB%B0%9C/RaidSystemFedora.md)
