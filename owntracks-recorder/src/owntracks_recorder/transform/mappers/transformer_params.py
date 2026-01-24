from dataclasses import dataclass

from owntracks_recorder.transform.api import OwntracksLocation
from owntracks_recorder.transform.meta import TransformRunMetadata
from owntracks_recorder.transform.schemas import Schemas


@dataclass
class TransformerParams:
    device: str
    schemas: Schemas
    metadata: TransformRunMetadata
    data: OwntracksLocation
