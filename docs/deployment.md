# Streamlit Cloud 배포 가이드

이 문서는 Nemo Store 프로젝트를 GitHub에 업로드하고 Streamlit Cloud에 배포하는 과정을 설명합니다.

## 1. 사전 준비
- **GitHub 계정:** 코드를 업로드할 개인 리포지토리가 필요합니다.
- **Streamlit Cloud 계정:** [streamlit.io/cloud](https://streamlit.io/cloud)에서 GitHub 계정으로 가입하세요.
- **필수 파일 확인:** 
  - `requirements.txt`: Streamlit Cloud 환경에서 설치할 라이브러리 목록
  - `src/app.py`: 메인 실행 파일
  - `data/nemo_stores.db`: 데이터베이스 파일 (배포 시 함께 포함하거나 외부 DB 연동 필요)

## 2. GitHub에 코드 업로드
1. **GitHub 리포지토리 생성:** GitHub에서 새 리포지토리(예: `nemo-store-dash`)를 생성합니다.
2. **로컬 코드를 GitHub에 푸시:**
   ```bash
   # 프로젝트 루트 폴더에서 실행
   git init
   git add .
   git commit -m "Initial commit: Streamlit app and data"
   git branch -M main
   git remote add origin https://github.com/사용자이름/리포지토리이름.git
   git push -u origin main
   ```
   > [!WARNING]
   > **중요: DB 파일 배포 관련**
   > - 만약 `file is not a database` 오류가 발생한다면, GitHub에 `.db` 파일이 제대로 업로드되지 않았을 가능성이 큽니다.
   > - **GitHub LFS:** 100MB가 넘는 파일은 Git LFS를 사용해야 하지만, Streamlit Cloud는 기본적으로 LFS 파일을 직접 가져오지 못할 수 있습니다.
   > - **해결책:** DB 파일이 너무 크지 않다면 LFS 없이 직접 푸시하거나, 데이터를 수집하는 `collect.py`를 배포 환경에서 실행할 수 있는 구조(예: GitHub Actions)를 고려해야 합니다.
   > - 로컬에서 오류 발생 시 `python src/collect.py`를 다시 실행하면 DB 파일이 유효한 상태로 초기화됩니다.

## 3. Streamlit Cloud 배포 설정
1. [Streamlit Cloud](https://share.streamlit.io/)에 접속하여 로그인합니다.
2. **"Create app"** 버튼을 클릭합니다.
3. **"Deploy a public app"** 섹션에서 GitHub 리포지토리를 선택합니다.
   - **Repository:** `사용자이름/리포지토리이름`
   - **Branch:** `main`
   - **Main file path:** `src/app.py`  (※ 주의: 루트가 아니므로 경로를 정확히 입력해야 합니다)
4. **"Deploy!"**를 클릭하면 배포가 시작됩니다.

## 4. 환경 변수 및 보안 (선택 사항)
만약 API 키나 보안이 필요한 정보가 있다면, Streamlit Cloud 설정의 **Secrets** 탭에서 지정하고 `st.secrets`를 통해 코드 내에서 사용할 수 있습니다.

## 5. 배포 확인 및 업데이트
- 배포가 완료되면 부여된 URL을 통해 대시보드에 접속할 수 있습니다.
- 로컬에서 코드를 수정하고 GitHub에 `push`하면 Streamlit Cloud에서 자동으로 변경 사항을 감지하여 앱을 다시 빌드합니다.
