import pytest
from busy_beaver.models import KeyValueStore


def test_put_get(kv_store):
    expected_value = "value"

    kv_store.put("key", expected_value)
    returned_value = kv_store.get("key")

    assert returned_value == expected_value


def test_put_get_int(kv_store):
    expected_value = 100

    kv_store.put_int("key", expected_value)
    returned_value = kv_store.get_int("key")

    assert returned_value == expected_value


def test_put_overwrite(kv_store):
    expected_value = 150
    kv_store.put_int("key", 100)
    kv_store.put_int("key", expected_value)

    returned_value = kv_store.get_int("key")

    assert returned_value == expected_value
    all_records = KeyValueStore.query.filter_by(key="key").all()
    assert len(all_records) == 1


def test_get_key_does_not_exist_raise_ValueError(kv_store):
    with pytest.raises(ValueError):
        kv_store.get("key_does_not_exist")
