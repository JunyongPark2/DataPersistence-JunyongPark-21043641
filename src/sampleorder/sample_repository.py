from __future__ import annotations

from pathlib import Path

from sampleorder.exceptions import NotFoundError
from sampleorder.json_store import JsonFileStore
from sampleorder.models import Sample

_ENTITY_NAME = "Sample"


class SampleRepository:
    def __init__(self, path: Path | str):
        self._store = JsonFileStore(path)

    def create(self, name: str, avg_production_time: float, yield_rate: float, stock: int = 0) -> Sample:
        records = self._store.load()
        sample_id = self._next_id(records)
        sample = Sample(
            sample_id=sample_id,
            name=name,
            avg_production_time=avg_production_time,
            yield_rate=yield_rate,
            stock=stock,
        )
        records.append(sample.to_dict())
        self._store.save(records)
        return sample

    def get(self, sample_id: str) -> Sample:
        for record in self._store.load():
            if record["sample_id"] == sample_id:
                return Sample.from_dict(record)
        raise NotFoundError(_ENTITY_NAME, sample_id)

    def list_all(self) -> list[Sample]:
        return [Sample.from_dict(r) for r in self._store.load()]

    def search(self, keyword: str) -> list[Sample]:
        keyword_lower = keyword.lower()
        return [s for s in self.list_all() if keyword_lower in s.name.lower()]

    def update(self, sample_id: str, **fields) -> Sample:
        if "stock" in fields and fields["stock"] < 0:
            raise ValueError(f"stock cannot be negative: {fields['stock']}")
        records = self._store.load()
        for record in records:
            if record["sample_id"] == sample_id:
                record.update(fields)
                self._store.save(records)
                return Sample.from_dict(record)
        raise NotFoundError(_ENTITY_NAME, sample_id)

    def delete(self, sample_id: str) -> None:
        records = self._store.load()
        remaining = [r for r in records if r["sample_id"] != sample_id]
        if len(remaining) == len(records):
            raise NotFoundError(_ENTITY_NAME, sample_id)
        self._store.save(remaining)

    @staticmethod
    def _next_id(records: list[dict]) -> str:
        max_num = 0
        for record in records:
            num = int(record["sample_id"].split("-")[1])
            max_num = max(max_num, num)
        return f"S-{max_num + 1:03d}"
