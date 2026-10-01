from typing import List, Dict, Any
from dataclasses import dataclass
from worlds.AutoWorld import PerGameCommonOptions
from Options import Choice, OptionGroup, Toggle, Range

GOAL_NAMES = {
    0: "BigJam_Race_D",
    1: "Race_S_PowerGary",
}

def get_goal_name(world) -> str:
    return GOAL_NAMES.get(world.options.Goal.value, "BigJam_Race_D")

def create_option_groups() -> List[OptionGroup]:
    option_group_list: List[OptionGroup] = []
    for name, options in bobo_option_groups.items():
        option_group_list.append(OptionGroup(name=name, options=options))

    return option_group_list

class Goal(Choice):
    """
    Pick goal for the game. Big Jam for faster runs, Power Gary for longer runs.
    If Power Gary is selected, Sagas will be forced on.
    """
    display_name = "Goal"
    option_big_jam = 0
    option_power_gary = 1
    default = 0

class BoboTicketsRequired(Range):
    """
    How many Bobo Tickets are required to unlock the goal competition?
    """
    display_name = "Bobo Tickets Required"
    range_start = 1
    range_end = 10
    default = 3

class SnackMultiplier(Range):
    """
    Multiplier for snack stats
    1 = Normal (1x), 2 = 2x, etc.
    """
    display_name = "Snack Multiplier"
    range_start = 1
    range_end = 1000
    default = 1

class UnlimitedSnacks(Toggle):
    """
    If enabled, the daily feeding limit will be removed,
    allowing you to feed your bobo an unlimited amount of snacks per day.
    """
    display_name = "Unlimited Snacks"

class CompetitionsPerUnlock(Range):
    """
    How many competitions unlock (per rank) each time a Progressive Competitions item is received.
    """
    display_name = "Competitions Per Unlock"
    range_start = 1
    range_end = 15
    default = 4

class SagasEnabled(Toggle):
    """
    Whether or not sagas are enabled / within logic. If you selected power gary, this option will be forced on.
    """
    display_name = "Enable Sagas"

@dataclass
class BoboOptions(PerGameCommonOptions):
    Goal:                        Goal
    BoboTicketsRequired:         BoboTicketsRequired
    SnackMultiplier:             SnackMultiplier
    UnlimitedSnacks:             UnlimitedSnacks
    CompetitionsPerUnlock:       CompetitionsPerUnlock
    SagasEnabled:                SagasEnabled

bobo_option_groups: Dict[str, List[Any]] = {
    "General Options": [Goal, 
        BoboTicketsRequired, 
        SnackMultiplier, 
        UnlimitedSnacks, 
        CompetitionsPerUnlock, 
        SagasEnabled
    ],
}