from typing import Dict, TYPE_CHECKING
import logging

from .Types import LocData
from .Options import get_goal_name

if TYPE_CHECKING:
    from . import BoboWorld

def did_include_extra_locations(world: "BoboWorld") -> bool:
    return bool(world.options.ExtraLocations)

def get_total_locations(world: "BoboWorld") -> int:
    # This is the total that we'll keep updating as we count how many locations there are
    total = 0
    for name in location_table:
        # If we did not turn on extra locations (see how readable it is with that thing from the top)
        # AND the name of it is found in our extra locations table, then that means we dont want to count it
        # So continue moves onto the next name in the table
        if not did_include_extra_locations(world) and name in extra_locations:
            continue

        # If the location is valid though, count it
        if is_valid_location(world, name):
            total += 1

    return total

def get_location_names() -> Dict[str, int]:
    names = {name: data.ap_code for name, data in location_table.items()}

    return names

# check valid location for extra locations
def is_valid_location(world: "BoboWorld", name) -> bool:
    if not did_include_extra_locations(world) and name in extra_locations:
        return False
    if name in event_locations:
        goal_asset = get_goal_name(world)
        if event_locations[name].asset_name != goal_asset:
            return False
    return True

bobo_locations = {
    # E Rank
    "Baby's First Steps (Race, E)": LocData(20050100, "Competitions", "BabysFirstSteps_Race_E", "E"),
    "Bigger Water Train (Race, E)": LocData(20050101, "Competitions", "BiggerWaterTrain_Race_E", "E"),
    "Comet O'Clock (Race, E)": LocData(20050102, "Competitions", "CometOClock_Race_E", "E"),
    "I Can Climb That (Race, E)": LocData(20050103, "Competitions", "ICanClimbThat_Race_E", "E"),
    "In The Drink (Brawl, E)": LocData(20050104, "Competitions", "InTheDrink_Brawl_E", "E"),
    "Lean Milk Baby (Brawl, E)": LocData(20050105, "Competitions", "LeanMilkBaby_Brawl_E", "E"),
    "Let's Try Climbing (Race, E)": LocData(20050106, "Competitions", "Let'sTryClimbing_Race_E", "E"),
    "Little Water Train (Race, E)": LocData(20050107, "Competitions", "LittleWaterTrain_Race_E", "E"),
    "Punch the Baby (Brawl, E)": LocData(20050108, "Competitions", "PunchTheBaby_Brawl_E", "E"),
    "Qwench (Race, E)": LocData(20050109, "Competitions", "Qwench_Race_E", "E"),
    "Still Crawling (Race, E)": LocData(20050110, "Competitions", "StillCrawling_Race_E", "E"),
    "Swim Lessons (Race, E)": LocData(20050111, "Competitions", "SwimLessons_Race_E", "E"),
    "The New Me (Race, E)": LocData(20050112, "Competitions", "TheNewMe_Race_E", "E"),
    "Up To The Moon (Race, E)": LocData(20050113, "Competitions", "UpToTheMoon_Race_E", "E"),

    # D Rank
    "Boy Alphard (Race, D)": LocData(20050114, "Competitions", "Alphard_Race_D", "D"),
    "Beam With a View (Race, D)": LocData(20050115, "Competitions", "BeamWithAView_Race_D", "D"),
    "Beefy (Brawl, D)": LocData(20050116, "Competitions", "Beefy_Brawl_D", "D"),
    "Big Jam (Race, D)": LocData(20050117, "Competitions", "BigJam_Race_D", "D"),
    "Channel It (Race, D)": LocData(20050118, "Competitions", "ChannelIt_Race_D", "D"),
    "Crawfish Coo (Brawl, D)": LocData(20050119, "Competitions", "CrawfishCoo_Brawl_D", "D"),
    "Double Kee Laps (Race, D)": LocData(20050120, "Competitions", "Double Kee Laps_Race_D", "D"),
    "Drippy (Brawl, D)": LocData(20050121, "Competitions", "Drippy_Brawl_D", "D"),
    "Little Longer Now (Race, D)": LocData(20050122, "Competitions", "LittleLongerNow_Race_D", "D"),
    "Mini Match (Brawl, D)": LocData(20050123, "Competitions", "MiniMatch_Brawl_D", "D"),
    "Muckula (Race, D)": LocData(20050124, "Competitions", "Muckula_Race_D_Relay", "D"),
    "Pow (Brawl, D)": LocData(20050125, "Competitions", "Pow_Brawl_D", "D"),
    "Pumpkick (Brawl, D)": LocData(20050126, "Competitions", "Pumpkick_Brawl_D", "D"),
    "Punch It (Race, D)": LocData(20050127, "Competitions", "PunchIt_Race_D", "D"),
    "Splish Block (Race, D)": LocData(20050128, "Competitions", "SplishBlock_Race_D", "D"),
    "Take Me Out (Brawl, D)": LocData(20050129, "Competitions", "TakeMeOut_Brawl_D", "D"),
    "Test the Jump (Race, D)": LocData(20050130, "Competitions", "TestTheJump_Race_D", "D"),
    "Through the Cave (Race, D)": LocData(20050131, "Competitions", "ThroughTheCave_Race_D", "D"),
    "Under The Scramble (Brawl, D)": LocData(20050132, "Competitions", "UndertheScramble_Brawl_D", "D"),
    "Vertical Doggy Paddle (Race, D)": LocData(20050133, "Competitions", "VerticalDoggyPaddle_Race_D", "D"),
    "Walk Along High (Race, D)": LocData(20050134, "Competitions", "WalkAlongHigh_Race_D", "D"),
    "Wavey Baby (Race, D)": LocData(20050135, "Competitions", "WaveyBaby_Race_D", "D"),
    "Woovy (Race, D)": LocData(20050136, "Competitions", "Woovy_Race_D", "D"),
    "You Jump, I Climb (Race, D)": LocData(20050137, "Competitions", "YouJumpIClimb_Race_D_Relay", "D"),

    # C Rank
    "Bring It (Brawl, C)": LocData(20050138, "Competitions", "BringIt_Brawl_C", "C"),
    "Coral (Race, C)": LocData(20050139, "Competitions", "Coral_Race", "C"),
    "Course and Rough (Race, C)": LocData(20050140, "Competitions", "CourseAndRough_Race_C", "C"),
    "Dinosaur Ken (Brawl, C)": LocData(20050141, "Competitions", "DinosaurKen_Brawl_C", "C"),
    "Discounted Island Tour (Race, C)": LocData(20050142, "Competitions", "DiscountedTour_Race_C_Relay", "C"),
    "Final Straw (Race, C)": LocData(20050143, "Competitions", "FinalStraw_Race_C", "C"),
    "Flower (Race, C)": LocData(20050144, "Competitions", "Flower_Race", "C"),
    "From the Top Rope (Race, C)": LocData(20050145, "Competitions", "FromTheTopRope_Race_C", "C"),
    "Glide Wandering (Race, C)": LocData(20050146, "Competitions", "GliderWandering_Race_C", "C"),
    "Happy New Year! (Race, C)": LocData(20050147, "Competitions", "HappyNewYear_Race_C", "C"),
    "Hotel Privago (Race, C)": LocData(20050148, "Competitions", "HotelPrivago_Race_C", "C"),
    "Late Night Jog (Race, C)": LocData(20050149, "Competitions", "LateNightJog_Race_C", "C"),
    "Oblivio (Race, C)": LocData(20050150, "Competitions", "Oblivio_Race_C", "C"),
    "Pick Me Corner (Race, C)": LocData(20050151, "Competitions", "PickMeCorner_Race_C_Relay", "C"),
    "Resist This (Brawl, C)": LocData(20050152, "Competitions", "ResistThis_Brawl_C", "C"),
    "Roundabout Rolled (Race, C)": LocData(20050153, "Competitions", "RoundaboutRolled_Race_C", "C"),
    "Stranded (Brawl, C)": LocData(20050154, "Competitions", "Stranded_Brawl_C", "C"),
    "Up and Over (Race, C)": LocData(20050155, "Competitions", "UpAndOver_Race_C", "C"),
    "Up the TAG (Race, C)": LocData(20050156, "Competitions", "UptheTAG_Race_C", "C"),
    "Walking on Water (Race, C)": LocData(20050157, "Competitions", "WalkingOnWater_Race_C", "C"),
    "Water Boarding (Race, C)": LocData(20050158, "Competitions", "WaterBoarding_Race_C", "C"),
    "Water Kee (Race, C)": LocData(20050159, "Competitions", "WaterKee_Race_C", "C"),
    "What is This Wall? (Race, C)": LocData(20050160, "Competitions", "WhatIsThisWall_Race_C", "C"),
    "Yoooo (Race, C)": LocData(20050161, "Competitions", "Yoooo_Race_C", "C"),

    # B Rank
    "Korn For Us (Race, B)": LocData(20050162, "Competitions", "AxeAway_Race_B", "B"),
    "Boulder (Race, B)": LocData(20050163, "Competitions", "Boulder_Race", "B"),
    "Bright Swim (Race, B)": LocData(20050164, "Competitions", "BrightSwim_Race_B", "B"),
    "Choose You (Race, B)": LocData(20050165, "Competitions", "ChooseYou_Race_B_Relay", "B"),
    "Cliff (Brawl, B)": LocData(20050166, "Competitions", "Cliff_Brawl", "B"),
    "Couple Caving (Race, B)": LocData(20050167, "Competitions", "CoupleCaving_Race_B_Relay", "B"),
    "Cream of Biceps (Race, B)": LocData(20050168, "Competitions", "CreamOfBiceps_Race_B", "B"),
    "Dangerous Walls (Race, B)": LocData(20050169, "Competitions", "DangerousWalls_Race_B", "B"),
    "Dark Swim (Race, B)": LocData(20050170, "Competitions", "DarkSwim_Race_B", "B"),
    "Day of the Doubloon (Race, B)": LocData(20050171, "Competitions", "DayOfTheDoubloon_Race_B", "B"),
    "Devil Pair (Race, B)": LocData(20050172, "Competitions", "DevilPair_Race_B_Relay", "B"),
    "Dinner Time (Brawl, B)": LocData(20050173, "Competitions", "DinnerTime_Brawl_B", "B"),
    "Froodoo (Race, B)": LocData(20050174, "Competitions", "Froodoo_Race_B", "B"),
    "Group Island Tour (Race, B)": LocData(20050175, "Competitions", "GroupIslandTour_Race_B", "B"),
    "Heardolls (Race, B)": LocData(20050176, "Competitions", "Heardolls_Race_B", "B"),
    "KB Vert (Race, B)": LocData(20050177, "Competitions", "KBVert_Race_B", "B"),
    "Late Night Scuffle (Brawl, B)": LocData(20050178, "Competitions", "LateNightScuffle_Brawl_B", "B"),
    "Leaf (Race, B)": LocData(20050179, "Competitions", "Leaf_Race", "B"),
    "Long Distance (Race, B)": LocData(20050180, "Competitions", "LongDistance_Race_B", "B"),
    "Long Jump (Race, B)": LocData(20050181, "Competitions", "LongJump_Race_B", "B"),
    "Milk Cert (Race, B)": LocData(20050182, "Competitions", "MilkCert_Race_B", "B"),
    "Non-Dairy (Brawl, B)": LocData(20050183, "Competitions", "NonDairy_Brawl_B", "B"),
    "Pier (Brawl, B)": LocData(20050184, "Competitions", "Pier_Brawl", "B"),
    "Quick Hands (Brawl, B)": LocData(20050185, "Competitions", "QuickHands_Brawl_B", "B"),
    "Rope Soap (Race, B)": LocData(20050186, "Competitions", "RopeSoap_Race_B", "B"),
    "Skater Boy (Race, B)": LocData(20050187, "Competitions", "SkaterBoy_Race_B", "B"),
    "Slow and Steady (Race, B)": LocData(20050188, "Competitions", "SlowAndSteady_Race_B", "B"),
    "5 Species Showcase (Race, B)": LocData(20050189, "Competitions", "SpeciesShowcase_Race", "B"),
    "Sticky Sit (Brawl, B)": LocData(20050190, "Competitions", "StickySit_Brawl_B", "B"),
    "Traffic Light (Race, B)": LocData(20050191, "Competitions", "TrafficLight_Race_B_Relay", "B"),

    # A Rank
    "Black Water (Race, A)": LocData(20050192, "Competitions", "BlackWater_Race_A_Relay", "A"),
    "Bound Up Bundle Up (Race, A)": LocData(20050193, "Competitions", "BoundUp_Race_A", "A"),
    "Clean Supreme (Race, A)": LocData(20050194, "Competitions", "CleanSupreme_Race_A", "A"),
    "Dark Doubloon (Race, A)": LocData(20050195, "Competitions", "DarkDoubloon_Race_A", "A"),
    "Dive (Race, A)": LocData(20050196, "Competitions", "Dive_Race", "A"),
    "Frontline (Race, A)": LocData(20050197, "Competitions", "Frontline_Race_A", "A"),
    "Galaxy Garden (Brawl, A)": LocData(20050198, "Competitions", "GalaxyGarden_Brawl_A", "A"),
    "Heaven Together (Race, A)": LocData(20050199, "Competitions", "HeavenTogether_Race_A_Relay", "A"),
    "Helicopter (Race, A)": LocData(20050200, "Competitions", "Helicopter_Race", "A"),
    "IRS (Brawl, A)": LocData(20050201, "Competitions", "IRS_Brawl_A", "A"),
    "Island Tour (Race, A)": LocData(20050202, "Competitions", "IslandTour_Race_A", "A"),
    "Lava Guava (Race, A)": LocData(20050203, "Competitions", "LavaGuava_Race_A", "A"),
    "Lumi Lumi Lumi (Race, A)": LocData(20050204, "Competitions", "LumiLumiLumi_Race_A", "A"),
    "Master Swordsman (Brawl, A)": LocData(20050205, "Competitions", "MasterSwordsman_Brawl_A", "A"),
    "Pool to Air (Race, A)": LocData(20050206, "Competitions", "PoolToAir_Race_A", "A"),
    "Stranded High (Brawl, A)": LocData(20050207, "Competitions", "StrandedHigh_Brawl_A", "A"),
    "This Spoon Is Taken (Race, A)": LocData(20050208, "Competitions", "ThisSpoonIsTaken_Race_A", "A"),
    "Very Important Person (Race, A)": LocData(20050209, "Competitions", "VIP_Race_A", "A"),
    "Wanna Help Me Jump? (Race, A)": LocData(20050210, "Competitions", "WannaHelpMeJump_A_Relay", "A"),
    "Water to Cliff (Race, A)": LocData(20050211, "Competitions", "WaterToCliff_Race_A", "A"),
    "Wet Walk (Race, A)": LocData(20050212, "Competitions", "WetWalk_Race_A", "A"),

    # S Rank
    "Aero Vine (Race, S)": LocData(20050213, "Competitions", "AeroVine_Race_S", "S"),
    "Alley (Brawl, S)": LocData(20050214, "Competitions", "Alley_Brawl", "S"),
    "Betelgeuse (Race, S)": LocData(20050215, "Competitions", "Betelgeuse_Race_S", "S"),
    "Cloud (Race, S)": LocData(20050216, "Competitions", "Cloud_Race", "S"),
    "The Dark Gauntlet (Race, S)": LocData(20050217, "Competitions", "DarkGauntlet_Race_S", "S"),
    "FIRE (Race, S)": LocData(20050218, "Competitions", "FIRE_Race_S", "S"),
    "Friendly Neighborhood (Race, S)": LocData(20050219, "Competitions", "FriendlyNeighborhood_Race_S", "S"),
    "The Gauntlet (Race, S)": LocData(20050220, "Competitions", "Gauntlet_Race_S", "S"),
    "Metro Party (Race, S)": LocData(20050221, "Competitions", "MetroParty_Race_S_Relay", "S"),
    "Mile High Lock (Brawl, S)": LocData(20050222, "Competitions", "MileHigh_Brawl_S", "S"),
    "Night Dippy (Race, S)": LocData(20050223, "Competitions", "NightDippy_Race_S", "S"),
    "No Touch (Brawl, S)": LocData(20050224, "Competitions", "NoTouch_Brawl_S", "S"),
    "Parallax (Race, S)": LocData(20050225, "Competitions", "Parallax_Race_S_Relay", "S"),
    "Puff Pounding (Brawl, S)": LocData(20050226, "Competitions", "PuffPounding_Brawl_S", "S"),
    "Pull Up Those Hips (Race, S)": LocData(20050227, "Competitions", "PullUpThoseHips_Race_S", "S"),
    "Rigel In Second (Race, S)": LocData(20050228, "Competitions", "RigelInSecond_Race_S", "S"),
    "Rock The Boat (Race, S)": LocData(20050229, "Competitions", "RockTheBoat_Race_S", "S"),
    "Run Run Run (Race, S)": LocData(20050230, "Competitions", "RunRunRun_Race_S", "S"),
    "Saddle Suds (Brawl, S)": LocData(20050231, "Competitions", "SadalSuds_Brawl_S", "S"),
    "Sadder Boys (Race, S)": LocData(20050232, "Competitions", "SadderBoys_Race_S", "S"),
    "True Sparkle (Race, S)": LocData(20050233, "Competitions", "TrueSparkle_Race_S", "S"),
    "Wind Around (Race, S)": LocData(20050234, "Competitions", "WindAround_Race_S", "S"),
    "With That Thang (Race, S)": LocData(20050235, "Competitions", "WithThatThang_Race_S", "S"),
}

saga_locations = {
    # Saga Competitions
    "First Dash (Race, E)":                 LocData(20050300, "Competitions", "Race_E_FirstDash", "E"),
    "Second Dash (Race, D)":                LocData(20050301, "Competitions", "Race_D_SecondDash", "D"),
    "Third Dash (Race, C)":                 LocData(20050302, "Competitions", "Race_C_ThirdDash", "C"),
    "Fourth Dash (Race, B)":                LocData(20050303, "Competitions", "Race_B_FourthDash", "B"),
    "Fifth Dash (Race, A)":                 LocData(20050304, "Competitions", "Race_A_FifthDash", "A"),
    "Sixth Dash (Race, S)":                 LocData(20050305, "Competitions", "Race_S_SixthDash", "S"),
    "Sky Kick (Brawl, E)":                  LocData(20050306, "Competitions", "Brawl_E_SkyKick", "E"),
    "Twinkle Up (Race, D)":                 LocData(20050307, "Competitions", "Race_D_TwinkleUp", "D"),
    "Teeny Croquette (Race, C)":            LocData(20050308, "Competitions", "Race_C_TeenyCroquette", "C"),
    "Vamola Cola (Race, B)":                LocData(20050309, "Competitions", "Race_B_VamolaCola", "B"),
    "First Wet (Race, E)":                  LocData(20050310, "Competitions", "Race_E_FirstWet", "E"),
    "Second Wet (Race, D)":                 LocData(20050311, "Competitions", "Race_D_SecondWet", "D"),
    "Third Wet (Race, C)":                  LocData(20050312, "Competitions", "Race_C_ThirdWet", "C"),
    "Fourth Wet (Race, B)":                 LocData(20050313, "Competitions", "Race_B_FourthWet", "B"),
    "Fifth Wet (Race, A)":                  LocData(20050314, "Competitions", "Race_A_FifthWet", "A"),
    "Sixth Wet (Race, S)":                  LocData(20050315, "Competitions", "Race_S_SixthWet", "S"),
    "Tizzy (Race, E)":                      LocData(20050316, "Competitions", "Race_E_Tizzy", "E"),
    "Carbonated (Race, D)":                 LocData(20050317, "Competitions", "Race_D1_Carbonated", "D"),
    "Eat Jump Game (Race, D)":              LocData(20050318, "Competitions", "Race_D2_EatJumpGame", "D"),
    "Power Gary (Race, S)":                 LocData(20050319, "Competitions", "Race_S_PowerGary", "S"),
    "Break Down (Race, D)":                 LocData(20050320, "Competitions", "Race_D_BreakDown", "D"),
    "Have The Power (Brawl, C)":            LocData(20050321, "Competitions", "Brawl_C_HaveThePower", "C"),
    "Bub The Beezle (Race, B)":             LocData(20050322, "Competitions", "Race_B_BubTheBeezle", "B"),
    "Berry Bee (Brawl, D)":                 LocData(20050323, "Competitions", "Brawl_D_BerryBee", "D"),
    "Amor We Go (Race, C)":                 LocData(20050324, "Competitions", "Race_C1_Amor We Go", "C"),
    "Nana Boo (Race, C)":                   LocData(20050325, "Competitions", "Race_C2_NanaBoo", "C"),
    "Welon Welon Welon (Race, B)":          LocData(20050326, "Competitions", "Race_B_WelonWelonWelon", "B"),
    "Drop Kick (Race, D)":                  LocData(20050327, "Competitions", "Race_D_DropKick", "D"),
    "Fist To A Gun Fight (Race, B)":        LocData(20050328, "Competitions", "Race_B_FistToAGunFight", "B"),
    "Is This Cheating (Race, S)":           LocData(20050329, "Competitions", "Race_S_IsThisCheating", "S"),
    "First Hop (Race, E)":                  LocData(20050330, "Competitions", "Race_E_FirstHop", "E"),
    "Second Hop (Race, D)":                 LocData(20050331, "Competitions", "Race_D_SecondHop", "D"),
    "Third Hop (Race, C)":                  LocData(20050332, "Competitions", "Race_C_ThirdHop", "C"),
    "Fourth Hop (Race, B)":                 LocData(20050333, "Competitions", "Race_B_FourthHop", "B"),
    "Fifth Hop (Race, A)":                  LocData(20050334, "Competitions", "Race_A_FifthHop", "A"),
    "Sixth Hop (Race, S)":                 LocData(20050335, "Competitions", "Race_S_SixthHop", "S"),
    "Indefatigable (Brawl, B)":             LocData(20050336, "Competitions", "Brawl_B1_Indefatigable", "B"),
    "Robusticity (Brawl, B)":               LocData(20050337, "Competitions", "Brawl_B2_Robusticity", "B"),
    "Peripatetic (Brawl, A)":               LocData(20050338, "Competitions", "Brawl_A_Peripatetic", "A"),
    "Terrestrial (Brawl, S)":               LocData(20050339, "Competitions", "Brawl_S1_Terrestrial", "S"),
    "Polymathic (Brawl, S)":               LocData(20050340, "Competitions", "Brawl_S2_Polymathic", "S"),
    "Simple Beam (Race, D)":                LocData(20050341, "Competitions", "Race_D_SimpleBeam", "D"),
    "Splash Board (Race, C)":               LocData(20050342, "Competitions", "Race_C_SplashBoard", "C"),
    "Slalom (Race, B)":                     LocData(20050343, "Competitions", "Race_B1_Slalom", "B"),
    "Across The Towers (Race, B)":          LocData(20050344, "Competitions", "Race_B2_AcrossTheTowers", "B"),
    "The Kelp (Race, A)":                   LocData(20050345, "Competitions", "Race_A_TheKelp", "A"),
    "VIV-O OPERA (Race, C)":                LocData(20050346, "Competitions", "Race_C_VIV-O OPERA", "C"),
    "First Jug (Race, E)":                  LocData(20050347, "Competitions", "Race_E_FirstJug", "E"),
    "Second Jug (Race, D)":                 LocData(20050348, "Competitions", "Race_D_SecondJug", "D"),
    "Third Jug (Race, C)":                  LocData(20050349, "Competitions", "Race_C_ThirdJug", "C"),
    "Fourth Jug (Race, B)":                 LocData(20050350, "Competitions", "Race_B_FourthJug", "B"),
    "Fifth Jug (Race, A)":                  LocData(20050351, "Competitions", "Race_A_FifthJug", "A"),
    "Sixth Jug (Race, S)":                 LocData(20050352, "Competitions", "Race_S_SixthJug", "S"),
    "First Iron (Race, E)":                 LocData(20050353, "Competitions", "Race_E_FirstIron", "E"),
    "Second Iron (Race, D)":                LocData(20050354, "Competitions", "Race_D_SecondIron", "D"),
    "Third Iron (Race, C)":                 LocData(20050355, "Competitions", "Race_C_Third_Iron", "C"),
    "Fourth Iron (Race, B)":                LocData(20050356, "Competitions", "Race_B_FourthIron", "B"),
    "Fifth Iron (Race, A)":                 LocData(20050357, "Competitions", "Race_A_FifthIron", "A"),
    "Sixth Iron (Race, S)":                LocData(20050358, "Competitions", "Race_S_SixthIron", "S"),
    "2 of Hearts (Brawl, D)":               LocData(20050359, "Competitions", "Brawl_D_2ofHearts", "D"),
    "Bink (Brawl, C)":                      LocData(20050360, "Competitions", "Brawl_C1_Bink", "C"),
    "Nano (Brawl, C)":                      LocData(20050361, "Competitions", "Brawl_C2_Nano", "C"),
    "Kiki (Brawl, B)":                      LocData(20050362, "Competitions", "Brawl_B_Kiki", "B"),
    "Moto (Brawl, A)":                      LocData(20050363, "Competitions", "Brawl_A1_Moto", "A"),
    "Punk Brother (Brawl, A)":              LocData(20050364, "Competitions", "Brawl_A2_PunkBrother", "A"),
    "Cat (Race, D)":                        LocData(20050365, "Competitions", "Race_D_Cat", "D"),
    "Rhino (Race, C)":                      LocData(20050366, "Competitions", "Race_C_Rhino", "C"),
    "Bunny (Race, B)":                      LocData(20050367, "Competitions", "Race_B_Bunny", "B"),
    "Monkey (Race, B)":                     LocData(20050368, "Competitions", "Race_B_Monkey", "B"),
    "Penguin (Race, A)":                    LocData(20050369, "Competitions", "Race_A_Penguin", "A"),
    "Red (Brawl, E)":                       LocData(20050370, "Competitions", "Brawl_E_Red", "E"),
    "Green (Brawl, E)":                     LocData(20050371, "Competitions", "Brawl_E_Green", "E"),
    "Blue (Brawl, D)":                      LocData(20050372, "Competitions", "Brawl_D_Blue", "D"),
    "Naked Feather (Race, D)":              LocData(20050373, "Competitions", "Race_D_NakedFeather", "D"),
    "Ferry To Gondo (Race, C)":             LocData(20050374, "Competitions", "Race_C_FerryToGondo", "C"),
    "Believe Me (Brawl, B)":                LocData(20050375, "Competitions", "Brawl_B_BelieveMe", "B"),
    "See The Hero (Race, A)":               LocData(20050376, "Competitions", "Race_A_SeeTheHero", "A"),
}

pubworks_locations = {
    "Public Works - Fix Benches":                       LocData(20050700, "Public Works", "PWP_FixBenches"),
    "Public Works - Basketball Hoop":                   LocData(20050701, "Public Works", "PWP_BasketballHoop"),
    "Public Works - Bench in Garden":                   LocData(20050702, "Public Works", "PWP_BenchInGarden"),
    "Public Works - Bobo Copy Machine":                 LocData(20050703, "Public Works", "PWP_BoboCopier"),
    "Public Works - Bobo Full Stat Viewer":             LocData(20050704, "Public Works", "PWP_BoboFullStatViewer"),
    "Public Works - Boombox":                           LocData(20050705, "Public Works", "PWP_Boombox"),
    "Public Works - Additional Camps":                  LocData(20050706, "Public Works", "PWP_CampUpgrade"),
    "Public Works - Cave Excursion":                    LocData(20050707, "Public Works", "PWP_Excursion_Caves"),
    "Public Works - Deep Forest Excursion":             LocData(20050708, "Public Works", "PWP_Excursion_DeepForest"),
    "Public Works - Gumball Machine":                   LocData(20050709, "Public Works", "PWP_GumballMachine"),
    "Public Works - Increase Competitions Per Day":     LocData(20050710, "Public Works", "PWP_IncreasedCompetitionsPerDay"),
    "Public Works - Increase Item Storage in Bayfarer": LocData(20050711, "Public Works", "PWP_IncreasedItemStorageInBoat"),
    "Public Works - Soccer Ball":                       LocData(20050712, "Public Works", "PWP_SoccerBall"),
    "Public Works - Storage Shed":                      LocData(20050713, "Public Works", "PWP_StorageShed"),
    "Public Works - Toy Blocks":                        LocData(20050714, "Public Works", "PWP_ToyBlocks"),
    "Public Works - Tree Farm Excursion":               LocData(20050715, "Public Works", "PWP_Excursion_TreeFarm"),
    "Public Works - TV":                                LocData(20050716, "Public Works", "PWP_TV"),
    "Public Works - Vending Machine":                   LocData(20050717, "Public Works", "PWP_VendingMachine"),
    "Public Works - Secret Garden":                     LocData(20050718, "Public Works", "PWP_SecretGarden"),
    "Public Works - Restaurant":                        LocData(20050719, "Public Works", "PWP_Restaurant"),
    "Public Works - Item Shop":                         LocData(20050720, "Public Works", "PWP_ItemShop"),
    "Public Works - Animal Cracker Shop":               LocData(20050721, "Public Works", "PWP_AnimalCrackerShop"),
    "Public Works - Costume Shop":                      LocData(20050722, "Public Works", "PWP_CostumeShop"),
    "Public Works - Original Bobo Statue":              LocData(20050723, "Public Works", "PWP_OriginalBoboStatue"),
    "Public Works - Fairy Garden":                      LocData(20050724, "Public Works", "PWP_SkyGarden"),
}

extra_locations = {}

event_locations = {
    "Beat Big Jam":    LocData(None, "Competitions", "BigJam_Race_D", "D"),
    "Beat Power Gary": LocData(None, "Competitions", "Race_S_PowerGary", "S"),
}

location_table = {
    **bobo_locations,
    **saga_locations,
    **pubworks_locations,
    **extra_locations,
    **event_locations,
}