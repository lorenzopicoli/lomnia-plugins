import jsonschema

from firefox.transform.mappers.transformer_params import WebsiteTransformerParams


def transform_website(params: WebsiteTransformerParams):
    data = params.place
    transformed = {
        "id": "firefox_" + str(data.guid),
        "entityType": "website",
        "version": "1",
    }

    if params.schemas.website is not None:
        try:
            jsonschema.validate(instance=transformed, schema=params.schemas.website)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise
    params.metadata.record("website", None)
    return transformed
