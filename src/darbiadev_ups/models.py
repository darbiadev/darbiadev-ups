from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import Self


def _parse_references(reference_datas: list[dict]) -> list[str]:
    references = set(reference_data.get("Value") for reference_data in reference_datas)
    return list(reference for reference in references if reference is not None)


def _force_list_dicts(data: dict | list[dict] | None) -> list[dict]:
    if data is None:
        data = {}
    if isinstance(data, dict):
        data = [data]
    return data


@dataclass
class Address:
    city: str
    state_province_code: str
    postal_code: str
    country_code: str

    @staticmethod
    def from_dict(data: dict) -> Self:
        city_ = data.get("City")
        state_province_code_ = data.get("StateProvinceCode")
        postal_code_ = data.get("PostalCode")
        country_code_ = data.get("CountryCode")
        return Address(city_, state_province_code_, postal_code_, country_code_)


@dataclass
class ActivityLocation:
    address: Address
    code: str
    description: str
    signed_for_by_name: str

    @staticmethod
    def from_dict(data: dict) -> Self:
        address_ = Address.from_dict(data.get("Address"))
        code_ = data.get("Code")
        description_ = data.get("Description")
        signed_for_by_name_ = data.get("SignedForByName")
        return ActivityLocation(address_, code_, description_, signed_for_by_name_)


@dataclass
class Status:
    type: str
    description: str
    code: str

    @staticmethod
    def from_dict(data: dict) -> Self:
        type_ = data.get("Type")
        description_ = data.get("Description")
        code_ = data.get("Code")
        return Status(type_, description_, code_)


@dataclass
class Activity:
    location: ActivityLocation
    status: Status
    date: str
    time: str

    @staticmethod
    def from_dict(data: dict) -> Self:
        location_ = ActivityLocation.from_dict(data.get("ActivityLocation"))
        status_ = Status.from_dict(data.get("Status"))
        date_ = data.get("Date")
        time_ = data.get("Time")
        return Activity(location_, status_, date_, time_)


@dataclass
class UnitOfMeasurement:
    code: str

    @staticmethod
    def from_dict(data: dict) -> Self:
        code_ = data.get("Code")
        return UnitOfMeasurement(code_)


@dataclass
class PackageWeight:
    unit_of_measurement: UnitOfMeasurement
    weight: str

    @staticmethod
    def from_dict(data: dict) -> Self:
        unit_of_measurement_ = UnitOfMeasurement.from_dict(data.get("UnitOfMeasurement"))
        weight_ = data.get("Weight")
        return PackageWeight(unit_of_measurement_, weight_)


@dataclass
class Package:
    tracking_number: str
    activity: list[Activity]
    package_weight: PackageWeight
    reference_numbers: list[str]

    @staticmethod
    def from_dict(data: dict) -> Self:
        tracking_number_ = data.get("TrackingNumber")
        activity_ = [Activity.from_dict(activity_data) for activity_data in _force_list_dicts(data.get("Activity"))]
        package_weight_ = PackageWeight.from_dict(data.get("PackageWeight"))
        reference_numbers_ = _parse_references(_force_list_dicts(data.get("ReferenceNumber")))
        return Package(tracking_number_, activity_, package_weight_, reference_numbers_)


@dataclass
class Service:
    code: str
    description: str

    @staticmethod
    def from_dict(data: dict) -> Self:
        code_ = data.get("Code")
        description_ = data.get("Description")
        return Service(code_, description_)


@dataclass
class ShipmentWeight:
    unit_of_measurement: UnitOfMeasurement
    weight: str

    @staticmethod
    def from_dict(data: dict) -> Self:
        unit_of_measurement_ = UnitOfMeasurement.from_dict(data.get("UnitOfMeasurement"))
        weight_ = data.get("Weight")
        return ShipmentWeight(unit_of_measurement_, weight_)


@dataclass
class ShipmentType:
    code: str
    description: str

    @staticmethod
    def from_dict(data: dict) -> Self:
        code_ = data.get("Code")
        description_ = data.get("Description")
        return ShipmentType(code_, description_)


@dataclass
class Shipment:
    shipment_type: ShipmentType | None
    shipper_number: str
    shipment_weight: ShipmentWeight
    service: Service
    reference_numbers: list[str]
    pickup_date: str
    package: list[Package]

    @staticmethod
    def from_dict(data: dict) -> Self:
        if shipment_type_data := data.get("ShipmentType") is not None:
            shipment_type_ = ShipmentType.from_dict(shipment_type_data)
        else:
            shipment_type_ = None
        shipper_number_ = data.get("ShipperNumber")
        shipment_weight_ = ShipmentWeight.from_dict(data.get("ShipmentWeight"))
        service_ = Service.from_dict(data.get("Service"))
        reference_numbers_ = _parse_references(_force_list_dicts(data.get("ReferenceNumber")))
        pickup_date_ = data.get("PickupDate")
        package_ = [Package.from_dict(package_data) for package_data in _force_list_dicts(data.get("Package"))]
        return Shipment(
            shipment_type_,
            shipper_number_,
            shipment_weight_,
            service_,
            reference_numbers_,
            pickup_date_,
            package_,
        )
