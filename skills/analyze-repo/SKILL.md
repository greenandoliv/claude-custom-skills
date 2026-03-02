---
name: analyze-repo
description: Use this skill when the user wants to analyze a codebase, repository, or local project directory. Trigger when the user provides a GitHub URL and asks for analysis, says "analyze this repo", "explain this codebase", "give me an overview of this project", "what does this repo do", "analyze this code", "summarize this project", "create a report for this repo", or similar requests. Also trigger when the user shares a local path and asks Claude to understand or document the code structure. Always use this skill for any in-depth codebase analysis task that should produce a structured markdown report.
allowed-tools: Bash(git clone:*), Bash(gh repo:*), Bash(gh api:*), Bash(ls:*), Bash(find:*), Bash(date:*), Bash(rm:*), Bash(mkdir:*), Glob, Grep, Read, Task, Write
---

# Analyze Repo Skill

당신은 코드 분석 전문가입니다. GitHub URL 또는 로컬 디렉토리를 분석하여 종합적인 마크다운 리포트를 생성합니다.

## 입력 판별

- `https://github.com/` 또는 `github.com/` 으로 시작 → GitHub URL
- 그 외 → 로컬 경로

## 실행 절차

### 1단계: 코드 수집

**GitHub URL인 경우:**
```bash
gh repo clone <url> /tmp/repo-analysis/<repo-name> -- --depth=1
```
분석 경로: `/tmp/repo-analysis/<repo-name>`

**로컬 경로인 경우:**
분석 경로: 입력된 경로 그대로 사용

### 2단계: 기본 정보 수집

- repo 이름 (경로의 마지막 컴포넌트)
- 오늘 날짜 (`date +%Y-%m-%d`)
- 최상위 파일 목록 (`ls -la <path>`)

### 3단계: 병렬 subagent 분석

Task tool을 사용해 아래 4개 agent를 **동시에** 실행합니다.

**Agent 1 - 구조 분석:**
```
<path>의 디렉토리 구조를 분석합니다.
1. find <path> -type f | head -100 으로 전체 파일 목록 파악
2. 깊이 3단계 디렉토리 트리 생성 (find <path> -maxdepth 3 -not -path '*/\.*' -not -path '*/node_modules/*' -not -path '*/__pycache__/*' -not -path '*/venv/*')
3. 각 디렉토리/파일의 역할 설명
4. 어느 파일부터 읽어야 하는지 "Start Here" 가이드
5. README.md, package.json, pyproject.toml, Cargo.toml 등 메타데이터 파일 읽기
결과를 마크다운 형식으로 반환하세요.
```

**Agent 2 - 기능 및 의존성 분석:**
```
<path>의 기능과 의존성을 분석합니다.
1. package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod 등 의존성 파일 읽기
2. 주요 기능 목록 파악 (README, 소스코드 훑기)
3. 기술 스택 파악 (언어, 프레임워크, 주요 라이브러리)
4. 외부 API/서비스 연동 여부 확인 (grep으로 API 키, endpoint 패턴 검색)
5. 환경변수 목록 파악 (.env.example, README의 환경설정 섹션)
6. 인프라/도구 파악 (Dockerfile, .github/workflows, Makefile 등)
결과를 마크다운 형식으로 반환하세요.
```

**Agent 3 - 진입점 및 실행 흐름 분석:**
```
<path>의 실행 흐름을 분석합니다.
1. main 파일, 진입점 파악 (main.py, index.js, main.go, src/main.rs 등)
2. README의 설치/실행 방법 섹션 읽기
3. 핵심 실행 경로 추적 (main → 핵심 함수들)
4. 데이터 흐름 파악 (입력 → 처리 → 출력)
5. 설정 파일 위치 및 주요 옵션 파악
진입점부터 주요 처리까지의 흐름을 단계별로 설명하고, 마크다운 형식으로 반환하세요.
```

**Agent 4 - 아키텍처 분석:**
```
<path>의 아키텍처를 분석합니다.
1. 전체 모듈/컴포넌트 구조 파악
2. 레이어 구조 파악 (프레젠테이션/비즈니스/데이터 등)
3. 모듈 간 의존 관계 파악 (import 패턴 분석)
4. 설계 패턴 식별 (MVC, 이벤트 기반, 파이프라인 등)
5. 핵심 클래스/함수 관계 파악

다음 3가지 Mermaid 다이어그램을 생성하세요:
- 전체 시스템 흐름도 (flowchart TD)
- 컴포넌트/모듈 관계도 (graph TD)
- 핵심 시나리오 시퀀스 다이어그램 (sequenceDiagram)

마크다운 형식으로 반환하세요.
```

### 4단계: 마크다운 리포트 생성

4개 agent의 결과를 통합하여 아래 구조로 파일을 생성합니다.

출력 파일 경로: `~/workspace/obsidian/secondbrain/_Inbox/repo-analysis-<repo-name>-<YYYY-MM-DD>.md`

## 출력 템플릿

```markdown
# 📦 <repo-name> 코드 분석

> 분석일: <YYYY-MM-DD> | 출처: <github-url-or-local-path>

## 0. 한눈에 보기 (TL;DR)
- **한 줄 요약**: 이 프로젝트가 무엇을 하는지 한 문장으로
- **핵심 가치**: 어떤 문제를 해결하는가
- **주요 기능 3가지**: 가장 중요한 기능 요약
- **대상 사용자**: 누가 이 프로젝트를 사용하는가
- **빠른 시작**: 설치 → 실행까지 3줄 요약

## 1. 핵심 개념 (Key Concepts)
[이 프로젝트를 이해하는 데 필요한 도메인 용어/개념 설명]

## 2. 디렉토리 구조
### 전체 파일 트리 (깊이 3단계)
### 파일별 역할
### Start Here 가이드

## 3. 기술 스택 & 외부 의존성
### 언어 & 프레임워크
### 주요 라이브러리
### 인프라/도구
### 외부 API/서비스

## 4. 환경 설정
### 환경변수 목록
### 설정 파일

## 5. 주요 기능

## 6. 실행 방법
### 사전 요구사항
### 설치
### 실행 (개발/프로덕션)

## 7. 동작 Flow (Flowchart)
[Mermaid flowchart]

## 8. 아키텍처 (모듈 관계도)
[Mermaid graph]

## 9. 주요 Sequence Diagram
[Mermaid sequenceDiagram]
```

## 완료 후 안내

분석 완료 시 다음을 알립니다:
1. 생성된 파일 경로
2. 분석 대상 (repo 이름, URL 또는 로컬 경로)
3. 주요 발견사항 3줄 요약

GitHub URL로 클론한 경우 `/tmp/repo-analysis/<repo-name>` 디렉토리는 유지합니다 (재분석 시 재사용 가능).
