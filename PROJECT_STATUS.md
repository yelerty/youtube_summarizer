# 프로젝트 상태 (2025-10-10)

## 최근 작업 내역

### 1. Git 저장소 설정
- 원격 저장소: `git@github.com:yelerty/youtube_summarizer.git`
- 최신 커밋: "Fix indentation errors in Python files" (6e9a753)

### 2. 보안 개선
- Notion API 토큰을 환경변수로 분리 (`.env` 파일 사용)
- `.env.example` 템플릿 추가
- GitHub Push Protection 이슈 해결

### 3. 새 파일 추가: `summarize.py`
- **위치**: `/Users/jihong/auto/youtube-summarizer-ollama/summarize.py`
- **기능**: 명령줄에서 YouTube URL을 입력받아 요약을 터미널에 출력
- **사용법**: `python summarize.py <YouTube URL>`
- **특징**:
  - 모든 영상을 영어로 요약
  - 최종 결과를 한국어로 번역
  - 언어 감지 없이 일관된 처리 방식

### 4. 패키지 업그레이드
- `youtube-transcript-api`: 0.6.3 → 1.2.2 (API 변경됨)
- `langchain-ollama`: 0.1.3 → 0.2.1
- API 변경에 따른 코드 수정 완료

### 5. 버그 수정
- 들여쓰기 오류 수정 (탭 → 스페이스)
  - `youtube_summary.py:164`
  - `handle_notion.py:52-54`

## 현재 프로젝트 구조

```
youtube-summarizer-ollama/
├── .env                    # 환경변수 (Notion API 토큰) - gitignore됨
├── .env.example           # 환경변수 템플릿
├── summarize.py           # 새로 추가: CLI 요약 도구 ⭐
├── youtube_summary.py     # Notion DB 연동 버전
├── handle_notion.py       # Notion API 연동 모듈
├── main.py               # Gradio UI 버전
├── requirements.txt      # Python 패키지 목록
└── output_title.json     # 요약 결과 출력 파일
```

## 실행 방법

### A. Notion 연동 버전 (`youtube_summary.py`)
```bash
# Notion DB에서 미사용 URL을 자동으로 가져와 처리
python youtube_summary.py
# 결과: output_title.json에 저장
```

### B. CLI 버전 (`summarize.py`) ⭐ 새로 추가
```bash
# 명령줄에서 YouTube URL 직접 입력
python summarize.py "https://youtu.be/VIDEO_ID"
# 결과: 터미널에 한국어로 출력
```

### C. Gradio UI 버전 (`main.py`)
```bash
# 웹 브라우저 UI로 실행
python main.py
# 브라우저에서 http://localhost:7860 접속
```

## 환경 설정

### 필수 사항
1. **Python 3.12+**
2. **Ollama 서버 실행**
   ```bash
   ollama serve
   ```
3. **llama3.2 모델 설치**
   ```bash
   ollama pull llama3.2
   ```

### 환경변수 (.env)
```bash
NOTION_API_TOKEN=your_notion_api_token_here
NOTION_DATABASE_ID=your_notion_database_id_here
```

## 알려진 이슈

### 1. YouTube Transcript API 제한
- 일부 영상은 자막 접근이 제한되어 있음
- 에러: "no element found: line 1, column 0"
- 해결: 자막이 제공되는 다른 영상 사용

### 2. 패키지 버전 충돌
- `browser-use` 패키지와 `langchain-ollama` 버전 충돌 경고
- 현재 프로젝트는 정상 작동하나, `browser-use` 사용 시 주의 필요

## 다음 작업 제안

### 우선순위 높음
1. [ ] Notion DB 'used' 플래그 자동 업데이트 기능 추가
2. [ ] 에러 처리 개선 (자막 없는 영상 대응)
3. [ ] `summarize.py`를 git에 커밋

### 우선순위 중간
4. [ ] 요약 품질 개선 (프롬프트 튜닝)
5. [ ] 로깅 시스템 추가
6. [ ] 테스트 코드 작성

### 우선순위 낮음
7. [ ] 다른 LLM 모델 지원 (예: qwen2.5:7b)
8. [ ] 배치 처리 기능 (여러 URL 한번에 처리)
9. [ ] 요약 결과를 Notion DB에 자동 저장

## Git 상태

### 커밋되지 않은 파일들
```
?? next_todo_list.txt
?? nt2pandas.py
?? old_example.py
?? one_shot.py
?? output_title.json
?? temp_handlenotion.py
?? you_get_infor.py
?? summarize.py  ⭐ 새로 추가됨 - 커밋 필요!
```

### 마지막 커밋
```
6e9a753 Fix indentation errors in Python files
edb842b Integrate Notion API to auto-fetch YouTube URLs for processing
```

## 참고 사항

- Ollama 서버는 `http://localhost:11434`에서 실행됨
- LLM temperature는 0으로 설정 (일관된 결과)
- 청크 크기: 4000 토큰, 오버랩: 0
- 요약 방식: LangChain map-reduce

## 연락처 및 리소스

- GitHub Repo: https://github.com/yelerty/youtube_summarizer
- Original Repo: https://github.com/casedone/youtube-summarizer-ollama
- Ollama: https://ollama.com/
- LangChain Docs: https://python.langchain.com/
