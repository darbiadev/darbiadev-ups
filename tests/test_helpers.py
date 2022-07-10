"""Testing the helpers"""

from darbiadev_ups import helpers


def test_nested_dict_parser():
    """Tested expected return values from nested dict parser"""
    dct = {"key1": {"key2": "value"}}
    assert helpers.get_nested_dict_value(dct, "key1") == {"key2": "value"}
    assert helpers.get_nested_dict_value(dct, "key1.key2") == "value"
    assert helpers.get_nested_dict_value(dct, "key3") is None
