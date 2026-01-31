from dataclasses import dataclass

from firefox.transform.meta import TransformRunMetadata
from firefox.transform.models import MozHistoryVisit, MozPlace
from firefox.transform.schemas import Schemas


@dataclass
class WebsiteTransformerParams:
    schemas: Schemas
    metadata: TransformRunMetadata
    place: MozPlace


@dataclass
class WebsiteVisitTransformerParams:
    schemas: Schemas
    metadata: TransformRunMetadata
    place: MozHistoryVisit
