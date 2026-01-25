from dataclasses import dataclass

from legacy_locations.transform.meta import TransformRunMetadata
from legacy_locations.transform.models import LegacyLocation
from legacy_locations.transform.schemas import Schemas


@dataclass
class TransformerParams:
    device: str
    schemas: Schemas
    metadata: TransformRunMetadata
    data: LegacyLocation
