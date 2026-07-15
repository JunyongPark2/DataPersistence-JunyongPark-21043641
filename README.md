# 반도체 시료/주문 데이터 영속성 계층 (DataPersistence)

S-Semi 반도체 시료 생산주문관리 시스템의 "데이터 영속성 처리" 미션 구현체입니다.
JSON 파일을 저장소로 사용하여 Sample(시료)/Order(주문) 데이터를 CRUD로 관리합니다.

설계 문서: `docs/superpowers/specs/2026-07-15-data-persistence-design.md`

## 구조

- `src/sampleorder/models.py` — Sample, Order, OrderStatus
- `src/sampleorder/json_store.py` — 원자적 쓰기를 지원하는 JSON 파일 I/O
- `src/sampleorder/sample_repository.py` — Sample CRUD + 이름 검색
- `src/sampleorder/order_repository.py` — Order CRUD + 상태별 조회
- `main.py` — CRUD 및 영속성(재실행해도 데이터 유지)을 보여주는 콘솔 데모
- `data/` — JSON 데이터 파일 저장 위치 (실행 시 자동 생성)

## 실행

```bash
pip install -r requirements.txt
python main.py
```

두 번 이상 실행해 `data/samples.json`, `data/orders.json`에 저장된 데이터가 유지되는지 확인할 수 있습니다.

## 테스트

```bash
pip install -r requirements.txt
pytest -v
```
