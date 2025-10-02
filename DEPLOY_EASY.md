# 🚀 가장 쉬운 Streamlit Cloud 배포 방법

## 방법 1: GitHub Desktop 사용 (추천)

### 1단계: GitHub Desktop 설치 및 업로드
1. **GitHub Desktop 다운로드**: https://desktop.github.com
2. GitHub 계정으로 로그인
3. **File → Add Local Repository** 선택
4. 폴더 경로: `/Users/mimir/PromptMaker` 선택
5. **Publish repository** 클릭
   - Name: `PromptMaker`
   - Description: `AI Prompt Maker for Game Development`
   - ☑️ Keep this code private 체크 해제 (Public으로)
6. **Publish repository** 클릭

### 2단계: Streamlit Cloud 배포
1. **https://share.streamlit.io** 접속
2. **Sign in with GitHub** 클릭
3. **New app** 버튼 클릭
4. 설정:
   - Repository: `YOUR_USERNAME/PromptMaker`
   - Branch: `main`
   - Main file path: `app.py`
5. **Deploy!** 클릭

### 완료! 🎉
5분 후 `https://YOUR-APP.streamlit.app`에서 접속 가능

---

## 방법 2: GitHub 웹사이트 사용

### 1단계: 파일 압축
터미널에서:
```bash
cd /Users/mimir/PromptMaker
zip -r PromptMaker.zip . -x "venv/*" "*.pyc" "__pycache__/*" ".git/*"
```

### 2단계: GitHub에 업로드
1. **https://github.com/new** 에서 저장소 생성
   - Name: `PromptMaker`
   - Public 선택
2. **uploading an existing file** 클릭
3. `PromptMaker.zip` 파일을 드래그 앤 드롭
4. **Commit changes** 클릭
5. 압축 파일 업로드 후 압축 해제

### 3단계: Streamlit Cloud 배포 (위와 동일)

---

## 방법 3: 명령줄 사용

### 1단계: GitHub 저장소 생성
1. https://github.com/new 접속
2. Repository name: `PromptMaker`
3. Public 선택
4. **Create repository** 클릭

### 2단계: Personal Access Token 생성
1. https://github.com/settings/tokens 접속
2. **Generate new token (classic)** 클릭
3. Note: `PromptMaker Deploy`
4. Select scopes: ☑️ **repo** 체크
5. **Generate token** 클릭
6. 토큰 복사 (나중에 볼 수 없음!)

### 3단계: 코드 푸시
터미널에서 (YOUR_USERNAME을 실제 GitHub 사용자명으로 변경):

```bash
cd /Users/mimir/PromptMaker

# GitHub 저장소 연결
git remote add origin https://github.com/YOUR_USERNAME/PromptMaker.git

# 푸시
git push -u origin main
```

Username 입력: `YOUR_USERNAME`
Password 입력: `복사한 Personal Access Token 붙여넣기`

### 4단계: Streamlit Cloud 배포
1. https://share.streamlit.io 접속
2. Sign in with GitHub
3. New app 클릭
4. Repository: `YOUR_USERNAME/PromptMaker` 선택
5. Deploy! 클릭

---

## 🎯 추천: GitHub Desktop 사용!

**가장 쉽고 빠른 방법은 GitHub Desktop입니다.**
- GUI로 쉽게 업로드
- 토큰 불필요
- 클릭 몇 번으로 완료

다운로드: https://desktop.github.com

---

## ❓ 문제 해결

### "Authentication failed" 에러
→ Personal Access Token을 사용하세요 (비밀번호 사용 불가)

### Streamlit Cloud에서 앱이 안 보임
→ 저장소가 Public인지 확인

### 빌드 실패
→ Python 버전을 3.11로 설정
