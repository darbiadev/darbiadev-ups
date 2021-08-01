#!/usr/bin/env python

from datetime import datetime
from enum import Enum, auto

import requests


class _AuthType(Enum):
    """An enum for the authentication types"""
    HEADERS = auto()
    JSON = auto()


class UPSServices:
    """
    A class wrapping UPS' API.
    """

    def __init__(
            self,
            base_url: str,
            username: str,
            password: str,
            access_license_number: str
    ):
        self.base_url: str = base_url
        self.__username: str = username
        self.__password: str = password
        self.__access_license_number: str = access_license_number

    def __auth_headers(self) -> dict[str, ...]:
        """Return authentication headers as dictionary"""
        return {
            'Username': self.__username,
            'Password': self.__password,
            'AccessLicenseNumber': self.__access_license_number,
        }

    def __auth_dict(self) -> dict[str, ...]:
        """Return authentication JSON as dictionary"""
        return {
            'UPSSecurity': {
                'UsernameToken': {
                    'Username': self.__username,
                    'Password': self.__password,
                },
                'ServiceAccessToken': {
                    'AccessLicenseNumber': self.__access_license_number,
                }
            }
        }

    def _make_request(
            self,
            method: str,
            auth_type: _AuthType,
            service: str,
            data: dict[str, ...]
    ) -> dict:
        args = {
            'method': method,
            'url': self.base_url + service,
            'json': data
        }

        if auth_type == _AuthType.HEADERS:
            args['headers'] = self.__auth_headers()
        elif auth_type == _AuthType.JSON:
            args['json'] = args['json'] | self.__auth_dict()
        else:
            raise ValueError(f'Invalid auth_type {auth_type}')

        response = requests.request(**args)
        response.raise_for_status()
        return response.json()

    def track(
            self,
            tracking_number: str
    ) -> dict:
        """Get tracking details for a tracking number"""
        service: str = 'rest/Track'

        data = {
            'TrackRequest': {
                'Request': {
                    'RequestOption': '1',
                    'TransactionReference': {
                        'CustomerContext': tracking_number + ' ' + str(datetime.now().isoformat())
                    }
                },
                'InquiryNumber': tracking_number
            }
        }

        return self._make_request(method='post', auth_type=_AuthType.JSON, service=service, data=data)

    def check_address(
            self,
            street_lines: list[str],
            city: str,
            state: str,
            postal_code: str,
            country: str
    ):
        """Validate an address"""
        service: str = 'addressvalidation/v1/3'

        data = {
            'XAVRequest': {
                'AddressKeyFormat': {
                    'AddressLine': street_lines,
                    'PoliticalDivision2': city,
                    'PoliticalDivision1': state,
                    'PostcodePrimaryLow': postal_code,
                    'CountryCode': country
                }
            }
        }

        return self._make_request(method='post', auth_type=_AuthType.HEADERS, service=service, data=data)

    def time_in_transit(
            self,
            from_state: str,
            from_postal_code: str,
            from_country: str,
            to_state: str,
            to_postal_code: str,
            to_country: str,
            weight: str,
            pickup_date: str = None
    ) -> dict:
        """Estimate transit time"""
        service: str = 'rest/TimeInTransit'

        if pickup_date is None:
            pickup_date = datetime.today().strftime('%Y%m%d')

        data = {
            "TimeInTransitRequest": {
                "Request": {
                    "RequestOption": "TNT",
                    "TransactionReference": {
                        "CustomerContext": to_postal_code + ' ' + str(datetime.now().isoformat()),
                        "TransactionIdentifier": ""
                    }
                },
                "ShipFrom": {
                    "Address": {
                        "StateProvinceCode": from_state,
                        "PostalCode": from_postal_code,
                        "CountryCode": from_country
                    }
                },
                "ShipTo": {
                    "Address": {
                        "StateProvinceCode": to_state,
                        "PostalCode": to_postal_code,
                        "CountryCode": to_country
                    }
                },
                "Pickup": {
                    "Date": pickup_date
                },
                "ShipmentWeight": {
                    "UnitOfMeasurement": {
                        "Code": "LBS",
                        "Description": "Pounds"
                    },
                    "Weight": weight
                }
            }
        }

        return self._make_request(method='post', auth_type=_AuthType.JSON, service=service, data=data)