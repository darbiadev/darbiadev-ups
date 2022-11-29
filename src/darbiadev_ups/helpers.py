"""Helper functions"""

from __future__ import annotations

from datetime import datetime

from darbia.utils.mappings import get_nested_dict_value

from darbiadev_ups.models import Shipment


def _parse_datetime(date: str, time: str) -> datetime:
    return datetime.strptime(date + time, "%Y%m%d%H%M%S")


def _get_value(data: dict, keypath: str, default: str | None = None) -> str | list[dict] | None:
    value: str | dict | list[dict] | None = get_nested_dict_value(data, keypath, default)
    if isinstance(value, dict):
        value = [value]
    return value


def parse_tracking_response(response: dict) -> Shipment:
    """Parse tracking data"""
    # print(response)
    return Shipment.from_dict(response["TrackResponse"]["Shipment"])


def parse_address_validation_response(response: dict, include_original: bool = False) -> dict:
    """Parse address validation data"""

    output = {
        "status": None,
        "classification": "",
        "street_address": "",
        "region": "",
    }

    errors: list[str] | None = _get_value(response, "response.errors")
    if errors is not None:
        output["status"] = "\n".join(errors)

    # Remove the top level wrapper
    try:
        response = response["XAVResponse"]
    except KeyError:
        pass

    no_candidates_indicator: str | None = _get_value(response, "NoCandidatesIndicator")
    valid_address_indicator: str | None = _get_value(response, "ValidAddressIndicator")

    if no_candidates_indicator is not None:
        output["status"] = "Address unknown, No candidates"

    address_classification: str | None = _get_value(response, "AddressClassification.Description")
    if address_classification == "Unknown":
        output["status"] = "Address unknown, No candidates"

    if output["status"] is None:
        candidates = list(response["Candidate"])
        first_candidate = candidates[0]

        output["classification"] = _get_value(first_candidate, "AddressClassification.Description", "Unknown")

        street_address = _get_value(first_candidate, "AddressKeyFormat.AddressLine")
        output["street_address"] = " ".join(list(street_address))

        output["region"] = _get_value(first_candidate, "AddressKeyFormat.Region")

        if valid_address_indicator is not None:
            output["status"] = "Valid"

    if include_original:
        output = {"_original": response} | output

    return output


def parse_time_in_transit_response(response: dict, include_original: bool = False) -> dict:
    """Parse time in transit data"""
    alert: str = _get_value(response, "TimeInTransitResponse.Response.Alert.Description")

    output = {
        "alert": alert,
        "services": [],
    }

    service_data = _get_value(response, "TimeInTransitResponse.TransitResponse.ServiceSummary", [])
    for service in service_data:
        service_name = _get_value(service, "Service.Description")

        pickup_date = _get_value(service, "EstimatedArrival.Pickup.Date")
        pickup_time = _get_value(service, "EstimatedArrival.Pickup.Time")
        pickup_datetime = datetime.strptime(pickup_date + pickup_time, "%Y%m%d%H%M%S")

        arrival_date = _get_value(service, "EstimatedArrival.Arrival.Date")
        arrival_time = _get_value(service, "EstimatedArrival.Arrival.Time")
        arrival_datetime = datetime.strptime(arrival_date + arrival_time, "%Y%m%d%H%M%S")

        business_days_in_transit = _get_value(service, "EstimatedArrival.BusinessDaysInTransit")
        day_of_week = _get_value(service, "EstimatedArrival.DayOfWeek")
        customer_center_cutoff = datetime.strptime(
            _get_value(service, "EstimatedArrival.CustomerCenterCutoff"), "%H%M%S"
        ).time()

        output["services"].append(
            {
                "service_name": service_name,
                "pickup_time": str(pickup_datetime),
                "arrival_time": str(arrival_datetime),
                "business_days_in_transit": business_days_in_transit,
                "day_of_week": day_of_week,
                "customer_center_cutoff": str(customer_center_cutoff),
            }
        )

    if include_original:
        output = {"_original": response} | output

    return output
