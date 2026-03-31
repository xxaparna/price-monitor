from backend.ingestion.grailed import GrailedCollector
from backend.ingestion.fashionphile import FashionphileCollector
from backend.ingestion.firstdibs import FirstDibsCollector

ALL_COLLECTORS = [
    GrailedCollector,
    FashionphileCollector,
    FirstDibsCollector,
]
