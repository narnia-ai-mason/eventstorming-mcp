# Event Storming MCP 서버 사용 가이드

## 개요

Event Storming MCP는 Domain-Driven Design(DDD)의 Event Storming 워크샵을 텍스트 기반 환경에서 진행할 수 있도록 설계된 MCP(Model Context Protocol) 서버입니다. 시각적 도구(화이트보드, Miro 등)가 없어도 구조화된 JSON 데이터로 워크샵의 모든 요소를 체계적으로 관리할 수 있습니다.

## 주요 기능

### 1. 워크샵 관리
- 여러 Event Storming 세션 생성 및 저장
- 워크샵 메타데이터 관리 (이름, 도메인, 퍼실리테이터)
- 자동 타임스탬프 및 버전 관리

### 2. DDD 핵심 요소 지원
전통적인 Event Storming의 모든 요소를 색상 체계와 함께 지원:
- **도메인 이벤트** (Domain Events) - 오렌지색
- **커맨드** (Commands) - 파란색  
- **액터** (Actors) - 노란색
- **애그리게잇** (Aggregates) - 연한 노란색
- **정책/규칙** (Policies) - 연보라색
- **읽기 모델** (Read Models) - 초록색
- **외부 시스템** (External Systems) - 분홍색
- **핫스팟** (Hotspots) - 빨간색 (문제 영역)

### 3. 바운디드 컨텍스트 관리
- 바운디드 컨텍스트 정의
- 요소를 컨텍스트에 할당하여 그룹핑
- 컨텍스트별 통계 및 분석

### 4. 관계 및 흐름 추적
- 요소 간 인과관계 (triggers/triggered_by)
- 시간 흐름에 따른 이벤트 순서
- 이벤트 체인 시각화

### 5. 분석 및 검색
- 키워드 기반 요소 검색
- 워크샵 통계 및 분석
- 타임라인 뷰
- 이벤트 흐름 시각화

### 6. 데이터 관리
- JSON 기반 구조화된 저장
- 워크샵 내보내기/가져오기
- 파일 시스템 기반 영구 저장

## 설치 및 실행

### 프로젝트 초기화
```bash
git clone https://github.com/narnia-ai-mason/eventstorming-mcp.git
cd eventstorming-mcp
```

### 필수 요구사항
```bash
uv sync
```

### Claude Desktop 설정
`claude_desktop_config.json`에 추가:
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

## 도구 목록 (23개)

### 워크샵 관리 (3개)
1. **eventstorming_create_workshop** - 새 워크샵 생성
2. **eventstorming_list_workshops** - 워크샵 목록 조회
3. **eventstorming_load_workshop** - 워크샵 로드

### 요소 관리 (3개)
4. **eventstorming_add_element** - 요소 추가 (모든 타입)
5. **eventstorming_update_element** - 요소 수정
6. **eventstorming_delete_element** - 요소 삭제

### 바운디드 컨텍스트 (2개)
7. **eventstorming_create_bounded_context** - 컨텍스트 생성
8. **eventstorming_assign_to_context** - 요소를 컨텍스트에 할당

### 조회 및 분석 (5개)
9. **eventstorming_search_elements** - 요소 검색
10. **eventstorming_get_timeline** - 타임라인 뷰
11. **eventstorming_get_context_overview** - 컨텍스트 개요
12. **eventstorming_get_statistics** - 통계 분석
13. **eventstorming_visualize_flow** - 이벤트 흐름 시각화

### 데이터 관리 (2개)
14. **eventstorming_export_workshop** - 워크샵 내보내기
15. **eventstorming_import_workshop** - 워크샵 가져오기

## 사용 시나리오 예제

### 시나리오 1: 전자상거래 주문 관리 워크샵

#### 1단계: 워크샵 생성
```json
{
  "name": "E-commerce Order Management",
  "description": "주문 처리 프로세스 분석 워크샵",
  "domain": "E-commerce",
  "facilitators": ["김철수", "이영희"]
}
```

#### 2단계: 핵심 도메인 이벤트 추가
```
- Order Placed (주문 접수됨)
- Payment Processed (결제 처리됨)
- Order Confirmed (주문 확정됨)
- Items Picked (상품 피킹됨)
- Order Shipped (배송 시작됨)
- Order Delivered (배송 완료됨)
```

#### 3단계: 커맨드 및 액터 추가
```
커맨드:
- Place Order (주문하기)
- Process Payment (결제 처리하기)
- Confirm Order (주문 확정하기)
- Pick Items (상품 피킹하기)

액터:
- Customer (고객)
- Payment Service (결제 서비스)
- Warehouse Staff (창고 직원)
- Delivery Service (배송 서비스)
```

#### 4단계: 관계 설정
```
Customer → Place Order → Order Placed
Order Placed → Process Payment → Payment Processed
Payment Processed → Confirm Order → Order Confirmed
Order Confirmed → Pick Items → Items Picked
Items Picked → Ship Order → Order Shipped
```

#### 5단계: 바운디드 컨텍스트 정의
```
1. Order Management Context
   - Order Placed
   - Order Confirmed
   - Place Order

2. Payment Context
   - Payment Processed
   - Process Payment
   - Payment Service

3. Fulfillment Context
   - Items Picked
   - Order Shipped
   - Order Delivered
   - Warehouse Staff
```

#### 6단계: 애그리게잇 추가
```
- Order (주문)
- Payment (결제)
- Shipment (배송)
```

#### 7단계: 정책/규칙 추가
```
- "결제가 실패하면 주문 취소"
- "재고 부족 시 부분 배송"
- "3일 이상 배송 지연 시 고객 알림"
```

#### 8단계: 핫스팟 표시
```
- "결제 타임아웃 처리 방법"
- "재고 동시성 문제"
- "배송 추적 정확도"
```

### 시나리오 2: 의료 시스템 환자 진료 프로세스

#### 워크샵 구조
```
Domain: Healthcare
Workshop: Patient Care Journey

바운디드 컨텍스트:
1. Appointment Management
2. Clinical Documentation
3. Billing & Insurance
4. Pharmacy

핵심 이벤트 흐름:
Patient Registered → Appointment Scheduled → 
Patient Checked In → Consultation Completed → 
Prescription Issued → Payment Processed
```

## 실전 워크샵 진행 가이드

### 1단계: 준비 (5분)
```
1. 워크샵 생성
2. 도메인 정의
3. 참여자 등록
```

### 2단계: 도메인 이벤트 발견 (30분)
```
1. "~했다", "~됨" 형태로 이벤트 작성
2. 시간 순서로 배치 (position 사용)
3. 중요 이벤트부터 시작
4. 예외 상황 이벤트 추가
```

### 3단계: 커맨드 및 액터 식별 (20분)
```
1. 각 이벤트를 촉발하는 커맨드 추가
2. 커맨드를 실행하는 액터 식별
3. triggers/triggered_by 관계 설정
```

### 4단계: 비즈니스 규칙 정리 (15분)
```
1. 자동화된 규칙을 정책으로 추가
2. 비즈니스 룰 명확화
3. 예외 처리 규칙 정의
```

### 5단계: 애그리게잇 설계 (20분)
```
1. 연관된 이벤트/커맨드 그룹화
2. 트랜잭션 경계 식별
3. 애그리게잇 추가
```

### 6단계: 바운디드 컨텍스트 정의 (20분)
```
1. 논리적으로 응집된 영역 식별
2. 컨텍스트 생성 및 명명
3. 요소들을 컨텍스트에 할당
4. 컨텍스트 간 관계 분석
```

### 7단계: 문제 영역 표시 (10분)
```
1. 불확실한 영역을 핫스팟으로 표시
2. 기술적 도전 과제 기록
3. 비즈니스 리스크 영역 표시
```

### 8단계: 검토 및 정리 (15분)
```
1. 전체 흐름 검토 (visualize_flow 사용)
2. 통계 확인 (get_statistics 사용)
3. 타임라인 검증 (get_timeline 사용)
4. 워크샵 내보내기 (export_workshop 사용)
```

## 고급 활용 팁

### 1. 효과적인 검색 활용
```
- 특정 개념 찾기: search_elements(query="payment")
- 타입별 필터: element_type="event"
- 컨텍스트별 필터: bounded_context_id="ctx-123"
```

### 2. 이벤트 흐름 분석
```
- 전체 흐름 보기: visualize_flow() (start 없이)
- 특정 지점부터 추적: visualize_flow(start_element_id="evt-123")
- 깊이 제한: max_depth=3
```

### 3. 통계 활용
```
- 컨텍스트 커버리지 확인
- 타입별 분포 분석
- 관계 밀도 측정
- 미할당 요소 파악
```

### 4. 협업 워크플로우
```
1. 워크샵 진행 중 실시간 업데이트
2. 주기적으로 export하여 백업
3. 팀원과 JSON 공유
4. 각자 작업 후 merge
5. import로 통합
```

### 5. 반복적 개선
```
1. 초기 워크샵 진행
2. 통계로 완성도 확인
3. 부족한 영역 보완
4. 바운디드 컨텍스트 재조정
5. 흐름 재검증
```

## 베스트 프랙티스

### 도메인 이벤트 작성
✅ 좋은 예:
- "Order Placed"
- "Payment Processed"
- "Invoice Generated"

❌ 나쁜 예:
- "Place Order" (이건 커맨드)
- "Processing Payment" (진행형 X)
- "Order" (이건 애그리게잇)

### 커맨드 작성
✅ 좋은 예:
- "Place Order"
- "Cancel Subscription"
- "Update Address"

❌ 나쁜 예:
- "Order Placing"
- "Subscription"
- "Address Updated" (이건 이벤트)

### 바운디드 컨텍스트 정의
✅ 좋은 원칙:
- 명확한 책임 범위
- 자율적 운영 가능
- 응집도 높은 요소 그룹
- 다른 컨텍스트와 느슨한 결합

❌ 피해야 할 것:
- 너무 큰 컨텍스트 (God Context)
- 너무 작은 컨텍스트 (Anemic Context)
- 불명확한 경계
- 순환 의존성

### 위치(Position) 활용
```
- 0번대: 시작 이벤트
- 10번대: 초기 처리
- 20번대: 중간 처리
- 30번대: 완료 처리
- 99번: 에러/예외 처리

간격을 두면 나중에 중간 삽입 용이
```

### 관계 설정
```
- 직접적인 인과관계만 연결
- 순환 참조 주의
- 너무 많은 관계는 복잡도 증가
- 핵심 흐름에 집중
```

## 문제 해결

### 워크샵을 찾을 수 없음
```
문제: "Workshop not found" 에러
해결: 
1. list_workshops로 ID 확인
2. 정확한 ID 사용
3. 파일 권한 확인
```

### 요소 관계가 복잡함
```
문제: 관계가 너무 많아 혼란스러움
해결:
1. visualize_flow로 전체 구조 파악
2. 컨텍스트별로 분리 검토
3. 핵심 흐름만 남기고 부차적 관계 제거
```

### 바운디드 컨텍스트 경계가 불명확
```
문제: 어떤 요소를 어느 컨텍스트에 넣어야 할지 모름
해결:
1. 응집도 기준으로 판단
2. 변경 이유가 같은 것끼리 그룹
3. 팀 구조 고려
4. 반복적으로 조정
```

## 데이터 구조

### Workshop JSON 구조
```json
{
  "metadata": {
    "id": "uuid",
    "name": "워크샵 이름",
    "description": "설명",
    "domain": "도메인",
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp",
    "facilitators": ["이름1", "이름2"]
  },
  "elements": [
    {
      "id": "uuid",
      "type": "event|command|actor|aggregate|policy|read_model|external_system|hotspot",
      "name": "요소 이름",
      "description": "설명",
      "position": 0,
      "notes": "노트",
      "created_at": "ISO timestamp",
      "updated_at": "ISO timestamp",
      "created_by": "작성자",
      "triggers": ["element_id1", "element_id2"],
      "triggered_by": ["element_id3"],
      "bounded_context_id": "context_id"
    }
  ],
  "bounded_contexts": [
    {
      "id": "uuid",
      "name": "컨텍스트 이름",
      "description": "설명",
      "element_ids": ["elem1", "elem2"],
      "color": "#FF5733"
    }
  ]
}
```

## 출력 형식

대부분의 도구는 `response_format` 매개변수로 출력 형식을 지정할 수 있습니다:

### Markdown 형식 (기본값)
- 읽기 쉬운 형식
- 헤더, 목록, 강조 사용
- 사람이 검토하기 좋음

### JSON 형식
- 구조화된 데이터
- 프로그래밍 처리 가능
- 다른 도구와 통합 용이

## 저장 위치

워크샵 데이터는 다음 위치에 저장됩니다:
```
~/.eventstorming_workshops/{workshop_id}.json
```

## 성능 고려사항

### 문자 제한
- 응답 크기 제한: 25,000자
- 초과 시 자동 truncate
- 페이지네이션 제안 제공

### 대용량 워크샵
```
요소가 많을 경우:
1. 타입별로 나눠 조회
2. 컨텍스트별로 나눠 조회
3. 검색 기능 활용
4. JSON 형식으로 직접 처리
```

## 확장 아이디어

### 향후 추가 가능 기능
1. 버전 관리 (Git 통합)
2. 다중 사용자 협업
3. 실시간 동기화
4. 템플릿 시스템
5. 시각화 내보내기 (PlantUML, Mermaid)
6. AI 기반 제안
7. 일관성 검증
8. 문서 자동 생성

## 참고 자료

- Event Storming 공식 사이트: https://www.eventstorming.com/
- Domain-Driven Design 커뮤니티: https://www.dddcommunity.org/
- Alberto Brandolini의 "Introducing EventStorming" 책

## 라이센스 및 기여

이 MCP 서버는 Event Storming 커뮤니티와 DDD 실무자들을 위한 오픈 소스 도구입니다.

---

**버전**: 1.0  
**최종 업데이트**: 2025-10-21  
**호환성**: MCP Python SDK, FastMCP
