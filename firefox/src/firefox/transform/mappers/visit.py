import jsonschema

from firefox.config import THIRD_PARTY_NAME, VISIT_DATE_DEDUPE_BUCKET
from firefox.transform.mappers.transformer_params import WebsiteVisitTransformerParams
from firefox.transform.mappers.utils.iso_utc import iso_utc
from firefox.transform.mappers.utils.microseconds_to_datetime import microseconds_to_datetime
from firefox.transform.mappers.utils.remove_none_values import remove_none_values
from firefox.transform.mappers.visit_type import transform_visit_type
from firefox.transform.mappers.website import get_website_id


def get_visit_id(place_guid: str | None, visit_date: int, visit_type: int | None):
    # Visits synced across devices don't have the exact same visit date, but checking for visits to the same
    # page, with the same type within 0.002 seconds of each other feels like a safe way to consider them the same
    return f"firefox_{place_guid!s}_{(visit_date // VISIT_DATE_DEDUPE_BUCKET)!s}_{visit_type}"


def transform_website_visit(params: WebsiteVisitTransformerParams):
    data = params.place
    visit_date = microseconds_to_datetime(data.visit_date)
    transformed = remove_none_values({
        "id": get_visit_id(data.place_guid, data.visit_date, data.visit_type),
        "source": THIRD_PARTY_NAME,
        "entityType": "websiteVisit",
        "version": "1",
        "websiteId": get_website_id(data.place_guid),
        "fileDownloaded": data.downloaded_file,
        "recordedAt": iso_utc(visit_date),
    })

    if data.from_visit_place_guid and data.from_visit_visit_date and data.from_visit_visit_type:
        transformed["fromVisitId"] = get_visit_id(
            data.from_visit_place_guid, data.from_visit_visit_date, data.from_visit_visit_type
        )
    if data.visit_type is not None:
        transformed["type"] = transform_visit_type(data.visit_type)

    if params.schemas.website is not None:
        try:
            jsonschema.validate(instance=transformed, schema=params.schemas.website_visit)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise
    params.metadata.record("website_visit", visit_date)
    return transformed
