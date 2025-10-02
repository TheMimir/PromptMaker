# 🖥️ GitHub Desktop으로 배포하기

## Step 1: GitHub Desktop 설치 및 설정

### 1-1. GitHub Desktop 다운로드
- **다운로드 링크**: https://desktop.github.com
- 설치 후 실행

### 1-2. GitHub 계정 로그인
1. GitHub Desktop 실행
2. **File → Options (또는 Preferences on Mac)**
3. **Accounts** 탭 선택
4. **Sign in** 클릭하여 GitHub 계정으로 로그인

---

## Step 2: 프로젝트 추가하기

### 2-1. 로컬 저장소 추가
1. GitHub Desktop에서 **File → Add Local Repository** 클릭
2. **Choose...** 버튼 클릭
3. 폴더 선택: `/Users/mimir/PromptMaker`
4. **Add Repository** 클릭

**화면 예시:**
```
┌─────────────────────────────────┐
│  Add Local Repository           │
├─────────────────────────────────┤
│  Local Path:                    │
│  /Users/mimir/PromptMaker   [📁]│
│                                 │
│  [Cancel]    [Add Repository]   │
└─────────────────────────────────┘
```

### 2-2. 변경사항 확인
- 좌측에 변경된 파일 목록이 표시됩니다
- 이미 커밋되어 있으므로 "No local changes" 표시될 수 있습니다

---

## Step 3: GitHub에 게시하기

### 3-1. Publish Repository
1. 상단 중앙에 **"Publish repository"** 버튼 클릭
2. 다음 정보 입력:
   ```
   Name: PromptMaker
   Description: AI Prompt Maker for Game Development

   ☑️ Keep this code private 체크 해제
      (Public으로 설정해야 무료 배포 가능)

   Organization: None (개인 계정 선택)
   ```
3. **Publish Repository** 버튼 클릭

### 3-2. 업로드 대기
- 진행 상황 바가 표시됩니다
- 완료되면 "View on GitHub" 버튼이 나타납니다

**완료!** 🎉 이제 GitHub에 코드가 업로드되었습니다.

---

## Step 4: Streamlit Cloud 배포

### 4-1. Streamlit Cloud 접속
1. 브라우저에서 **https://share.streamlit.io** 접속
2. **"Sign in with GitHub"** 버튼 클릭
3. GitHub 계정으로 로그인
4. 권한 요청 시 **"Authorize"** 클릭

### 4-2. 새 앱 배포
1. **"New app"** 버튼 클릭 (우측 상단)
2. 다음 정보 입력:

```
┌─────────────────────────────────────────┐
│  Deploy an app                          │
├─────────────────────────────────────────┤
│  Repository:                            │
│  [YOUR_USERNAME/PromptMaker        ▼]   │
│                                         │
│  Branch:                                │
│  [main                             ▼]   │
│                                         │
│  Main file path:                        │
│  [app.py                               ]│
│                                         │
│  App URL (optional):                    │
│  [ai-prompt-maker                      ]│
│  .streamlit.app                         │
│                                         │
│  Advanced settings... ▼                 │
│                                         │
│  [Cancel]              [Deploy!]        │
└─────────────────────────────────────────┘
```

3. **Deploy!** 버튼 클릭

### 4-3. 빌드 대기
- 빌드 로그가 실시간으로 표시됩니다
- 첫 배포는 약 3-5분 소요
- 진행 상황:
  ```
  ⏳ Installing dependencies...
  ⏳ Building...
  ✅ Your app is live!
  ```

---

## Step 5: 완료! 🎉

### 배포 완료 후:
- **앱 URL**: `https://ai-prompt-maker.streamlit.app` (또는 입력한 이름)
- 이 URL을 누구에게나 공유 가능!
- GitHub에 코드를 푸시하면 자동으로 재배포됩니다

### 앱 관리:
- **Streamlit Cloud 대시보드**: https://share.streamlit.io
- 여기서 앱 상태 확인, 로그 보기, 재시작 가능

---

## 🔄 코드 업데이트하기

### 향후 코드 수정 시:

**GitHub Desktop에서:**
1. 코드 수정 후 GitHub Desktop 실행
2. 변경사항이 자동으로 감지됨
3. 좌측 하단에 커밋 메시지 입력
4. **"Commit to main"** 버튼 클릭
5. 상단의 **"Push origin"** 버튼 클릭

**자동 재배포:**
- GitHub에 푸시하면 Streamlit Cloud가 자동으로 감지
- 2-3분 후 업데이트된 앱이 배포됨

---

## ❓ 문제 해결

### GitHub Desktop에서 저장소가 안 보임
→ 폴더 경로 확인: `/Users/mimir/PromptMaker`

### "Publish" 버튼이 비활성화됨
→ 이미 게시되었습니다. "View on GitHub" 클릭

### Streamlit Cloud에서 저장소가 안 보임
→ 저장소가 Public인지 확인
→ GitHub 권한 재승인 필요할 수 있음

### 빌드 실패
→ Streamlit Cloud 로그 확인
→ Python 버전을 3.11로 설정

---

## 📌 중요 체크리스트

배포 전 확인사항:
- ✅ GitHub Desktop 설치됨
- ✅ GitHub 계정으로 로그인됨
- ✅ 저장소를 Public으로 설정
- ✅ `app.py` 파일 경로 확인
- ✅ `requirements.txt` 파일 존재

모두 완료되면 배포 성공! 🚀
