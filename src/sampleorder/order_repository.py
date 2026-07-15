from __future__ import annotations

from pathlib import Path

from sampleorder.exceptions import NotFoundError
from sampleorder.json_store import JsonFileStore
from sampleorder.models import Order, OrderStatus

_ENTITY_NAME = "Order"


class OrderRepository:
    def __init__(self, path: Path | str):
        self._store = JsonFileStore(path)

    def create(self, sample_id: str, customer_name: str, quantity: int, created_at: str) -> Order:
        records = self._store.load()
        date_str = created_at[:10].replace("-", "")
        order_id = self._next_id(records, date_str)
        order = Order(
            order_id=order_id,
            sample_id=sample_id,
            customer_name=customer_name,
            quantity=quantity,
            status=OrderStatus.RESERVED,
            created_at=created_at,
        )
        records.append(order.to_dict())
        self._store.save(records)
        return order

    def get(self, order_id: str) -> Order:
        for record in self._store.load():
            if record["order_id"] == order_id:
                return Order.from_dict(record)
        raise NotFoundError(_ENTITY_NAME, order_id)

    def list_all(self) -> list[Order]:
        return [Order.from_dict(r) for r in self._store.load()]

    def list_by_status(self, status: OrderStatus) -> list[Order]:
        return [o for o in self.list_all() if o.status == status]

    def update(self, order_id: str, **fields) -> Order:
        if "status" in fields and isinstance(fields["status"], OrderStatus):
            fields["status"] = fields["status"].value
        records = self._store.load()
        for record in records:
            if record["order_id"] == order_id:
                record.update(fields)
                self._store.save(records)
                return Order.from_dict(record)
        raise NotFoundError(_ENTITY_NAME, order_id)

    def delete(self, order_id: str) -> None:
        records = self._store.load()
        remaining = [r for r in records if r["order_id"] != order_id]
        if len(remaining) == len(records):
            raise NotFoundError(_ENTITY_NAME, order_id)
        self._store.save(remaining)

    @staticmethod
    def _next_id(records: list[dict], date_str: str) -> str:
        prefix = f"ORD-{date_str}-"
        max_seq = 0
        for record in records:
            if record["order_id"].startswith(prefix):
                seq = int(record["order_id"].split("-")[2])
                max_seq = max(max_seq, seq)
        return f"{prefix}{max_seq + 1:04d}"
