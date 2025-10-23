# Event Storming MCP 실전 튜토리얼

## 튜토리얼: 전자상거래 주문 시스템 Event Storming

이 튜토리얼에서는 전자상거래 플랫폼의 주문 관리 시스템을 Event Storming으로 모델링하는 전체 과정을 단계별로 안내합니다.

---

## 목차

1. [워크샵 설정](#1-워크샵-설정)
2. [도메인 이벤트 추가](#2-도메인-이벤트-추가)
3. [커맨드와 액터 식별](#3-커맨드와-액터-식별)
4. [관계 설정](#4-관계-설정)
5. [애그리게잇 정의](#5-애그리게잇-정의)
6. [정책 및 규칙 추가](#6-정책-및-규칙-추가)
7. [바운디드 컨텍스트 구성](#7-바운디드-컨텍스트-구성)
8. [읽기 모델 추가](#8-읽기-모델-추가)
9. [외부 시스템 식별](#9-외부-시스템-식별)
10. [핫스팟 표시](#10-핫스팟-표시)
11. [분석 및 검증](#11-분석-및-검증)

---

## 1. 워크샵 설정

### 워크샵 생성하기

**도구**: `eventstorming_create_workshop`

```json
{
  "name": "E-commerce Order Management System",
  "description": "온라인 쇼핑몰의 주문 접수부터 배송 완료까지의 전체 프로세스를 분석하고 모델링",
  "domain": "E-commerce",
  "facilitators": ["김도메인", "이이벤트"]
}
```

**응답 예시**:
```json
{
  "success": true,
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "E-commerce Order Management System",
  "message": "Workshop 'E-commerce Order Management System' created successfully"
}
```

💡 **팁**: `workshop_id`를 복사해두세요. 모든 후속 작업에서 사용됩니다.

---

## 2. 도메인 이벤트 추가

Event Storming의 핵심은 도메인 이벤트입니다. 시스템에서 일어나는 중요한 일들을 "~했다", "~됨" 형태로 기록합니다.

### 2.1 주문 접수 단계

**도구**: `eventstorming_add_element`

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Order Placed",
  "description": "고객이 장바구니에서 주문을 확정하고 주문이 시스템에 접수됨",
  "position": 0,
  "notes": "주문 번호 생성, 재고 예약 시작",
  "created_by": "김도메인"
}
```

### 2.2 결제 처리 단계

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Payment Authorized",
  "description": "결제 수단이 검증되고 결제 승인이 완료됨",
  "position": 10,
  "notes": "PG사 연동, 신용카드/간편결제 지원"
}
```

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Payment Captured",
  "description": "실제 결제 금액이 차감되고 거래가 확정됨",
  "position": 11,
  "notes": "취소 불가 시점"
}
```

### 2.3 주문 확정 및 처리 단계

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Order Confirmed",
  "description": "결제가 완료되어 주문이 확정됨",
  "position": 20,
  "notes": "고객에게 주문 확인 이메일 발송"
}
```

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Inventory Reserved",
  "description": "주문한 상품의 재고가 예약됨",
  "position": 21,
  "notes": "실재고 차감은 출고 시점"
}
```

### 2.4 배송 준비 단계

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Items Picked",
  "description": "창고에서 상품이 피킹되어 포장 준비됨",
  "position": 30,
  "notes": "바코드 스캔으로 검증"
}
```

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Package Prepared",
  "description": "상품이 포장되고 송장이 발행됨",
  "position": 31,
  "notes": "무게/크기 측정, 배송비 확정"
}
```

### 2.5 배송 단계

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Order Shipped",
  "description": "택배사에 인계되어 배송이 시작됨",
  "position": 40,
  "notes": "운송장 번호 고객 통지"
}
```

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Order In Transit",
  "description": "배송 중간 거점 도착",
  "position": 41,
  "notes": "실시간 배송 추적"
}
```

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Order Delivered",
  "description": "고객에게 상품이 배달 완료됨",
  "position": 50,
  "notes": "수령 확인, 배송 완료 알림"
}
```

### 2.6 예외 상황 이벤트

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Payment Failed",
  "description": "결제 승인이 실패함",
  "position": 12,
  "notes": "한도 초과, 카드 오류 등"
}
```

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Order Cancelled",
  "description": "주문이 취소됨",
  "position": 99,
  "notes": "고객 요청 또는 재고 부족"
}
```

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "event",
  "name": "Delivery Failed",
  "description": "배송 시도가 실패함",
  "position": 42,
  "notes": "부재, 주소 오류 등"
}
```

---

## 3. 커맨드와 액터 식별

이제 각 이벤트를 발생시키는 커맨드와 그 커맨드를 실행하는 액터를 추가합니다.

### 3.1 액터 추가

**고객 액터**:
```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "actor",
  "name": "Customer",
  "description": "온라인 쇼핑몰 사용자",
  "position": 0
}
```

**시스템 액터**:
```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "actor",
  "name": "Payment Gateway",
  "description": "외부 결제 처리 시스템",
  "position": 10
}
```

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "actor",
  "name": "Warehouse Staff",
  "description": "창고 작업자",
  "position": 30
}
```

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "actor",
  "name": "Delivery Service",
  "description": "택배 서비스",
  "position": 40
}
```

### 3.2 커맨드 추가

**주문 생성 커맨드**:
```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "command",
  "name": "Place Order",
  "description": "장바구니에서 주문하기 버튼 클릭",
  "position": 0,
  "notes": "결제 정보 및 배송지 검증 필요"
}
```

**결제 처리 커맨드**:
```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "command",
  "name": "Authorize Payment",
  "description": "결제 승인 요청",
  "position": 10
}
```

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "command",
  "name": "Capture Payment",
  "description": "결제 금액 실제 차감",
  "position": 11
}
```

**주문 처리 커맨드**:
```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "command",
  "name": "Confirm Order",
  "description": "주문 확정 처리",
  "position": 20
}
```

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "command",
  "name": "Reserve Inventory",
  "description": "재고 예약",
  "position": 21
}
```

**피킹 및 포장 커맨드**:
```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "command",
  "name": "Pick Items",
  "description": "상품 피킹",
  "position": 30
}
```

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "command",
  "name": "Prepare Package",
  "description": "포장 및 송장 발행",
  "position": 31
}
```

**배송 커맨드**:
```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "command",
  "name": "Ship Order",
  "description": "택배사 인계",
  "position": 40
}
```

**취소 커맨드**:
```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "command",
  "name": "Cancel Order",
  "description": "주문 취소 처리",
  "position": 99
}
```

---

## 4. 관계 설정

이제 요소들 간의 인과관계를 설정합니다. 실제로는 각 요소를 추가할 때 `triggers`와 `triggered_by`를 함께 설정하거나, 나중에 `eventstorming_update_element`로 업데이트할 수 있습니다.

### 예시: "Place Order" 커맨드 업데이트

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "element_id": "place-order-cmd-id",
  "triggers": ["order-placed-event-id"]
}
```

### 전체 흐름 체인

```
Customer → Place Order → Order Placed
Order Placed → Authorize Payment → Payment Authorized
Payment Authorized → Capture Payment → Payment Captured
Payment Captured → Confirm Order → Order Confirmed
Order Confirmed → Reserve Inventory → Inventory Reserved
Inventory Reserved → Pick Items → Items Picked
Items Picked → Prepare Package → Package Prepared
Package Prepared → Ship Order → Order Shipped
Order Shipped → (Delivery Service) → Order Delivered
```

---

## 5. 애그리게잇 정의

애그리게잇은 일관성 경계를 나타냅니다. 관련된 이벤트와 커맨드를 묶어 트랜잭션 범위를 정의합니다.

### Order 애그리게잇

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "aggregate",
  "name": "Order",
  "description": "주문 애그리게잇 - 주문 상태 및 이력 관리",
  "position": 0,
  "notes": "주문 생성, 확정, 취소 등 주문 생명주기 관리"
}
```

### Payment 애그리게잇

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "aggregate",
  "name": "Payment",
  "description": "결제 애그리게잇 - 결제 정보 및 상태 관리",
  "position": 10,
  "notes": "승인, 차감, 환불 등 결제 트랜잭션 관리"
}
```

### Inventory 애그리게잇

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "aggregate",
  "name": "Inventory",
  "description": "재고 애그리게잇 - 재고 수량 및 예약 관리",
  "position": 21,
  "notes": "재고 예약, 차감, 복구 등 재고 일관성 보장"
}
```

### Shipment 애그리게잇

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "aggregate",
  "name": "Shipment",
  "description": "배송 애그리게잇 - 배송 정보 및 추적 관리",
  "position": 40,
  "notes": "배송 상태, 운송장 번호, 배송 이력"
}
```

---

## 6. 정책 및 규칙 추가

비즈니스 규칙과 자동화된 정책을 명시합니다.

### 결제 실패 시 처리 정책

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "policy",
  "name": "Payment Failure Policy",
  "description": "결제 실패 시 자동으로 주문 취소 및 재고 복구",
  "position": 12,
  "notes": "3회 재시도 후 최종 취소"
}
```

### 재고 부족 정책

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "policy",
  "name": "Insufficient Inventory Policy",
  "description": "재고 부족 시 주문 취소 또는 부분 배송",
  "position": 22,
  "notes": "고객 선택 옵션: 전체 취소 or 부분 배송"
}
```

### 배송 지연 알림 정책

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "policy",
  "name": "Shipping Delay Notification Policy",
  "description": "예상 배송일로부터 3일 이상 지연 시 고객에게 자동 알림",
  "position": 43,
  "notes": "SMS + 이메일 발송, 보상 쿠폰 제공"
}
```

### 자동 구매 확정 정책

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "policy",
  "name": "Auto Confirmation Policy",
  "description": "배송 완료 후 7일이 지나면 자동으로 구매 확정",
  "position": 51,
  "notes": "구매 확정 시 판매자에게 정산"
}
```

---

## 7. 바운디드 컨텍스트 구성

이제 관련 요소들을 논리적으로 그룹화하여 바운디드 컨텍스트를 만듭니다.

### 7.1 Order Management Context 생성

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Order Management",
  "description": "주문 접수, 확정, 취소 등 주문 생명주기 관리",
  "color": "#3498db"
}
```

**할당할 요소들**:
- Order Placed (event)
- Order Confirmed (event)
- Order Cancelled (event)
- Place Order (command)
- Confirm Order (command)
- Cancel Order (command)
- Order (aggregate)
- Customer (actor)

### 7.2 Payment Context 생성

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Payment",
  "description": "결제 처리 및 검증",
  "color": "#2ecc71"
}
```

**할당할 요소들**:
- Payment Authorized (event)
- Payment Captured (event)
- Payment Failed (event)
- Authorize Payment (command)
- Capture Payment (command)
- Payment (aggregate)
- Payment Gateway (actor)
- Payment Failure Policy (policy)

### 7.3 Inventory Context 생성

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Inventory",
  "description": "재고 관리 및 예약",
  "color": "#f39c12"
}
```

**할당할 요소들**:
- Inventory Reserved (event)
- Reserve Inventory (command)
- Inventory (aggregate)
- Insufficient Inventory Policy (policy)

### 7.4 Fulfillment Context 생성

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Fulfillment",
  "description": "주문 피킹, 포장, 배송",
  "color": "#9b59b6"
}
```

**할당할 요소들**:
- Items Picked (event)
- Package Prepared (event)
- Order Shipped (event)
- Order In Transit (event)
- Order Delivered (event)
- Delivery Failed (event)
- Pick Items (command)
- Prepare Package (command)
- Ship Order (command)
- Shipment (aggregate)
- Warehouse Staff (actor)
- Delivery Service (actor)
- Shipping Delay Notification Policy (policy)
- Auto Confirmation Policy (policy)

### 7.5 요소 할당 예시

**도구**: `eventstorming_assign_to_context`

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "context_id": "order-management-context-id",
  "element_ids": [
    "order-placed-event-id",
    "order-confirmed-event-id",
    "order-cancelled-event-id",
    "place-order-cmd-id",
    "confirm-order-cmd-id",
    "cancel-order-cmd-id",
    "order-aggregate-id",
    "customer-actor-id"
  ]
}
```

---

## 8. 읽기 모델 추가

사용자에게 정보를 제공하기 위한 읽기 모델을 추가합니다.

### Order History Read Model

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "read_model",
  "name": "Order History",
  "description": "고객의 주문 이력 조회용 읽기 모델",
  "position": 1,
  "notes": "주문 목록, 상세 정보, 배송 추적"
}
```

### Inventory Status Read Model

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "read_model",
  "name": "Inventory Status",
  "description": "실시간 재고 현황 조회용 읽기 모델",
  "position": 22,
  "notes": "가용 재고, 예약 재고, 입고 예정"
}
```

### Delivery Tracking Read Model

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "read_model",
  "name": "Delivery Tracking",
  "description": "배송 추적 정보 조회용 읽기 모델",
  "position": 41,
  "notes": "현재 위치, 예상 도착 시간, 배송 이력"
}
```

---

## 9. 외부 시스템 식별

시스템이 의존하는 외부 서비스를 명시합니다.

### Payment Gateway System

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "external_system",
  "name": "PG Service (Toss, Stripe)",
  "description": "외부 결제 게이트웨이",
  "position": 10,
  "notes": "API 타임아웃: 30초, 재시도 정책 필요"
}
```

### Courier API

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "external_system",
  "name": "Courier Tracking API",
  "description": "택배사 배송 추적 API",
  "position": 41,
  "notes": "실시간 위치 정보, Webhook 지원"
}
```

### Notification Service

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "external_system",
  "name": "SMS/Email Service",
  "description": "알림 발송 서비스",
  "position": 99,
  "notes": "주문 확인, 배송 알림 등"
}
```

---

## 10. 핫스팟 표시

불확실하거나 문제가 될 수 있는 영역을 핫스팟으로 표시합니다.

### Payment Timeout 핫스팟

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "hotspot",
  "name": "Payment Gateway Timeout Handling",
  "description": "PG 타임아웃 시 주문 상태 관리 방법 불명확",
  "position": 10,
  "notes": "재시도 로직? 주문 취소? 수동 확인? - 논의 필요"
}
```

### Inventory Concurrency 핫스팟

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "hotspot",
  "name": "Inventory Concurrent Reservation",
  "description": "동시 주문 시 재고 예약 동시성 문제",
  "position": 21,
  "notes": "낙관적 잠금? 비관적 잠금? 분산 락? - 성능 vs 정합성"
}
```

### Delivery Failure Recovery 핫스팟

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "hotspot",
  "name": "Delivery Failure Recovery Process",
  "description": "배송 실패 시 재배송 프로세스 미정의",
  "position": 42,
  "notes": "자동 재배송? 고객 재요청? 환불 처리? - 비용 vs 고객 만족"
}
```

### Partial Shipment 핫스팟

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "hotspot",
  "name": "Partial Shipment Complexity",
  "description": "부분 배송 시 결제, 재고, 배송비 처리 복잡도",
  "position": 23,
  "notes": "분할 배송 정책, 추가 배송비 부담 주체 - 복잡도 높음"
}
```

---

## 11. 분석 및 검증

워크샵이 완성되면 다양한 분석 도구로 검증합니다.

### 11.1 통계 확인

**도구**: `eventstorming_get_statistics`

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "response_format": "markdown"
}
```

**예상 결과**:
```markdown
# Workshop Statistics: E-commerce Order Management System

## Overview
- Domain: E-commerce
- Total Elements: 45
- Bounded Contexts: 4

## Elements by Type
- event: 12
- command: 9
- actor: 4
- aggregate: 4
- policy: 4
- read_model: 3
- external_system: 3
- hotspot: 4

## Elements by Bounded Context
- Order Management: 8
- Payment: 7
- Inventory: 4
- Fulfillment: 15

## Relationships
- Elements with outgoing triggers: 9
- Total trigger links: 11

## Context Coverage
- Elements assigned to contexts: 42
- Elements without context: 3
- Coverage: 93.3%
```

### 11.2 타임라인 검증

**도구**: `eventstorming_get_timeline`

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "element_type": "event",
  "response_format": "markdown"
}
```

이벤트들이 시간 순서대로 올바르게 배치되었는지 확인합니다.

### 11.3 이벤트 흐름 시각화

**도구**: `eventstorming_visualize_flow`

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "max_depth": 10
}
```

**예상 결과**:
```markdown
# Event Flow Visualization

## Flow from: Place Order
→ [command] Place Order
  → [event] Order Placed
    → [command] Authorize Payment
      → [event] Payment Authorized
        → [command] Capture Payment
          → [event] Payment Captured
            → [command] Confirm Order
              → [event] Order Confirmed
                → [command] Reserve Inventory
                  → [event] Inventory Reserved
```

### 11.4 컨텍스트 개요

**도구**: `eventstorming_get_context_overview`

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "response_format": "markdown"
}
```

각 바운디드 컨텍스트의 완성도와 균형을 확인합니다.

### 11.5 핫스팟 검색

**도구**: `eventstorming_search_elements`

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "timeout",
  "element_type": "hotspot"
}
```

미해결 문제들을 모아서 후속 논의 계획을 세웁니다.

---

## 12. 워크샵 내보내기 및 공유

### 내보내기

**도구**: `eventstorming_export_workshop`

```json
{
  "workshop_id": "550e8400-e29b-41d4-a716-446655440000",
  "include_metadata": true
}
```

JSON 파일을 팀원들과 공유하거나 Git 저장소에 커밋합니다.

---

## 다음 단계

1. **핫스팟 해결**: 표시된 문제 영역에 대한 심화 논의
2. **구현 계획**: 바운디드 컨텍스트별 개발 우선순위 결정
3. **마이크로서비스 설계**: 각 컨텍스트를 독립 서비스로 설계
4. **API 정의**: 컨텍스트 간 통신 인터페이스 설계
5. **이벤트 스키마 정의**: 도메인 이벤트의 데이터 구조 정의

---

## 베스트 프랙티스 요약

✅ **DO**:
- 이벤트는 과거형으로
- 핵심 흐름부터 시작
- 예외 상황도 포함
- 바운디드 컨텍스트 경계 명확히
- 핫스팟 솔직하게 표시

❌ **DON'T**:
- 너무 세밀한 이벤트 (UI 클릭 등)
- 기술 용어로만 표현
- 완벽주의 (반복적 개선)
- 컨텍스트 간 강한 결합

---

**완료! 🎉**

이제 구조화된 Event Storming 워크샵 데이터를 바탕으로 실제 시스템 설계와 구현을 시작할 수 있습니다.
