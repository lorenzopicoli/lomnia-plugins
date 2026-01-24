import jsonschema

from owntracks_recorder.transform.mappers.transformer_params import TransformerParams
from owntracks_recorder.transform.mappers.utils.remove_none_values import remove_none_values


def transform_device(params: TransformerParams):
    transformed_device = remove_none_values({
        "id": params.device,
        "entityType": "device",
        "source": "owntracks",
        "version": "1",
    })
    try:
        jsonschema.validate(instance=transformed_device, schema=params.schemas.device)
    except jsonschema.ValidationError as e:
        print(f"Device transformation validation error: {e.message}")
        raise
    params.metadata.record_device()
    return transformed_device
