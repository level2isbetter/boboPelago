from worlds.generic.Rules import add_rule
from .Locations import location_table, is_valid_location, event_locations
from .CompetitionUnlocks import get_competition_unlock_order, get_saga_unlock_order, SAGA_RACES, get_goal_saga
from .Options import get_goal_name
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import BoboWorld

# This is the last big thing to do (at least for me)
# This is where you add item
# These are omega simplified rules
# There are a ton of different ways you can add rules from amoount of items you need to optional items
# Theres also difficulty options and a bunch others
# Id suggest going through a bunch of different ap worlds and seeing how they do the rules
# Even better if its a game you know a lot about and can tell what you need to get to certain locations
def set_rules(world: "BoboWorld"):
    player = world.player

    thresholds = get_competition_unlock_order(world)
    saga_thresholds = get_saga_unlock_order(world)
    asset_to_saga = {asset: saga for saga, assets in SAGA_RACES.items() for asset in assets}
    asset_to_locname = {
        data.asset_name: loc_name
        for loc_name, data in location_table.items()
        if data.asset_name and loc_name not in event_locations
    }
    
    for loc_name, data in location_table.items():
        if not is_valid_location(world, loc_name):
            continue
        if data.asset_name not in thresholds:
            continue
        required = thresholds[data.asset_name]
        if required == 0:
            continue
        add_rule(
            world.multiworld.get_location(loc_name, player),
            lambda state, idx=required: state.has("Progressive Competitions", player, idx)
        )
    
    goal_saga = get_goal_saga(world)

    for loc_name, data in location_table.items():
        if not is_valid_location(world, loc_name):
            continue
        saga_key = asset_to_saga.get(data.asset_name)
        if saga_key is None or saga_key == goal_saga:
            continue
        required = saga_thresholds.get(saga_key, 0)
        if required == 0:
            continue
        add_rule(
            world.multiworld.get_location(loc_name, player),
            lambda state, idx=required: state.has("Progressive Sagas", player, idx)
        )

    goal_asset = get_goal_name(world)
    ticket_required = world.options.BoboTicketsRequired.value

    if goal_saga:
        for asset in SAGA_RACES.get(goal_saga, []):
            loc = asset_to_locname.get(asset)
            if loc:
                add_rule(
                    world.multiworld.get_location(loc, player),
                    lambda state: state.has("Bobo Ticket", player, ticket_required)
                )
    else:
        goal_loc_name = asset_to_locname.get(goal_asset)
        if goal_loc_name:
            add_rule(
                world.multiworld.get_location(goal_loc_name, player),
                lambda state: state.has("Bobo Ticket", player, ticket_required)
            )

    # Victory :)
    world.multiworld.completion_condition[player] = lambda state: state.has("Victory", player)