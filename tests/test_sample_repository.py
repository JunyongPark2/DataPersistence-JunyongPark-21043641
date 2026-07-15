import pytest

from sampleorder.exceptions import NotFoundError
from sampleorder.sample_repository import SampleRepository


def test_create_assigns_sequential_ids(sample_repo):
    first = sample_repo.create(name="실리콘 웨이퍼-8인치", avg_production_time=0.5, yield_rate=0.92, stock=480)
    second = sample_repo.create(name="GaN 에피택셜-4인치", avg_production_time=0.3, yield_rate=0.78, stock=220)

    assert first.sample_id == "S-001"
    assert second.sample_id == "S-002"


def test_create_defaults_stock_to_zero(sample_repo):
    sample = sample_repo.create(name="포토레지스트-PR7", avg_production_time=0.2, yield_rate=0.95)

    assert sample.stock == 0


def test_get_returns_created_sample(sample_repo):
    created = sample_repo.create(name="산화막 웨이퍼-SiO2", avg_production_time=0.6, yield_rate=0.88, stock=0)

    fetched = sample_repo.get(created.sample_id)

    assert fetched == created


def test_get_missing_raises_not_found(sample_repo):
    with pytest.raises(NotFoundError):
        sample_repo.get("S-999")


def test_list_all_returns_insertion_order(sample_repo):
    sample_repo.create(name="A", avg_production_time=0.1, yield_rate=0.9)
    sample_repo.create(name="B", avg_production_time=0.2, yield_rate=0.9)

    names = [s.name for s in sample_repo.list_all()]

    assert names == ["A", "B"]


def test_search_matches_case_insensitive_substring(sample_repo):
    sample_repo.create(name="실리콘 웨이퍼-8인치", avg_production_time=0.5, yield_rate=0.92)
    sample_repo.create(name="SiC 파워기판-6인치", avg_production_time=0.8, yield_rate=0.92)

    results = sample_repo.search("sic")

    assert [s.name for s in results] == ["SiC 파워기판-6인치"]


def test_update_overwrites_only_given_fields(sample_repo):
    created = sample_repo.create(name="실리콘 웨이퍼-8인치", avg_production_time=0.5, yield_rate=0.92, stock=480)

    updated = sample_repo.update(created.sample_id, stock=430)

    assert updated.stock == 430
    assert updated.name == "실리콘 웨이퍼-8인치"


def test_update_missing_raises_not_found(sample_repo):
    with pytest.raises(NotFoundError):
        sample_repo.update("S-999", stock=1)


def test_delete_removes_sample(sample_repo):
    created = sample_repo.create(name="실리콘 웨이퍼-8인치", avg_production_time=0.5, yield_rate=0.92)

    sample_repo.delete(created.sample_id)

    with pytest.raises(NotFoundError):
        sample_repo.get(created.sample_id)


def test_delete_missing_raises_not_found(sample_repo):
    with pytest.raises(NotFoundError):
        sample_repo.delete("S-999")


def test_data_persists_across_repository_instances(tmp_path):
    path = tmp_path / "samples.json"
    repo1 = SampleRepository(path)
    created = repo1.create(name="실리콘 웨이퍼-8인치", avg_production_time=0.5, yield_rate=0.92, stock=480)

    repo2 = SampleRepository(path)

    assert repo2.get(created.sample_id) == created
