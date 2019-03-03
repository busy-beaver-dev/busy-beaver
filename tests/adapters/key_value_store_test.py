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