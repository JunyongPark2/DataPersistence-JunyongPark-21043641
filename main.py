from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from sampleorder.models import OrderStatus
from sampleorder.order_repository import OrderRepository
from sampleorder.sample_repository import SampleRepository

DATA_DIR = Path(__file__).parent / "data"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    sample_repo = SampleRepository(DATA_DIR / "samples.json")
    order_repo = OrderRepository(DATA_DIR / "orders.json")

    print("=== 시료 등록 ===")
    existing = sample_repo.list_all()
    if existing:
        print(f"기존에 저장된 시료 {len(existing)}건을 불러왔습니다 (재실행해도 데이터가 유지됨을 확인).")
        for s in existing:
            print(f"  {s.sample_id} | {s.name} | 재고 {s.stock} ea")
    else:
        wafer = sample_repo.create(name="실리콘 웨이퍼-8인치", avg_production_time=0.5, yield_rate=0.92, stock=480)
        gan = sample_repo.create(name="GaN 에피택셜-4인치", avg_production_time=0.3, yield_rate=0.78, stock=220)
        print(f"등록 완료: {wafer.sample_id} {wafer.name}, {gan.sample_id} {gan.name}")

    print("\n=== 시료 검색: '웨이퍼' ===")
    for s in sample_repo.search("웨이퍼"):
        print(f"  {s.sample_id} | {s.name} | 재고 {s.stock} ea")

    first_sample = sample_repo.list_all()[0]

    print("\n=== 주문 생성 ===")
    order = order_repo.create(
        sample_id=first_sample.sample_id,
        customer_name="삼성전자 파운드리",
        quantity=100,
        created_at=now_iso(),
    )
    print(f"생성됨: {order.order_id} | 상태 {order.status.value}")

    print("\n=== 주문 승인 (RESERVED -> CONFIRMED) ===")
    confirmed = order_repo.update(order.order_id, status=OrderStatus.CONFIRMED)
    print(f"변경됨: {confirmed.order_id} | 상태 {confirmed.status.value}")

    print("\n=== CONFIRMED 상태 주문 목록 ===")
    for o in order_repo.list_by_status(OrderStatus.CONFIRMED):
        print(f"  {o.order_id} | {o.customer_name} | {o.quantity} ea")

    print("\n=== 시료 재고 차감 (update) ===")
    updated_sample = sample_repo.update(first_sample.sample_id, stock=first_sample.stock - order.quantity)
    print(f"재고 변경됨: {updated_sample.sample_id} | 재고 {updated_sample.stock} ea")

    print(f"\ndata/samples.json, data/orders.json 에 저장되었습니다. "
          f"프로그램을 다시 실행하면 위 데이터가 그대로 유지됩니다.")


if __name__ == "__main__":
    main()
