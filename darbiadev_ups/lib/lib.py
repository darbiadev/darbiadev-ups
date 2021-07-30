#!/usr/bin/env python

from datetime import datetime

import requests


class UPSServices:
    """A class wrapping UPS' API.

    This class wraps UPS' API.
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

    def _make_request(
            self,
            method: str,
            service: str,
            data: dict[str, ...],

    ) -> dict:
        args = {
            'method': method,
            'url': self.base_url + service,
            'json': data
        }

        response = requests.request(**args)
        response.raise_for_status()
        return response.json()

    def track(
            self,
            tracking_number: str
    ) -> dict:
        if not isinstance(tracking_number, str):
            raise ValueError('tracking_number must be a string')

        service: str = 'Track'

        data = {
            'UPSSecurity': {
                'UsernameToken': {
                    'Username': self.__username,
                    'Password': self.__password,
                },
                'ServiceAccessToken': {
                    'AccessLicenseNumber': self.__access_license_number,
                }
            }, 'TrackRequest': {
                'Request': {
                    'RequestOption': '1',
                    'TransactionReference': {
                        'CustomerContext': tracking_number + ' ' + str(datetime.now().isoformat())
                    }
                },
                'InquiryNumber': tracking_number
            }
        }

        response = self._make_request(method='post', service=service, data=data)

        return response
