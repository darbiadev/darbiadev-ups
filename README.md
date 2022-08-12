# darbiadev-ups
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fdarbiadev%2Fdarbiadev-ups.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fdarbiadev%2Fdarbiadev-ups?ref=badge_shield)


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


[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fdarbiadev%2Fdarbiadev-ups.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fdarbiadev%2Fdarbiadev-ups?ref=badge_large)
