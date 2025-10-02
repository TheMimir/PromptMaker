# 🚀 Streamlit Cloud 배포 가이드

## 1단계: GitHub 저장소 생성

1. https://github.com/new 에서 새 저장소 생성
   - Repository name: `PromptMaker` (또는 원하는 이름)
   - Public 선택 (무료 배포를 위해)
   - README, .gitignore, license 체크 **해제** (이미 있음)

2. 저장소 URL 복사 (예: `https://github.com/YOUR_USERNAME/PromptMaker.git`)

---

## 2단계: GitHub에 코드 푸시

터미널에서 다음 명령어 실행:

```bash
# GitHub 저장소 연결 (YOUR_USERNAME을 실제 사용자명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/PromptMaker.git

# 브랜치 이름 main으로 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

**인증 요청 시:**
- Username: GitHub 사용자명
- Password: Personal Access Token (PAT) 사용
  - PAT 생성: https://github.com/settings/tokens
  - Select scopes에서 `repo` 체크

---

## 3단계: Streamlit Cloud 배포

1. **Streamlit Cloud 접속**
   - https://share.streamlit.io 방문
   - "Sign in with GitHub" 클릭

2. **새 앱 배포**
   - "New app" 버튼 클릭
   - Repository: `YOUR_USERNAME/PromptMaker` 선택
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: 원하는 URL 입력 (예: `ai-prompt-maker`)

3. **고급 설정 (선택사항)**
   - Python version: 3.11 권장
   - 환경 변수는 필요 없음

4. **Deploy 클릭!**
   - 빌드 시간: 약 2-5분
   - 완료 후 URL: `https://YOUR-APP-NAME.streamlit.app`

---

## 4단계: 배포 확인

배포가 완료되면:
- ✅ 자동으로 앱이 실행됨
- ✅ HTTPS 자동 적용
- ✅ GitHub 푸시 시 자동 재배포

---

## 🔧 문제 해결

### 빌드 실패 시:
1. Streamlit Cloud 로그 확인
2. `requirements.txt` 확인
3. Python 버전 확인 (3.11 권장)

### 앱이 로드되지 않을 때:
1. 브라우저 새로고침 (Ctrl+F5)
2. Streamlit Cloud에서 "Reboot app" 시도
3. GitHub에 변경사항 푸시하여 재배포

---

## 📝 유지보수

### 코드 업데이트:
```bash
# 코드 수정 후
git add .
git commit -m "Update: 설명"
git push
```

### 자동 재배포:
- GitHub에 푸시하면 자동으로 Streamlit Cloud가 재배포합니다

---

## 🎉 완료!

배포 후 URL: `https://YOUR-APP-NAME.streamlit.app`

이 URL을 공유하면 누구나 앱을 사용할 수 있습니다!
