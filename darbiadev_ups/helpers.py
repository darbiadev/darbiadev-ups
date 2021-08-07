#!/usr/bin/env python

import datetime
from typing import Any, Union

from benedict import benedict

tracking_url = 'https://wwwapps.ups.com/WebTracking/processInputRequest?TypeOfInquiryNumber=T&InquiryNumber1={tracking_number}'


def parse_tracking_response(response: dict) -> dict:
    """Parse tracking data"""
    data: benedict = benedict(response)

    if result := data.get('TrackResponse.Shipment.Package'):
        return_value = {
            '_original': response,
            'shipment_references': set(dct['Value'] for dct in (data.get('TrackResponse.Shipment.ReferenceNumber') or [])),
            'packages': dict()
        }

        if not isinstance(result, list):
            result = [result]
        packages: list[dict] = [benedict(r) for r in result]

        for package in packages:
            return_value['packages'][package.get('TrackingNumber')] = {
                'status': package.get('Activity[0].Status.Description'),
                'references': [dct['Value'] for dct in (package.get('ReferenceNumber') or [])]
            }

        return_value['shipment_references'] = list(return_value['shipment_references'])
        return return_value
    elif error := data.get('Fault.detail.Errors.ErrorDetail.PrimaryErrorCode'):
        return {'external_error': error}
    else:
        return {'error': 'unknown response', 'full_response': data}


# TODO: Support multiple candidates
def parse_address_validation_response(response: dict) -> dict[str, Union[Union[None, str, list], Any]]:
    """Parse address validation data"""
    data: benedict = benedict(response)

    result = {
        '_original': response,
        'status': None,
        'classification': '',
        'street_address': '',
        'region': ''
    }

    try:
        if 'response.errors' in data:
            result['street_address'] = 'ERROR(S) VALIDATING ADDRESS'
            result['region'] = [error.get('message') for error in data['response.errors']]
            return result

        if 'XAVResponse.NoCandidatesIndicator' in data:
            result['street_address'] = 'Address unknown'
            result['region'] = 'No candidates'
            return result

        if data.get('XAVResponse.AddressClassification.Description', '') == 'Unknown':
            result['street_address'] = 'Address unknown'
            result['region'] = 'No candidates'
            return result

        result['classification'] = data.get('XAVResponse.Candidate.AddressClassification.Description', 'Unknown')

        candidates = data['XAVResponse.Candidate']
        if not isinstance(candidates, list):
            candidates = [candidates]
        first_candidate = benedict(candidates[0])

        result['classification'] = first_candidate.get('AddressClassification.Description', 'Unknown')

        street_address = first_candidate['AddressKeyFormat.AddressLine']
        if isinstance(street_address, list):
            result['street_address'] = ' '.join(street_address)
        else:
            result['street_address'] = street_address

        result['region'] = first_candidate['AddressKeyFormat.Region']
        if 'ValidAddressIndicator' in data['XAVResponse']:
            result['status'] = 'Valid'
        return result

    except KeyError:
        result['street_address'] = 'SYSTEM ERROR'
        result['region'] = 'Failed to validate address'
        return result


def parse_time_in_transit_response(response: dict) -> dict[str, Union[str, list[dict[str, str]]]]:
    """Parse time in transit data"""
    data: benedict = benedict(response)
    alert: str = data.get('TimeInTransitResponse.Response.Alert.Description')
    result = {'_original': response, 'alert': alert, 'services': []}

    try:
        services = data.get('TimeInTransitResponse.TransitResponse.ServiceSummary')
    except KeyError:
        return result

    for service in services:
        service = benedict(service)

        service_name = service.get('Service.Description')

        pickup_date = service.get('EstimatedArrival.Pickup.Date')
        pickup_time = service.get('EstimatedArrival.Pickup.Time')
        pickup_datetime = datetime.datetime.strptime(pickup_date + pickup_time, '%Y%m%d%H%M%S')

        arrival_date = service.get('EstimatedArrival.Arrival.Date')
        arrival_time = service.get('EstimatedArrival.Arrival.Time')
        arrival_datetime = datetime.datetime.strptime(arrival_date + arrival_time, '%Y%m%d%H%M%S')

        business_days_in_transit = service.get('EstimatedArrival.BusinessDaysInTransit')
        day_of_week = service.get('EstimatedArrival.DayOfWeek')
        customer_center_cutoff = datetime.datetime.strptime(
            service.get('EstimatedArrival.CustomerCenterCutoff'),
            '%H%M%S'
        ).time()

        result['services'].append({
            'service_name': service_name,
            'pickup_time': str(pickup_datetime),
            'arrival_time': str(arrival_datetime),
            'business_days_in_transit': business_days_in_transit,
            'day_of_week': day_of_week,
            'customer_center_cutoff': str(customer_center_cutoff)
        })

    return result
