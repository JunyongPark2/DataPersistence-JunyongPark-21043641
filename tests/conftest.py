import pytest

from sampleorder.order_repository import OrderRepository
from sampleorder.sample_repository import SampleRepository


@pytest.fixture
def sample_repo(tmp_path):
    return SampleRepository(tmp_path / "samples.json")


@pytest.fixture
def order_repo(tmp_path):
    return OrderRepository(tmp_path / "orders.json")
