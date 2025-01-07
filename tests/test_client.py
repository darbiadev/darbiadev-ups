"""Testing the client."""

import pytest

from darbiadev_ups import UPSServices


def test_invalid_auth_type_error() -> None:
    """An invalid auth type should cause a ValueError."""
    client = UPSServices(
        base_url="test",
        username="test",
        password="test",  # noqa: S106 -- placeholder value
        access_license_number="test",
    )
    with pytest.raises(ValueError, match="Invalid auth_type"):
        client.make_request(
            method="test",
            auth_type="test",
            service="test",
            data={},
        )
