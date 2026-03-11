# Nemo Store 매물 통합 대시보드 🏠

네모(Nemo) API를 통해 수집된 상가 매물 데이터를 시각화하고 분석하는 Streamlit 대시보드입니다.

## 주요 기능
- **매물 검색 및 필터링:** 제목, 가격(보증금/월세/권리금), 면적, 층수, 업종별 필터링
- **이미지 갤러리:** 매물 이미지와 함께 주요 정보 확인 및 상세 보기 팝업
- **시장 데이터 분석:** 업종별 분포, 층별 평균 월세, 면적 대비 월세 산점도 시각화
- **벤치마킹 지표:** 동일 업종 평균 대비 해당 매물의 월세 수준 분석

## 실행 방법 (로컬 환경)
1. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```
2. 데이터 수집 (최초 1회 또는 업데이트 시):
   ```bash
   python src/collect.py
   ```
3. 대시보드 실행:
   ```bash
   streamlit run src/app.py
   ```

## 배포 안내
GitHub 및 Streamlit Cloud 배포와 관련된 상세 내용은 `docs/deployment.md`를 참고하세요.
