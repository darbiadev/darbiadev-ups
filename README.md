# darbiadev-ups

This package provides a wrapper for UPS' API.

### Example usage

```python
from darbiadev_ups import UPSServices

client = UPSServices(
    base_url="https://onlinetools.ups.com/",
    username="username",
    password="password",
    access_license_number="access_license_number",
)

print(client.track("1Z12345E1305277940"))
```
