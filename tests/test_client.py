"""Testing the client"""

import pytest

from darbiadev_ups import UPSServices


def test_invalid_auth_type_error():
    """An invalid auth type should cause a ValueError"""
    with pytest.raises(ValueError):
        client = UPSServices(
            base_url="test",
            username="test",
            password="test",
            access_license_number="test",
        )
        client.make_request(
            method="test",
            auth_type="test",
            service="test",
            data={},
        )
