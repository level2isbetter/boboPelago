from BaseClasses import Region
from .Types import BoboLocation
from .Locations import location_table, is_valid_location
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import BoboWorld

def create_regions(world: "BoboWorld"):
    menu = create_region(world, "Menu")
    competitions = create_region_and_connect(world, "Competitions", "Menu -> Competitions", menu)
    sagas = create_region_and_connect(world, "Sagas", "Menu -> Sagas", menu)
    pubworks = create_region_and_connect(world, "Public Works", "Menu -> Public Works", menu)

def create_region(world: "BoboWorld", name: str) -> Region:
    reg = Region(name, world.player, world.multiworld)

    for (key, data) in location_table.items():
        if data.region == name:
            if not is_valid_location(world, key):
                continue
            location = BoboLocation(world.player, key, data.ap_code, reg)
            reg.locations.append(location)
    
    world.multiworld.regions.append(reg)
    return reg

def create_region_and_connect(world: "BoboWorld",
                               name: str, entrancename: str, connected_region: Region) -> Region:
    reg: Region = create_region(world, name)
    connected_region.connect(reg, entrancename)
    return reg