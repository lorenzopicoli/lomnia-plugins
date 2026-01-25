import jsonschema

from legacy_locations.transform.mappers.transformer_params import TransformerParams


def transform_device(params: TransformerParams):
    transformed_device = {"id": params.device, "entityType": "device", "source": "legacy_locations", "version": "1"}
    if params.schemas.device is not None:
        try:
            jsonschema.validate(instance=transformed_device, schema=params.schemas.device)
        except jsonschema.ValidationError as e:
            print(f"Valid data validation error: {e.message}")
            raise
    params.metadata.record_device()
    return transformed_device
