from BaseClasses import Tutorial
from worlds.AutoWorld import World, WebWorld
from .Items import item_table, create_itempool, create_item
from .Locations import location_table, get_location_names
from .Regions import create_regions
from .Rules import set_rules
from .Options import BoboOptions, create_option_groups, get_goal_name
from .CompetitionUnlocks import get_competition_unlock_order, get_saga_unlock_order, get_goal_saga, SAGA_RACES


class BoboWeb(WebWorld):
    theme = "partyTime"
    option_groups = create_option_groups()


class BoboWorld(World):
    """
    Bobo Bay is a cute Bobo-raising simulator!
    Raise, train, and compete with your Bobos across various tournaments.
    """

    game = "Bobo Bay"
    options_dataclass = BoboOptions
    options: BoboOptions

    item_name_to_id = {name: data.ap_code for name, data in item_table.items() if data.ap_code is not None}
    location_name_to_id = get_location_names()

    web = BoboWeb()

    def create_regions(self) -> None:
        create_regions(self)

    def set_rules(self) -> None:
        set_rules(self)

    def create_items(self) -> None:
        self.multiworld.itempool += create_itempool(self)

    def create_item(self, name: str):
        return create_item(self, name)

    def fill_slot_data(self) -> dict:
        return {
            "goal_asset_name":                          get_goal_name(self),
            "goal_saga_name":                           get_goal_saga(self) or "",
            "bobo_tickets_req":                         self.options.BoboTicketsRequired.value,
            "competition_unlock_thresholds":            get_competition_unlock_order(self),
            "snack_multiplier": getattr(self.options, "SnackMultiplier", 1).value
            if hasattr(self.options, "SnackMultiplier") else 1,
            "saga_unlock_thresholds":                   get_saga_unlock_order(self),
            "unlimited_snacks":                         bool(getattr(self.options, "UnlimitedSnacks", False)),
        }