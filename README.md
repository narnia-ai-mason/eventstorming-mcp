# Event Storming MCP Server

> Domain-Driven Design의 Event Storming 워크샵을 텍스트 기반 환경에서 체계적으로 진행할 수 있는 MCP 서버

[![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://www.python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-Latest-orange)](https://github.com/modelcontextprotocol/python-sdk)

## 🎯 개요

Event Storming MCP는 Alberto Brandolini가 창안한 Event Storming 기법을 디지털 환경에서 실행할 수 있도록 설계된 MCP(Model Context Protocol) 서버입니다. 물리적 화이트보드나 Miro 같은 시각적 도구 없이도, 구조화된 JSON 데이터로 워크샵의 모든 요소를 관리하고 분석할 수 있습니다.

### 주요 특징

✨ **완전한 Event Storming 지원**
- 8가지 핵심 요소 (이벤트, 커맨드, 액터, 애그리게잇, 정책, 읽기 모델, 외부 시스템, 핫스팟)
- 전통적인 색상 체계 반영
- 요소 간 인과관계 추적

🎨 **바운디드 컨텍스트 관리**
- DDD의 핵심 개념 구현
- 요소 그룹화 및 할당
- 컨텍스트별 통계 및 분석

📊 **강력한 분석 도구**
- 타임라인 뷰
- 이벤트 흐름 시각화
- 통계 및 리포팅
- 키워드 검색

💾 **데이터 관리**
- JSON 기반 영구 저장
- 워크샵 내보내기/가져오기
- 버전 관리 가능

## 🚀 빠른 시작

### 설치

```bash
# 프로젝트 다운로드
git clone https://github.com/narnia-ai-mason/eventstorming-mcp.git
cd eventstorming-mcp

# 필수 패키지 설치
uv sync
```

### Claude Desktop 설정

`claude_desktop_config.json` 파일에 다음을 추가:

```json
{
  "mcpServers": {
    "eventstorming": {
      "command": "uv",
      "args": [
        "uv",
        "--directory",
        "/path/to/eventstorming_mcp",
        "run",
        "eventstorming_mcp.py"
      ]
    }
  }
}
```

### 첫 워크샵 시작

```python
# 1. 워크샵 생성
eventstorming_create_workshop({
  "name": "My First Event Storming",
  "domain": "E-commerce"
})

# 2. 이벤트 추가
eventstorming_add_element({
  "workshop_id": "...",
  "type": "event",
  "name": "Order Placed"
})

# 3. 워크샵 로드
eventstorming_load_workshop({
  "workshop_id": "..."
})
```

## 📚 문서

### 주요 문서

- **[사용 가이드](eventstorming_mcp_guide.md)** - 전체 기능 및 사용법
- **[실전 튜토리얼](eventstorming_tutorial.md)** - 전자상거래 예제로 배우기
- **[API 레퍼런스](#api-레퍼런스)** - 모든 도구 상세 설명

### Event Storming이란?

Event Storming은 복잡한 비즈니스 도메인을 빠르게 탐색하고 모델링하는 워크샵 기법입니다:

1. **도메인 이벤트** 발견 (오렌지 포스트잇)
2. **커맨드** 식별 (파란 포스트잇)
3. **액터** 표시 (노란 포스트잇)
4. **애그리게잇** 정의 (연한 노란 포스트잇)
5. **바운디드 컨텍스트** 구성

더 자세한 내용: [EventStorming.com](https://www.eventstorming.com)

## 🛠 도구 목록

### 워크샵 관리 (3개)

| 도구 | 설명 |
|------|------|
| `eventstorming_create_workshop` | 새 워크샵 생성 |
| `eventstorming_list_workshops` | 워크샵 목록 조회 |
| `eventstorming_load_workshop` | 워크샵 로드 |

### 요소 관리 (3개)

| 도구 | 설명 |
|------|------|
| `eventstorming_add_element` | 요소 추가 (모든 타입) |
| `eventstorming_update_element` | 요소 수정 |
| `eventstorming_delete_element` | 요소 삭제 |

### 바운디드 컨텍스트 (2개)

| 도구 | 설명 |
|------|------|
| `eventstorming_create_bounded_context` | 컨텍스트 생성 |
| `eventstorming_assign_to_context` | 요소 할당 |

### 조회 및 분석 (5개)

| 도구 | 설명 |
|------|------|
| `eventstorming_search_elements` | 키워드 검색 |
| `eventstorming_get_timeline` | 타임라인 뷰 |
| `eventstorming_get_context_overview` | 컨텍스트 개요 |
| `eventstorming_get_statistics` | 통계 분석 |
| `eventstorming_visualize_flow` | 이벤트 흐름 시각화 |

### 데이터 관리 (2개)

| 도구 | 설명 |
|------|------|
| `eventstorming_export_workshop` | 워크샵 내보내기 |
| `eventstorming_import_workshop` | 워크샵 가져오기 |

**총 15개 도구**

## 💡 사용 예제

### 전자상거래 주문 시스템

```python
# 워크샵 생성
workshop = create_workshop({
  "name": "E-commerce Order System",
  "domain": "E-commerce"
})

# 주요 이벤트 추가
add_element({
  "type": "event",
  "name": "Order Placed",
  "position": 0
})

add_element({
  "type": "event",
  "name": "Payment Processed",
  "position": 10
})

# 바운디드 컨텍스트 생성
create_bounded_context({
  "name": "Order Management",
  "description": "주문 생명주기 관리"
})

# 통계 확인
get_statistics({"workshop_id": "..."})
```

더 많은 예제: [실전 튜토리얼](docs/eventstorming_tutorial.md)

## 📊 데이터 구조

### Workshop JSON

```json
{
  "metadata": {
    "id": "uuid",
    "name": "워크샵 이름",
    "domain": "도메인",
    "created_at": "2025-10-21T10:00:00Z",
    "updated_at": "2025-10-21T15:30:00Z",
    "facilitators": ["이름1", "이름2"]
  },
  "elements": [
    {
      "id": "uuid",
      "type": "event",
      "name": "Order Placed",
      "description": "주문이 접수됨",
      "position": 0,
      "triggers": ["payment-cmd-id"],
      "triggered_by": ["place-order-cmd-id"],
      "bounded_context_id": "order-ctx-id"
    }
  ],
  "bounded_contexts": [
    {
      "id": "uuid",
      "name": "Order Management",
      "element_ids": ["event-1", "cmd-1"],
      "color": "#3498db"
    }
  ]
}
```

## 🎨 요소 타입 및 색상

| 타입 | 색상 | 용도 |
|------|------|------|
| Event | 🟧 오렌지 | 도메인에서 발생한 일 |
| Command | 🟦 파랑 | 시스템에 대한 명령 |
| Actor | 🟨 노랑 | 명령을 실행하는 주체 |
| Aggregate | 📄 연한 노랑 | 일관성 경계 |
| Policy | 🟪 연보라 | 자동화된 규칙 |
| Read Model | 🟩 초록 | 조회용 모델 |
| External System | 🩷 분홍 | 외부 시스템 |
| Hotspot | 🟥 빨강 | 문제/불확실 영역 |

## 📁 파일 저장 위치

워크샵 데이터는 다음 위치에 저장됩니다:

```
~/.eventstorming_workshops/
  ├── {workshop-id-1}.json
  ├── {workshop-id-2}.json
  └── ...
```

## 🔧 고급 기능

### 이벤트 흐름 추적

```python
# 특정 이벤트부터 흐름 추적
visualize_flow({
  "workshop_id": "...",
  "start_element_id": "order-placed-id",
  "max_depth": 5
})
```

### 컨텍스트 커버리지 분석

```python
# 바운디드 컨텍스트 할당률 확인
statistics = get_statistics({"workshop_id": "..."})
# Coverage: 93.3% of elements are contextualized
```

### 핫스팟 관리

```python
# 문제 영역 표시
add_element({
  "type": "hotspot",
  "name": "Payment Timeout Handling",
  "description": "타임아웃 시 처리 방법 미정의",
  "notes": "재시도? 취소? 수동 확인?"
})

# 핫스팟 검색
search_elements({
  "query": "timeout",
  "element_type": "hotspot"
})
```

## 🤝 워크샵 진행 가이드

### 권장 진행 순서 (2시간)

1. **준비** (5분)
   - 워크샵 생성
   - 참여자 소개

2. **도메인 이벤트 발견** (30분)
   - 중요 이벤트부터 작성
   - 시간 순서로 배치

3. **커맨드 및 액터** (20분)
   - 각 이벤트의 트리거 식별
   - 실행 주체 명확화

4. **비즈니스 규칙** (15분)
   - 정책 정의
   - 예외 처리 규칙

5. **애그리게잇 설계** (20분)
   - 트랜잭션 경계 식별
   - 관련 요소 그룹화

6. **바운디드 컨텍스트** (20분)
   - 논리적 경계 정의
   - 요소 할당

7. **검토 및 정리** (10분)
   - 흐름 검증
   - 통계 확인
   - 워크샵 내보내기

## 🐛 문제 해결

### 일반적인 문제

**Q: 워크샵을 찾을 수 없습니다**
```bash
# 워크샵 목록 확인
eventstorming_list_workshops()

# 올바른 ID 사용 확인
```

**Q: 관계가 너무 복잡합니다**
```bash
# 흐름 시각화로 구조 파악
eventstorming_visualize_flow()

# 컨텍스트별로 분리
create_bounded_context()
```

**Q: 컨텍스트 경계가 불명확합니다**
```bash
# 통계로 응집도 확인
get_statistics()

# 반복적으로 재조정
```

## 📝 베스트 프랙티스

### ✅ DO

- 도메인 이벤트는 과거형으로 작성
- 핵심 흐름부터 시작
- 예외 상황도 포함
- 바운디드 컨텍스트 경계 명확히
- 핫스팟을 솔직하게 표시

### ❌ DON'T

- 너무 세밀한 이벤트 (UI 클릭 등)
- 기술 용어로만 표현
- 완벽주의 추구 (반복적 개선)
- 컨텍스트 간 강한 결합

## 🔮 향후 계획

- [ ] PlantUML/Mermaid 다이어그램 생성
- [ ] Git 버전 관리 통합
- [ ] 템플릿 시스템
- [ ] AI 기반 제안 기능
- [ ] 실시간 협업 지원
- [ ] 일관성 검증 도구
- [ ] 문서 자동 생성

## 📚 참고 자료

- [Event Storming 공식 사이트](https://www.eventstorming.com)
- [Alberto Brandolini - Introducing EventStorming](https://leanpub.com/introducing_eventstorming)
- [DDD Community](https://www.dddcommunity.org)
- [Model Context Protocol](https://modelcontextprotocol.io)

## 📄 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 🙏 기여

Issue 및 Pull Request 환영합니다!

---

**Made with ❤️ for the DDD and Event Storming community**

*Version 1.0 | Last Updated: 2025-10-21*
