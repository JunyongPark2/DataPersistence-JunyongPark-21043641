from sampleorder.exceptions import DuplicateError, NotFoundError
from sampleorder.models import Order, OrderStatus, Sample


def test_sample_to_dict_and_from_dict_round_trip():
    sample = Sample(
        sample_id="S-001",
        name="실리콘 웨이퍼-8인치",
        avg_production_time=0.5,
        yield_rate=0.92,
        stock=480,
    )

    data = sample.to_dict()
    restored = Sample.from_dict(data)

    assert data == {
        "sample_id": "S-001",
        "name": "실리콘 웨이퍼-8인치",
        "avg_production_time": 0.5,
        "yield_rate": 0.92,
        "stock": 480,
    }
    assert restored == sample


def test_order_to_dict_and_from_dict_round_trip():
    order = Order(
        order_id="ORD-20260416-0001",
        sample_id="S-001",
        customer_name="삼성전자 파운드리",
        quantity=200,
        status=OrderStatus.RESERVED,
        created_at="2026-04-16T09:30:00",
    )

    data = order.to_dict()
    restored = Order.from_dict(data)

    assert data["status"] == "RESERVED"
    assert restored == order


def test_order_status_enum_members():
    assert {s.value for s in OrderStatus} == {
        "RESERVED",
        "REJECTED",
        "PRODUCING",
        "CONFIRMED",
        "RELEASE",
    }


def test_not_found_error_message():
    err = NotFoundError("Sample", "S-999")
    assert str(err) == "Sample not found: S-999"


def test_duplicate_error_message():
    err = DuplicateError("Order", "ORD-1")
    assert str(err) == "Order already exists: ORD-1"
