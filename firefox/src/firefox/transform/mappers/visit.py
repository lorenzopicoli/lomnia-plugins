import jsonschema

from firefox.transform.mappers.transformer_params import WebsiteVisitTransformerParams
from firefox.transform.mappers.utils.microseconds_to_datetime import microseconds_to_datetime


def transform_website_visit(params: WebsiteVisitTransformerParams):
    data = params.place
    visit_date = microseconds_to_datetime(data.visit_date)
    transformed = {
        "id": "firefox_" + str(data.place_guid) + str(data.visit_date),
        "entityType": "websiteVisit",
        "version": "1",
    }

    if params.schemas.website is not None:
        try:
            jsonschema.validate(instance=transformed, schema=params.schemas.website_visit)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise
    params.metadata.record("website_visit", visit_date)
    return transformed
