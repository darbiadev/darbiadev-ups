"""Helper functions"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def get_nested_dict_value(dct: dict, keypath: str, default=None, separator: str = ".") -> Any:
    """Parse nested values from dictionaries"""
    keys = keypath.split(separator)

    value = dct
    for key in keys:
        value = value.get(key)

        if not value:
            value = default
            break

    return value


def parse_tracking_response(response: dict, include_original: bool = False) -> dict:
    """Parse tracking data"""
    output = {}

    error: str | None = get_nested_dict_value(response, "Fault.detail.Errors.ErrorDetail.PrimaryErrorCode")
    if error is not None:
        output = {"external_error": error}

    package_data: dict | list[dict] = get_nested_dict_value(response, "TrackResponse.Shipment.Package")
    if package_data is not None:
        data = {}

        shipment_references = set()
        shipment_reference_data: list = get_nested_dict_value(response, "TrackResponse.Shipment.ReferenceNumber")
        if isinstance(shipment_reference_data, dict):
            shipment_reference_data = [shipment_reference_data]
        for shipment_reference in shipment_reference_data:
            shipment_references.add(shipment_reference["Value"])
        data["shipment_references"] = list(shipment_references)

        packages = {}
        if isinstance(package_data, dict):
            package_data = [package_data]
        for package in package_data:
            package_tracking_number = package.get("TrackingNumber")

            package_references = set()
            package_references_data = package.get("ReferenceNumber")
            if isinstance(package_references_data, dict):
                package_references_data = [package_references_data]
            for package_reference in package_references_data:
                package_references.add(package_reference["Value"])

            most_recent_activity = package.get("Activity")[0]
            most_recent_activity_status = most_recent_activity["Status"]["Description"]

            packages[package_tracking_number] = {
                "status": most_recent_activity_status,
                "references": list(package_references),
            }
        data["packages"] = packages

        output = data

    if len(output.keys()) == 0:
        output = {"error": "failed to parse response"}

    if include_original:
        output = {"_original": response} | output

    return output


def parse_address_validation_response(response: dict, include_original: bool = False) -> dict:
    """Parse address validation data"""

    output = {
        "status": None,
        "classification": "",
        "street_address": "",
        "region": "",
    }

    errors: list[str] | None = get_nested_dict_value(response, "response.errors")
    if errors is not None:
        output["status"] = "\n".join(errors)

    # Remove the top level wrapper
    try:
        response = response["XAVResponse"]
    except KeyError:
        pass

    no_candidates_indicator: str | None = get_nested_dict_value(response, "NoCandidatesIndicator")
    valid_address_indicator: str | None = get_nested_dict_value(response, "ValidAddressIndicator")

    if no_candidates_indicator is not None:
        output["status"] = "Address unknown, No candidates"

    address_classification: str | None = get_nested_dict_value(response, "AddressClassification.Description")
    if address_classification == "Unknown":
        output["status"] = "Address unknown, No candidates"

    if output["status"] is None:
        candidates = list(response["Candidate"])
        first_candidate = candidates[0]

        output["classification"] = get_nested_dict_value(
            first_candidate, "AddressClassification.Description", "Unknown"
        )

        street_address = get_nested_dict_value(first_candidate, "AddressKeyFormat.AddressLine")
        output["street_address"] = " ".join(list(street_address))

        output["region"] = get_nested_dict_value(first_candidate, "AddressKeyFormat.Region")

        if valid_address_indicator is not None:
            output["status"] = "Valid"

    if include_original:
        output = {"_original": response} | output

    return output


def parse_time_in_transit_response(response: dict, include_original: bool = False) -> dict:
    """Parse time in transit data"""
    alert: str = get_nested_dict_value(response, "TimeInTransitResponse.Response.Alert.Description")

    output = {
        "alert": alert,
        "services": [],
    }

    service_data = get_nested_dict_value(response, "TimeInTransitResponse.TransitResponse.ServiceSummary", [])
    for service in service_data:
        service_name = get_nested_dict_value(service, "Service.Description")

        pickup_date = get_nested_dict_value(service, "EstimatedArrival.Pickup.Date")
        pickup_time = get_nested_dict_value(service, "EstimatedArrival.Pickup.Time")
        pickup_datetime = datetime.strptime(pickup_date + pickup_time, "%Y%m%d%H%M%S")

        arrival_date = get_nested_dict_value(service, "EstimatedArrival.Arrival.Date")
        arrival_time = get_nested_dict_value(service, "EstimatedArrival.Arrival.Time")
        arrival_datetime = datetime.strptime(arrival_date + arrival_time, "%Y%m%d%H%M%S")

        business_days_in_transit = get_nested_dict_value(service, "EstimatedArrival.BusinessDaysInTransit")
        day_of_week = get_nested_dict_value(service, "EstimatedArrival.DayOfWeek")
        customer_center_cutoff = datetime.strptime(
            get_nested_dict_value(service, "EstimatedArrival.CustomerCenterCutoff"), "%H%M%S"
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
