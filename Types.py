from typing import NamedTuple, Optional
from enum import IntEnum
from BaseClasses import Item, Location, ItemClassification


class BoboLocation(Location):
    game: str = "Bobo Bay"


class BoboBayItem(Item):
    game: str = "Bobo Bay"


class ItemData(NamedTuple):
    ap_code: Optional[int]
    classification: ItemClassification
    quantity: int = 1


class LocData(NamedTuple):
    ap_code: Optional[int]
    region: str
    asset_name: str = ""
    rank: str = ""


# Placeholders used by the skeleton template
class ChapterType(IntEnum):
    COMPETITIONS = 1


chapter_type_to_name = {
    ChapterType.COMPETITIONS: "Competitions",
}