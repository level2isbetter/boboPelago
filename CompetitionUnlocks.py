from typing import Dict, List, TYPE_CHECKING
from .Locations import location_table
from .Options import get_goal_name

if TYPE_CHECKING:
    from . import BoboWorld

RANK_ORDER = ["E", "D", "C", "B", "A", "S"]
SAGA_ORDER = [
    "Saga_GumballCup", "Saga_FruitCup", "Saga_CrackthrustCup", 
    "Saga_SeagrassCup","Saga_MythicStar", "Saga_BeastStar", 
    "Saga_WildOpen", "Saga_MasqueradeCup", "Saga_ThingBowl",
    "Saga_DashClassic", "Saga_WetClassic", "Saga_JugClassic",
    "Saga_IronClassic", "Saga_HopClassic", "Saga_CosmicStar", 
    "Saga_HotTopChampionship", "Saga_GearStar", "Saga_FairyCup",
    "Saga_TheFinalStar",
]

SAGA_RACES = {
    "Saga_GumballCup": ["Brawl_E_Red", "Brawl_E_Green", "Brawl_D_Blue"],
    "Saga_FruitCup": ["Brawl_D_BerryBee", "Race_C1_Amor We Go", "Race_C2_NanaBoo", "Race_B_WelonWelonWelon"],
    "Saga_CrackthrustCup": ["Race_E_Tizzy", "Race_D1_Carbonated", "Race_D2_EatJumpGame"],
    "Saga_SeagrassCup": ["Race_D_SimpleBeam", "Race_C_SplashBoard", "Race_B1_Slalom", "Race_B2_AcrossTheTowers", "Race_A_TheKelp"],
    "Saga_MythicStar": ["Brawl_E_SkyKick", "Race_D_TwinkleUp", "Race_C_TeenyCroquette"],
    "Saga_BeastStar": ["Race_D_BreakDown", "Brawl_C_HaveThePower", "Race_B_BubTheBeezle"],
    "Saga_WildOpen": ["Race_D_Cat", "Race_C_Rhino", "Race_B_Bunny", "Race_B_Monkey", "Race_A_Penguin"],
    "Saga_MasqueradeCup": ["Brawl_D_2ofHearts", "Brawl_C1_Bink", "Brawl_C2_Nano", "Brawl_B_Kiki", "Brawl_A1_Moto", "Brawl_A2_PunkBrother"],
    "Saga_ThingBowl": ["Race_D_DropKick", "Race_B_FistToAGunFight", "Race_S_IsThisCheating"],
    "Saga_DashClassic": ["Race_E_FirstDash", "Race_D_SecondDash", "Race_C_ThirdDash", "Race_B_FourthDash", "Race_A_FifthDash", "Race_S_SixthDash"],
    "Saga_WetClassic": ["Race_E_FirstWet", "Race_D_SecondWet", "Race_C_ThirdWet", "Race_B_FourthWet", "Race_A_FifthWet", "Race_S_SixthWet"],
    "Saga_JugClassic": ["Race_E_FirstJug", "Race_D_SecondJug", "Race_C_ThirdJug", "Race_B_FourthJug", "Race_A_FifthJug", "Race_S_SixthJug"],
    "Saga_IronClassic": ["Race_E_FirstIron", "Race_D_SecondIron", "Race_C_Third_Iron", "Race_B_FourthIron", "Race_A_FifthIron", "Race_S_SixthIron"],
    "Saga_HopClassic": ["Race_E_FirstHop", "Race_D_SecondHop", "Race_C_ThirdHop", "Race_B_FourthHop", "Race_A_FifthHop", "Race_S_SixthHop"],
    "Saga_CosmicStar": ["Race_B_VamolaCola"],
    "Saga_HotTopChampionship": ["Brawl_B1_Indefatigable", "Brawl_B2_Robusticity", "Brawl_A_Peripatetic", "Brawl_S1_Terrestrial", "Brawl_S2_Polymathic"],
    "Saga_GearStar": ["Race_C_VIV-O OPERA"],
    "Saga_FairyCup": ["Race_D_NakedFeather", "Race_C_FerryToGondo", "Brawl_B_BelieveMe", "Race_A_SeeTheHero"],
    "Saga_TheFinalStar": ["Race_S_PowerGary"],
}

_ASSET_TO_SAGA = {asset: saga for saga, assets in SAGA_RACES.items() for asset in assets}

def get_goal_saga(world: "BoboWorld") -> str:
    return _ASSET_TO_SAGA.get(get_goal_name(world))

def get_competition_unlock_order(world: "BoboWorld") -> Dict[str, int]:
    batch_size = world.options.CompetitionsPerUnlock.value
    goal_asset = get_goal_name(world)
    saga_assets = {asset for assets in SAGA_RACES.values() for asset in assets}

    thresholds: Dict[str, int] = {}
    batch_offset = 0
    for rank in RANK_ORDER:
        names = [
            data.asset_name for data in location_table.values()
            if data.rank == rank
            and data.asset_name
            and data.asset_name != goal_asset
            and data.asset_name not in saga_assets
        ]
        for i, name in enumerate(names):
            thresholds[name] = batch_offset + (i // batch_size)
        if names:
            batch_offset += ((len(names) - 1) // batch_size) + 1
    return thresholds

def build_saga_unlock_order(world: "BoboWorld") -> Dict[str, int]:
    batch_size = world.options.SagasPerUnlock.value
    goal_saga = get_goal_saga(world)
    order = [s for s in SAGA_ORDER if s != goal_saga]
    return {name: i // batch_size for i, name in enumerate(order)}

def get_saga_unlock_order(world: "BoboWorld") -> Dict[str, int]:
    if not hasattr(world, "_saga_unlock_cache"):
        world._saga_unlock_cache = build_saga_unlock_order(world)
    return world._saga_unlock_cache

def get_competition_unlock_order(world: "BoboWorld") -> Dict[str, int]:
    batch_size = world.options.CompetitionsPerUnlock.value
    goal_asset = get_goal_name(world)

    thresholds: Dict[str, int] = {}
    batch_offset = 0
    for rank in RANK_ORDER:
        names = [
            data.asset_name for data in location_table.values()
            if data.rank == rank and data.asset_name and data.asset_name != goal_asset
        ]
        for i, name in enumerate(names):
            thresholds[name] = batch_offset + (i // batch_size)
        if names:
            batch_offset += ((len(names) - 1) // batch_size) + 1
    return thresholds