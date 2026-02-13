"""Integration test configuration for API tests."""

import sys
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from api.dependencies.database import get_supabase
from api.main import app


def _make_mock_supabase(tables: dict | None = None) -> MagicMock:
    """Create a mock Supabase client backed by in-memory data.

    Args:
        tables: Optional dict of table_name -> list[dict] for pre-seeded data.

    Returns:
        MagicMock that mimics supabase.Client.table(...) chains.
    """
    if tables is None:
        tables = {}

    mock_client = MagicMock()

    def _table(name: str):
        if name not in tables:
            tables[name] = []
        rows = tables[name]

        table_mock = MagicMock()

        # --- INSERT ---
        def _insert(data):
            insert_mock = MagicMock()

            def _execute():
                from datetime import datetime, timezone

                row = deepcopy(data)
                if "created_at" not in row or row["created_at"] is None:
                    row["created_at"] = datetime.now(timezone.utc).isoformat()
                rows.append(row)
                result = MagicMock()
                result.data = [row]
                return result

            insert_mock.execute = _execute
            return insert_mock

        table_mock.insert = _insert

        # --- SELECT ---
        def _select(columns="*"):
            class QueryBuilder:
                def __init__(self):
                    self._filters = []
                    self._gte_filters = []
                    self._lte_filters = []
                    self._orders = []
                    self._range_start = None
                    self._range_end = None

                def eq(self, col, val):
                    self._filters.append((col, val))
                    return self

                def gte(self, col, val):
                    self._gte_filters.append((col, val))
                    return self

                def lte(self, col, val):
                    self._lte_filters.append((col, val))
                    return self

                def is_(self, col, val):
                    self._filters.append((col, val))
                    return self

                def order(self, col, desc=False):
                    self._orders.append((col, desc))
                    return self

                def range(self, start, end):
                    self._range_start = start
                    self._range_end = end
                    return self

                def execute(self):
                    filtered = list(rows)
                    for col, val in self._filters:
                        filtered = [r for r in filtered if str(r.get(col)) == str(val)]
                    for col, val in self._gte_filters:
                        filtered = [
                            r for r in filtered if str(r.get(col, "")) >= str(val)
                        ]
                    for col, val in self._lte_filters:
                        filtered = [
                            r for r in filtered if str(r.get(col, "")) <= str(val)
                        ]
                    for col, desc in reversed(self._orders):
                        filtered.sort(
                            key=lambda r, _col=col: r.get(_col, ""),
                            reverse=desc,
                        )
                    if self._range_start is not None:
                        filtered = filtered[self._range_start : self._range_end + 1]
                    result = MagicMock()
                    result.data = filtered
                    return result

            return QueryBuilder()

        table_mock.select = _select

        # --- DELETE ---
        def _delete():
            class DeleteBuilder:
                def __init__(self):
                    self._filters = []

                def eq(self, col, val):
                    self._filters.append((col, val))
                    return self

                def execute(self):
                    deleted = []
                    remaining = []
                    for r in rows:
                        match = all(str(r.get(c)) == str(v) for c, v in self._filters)
                        if match:
                            deleted.append(r)
                        else:
                            remaining.append(r)
                    rows.clear()
                    rows.extend(remaining)
                    result = MagicMock()
                    result.data = deleted
                    return result

            return DeleteBuilder()

        table_mock.delete = _delete

        # --- UPDATE ---
        def _update(data):
            class UpdateBuilder:
                def __init__(self):
                    self._data = data
                    self._filters = []

                def eq(self, col, val):
                    self._filters.append((col, val))
                    return self

                def execute(self):
                    from datetime import datetime, timezone

                    updated = []
                    for r in rows:
                        match = all(str(r.get(c)) == str(v) for c, v in self._filters)
                        if match:
                            # Update the row with new data
                            r.update(self._data)
                            if "updated_at" in self._data:
                                r["updated_at"] = self._data["updated_at"]
                            updated.append(deepcopy(r))
                    result = MagicMock()
                    result.data = updated
                    return result

            return UpdateBuilder()

        table_mock.update = _update

        return table_mock

    mock_client.table = _table
    return mock_client


@pytest.fixture
def mock_supabase():
    """Provide a mock Supabase client with empty tables."""
    return _make_mock_supabase()


@pytest.fixture
def override_supabase(mock_supabase):
    """Override get_supabase dependency with mock client."""
    app.dependency_overrides[get_supabase] = lambda: mock_supabase
    yield mock_supabase
    app.dependency_overrides.clear()
