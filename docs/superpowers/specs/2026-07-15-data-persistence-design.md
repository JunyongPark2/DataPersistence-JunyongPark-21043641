# 데이터 영속성 처리 설계 (반도체 시료 생산주문관리 시스템)

## 배경

S-Semi 반도체 시료 생산주문관리 시스템의 "미션1 - 데이터 영속성 처리" 항목 구현.
팀(개인)이 선택한 방식으로 데이터를 저장·불러오는 구조를 CRUD 포함하여 구현한다.

- 선택한 저장 방식: **JSON 파일**
- 대상 엔티티: **Sample(시료), Order(주문)**
- 산출물: Repository 계층(CRUD) + pytest 테스트 + 동작을 보여주는 간단한 콘솔 데모(main.py)
- 콘솔 UI 전체(MVC)는 별도 미션(ConsoleMVC)의 범위이므로 본 저장소에서는 다루지 않는다.

## 구조

```
DataPersistence/
  src/sampleorder/
    __init__.py
    models.py              # Sample, Order 데이터클래스 + OrderStatus enum
    exceptions.py          # NotFoundError, DuplicateError
    json_store.py          # 범용 JSON 파일 read/write (atomic write)
    sample_repository.py   # Sample CRUD
    order_repository.py    # Order CRUD
  data/
    samples.json
    orders.json
  main.py                  # CRUD 동작을 보여주는 콘솔 데모
  tests/
    conftest.py
    test_json_store.py
    test_sample_repository.py
    test_order_repository.py
  pyproject.toml
  requirements.txt
  README.md
```

## 모델

### Sample (시료)
| 필드 | 타입 | 설명 |
|---|---|---|
| sample_id | str | `S-001`, `S-002`... 자동 채번 |
| name | str | 시료명 |
| avg_production_time | float | 평균 생산시간(분/ea) |
| yield_rate | float | 수율 (0~1) |
| stock | int | 현재 재고 |

### Order (주문)
| 필드 | 타입 | 설명 |
|---|---|---|
| order_id | str | `ORD-YYYYMMDD-NNNN` 형식, 자동 채번 |
| sample_id | str | 참조하는 Sample ID |
| customer_name | str | 고객명 |
| quantity | int | 주문 수량 |
| status | OrderStatus | RESERVED / REJECTED / PRODUCING / CONFIRMED / RELEASE |
| created_at | str (ISO8601) | 생성 시각 |

### OrderStatus (Enum)
`RESERVED`, `REJECTED`, `PRODUCING`, `CONFIRMED`, `RELEASE`

## 영속성 계층

`JsonFileStore`
- 생성자에 파일 경로를 받음 (레포지토리별로 별도 파일/인스턴스)
- `load() -> list[dict]`: 파일이 없으면 빈 리스트 반환
- `save(records: list[dict]) -> None`: 임시 파일에 쓴 뒤 `os.replace`로 원자적 교체 (쓰기 도중 프로세스 종료 시에도 기존 파일 손상 방지)
- 순수 파일 I/O만 담당, 도메인 로직은 알지 못함

## Repository (CRUD)

두 Repository(`SampleRepository`, `OrderRepository`) 모두 동일한 패턴:

- `create(...) -> Sample|Order`: ID 자동 채번 후 저장. 이미 존재하는 ID를 명시적으로 넘기는 내부 API에서 중복 시 `DuplicateError`
- `get(id) -> Sample|Order`: 없으면 `NotFoundError`
- `list_all() -> list[...]`: 저장된 전체 레코드 반환 (파일 순서 유지)
- `update(id, **fields) -> Sample|Order`: 없으면 `NotFoundError`, 존재하는 필드만 갱신
- `delete(id) -> None`: 없으면 `NotFoundError`

추가 조회 기능 (PDF 기능 명세 반영):
- `SampleRepository.search(keyword) -> list[Sample]`: 이름에 keyword 포함하는 시료 검색
- `OrderRepository.list_by_status(status: OrderStatus) -> list[Order]`: 상태별 주문 조회

각 Repository는 매 CRUD 연산마다 `JsonFileStore`를 통해 즉시 파일에 반영한다 (인메모리 캐시 없음 → 재실행/재시작해도 항상 파일이 최신 상태, "영속성" 요구사항 충족). 데이터 규모가 작다는 도메인 가정 하에 매번 전체 로드/저장하는 단순한 구현을 택한다.

## 에러 처리

- `NotFoundError(id)`: get/update/delete 대상이 없을 때
- `DuplicateError(id)`: 이미 존재하는 ID로 생성 시도할 때 (자동 채번 경로에서는 발생하지 않음, 방어적 코드)

두 예외 모두 일반 `Exception` 서브클래스이며, 시스템 경계(존재하지 않을 수 있는 사용자 입력 ID) 방어용으로만 사용한다.

## main.py 데모 시나리오

1. SampleRepository/OrderRepository 초기화 (data/ 하위 JSON 파일 사용)
2. 시료 2~3건 등록(create)
3. 등록된 시료 목록 출력(list_all), 이름으로 검색(search)
4. 주문 1건 생성(create, 초기 상태 RESERVED)
5. 주문 상태를 CONFIRMED로 변경(update)
6. 상태별 주문 목록 출력(list_by_status)
7. 시료 재고 수정(update), 주문 삭제(delete) 예시
8. 재실행 시에도 이전에 저장된 데이터가 그대로 로드됨을 확인하는 안내 메시지 출력

## 테스트 (pytest)

`tests/conftest.py`에서 `tmp_path`를 이용해 실제 `data/*.json`을 건드리지 않는 임시 Repository 인스턴스를 fixture로 제공.

- `test_json_store.py`: 파일 없을 때 빈 리스트, save 후 load 시 동일 데이터, atomic write 후 파일 존재 확인
- `test_sample_repository.py`: create/get/list_all/search/update/delete 정상 동작, get·update·delete 대상 없을 때 NotFoundError, 파일을 새 Repository 인스턴스로 다시 열어도 데이터 유지(영속성 검증)
- `test_order_repository.py`: create/get/list_all/list_by_status/update/delete 정상 동작, 존재하지 않는 order_id에 대한 NotFoundError, 영속성 검증

## 범위 제외

- 콘솔 메뉴/MVC 구조 전체 (별도 ConsoleMVC 미션)
- 데이터 모니터링 Tool, Dummy 데이터 생성 Tool (별도 미션)
- 동시성 제어(파일 락) — 단일 프로세스 콘솔 앱 가정
