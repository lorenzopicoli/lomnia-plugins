import jsonschema

from firefox.config import THIRD_PARTY_NAME
from firefox.transform.mappers.transformer_params import WebsiteTransformerParams
from firefox.transform.mappers.utils.remove_none_values import remove_none_values


def get_website_id(guid: str | None):
    return "firefox_" + str(guid)


def transform_website(params: WebsiteTransformerParams):
    data = params.place
    transformed = remove_none_values({
        "id": get_website_id(data.guid),
        "source": THIRD_PARTY_NAME,
        "entityType": "website",
        "version": "1",
        "url": data.url,
        "title": data.title,
        "description": data.description,
        "previewImageUrl": data.preview_image_url,
    })

    if params.schemas.website is not None:
        try:
            jsonschema.validate(instance=transformed, schema=params.schemas.website)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise
    params.metadata.record("website", None)
    return transformed
