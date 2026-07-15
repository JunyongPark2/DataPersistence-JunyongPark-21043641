import pytest

from sampleorder.exceptions import NotFoundError
from sampleorder.models import OrderStatus
from sampleorder.order_repository import OrderRepository


def test_create_defaults_to_reserved_status(order_repo):
    order = order_repo.create(
        sample_id="S-001",
        customer_name="삼성전자 파운드리",
        quantity=200,
        created_at="2026-04-16T09:30:00",
    )

    assert order.status == OrderStatus.RESERVED


def test_create_assigns_id_with_date_prefix_and_sequence(order_repo):
    first = order_repo.create(sample_id="S-001", customer_name="A", quantity=1, created_at="2026-04-16T09:00:00")
    second = order_repo.create(sample_id="S-002", customer_name="B", quantity=1, created_at="2026-04-16T10:00:00")

    assert first.order_id == "ORD-20260416-0001"
    assert second.order_id == "ORD-20260416-0002"


def test_create_resets_sequence_for_new_date(order_repo):
    order_repo.create(sample_id="S-001", customer_name="A", quantity=1, created_at="2026-04-16T09:00:00")
    next_day = order_repo.create(sample_id="S-002", customer_name="B", quantity=1, created_at="2026-04-17T09:00:00")

    assert next_day.order_id == "ORD-20260417-0001"


def test_get_returns_created_order(order_repo):
    created = order_repo.create(sample_id="S-001", customer_name="A", quantity=5, created_at="2026-04-16T09:00:00")

    assert order_repo.get(created.order_id) == created


def test_get_missing_raises_not_found(order_repo):
    with pytest.raises(NotFoundError):
        order_repo.get("ORD-00000000-0000")


def test_list_all_returns_insertion_order(order_repo):
    order_repo.create(sample_id="S-001", customer_name="A", quantity=1, created_at="2026-04-16T09:00:00")
    order_repo.create(sample_id="S-002", customer_name="B", quantity=1, created_at="2026-04-16T09:01:00")

    customers = [o.customer_name for o in order_repo.list_all()]

    assert customers == ["A", "B"]


def test_list_by_status_filters_correctly(order_repo):
    reserved = order_repo.create(sample_id="S-001", customer_name="A", quantity=1, created_at="2026-04-16T09:00:00")
    confirmed = order_repo.create(sample_id="S-002", customer_name="B", quantity=1, created_at="2026-04-16T09:01:00")
    order_repo.update(confirmed.order_id, status=OrderStatus.CONFIRMED)

    reserved_orders = order_repo.list_by_status(OrderStatus.RESERVED)
    confirmed_orders = order_repo.list_by_status(OrderStatus.CONFIRMED)

    assert [o.order_id for o in reserved_orders] == [reserved.order_id]
    assert [o.order_id for o in confirmed_orders] == [confirmed.order_id]


def test_update_changes_status(order_repo):
    created = order_repo.create(sample_id="S-001", customer_name="A", quantity=1, created_at="2026-04-16T09:00:00")

    updated = order_repo.update(created.order_id, status=OrderStatus.CONFIRMED)

    assert updated.status == OrderStatus.CONFIRMED


def test_update_missing_raises_not_found(order_repo):
    with pytest.raises(NotFoundError):
        order_repo.update("ORD-00000000-0000", status=OrderStatus.REJECTED)


def test_delete_removes_order(order_repo):
    created = order_repo.create(sample_id="S-001", customer_name="A", quantity=1, created_at="2026-04-16T09:00:00")

    order_repo.delete(created.order_id)

    with pytest.raises(NotFoundError):
        order_repo.get(created.order_id)


def test_delete_missing_raises_not_found(order_repo):
    with pytest.raises(NotFoundError):
        order_repo.delete("ORD-00000000-0000")


def test_data_persists_across_repository_instances(tmp_path):
    path = tmp_path / "orders.json"
    repo1 = OrderRepository(path)
    created = repo1.create(sample_id="S-001", customer_name="A", quantity=1, created_at="2026-04-16T09:00:00")

    repo2 = OrderRepository(path)

    assert repo2.get(created.order_id) == created
