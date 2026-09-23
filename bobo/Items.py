import logging

from BaseClasses import Item, ItemClassification

from .Types import ItemData, ChapterType, BoboBayItem, chapter_type_to_name
from .Locations import get_total_locations
from typing import List, Dict, TYPE_CHECKING
from .CompetitionUnlocks import get_competition_unlock_order
from .CompetitionUnlocks import get_saga_unlock_order
from .Options import get_goal_name

if TYPE_CHECKING:
    from . import BoboWorld

def create_itempool(world: "BoboWorld") -> List[Item]:
    itempool: List[Item] = []

    goal_asset = get_goal_name(world)
    goal_event_name = "Beat Big Jam" if goal_asset == "BigJam_Race_D" else "Beat Power Gary"

    for name, data in bobo_items.items():
        if name not in ("Victory", "Bobo Ticket", "Progressive Competitions"):
            itempool.append(create_item(world, name))

    for name in pubworks_items:
        itempool.append(create_item(world, name))
    
    ticket_count = world.options.BoboTicketsRequired.value
    itempool += create_multiple_items(world, "Bobo Ticket", ticket_count, ItemClassification.progression)

    thresholds = get_competition_unlock_order(world)
    max_batch = max(thresholds.values()) if thresholds else 0
    itempool += create_multiple_items(world, "Progressive Competitions", max_batch, ItemClassification.progression)

    saga_thresholds = get_saga_unlock_order(world)
    max_saga_batch = max(saga_thresholds.values()) if saga_thresholds else 0
    itempool += create_multiple_items(world, "Progressive Sagas", max_saga_batch, ItemClassification.progression)

    victory = create_item(world, "Victory")
    world.multiworld.get_location(goal_event_name, world.player).place_locked_item(victory)

    needed_junk = get_total_locations(world) - len(itempool) - 1
    if needed_junk > 0:
        itempool += create_junk_items(world, needed_junk)

    return itempool

def create_item(world: "BoboWorld", name: str) -> Item:
    data = item_table[name]
    return BoboBayItem(name, data.classification, data.ap_code, world.player)

def create_multiple_items(world: "BoboWorld", name: str, count: int,
                          item_type: ItemClassification = ItemClassification.progression) -> List[Item]:
    data = item_table[name]
    itemlist: List[Item] = []

    for i in range(count):
        itemlist += [BoboBayItem(name, item_type, data.ap_code, world.player)]

    return itemlist

# junk items
def create_junk_items(world: "BoboWorld", count: int) -> List[Item]:
    junk_pool: List[Item] = []
    junk_names = list(junk_weights.keys())
    weights = list(junk_weights.values())

    for _ in range(count):
        chosen = world.random.choices(junk_names, weights=weights, k=1)[0]
        junk_pool.append(world.create_item(chosen))

    return junk_pool

bobo_items = {
    # Progression
    "Bobo Ticket":           ItemData(20050000, ItemClassification.progression),
    "Progressive Competitions": ItemData(20050001, ItemClassification.progression),
    "Progressive Sagas":     ItemData(20050002, ItemClassification.progression),

    # Trait Items
    "Balance Pole":       ItemData(20050400, ItemClassification.useful),
    "Skimboard":          ItemData(20050401, ItemClassification.useful),
    "Steel Chair":        ItemData(20050402, ItemClassification.useful),
    "Trainer Cube":       ItemData(20050403, ItemClassification.useful),
    "Plyo Box":           ItemData(20050404, ItemClassification.useful),
    "Lockpick":           ItemData(20050405, ItemClassification.useful),
    "Resistance Band":    ItemData(20050406, ItemClassification.useful),
    "Fake ID":            ItemData(20050407, ItemClassification.useful),
    "Teapot":             ItemData(20050408, ItemClassification.useful),
    "Glider":             ItemData(20050409, ItemClassification.useful),
    "Gun":                ItemData(20050410, ItemClassification.useful),
    "Slot Machine":       ItemData(20050411, ItemClassification.useful),
    "Dumbbell":           ItemData(20050412, ItemClassification.useful),
    "Fishing Rod":        ItemData(20050413, ItemClassification.useful),
    "Shovel":             ItemData(20050414, ItemClassification.useful),
    "Jump Rope":          ItemData(20050415, ItemClassification.useful),
    "Skillet":            ItemData(20050416, ItemClassification.useful),
    "Trident":            ItemData(20050417, ItemClassification.useful),
    "Lumi Star":          ItemData(20050418, ItemClassification.useful),
    "Sticky Hand":        ItemData(20050419, ItemClassification.useful),
    "Pile of Sand":       ItemData(20050420, ItemClassification.useful),
    "Teleporter":         ItemData(20050421, ItemClassification.useful),
    "Funnel":             ItemData(20050422, ItemClassification.useful),
    "Clipboard":          ItemData(20050423, ItemClassification.useful),
    "Boxing Gloves":      ItemData(20050424, ItemClassification.useful),
    "Ice Axes":           ItemData(20050425, ItemClassification.useful),
    "Good Luck Charm":    ItemData(20050426, ItemClassification.useful),
    "Mood Stabilizer":    ItemData(20050427, ItemClassification.useful),
    "Banana Peel":        ItemData(20050428, ItemClassification.useful),
    "Flint and Steel":    ItemData(20050429, ItemClassification.useful),
    "Skateboard":         ItemData(20050430, ItemClassification.useful),
    "Sword":              ItemData(20050431, ItemClassification.useful),
    "Inhaler":            ItemData(20050432, ItemClassification.useful),

    # Other Items (beds, etc)
    "Bed (Cute, Pink)":           ItemData(20050500, ItemClassification.useful),
    "Round Tent, Red":            ItemData(20050501, ItemClassification.useful),
    "Basic Sleeping Bag, Black":  ItemData(20050502, ItemClassification.useful),
    "Grave":                      ItemData(20050503, ItemClassification.useful),
    "Race Car, Blue":             ItemData(20050504, ItemClassification.useful),
    "Race Car, Red":              ItemData(20050505, ItemClassification.useful),
    "Round Tent, Yellow":         ItemData(20050506, ItemClassification.useful),
    "Cat Bed, Purple":            ItemData(20050507, ItemClassification.useful),
    "Bed (Cute, Red)":            ItemData(20050508, ItemClassification.useful),
    "Crib, Blue":                 ItemData(20050509, ItemClassification.useful),
    "Round Tent, Blue":           ItemData(20050510, ItemClassification.useful),
    "Round Tent, Black":          ItemData(20050511, ItemClassification.useful),
    "Medicine":                   ItemData(20050512, ItemClassification.useful),
    "Basic Sleeping Bag, Purple": ItemData(20050513, ItemClassification.useful),
    "Basic Sleeping Bag, White":  ItemData(20050514, ItemClassification.useful),
    "Basic Sleeping Bag, Blue":   ItemData(20050515, ItemClassification.useful),
    "Basic Sleeping Bag, Red":    ItemData(20050516, ItemClassification.useful),
    "Basic Sleeping Bag, Yellow": ItemData(20050517, ItemClassification.useful),
    "Basic Sleeping Bag, Green":  ItemData(20050518, ItemClassification.useful),
    "Bed (Cute, Black)":          ItemData(20050519, ItemClassification.useful),
    "Lily Pad Bed":               ItemData(20050520, ItemClassification.useful),
    "Trash Bed":                  ItemData(20050521, ItemClassification.useful),
    "Raft Bed":                   ItemData(20050522, ItemClassification.useful),
    "Race Car, Green":            ItemData(20050523, ItemClassification.useful),
    "Cat Bed, Blue":              ItemData(20050524, ItemClassification.useful),
    "Bed (Crib, Pink)":           ItemData(20050525, ItemClassification.useful),
    "Race Car, Black":            ItemData(20050526, ItemClassification.useful),
    
    # Snacks & Consumables
    "Bunny Cracker":         ItemData(20050050, ItemClassification.useful),
    "Crackthrust Hype":      ItemData(20050051, ItemClassification.useful),

    # Accessories & Wearables
    
    # Toys
    "Bunny Stuffed Animal":  ItemData(20050052, ItemClassification.useful),

    # Goal
    "Victory":               ItemData(20050099, ItemClassification.progression),
}

pubworks_items = {
    "Public Works - Fix Benches":                       ItemData(20050600, ItemClassification.useful),
    "Public Works - Basketball Hoop":                   ItemData(20050601, ItemClassification.useful),
    "Public Works - Bench in Garden":                   ItemData(20050602, ItemClassification.useful),
    "Public Works - Bobo Copy Machine":                 ItemData(20050603, ItemClassification.progression),
    "Public Works - Bobo Full Stat Viewer":             ItemData(20050604, ItemClassification.progression),
    "Public Works - Boombox":                           ItemData(20050605, ItemClassification.useful),
    "Public Works - Additional Camps":                  ItemData(20050606, ItemClassification.progression),
    "Public Works - Cave Excursion":                    ItemData(20050607, ItemClassification.progression),
    "Public Works - Deep Forest Excursion":             ItemData(20050608, ItemClassification.progression),
    "Public Works - Gumball Machine":                   ItemData(20050609, ItemClassification.useful),
    "Public Works - Increase Competitions Per Day":     ItemData(20050610, ItemClassification.progression),
    "Public Works - Increase Item Storage in Bayfarer": ItemData(20050611, ItemClassification.progression),
    "Public Works - Soccer Ball":                       ItemData(20050612, ItemClassification.useful),
    "Public Works - Storage Shed":                      ItemData(20050613, ItemClassification.progression),
    "Public Works - Toy Blocks":                        ItemData(20050614, ItemClassification.useful),
    "Public Works - Tree Farm Excursion":               ItemData(20050615, ItemClassification.progression),
    "Public Works - TV":                                ItemData(20050616, ItemClassification.useful),
    "Public Works - Vending Machine":                   ItemData(20050617, ItemClassification.useful),
    "Public Works - Secret Garden":                     ItemData(20050618, ItemClassification.progression),
    "Public Works - Restaurant":                        ItemData(20050619, ItemClassification.progression),
    "Public Works - Item Shop":                         ItemData(20050620, ItemClassification.progression),
    "Public Works - Animal Cracker Shop":               ItemData(20050621, ItemClassification.useful),
    "Public Works - Costume Shop":                      ItemData(20050622, ItemClassification.useful),
    "Public Works - Original Bobo Statue":              ItemData(20050623, ItemClassification.useful),
    "Public Works - Fairy Garden":                      ItemData(20050624, ItemClassification.progression),
}

junk_items = {
    "300 money":                   ItemData(20050090, ItemClassification.filler, 0),
    "Banana Cream Pie":            ItemData(20050092, ItemClassification.filler, 0),
    "Key Lime Pie":                ItemData(20050093, ItemClassification.filler, 0),
    "Blueberry Pie":               ItemData(20050094, ItemClassification.filler, 0),
    "Pecan Pie":                   ItemData(20050095, ItemClassification.filler, 0),
    "Thick Pie":                   ItemData(20050096, ItemClassification.filler, 0),
    "Thick Pie with Love":         ItemData(20050097, ItemClassification.filler, 0),
    "Baked Cake":                  ItemData(20050098, ItemClassification.filler, 0),
}

junk_weights = {
    "300 money": 50,
    "Banana Cream Pie":       5,
    "Key Lime Pie":           5,
    "Blueberry Pie":          5,
    "Pecan Pie":              5,
    "Thick Pie":              24,
    "Thick Pie with Love":    1,
    "Baked Cake":             5,
}

item_table = {
    **bobo_items,
    **junk_items,
    **pubworks_items,
}