"""
Card database for Commander gameplay.
Includes commonly played Commander staples across all categories.
"""
from typing import Optional
from core.card import Card, CardType, ManaCost, Color
from core.triggers import (
    create_etb_draw_trigger,
    create_dies_draw_trigger,
    create_etb_ramp_trigger,
)


def create_basic_cards():
    """Create a basic set of cards for testing."""
    cards = []
    
    # Basic Lands
    cards.extend([
        Card(
            id="plains_1",
            name="Plains",
            card_types=[CardType.LAND],
            colors=[Color.WHITE],
            oracle_text="T: Add {W}."
        ),
        Card(
            id="island_1",
            name="Island",
            card_types=[CardType.LAND],
            colors=[Color.BLUE],
            oracle_text="T: Add {U}."
        ),
        Card(
            id="swamp_1",
            name="Swamp",
            card_types=[CardType.LAND],
            colors=[Color.BLACK],
            oracle_text="T: Add {B}."
        ),
        Card(
            id="mountain_1",
            name="Mountain",
            card_types=[CardType.LAND],
            colors=[Color.RED],
            oracle_text="T: Add {R}."
        ),
        Card(
            id="forest_1",
            name="Forest",
            card_types=[CardType.LAND],
            colors=[Color.GREEN],
            oracle_text="T: Add {G}."
        ),
    ])
    
    # ===== RAMP & MANA ACCELERATION =====
    # Artifacts
    cards.extend([
        Card(
            id="sol_ring",
            name="Sol Ring",
            mana_cost=ManaCost(generic=1),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="T: Add {C}{C}."
        ),
        Card(
            id="arcane_signet",
            name="Arcane Signet",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="T: Add one mana of any color in your commander's color identity."
        ),
        Card(
            id="commander_sphere",
            name="Commander's Sphere",
            mana_cost=ManaCost(generic=3),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="T: Add one mana of any color in your commander's color identity. Sacrifice: Draw a card."
        ),
        Card(
            id="thought_vessel",
            name="Thought Vessel",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="You have no maximum hand size. T: Add {C}."
        ),
        Card(
            id="mind_stone",
            name="Mind Stone",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="T: Add {C}. 1, T, Sacrifice: Draw a card."
        ),
        Card(
            id="fellwar_stone",
            name="Fellwar Stone",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="T: Add one mana of any color that a land an opponent controls could produce."
        ),
        # Signets
        Card(
            id="azorius_signet",
            name="Azorius Signet",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="1, T: Add {W}{U}."
        ),
        Card(
            id="selesnya_signet",
            name="Selesnya Signet",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="1, T: Add {G}{W}."
        ),
        Card(
            id="gruul_signet",
            name="Gruul Signet",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="1, T: Add {R}{G}."
        ),
        Card(
            id="simic_signet",
            name="Simic Signet",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="1, T: Add {G}{U}."
        ),
        # Talismans
        Card(
            id="talisman_of_progress",
            name="Talisman of Progress",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="T: Add {C}. T: Add {W} or {U}. Talisman of Progress deals 1 damage to you."
        ),
        Card(
            id="talisman_of_unity",
            name="Talisman of Unity",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="T: Add {C}. T: Add {G} or {W}. Talisman of Unity deals 1 damage to you."
        ),
    ])
    
    # Green Ramp Spells
    cards.extend([
        Card(
            id="cultivate",
            name="Cultivate",
            mana_cost=ManaCost(generic=2, green=1),
            card_types=[CardType.SORCERY],
            colors=[Color.GREEN],
            oracle_text="Search your library for up to two basic land cards, reveal those cards, put one onto the battlefield tapped and the other into your hand, then shuffle."
        ),
        Card(
            id="kodamas_reach",
            name="Kodama's Reach",
            mana_cost=ManaCost(generic=2, green=1),
            card_types=[CardType.SORCERY],
            colors=[Color.GREEN],
            oracle_text="Search your library for up to two basic land cards, reveal those cards, put one onto the battlefield tapped and the other into your hand, then shuffle."
        ),
        Card(
            id="rampant_growth",
            name="Rampant Growth",
            mana_cost=ManaCost(generic=1, green=1),
            card_types=[CardType.SORCERY],
            colors=[Color.GREEN],
            oracle_text="Search your library for a basic land card, put it onto the battlefield tapped, then shuffle."
        ),
        Card(
            id="natures_lore",
            name="Nature's Lore",
            mana_cost=ManaCost(generic=1, green=1),
            card_types=[CardType.SORCERY],
            colors=[Color.GREEN],
            oracle_text="Search your library for a Forest card, put it onto the battlefield, then shuffle."
        ),
        Card(
            id="three_visits",
            name="Three Visits",
            mana_cost=ManaCost(generic=1, green=1),
            card_types=[CardType.SORCERY],
            colors=[Color.GREEN],
            oracle_text="Search your library for a Forest card, put it onto the battlefield, then shuffle."
        ),
        Card(
            id="farseek",
            name="Farseek",
            mana_cost=ManaCost(generic=1, green=1),
            card_types=[CardType.SORCERY],
            colors=[Color.GREEN],
            oracle_text="Search your library for a Plains, Island, Swamp, or Mountain card, put it onto the battlefield tapped, then shuffle."
        ),
        Card(
            id="explosive_vegetation",
            name="Explosive Vegetation",
            mana_cost=ManaCost(generic=3, green=1),
            card_types=[CardType.SORCERY],
            colors=[Color.GREEN],
            oracle_text="Search your library for up to two basic land cards, put them onto the battlefield tapped, then shuffle."
        ),
        Card(
            id="skyshroud_claim",
            name="Skyshroud Claim",
            mana_cost=ManaCost(generic=3, green=1),
            card_types=[CardType.SORCERY],
            colors=[Color.GREEN],
            oracle_text="Search your library for up to two Forest cards, put them onto the battlefield, then shuffle."
        ),
    ])
    
    # Mana Dorks
    cards.extend([
        Card(
            id="llanowar_elves",
            name="Llanowar Elves",
            mana_cost=ManaCost(green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=1,
            toughness=1,
            oracle_text="T: Add {G}."
        ),
        Card(
            id="elvish_mystic",
            name="Elvish Mystic",
            mana_cost=ManaCost(green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=1,
            toughness=1,
            oracle_text="T: Add {G}."
        ),
        Card(
            id="fyndhorn_elves",
            name="Fyndhorn Elves",
            mana_cost=ManaCost(green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=1,
            toughness=1,
            oracle_text="T: Add {G}."
        ),
        Card(
            id="birds_of_paradise",
            name="Birds of Paradise",
            mana_cost=ManaCost(green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=0,
            toughness=1,
            keywords=["flying"],
            oracle_text="Flying. T: Add one mana of any color."
        ),
        Card(
            id="avacyns_pilgrim",
            name="Avacyn's Pilgrim",
            mana_cost=ManaCost(green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=1,
            toughness=1,
            oracle_text="T: Add {W}."
        ),
    ])
    
    # ===== SIMPLE CREATURES =====
    cards.extend([
        Card(
            id="grizzly_bears",
            name="Grizzly Bears",
            mana_cost=ManaCost(generic=1, green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=2,
            toughness=2,
            oracle_text="A classic 2/2 for 2 mana."
        ),
        Card(
            id="serra_angel",
            name="Serra Angel",
            mana_cost=ManaCost(generic=3, white=2),
            card_types=[CardType.CREATURE],
            colors=[Color.WHITE],
            power=4,
            toughness=4,
            keywords=["flying", "vigilance"],
            oracle_text="Flying, vigilance"
        ),
        Card(
            id="shivan_dragon",
            name="Shivan Dragon",
            mana_cost=ManaCost(generic=4, red=2),
            card_types=[CardType.CREATURE],
            colors=[Color.RED],
            power=5,
            toughness=5,
            keywords=["flying"],
            oracle_text="Flying. {R}: Shivan Dragon gets +1/+0 until end of turn."
        ),
        Card(
            id="llanowar_elves",
            name="Llanowar Elves",
            mana_cost=ManaCost(green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=1,
            toughness=1,
            oracle_text="T: Add {G}."
        ),
        Card(
            id="lightning_bolt",
            name="Lightning Bolt",
            mana_cost=ManaCost(red=1),
            card_types=[CardType.INSTANT],
            colors=[Color.RED],
            oracle_text="Lightning Bolt deals 3 damage to any target."
        ),
        Card(
            id="counterspell",
            name="Counterspell",
            mana_cost=ManaCost(blue=2),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="Counter target spell."
        ),
        Card(
            id="giant_growth",
            name="Giant Growth",
            mana_cost=ManaCost(green=1),
            card_types=[CardType.INSTANT],
            colors=[Color.GREEN],
            oracle_text="Target creature gets +3/+3 until end of turn."
        ),
        Card(
            id="cancel",
            name="Cancel",
            mana_cost=ManaCost(generic=1, blue=2),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="Counter target spell."
        ),
        Card(
            id="negate",
            name="Negate",
            mana_cost=ManaCost(generic=1, blue=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="Counter target noncreature spell."
        ),
        Card(
            id="shock",
            name="Shock",
            mana_cost=ManaCost(red=1),
            card_types=[CardType.INSTANT],
            colors=[Color.RED],
            oracle_text="Shock deals 2 damage to any target."
        ),
        Card(
            id="swords_to_plowshares",
            name="Swords to Plowshares",
            mana_cost=ManaCost(white=1),
            card_types=[CardType.INSTANT],
            colors=[Color.WHITE],
            oracle_text="Exile target creature. Its controller gains life equal to its power."
        ),
        Card(
            id="path_to_exile",
            name="Path to Exile",
            mana_cost=ManaCost(white=1),
            card_types=[CardType.INSTANT],
            colors=[Color.WHITE],
            oracle_text="Exile target creature. Its controller may search their library for a basic land card."
        ),
    ])
    
    # ===== MORE REMOVAL =====
    # Spot Removal
    cards.extend([
        Card(
            id="beast_within",
            name="Beast Within",
            mana_cost=ManaCost(generic=2, green=1),
            card_types=[CardType.INSTANT],
            colors=[Color.GREEN],
            oracle_text="Destroy target permanent. Its controller creates a 3/3 green Beast creature token."
        ),
        Card(
            id="generous_gift",
            name="Generous Gift",
            mana_cost=ManaCost(generic=2, white=1),
            card_types=[CardType.INSTANT],
            colors=[Color.WHITE],
            oracle_text="Destroy target permanent. Its controller creates a 3/3 green Elephant creature token."
        ),
        Card(
            id="chaos_warp",
            name="Chaos Warp",
            mana_cost=ManaCost(generic=2, red=1),
            card_types=[CardType.INSTANT],
            colors=[Color.RED],
            oracle_text="The owner of target permanent shuffles it into their library, then reveals the top card of their library. If it's a permanent card, they put it onto the battlefield."
        ),
        Card(
            id="anguished_unmaking",
            name="Anguished Unmaking",
            mana_cost=ManaCost(generic=1, white=1, black=1),
            card_types=[CardType.INSTANT],
            colors=[Color.WHITE, Color.BLACK],
            oracle_text="Exile target nonland permanent. You lose 3 life."
        ),
        Card(
            id="assassins_trophy",
            name="Assassin's Trophy",
            mana_cost=ManaCost(black=1, green=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLACK, Color.GREEN],
            oracle_text="Destroy target permanent an opponent controls. Its controller may search their library for a basic land card, put it onto the battlefield, then shuffle."
        ),
        Card(
            id="vindicate",
            name="Vindicate",
            mana_cost=ManaCost(generic=1, white=1, black=1),
            card_types=[CardType.SORCERY],
            colors=[Color.WHITE, Color.BLACK],
            oracle_text="Destroy target permanent."
        ),
        Card(
            id="murder",
            name="Murder",
            mana_cost=ManaCost(generic=1, black=2),
            card_types=[CardType.INSTANT],
            colors=[Color.BLACK],
            oracle_text="Destroy target creature."
        ),
        Card(
            id="terminate",
            name="Terminate",
            mana_cost=ManaCost(black=1, red=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLACK, Color.RED],
            oracle_text="Destroy target creature. It can't be regenerated."
        ),
        Card(
            id="natures_claim",
            name="Nature's Claim",
            mana_cost=ManaCost(green=1),
            card_types=[CardType.INSTANT],
            colors=[Color.GREEN],
            oracle_text="Destroy target artifact or enchantment. Its controller gains 4 life."
        ),
        Card(
            id="return_to_dust",
            name="Return to Dust",
            mana_cost=ManaCost(generic=2, white=2),
            card_types=[CardType.INSTANT],
            colors=[Color.WHITE],
            oracle_text="Exile target artifact or enchantment. If you cast this spell during your main phase, you may exile up to one other target artifact or enchantment."
        ),
    ])
    
    # Board Wipes
    cards.extend([
        Card(
            id="wrath_of_god",
            name="Wrath of God",
            mana_cost=ManaCost(generic=2, white=2),
            card_types=[CardType.SORCERY],
            colors=[Color.WHITE],
            oracle_text="Destroy all creatures. They can't be regenerated."
        ),
        Card(
            id="damnation",
            name="Damnation",
            mana_cost=ManaCost(generic=2, black=2),
            card_types=[CardType.SORCERY],
            colors=[Color.BLACK],
            oracle_text="Destroy all creatures. They can't be regenerated."
        ),
        Card(
            id="blasphemous_act",
            name="Blasphemous Act",
            mana_cost=ManaCost(generic=8, red=1),
            card_types=[CardType.SORCERY],
            colors=[Color.RED],
            oracle_text="This spell costs {1} less to cast for each creature on the battlefield. Blasphemous Act deals 13 damage to each creature."
        ),
        Card(
            id="cyclonic_rift",
            name="Cyclonic Rift",
            mana_cost=ManaCost(generic=1, blue=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="Return target nonland permanent you don't control to its owner's hand. Overload {6}{U}"
        ),
        Card(
            id="toxic_deluge",
            name="Toxic Deluge",
            mana_cost=ManaCost(generic=2, black=1),
            card_types=[CardType.SORCERY],
            colors=[Color.BLACK],
            oracle_text="As an additional cost to cast this spell, pay X life. All creatures get -X/-X until end of turn."
        ),
    ])
    
    # ===== CARD DRAW =====
    cards.extend([
        Card(
            id="rhystic_study",
            name="Rhystic Study",
            mana_cost=ManaCost(generic=2, blue=1),
            card_types=[CardType.ENCHANTMENT],
            colors=[Color.BLUE],
            oracle_text="Whenever an opponent casts a spell, you may draw a card unless that player pays {1}."
        ),
        Card(
            id="phyrexian_arena",
            name="Phyrexian Arena",
            mana_cost=ManaCost(generic=1, black=2),
            card_types=[CardType.ENCHANTMENT],
            colors=[Color.BLACK],
            oracle_text="At the beginning of your upkeep, you draw a card and you lose 1 life."
        ),
        Card(
            id="esper_sentinel",
            name="Esper Sentinel",
            mana_cost=ManaCost(white=1),
            card_types=[CardType.ARTIFACT, CardType.CREATURE],
            colors=[Color.WHITE],
            power=1,
            toughness=1,
            oracle_text="Whenever an opponent casts their first noncreature spell each turn, draw a card unless that player pays {X}, where X is Esper Sentinel's power."
        ),
        Card(
            id="blue_suns_zenith",
            name="Blue Sun's Zenith",
            mana_cost=ManaCost(blue=3),  # {X}{U}{U}{U}
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="Target player draws X cards. Shuffle Blue Sun's Zenith into its owner's library."
        ),
        Card(
            id="harmonize",
            name="Harmonize",
            mana_cost=ManaCost(generic=2, green=2),
            card_types=[CardType.SORCERY],
            colors=[Color.GREEN],
            oracle_text="Draw three cards."
        ),
        Card(
            id="nights_whisper",
            name="Night's Whisper",
            mana_cost=ManaCost(generic=1, black=1),
            card_types=[CardType.SORCERY],
            colors=[Color.BLACK],
            oracle_text="You draw two cards and you lose 2 life."
        ),
        Card(
            id="sign_in_blood",
            name="Sign in Blood",
            mana_cost=ManaCost(black=2),  # {B}{B}
            card_types=[CardType.SORCERY],
            colors=[Color.BLACK],
            oracle_text="Target player draws two cards and loses 2 life."
        ),
        Card(
            id="stroke_of_genius",
            name="Stroke of Genius",
            mana_cost=ManaCost(generic=2, blue=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="Target player draws X cards."
        ),
    ])
    
    # ===== MORE CREATURES =====
    # Utility Creatures
    cards.extend([
        Card(
            id="solemn_simulacrum",
            name="Solemn Simulacrum",
            mana_cost=ManaCost(generic=4),
            card_types=[CardType.ARTIFACT, CardType.CREATURE],
            colors=[],
            power=2,
            toughness=2,
            oracle_text="When Solemn Simulacrum enters the battlefield, you may search your library for a basic land card, put it onto the battlefield tapped, then shuffle. When Solemn Simulacrum dies, you may draw a card.",
            triggered_abilities=[
                create_etb_ramp_trigger(),
                create_dies_draw_trigger(1),
            ],
        ),
        Card(
            id="mulldrifter",
            name="Mulldrifter",
            mana_cost=ManaCost(generic=4, blue=1),
            card_types=[CardType.CREATURE],
            colors=[Color.BLUE],
            power=2,
            toughness=2,
            keywords=["flying"],
            oracle_text="Flying. When Mulldrifter enters the battlefield, draw two cards. Evoke {2}{U}",
            triggered_abilities=[create_etb_draw_trigger(2)],
        ),
        Card(
            id="wood_elves",
            name="Wood Elves",
            mana_cost=ManaCost(generic=2, green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=1,
            toughness=1,
            oracle_text="When Wood Elves enters the battlefield, search your library for a Forest card, put it onto the battlefield tapped, then shuffle.",
            triggered_abilities=[create_etb_ramp_trigger()],
        ),
        Card(
            id="eternal_witness",
            name="Eternal Witness",
            mana_cost=ManaCost(generic=1, green=2),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=2,
            toughness=1,
            oracle_text="When Eternal Witness enters the battlefield, you may return target card from your graveyard to your hand."
        ),
        Card(
            id="reclamation_sage",
            name="Reclamation Sage",
            mana_cost=ManaCost(generic=2, green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=2,
            toughness=1,
            oracle_text="When Reclamation Sage enters the battlefield, you may destroy target artifact or enchantment."
        ),
        Card(
            id="acidic_slime",
            name="Acidic Slime",
            mana_cost=ManaCost(generic=3, green=2),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=2,
            toughness=2,
            keywords=["deathtouch"],
            oracle_text="Deathtouch. When Acidic Slime enters the battlefield, destroy target artifact, enchantment, or land."
        ),
    ])
    
    # Threats and Finishers
    cards.extend([
        Card(
            id="avenger_of_zendikar",
            name="Avenger of Zendikar",
            mana_cost=ManaCost(generic=5, green=2),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=5,
            toughness=5,
            oracle_text="When Avenger of Zendikar enters the battlefield, create a 0/1 green Plant creature token for each land you control."
        ),
        Card(
            id="craterhoof_behemoth",
            name="Craterhoof Behemoth",
            mana_cost=ManaCost(generic=5, green=3),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=5,
            toughness=5,
            keywords=["haste"],
            oracle_text="Haste. When Craterhoof Behemoth enters the battlefield, creatures you control gain trample and get +X/+X until end of turn, where X is the number of creatures you control."
        ),
        Card(
            id="consecrated_sphinx",
            name="Consecrated Sphinx",
            mana_cost=ManaCost(generic=4, blue=2),
            card_types=[CardType.CREATURE],
            colors=[Color.BLUE],
            power=4,
            toughness=6,
            keywords=["flying"],
            oracle_text="Flying. Whenever an opponent draws a card, you may draw two cards."
        ),
        Card(
            id="sun_titan",
            name="Sun Titan",
            mana_cost=ManaCost(generic=4, white=2),
            card_types=[CardType.CREATURE],
            colors=[Color.WHITE],
            power=6,
            toughness=6,
            keywords=["vigilance"],
            oracle_text="Vigilance. Whenever Sun Titan enters the battlefield or attacks, you may return target permanent card with mana value 3 or less from your graveyard to the battlefield."
        ),
        Card(
            id="inferno_titan",
            name="Inferno Titan",
            mana_cost=ManaCost(generic=4, red=2),
            card_types=[CardType.CREATURE],
            colors=[Color.RED],
            power=6,
            toughness=6,
            oracle_text="Inferno Titan deals 3 damage divided as you choose among one, two, or three targets whenever it enters the battlefield or attacks. {R}: Inferno Titan gets +1/+0 until end of turn."
        ),
        Card(
            id="primeval_titan",
            name="Primeval Titan",
            mana_cost=ManaCost(generic=4, green=2),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=6,
            toughness=6,
            keywords=["trample"],
            oracle_text="Trample. Whenever Primeval Titan enters the battlefield or attacks, you may search your library for up to two land cards, put them onto the battlefield tapped, then shuffle."
        ),
        Card(
            id="baleful_strix",
            name="Baleful Strix",
            mana_cost=ManaCost(blue=1, black=1),
            card_types=[CardType.ARTIFACT, CardType.CREATURE],
            colors=[Color.BLUE, Color.BLACK],
            power=1,
            toughness=1,
            keywords=["flying", "deathtouch"],
            oracle_text="Flying, deathtouch. When Baleful Strix enters the battlefield, draw a card.",
            triggered_abilities=[create_etb_draw_trigger(1)],
        ),
        Card(
            id="snapcaster_mage",
            name="Snapcaster Mage",
            mana_cost=ManaCost(generic=1, blue=1),
            card_types=[CardType.CREATURE],
            colors=[Color.BLUE],
            power=2,
            toughness=1,
            keywords=["flash"],
            oracle_text="Flash. When Snapcaster Mage enters the battlefield, target instant or sorcery card in your graveyard gains flashback until end of turn."
        ),
    ])
    
    # ===== MORE COUNTERSPELLS =====
    cards.extend([
        Card(
            id="swan_song",
            name="Swan Song",
            mana_cost=ManaCost(blue=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="Counter target enchantment, instant, or sorcery spell. Its controller creates a 2/2 blue Bird creature token with flying."
        ),
        Card(
            id="arcane_denial",
            name="Arcane Denial",
            mana_cost=ManaCost(generic=1, blue=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="Counter target spell. Its controller may draw up to two cards at the beginning of the next turn's upkeep. You draw a card at the beginning of the next turn's upkeep."
        ),
        Card(
            id="mana_drain",
            name="Mana Drain",
            mana_cost=ManaCost(blue=2),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="Counter target spell. At the beginning of your next main phase, add an amount of {C} equal to that spell's mana value."
        ),
        Card(
            id="force_of_will",
            name="Force of Will",
            mana_cost=ManaCost(generic=3, blue=2),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="You may pay 1 life and exile a blue card from your hand rather than pay this spell's mana cost. Counter target spell."
        ),
        Card(
            id="pact_of_negation",
            name="Pact of Negation",
            mana_cost=ManaCost(generic=0),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="Counter target spell. At the beginning of your next upkeep, pay {3}{U}{U}. If you don't, you lose the game."
        ),
        Card(
            id="mystical_dispute",
            name="Mystical Dispute",
            mana_cost=ManaCost(generic=2, blue=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="This spell costs {2} less to cast if it targets a blue spell. Counter target spell unless its controller pays {3}."
        ),
        Card(
            id="dovin_s_veto",
            name="Dovin's Veto",
            mana_cost=ManaCost(white=1, blue=1),
            card_types=[CardType.INSTANT],
            colors=[Color.WHITE, Color.BLUE],
            oracle_text="This spell can't be countered. Counter target noncreature spell."
        ),
    ])
    
    # ===== PROTECTION & COMBAT TRICKS =====
    cards.extend([
        Card(
            id="heroic_intervention",
            name="Heroic Intervention",
            mana_cost=ManaCost(generic=1, green=1),
            card_types=[CardType.INSTANT],
            colors=[Color.GREEN],
            oracle_text="Permanents you control gain hexproof and indestructible until end of turn."
        ),
        Card(
            id="teferi_s_protection",
            name="Teferi's Protection",
            mana_cost=ManaCost(generic=2, white=1),
            card_types=[CardType.INSTANT],
            colors=[Color.WHITE],
            oracle_text="Until your next turn, your life total can't change and you gain protection from everything. All permanents you control phase out."
        ),
        Card(
            id="boros_charm",
            name="Boros Charm",
            mana_cost=ManaCost(red=1, white=1),
            card_types=[CardType.INSTANT],
            colors=[Color.RED, Color.WHITE],
            oracle_text="Choose one: Boros Charm deals 4 damage to target player or planeswalker; or permanents you control gain indestructible until end of turn; or target creature gains double strike until end of turn."
        ),
        Card(
            id="flawless_maneuver",
            name="Flawless Maneuver",
            mana_cost=ManaCost(generic=2, white=1),
            card_types=[CardType.INSTANT],
            colors=[Color.WHITE],
            oracle_text="If you control a commander, you may cast this spell without paying its mana cost. Creatures you control gain indestructible until end of turn."
        ),
        Card(
            id="deflecting_swat",
            name="Deflecting Swat",
            mana_cost=ManaCost(generic=2, red=1),
            card_types=[CardType.INSTANT],
            colors=[Color.RED],
            oracle_text="If you control a commander, you may cast this spell without paying its mana cost. You may choose new targets for target spell or ability."
        ),
        Card(
            id="veil_of_summer",
            name="Veil of Summer",
            mana_cost=ManaCost(green=1),
            card_types=[CardType.INSTANT],
            colors=[Color.GREEN],
            oracle_text="Draw a card if an opponent cast a blue or black spell this turn. Spells you control can't be countered this turn. You and permanents you control gain hexproof from blue and from black until end of turn."
        ),
    ])
    
    # ===== TUTORS =====
    cards.extend([
        Card(
            id="demonic_tutor",
            name="Demonic Tutor",
            mana_cost=ManaCost(generic=1, black=1),
            card_types=[CardType.SORCERY],
            colors=[Color.BLACK],
            oracle_text="Search your library for a card, put it into your hand, then shuffle."
        ),
        Card(
            id="vampiric_tutor",
            name="Vampiric Tutor",
            mana_cost=ManaCost(black=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLACK],
            oracle_text="Search your library for a card, then shuffle and put that card on top. You lose 2 life."
        ),
        Card(
            id="enlightened_tutor",
            name="Enlightened Tutor",
            mana_cost=ManaCost(white=1),
            card_types=[CardType.INSTANT],
            colors=[Color.WHITE],
            oracle_text="Search your library for an artifact or enchantment card, reveal it, put it into your hand, then shuffle."
        ),
        Card(
            id="worldly_tutor",
            name="Worldly Tutor",
            mana_cost=ManaCost(green=1),
            card_types=[CardType.INSTANT],
            colors=[Color.GREEN],
            oracle_text="Search your library for a creature card, reveal it, put it on top of your library, then shuffle."
        ),
        Card(
            id="mystical_tutor",
            name="Mystical Tutor",
            mana_cost=ManaCost(blue=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="Search your library for an instant or sorcery card, reveal it, put it on top of your library, then shuffle."
        ),
        Card(
            id="chord_of_calling",
            name="Chord of Calling",
            mana_cost=ManaCost(generic=1, green=2),
            card_types=[CardType.INSTANT],
            colors=[Color.GREEN],
            oracle_text="Convoke. Search your library for a creature card with mana value X or less, put it onto the battlefield, then shuffle."
        ),
        Card(
            id="green_suns_zenith",
            name="Green Sun's Zenith",
            mana_cost=ManaCost(green=1),
            card_types=[CardType.SORCERY],
            colors=[Color.GREEN],
            oracle_text="Search your library for a green creature card with mana value X or less, put it onto the battlefield, then shuffle. Shuffle Green Sun's Zenith into its owner's library."
        ),
    ])
    
    # ===== COMBO PIECES & WIN CONDITIONS =====
    cards.extend([
        Card(
            id="thassas_oracle",
            name="Thassa's Oracle",
            mana_cost=ManaCost(generic=1, blue=1),
            card_types=[CardType.CREATURE],
            colors=[Color.BLUE],
            power=1,
            toughness=3,
            oracle_text="When Thassa's Oracle enters the battlefield, look at the top X cards of your library, where X is your devotion to blue. Put up to one of them on top and the rest on the bottom in a random order. If X is greater than or equal to the number of cards in your library, you win the game."
        ),
        Card(
            id="laboratory_maniac",
            name="Laboratory Maniac",
            mana_cost=ManaCost(generic=2, blue=1),
            card_types=[CardType.CREATURE],
            colors=[Color.BLUE],
            power=2,
            toughness=2,
            oracle_text="If you would draw a card while your library has no cards in it, you win the game instead."
        ),
        Card(
            id="aetherflux_reservoir",
            name="Aetherflux Reservoir",
            mana_cost=ManaCost(generic=4),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="Whenever you cast a spell, you gain 1 life for each spell you've cast this turn. Pay 50 life: Aetherflux Reservoir deals 50 damage to any target."
        ),
        Card(
            id="approach_of_the_second_sun",
            name="Approach of the Second Sun",
            mana_cost=ManaCost(generic=6, white=1),
            card_types=[CardType.SORCERY],
            colors=[Color.WHITE],
            oracle_text="If this spell was cast from your hand and you've cast another spell named Approach of the Second Sun this game, you win the game. Otherwise, put Approach of the Second Sun into its owner's library seventh from the top and you gain 7 life."
        ),
        Card(
            id="exsanguinate",
            name="Exsanguinate",
            mana_cost=ManaCost(generic=1, black=1),
            card_types=[CardType.SORCERY],
            colors=[Color.BLACK],
            oracle_text="Each opponent loses X life. You gain life equal to the life lost this way."
        ),
        Card(
            id="torment_of_hailfire",
            name="Torment of Hailfire",
            mana_cost=ManaCost(generic=1, black=1),
            card_types=[CardType.SORCERY],
            colors=[Color.BLACK],
            oracle_text="Repeat the following process X times. Each opponent loses 3 life unless that player sacrifices a nonland permanent or discards a card."
        ),
    ])
    
    # ===== MORE VALUE CREATURES =====
    cards.extend([
        Card(
            id="elvish_visionary",
            name="Elvish Visionary",
            mana_cost=ManaCost(generic=1, green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=1,
            toughness=1,
            oracle_text="When Elvish Visionary enters the battlefield, draw a card.",
            triggered_abilities=[create_etb_draw_trigger(1)],
        ),
        Card(
            id="skyscanner",
            name="Skyscanner",
            mana_cost=ManaCost(generic=3),
            card_types=[CardType.ARTIFACT, CardType.CREATURE],
            colors=[],
            power=1,
            toughness=1,
            keywords=["flying"],
            oracle_text="Flying. When Skyscanner enters the battlefield, draw a card.",
            triggered_abilities=[create_etb_draw_trigger(1)],
        ),
        Card(
            id="cloudkin_seer",
            name="Cloudkin Seer",
            mana_cost=ManaCost(generic=2, blue=1),
            card_types=[CardType.CREATURE],
            colors=[Color.BLUE],
            power=2,
            toughness=1,
            keywords=["flying"],
            oracle_text="Flying. When Cloudkin Seer enters the battlefield, draw a card.",
            triggered_abilities=[create_etb_draw_trigger(1)],
        ),
        Card(
            id="inspiring_overseer",
            name="Inspiring Overseer",
            mana_cost=ManaCost(generic=2, white=1),
            card_types=[CardType.CREATURE],
            colors=[Color.WHITE],
            power=2,
            toughness=1,
            keywords=["flying"],
            oracle_text="Flying. When Inspiring Overseer enters the battlefield, draw a card.",
            triggered_abilities=[create_etb_draw_trigger(1)],
        ),
        Card(
            id="priest_of_ancient_lore",
            name="Priest of Ancient Lore",
            mana_cost=ManaCost(generic=2, white=1),
            card_types=[CardType.CREATURE],
            colors=[Color.WHITE],
            power=2,
            toughness=1,
            oracle_text="When Priest of Ancient Lore enters the battlefield, draw a card.",
            triggered_abilities=[create_etb_draw_trigger(1)],
        ),
        Card(
            id="sakura_tribe_elder",
            name="Sakura-Tribe Elder",
            mana_cost=ManaCost(generic=1, green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=1,
            toughness=1,
            oracle_text="Sacrifice Sakura-Tribe Elder: Search your library for a basic land card, put it onto the battlefield tapped, then shuffle."
        ),
        Card(
            id="coiling_oracle",
            name="Coiling Oracle",
            mana_cost=ManaCost(green=1, blue=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN, Color.BLUE],
            power=1,
            toughness=1,
            oracle_text="When Coiling Oracle enters the battlefield, reveal the top card of your library. If it's a land card, put it onto the battlefield. Otherwise, put that card into your hand."
        ),
        Card(
            id="wall_of_blossoms",
            name="Wall of Blossoms",
            mana_cost=ManaCost(generic=1, green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=0,
            toughness=4,
            keywords=["defender"],
            oracle_text="Defender. When Wall of Blossoms enters the battlefield, draw a card.",
            triggered_abilities=[create_etb_draw_trigger(1)],
        ),
        Card(
            id="wall_of_omens",
            name="Wall of Omens",
            mana_cost=ManaCost(generic=1, white=1),
            card_types=[CardType.CREATURE],
            colors=[Color.WHITE],
            power=0,
            toughness=4,
            keywords=["defender"],
            oracle_text="Defender. When Wall of Omens enters the battlefield, draw a card.",
            triggered_abilities=[create_etb_draw_trigger(1)],
        ),
        Card(
            id="mesa_enchantress",
            name="Mesa Enchantress",
            mana_cost=ManaCost(generic=1, white=2),
            card_types=[CardType.CREATURE],
            colors=[Color.WHITE],
            power=0,
            toughness=2,
            oracle_text="Whenever you cast an enchantment spell, you may draw a card."
        ),
    ])
    
    # Dragons, Angels, and Big Threats
    cards.extend([
        Card(
            id="dragonlord_dromoka",
            name="Dragonlord Dromoka",
            mana_cost=ManaCost(generic=4, green=1, white=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN, Color.WHITE],
            power=5,
            toughness=7,
            keywords=["flying", "lifelink"],
            oracle_text="Flying, lifelink. Your opponents can't cast spells during your turn."
        ),
        Card(
            id="steel_hellkite",
            name="Steel Hellkite",
            mana_cost=ManaCost(generic=6),
            card_types=[CardType.ARTIFACT, CardType.CREATURE],
            colors=[],
            power=5,
            toughness=5,
            keywords=["flying"],
            oracle_text="Flying. {2}: Steel Hellkite gets +1/+0 until end of turn. {X}: Destroy each nonland permanent with mana value X whose controller was dealt combat damage by Steel Hellkite this turn."
        ),
        Card(
            id="utvara_hellkite",
            name="Utvara Hellkite",
            mana_cost=ManaCost(generic=6, red=2),
            card_types=[CardType.CREATURE],
            colors=[Color.RED],
            power=6,
            toughness=6,
            keywords=["flying"],
            oracle_text="Flying. Whenever a Dragon you control attacks, create a 6/6 red Dragon creature token with flying."
        ),
        Card(
            id="angel_of_serenity",
            name="Angel of Serenity",
            mana_cost=ManaCost(generic=4, white=3),
            card_types=[CardType.CREATURE],
            colors=[Color.WHITE],
            power=5,
            toughness=6,
            keywords=["flying"],
            oracle_text="Flying. When Angel of Serenity enters the battlefield, you may exile up to three other target creatures from the battlefield and/or creature cards from graveyards."
        ),
        Card(
            id="baneslayer_angel",
            name="Baneslayer Angel",
            mana_cost=ManaCost(generic=3, white=2),
            card_types=[CardType.CREATURE],
            colors=[Color.WHITE],
            power=5,
            toughness=5,
            keywords=["flying", "first strike", "lifelink"],
            oracle_text="Flying, first strike, lifelink, protection from Demons and from Dragons"
        ),
        Card(
            id="wurmcoil_engine",
            name="Wurmcoil Engine",
            mana_cost=ManaCost(generic=6),
            card_types=[CardType.ARTIFACT, CardType.CREATURE],
            colors=[],
            power=6,
            toughness=6,
            keywords=["deathtouch", "lifelink"],
            oracle_text="Deathtouch, lifelink. When Wurmcoil Engine dies, create a 3/3 colorless Phyrexian Wurm artifact creature token with deathtouch and a 3/3 colorless Phyrexian Wurm artifact creature token with lifelink."
        ),
    ])
    
    # More Utility Creatures
    cards.extend([
        Card(
            id="trophy_mage",
            name="Trophy Mage",
            mana_cost=ManaCost(generic=2, blue=1),
            card_types=[CardType.CREATURE],
            colors=[Color.BLUE],
            power=2,
            toughness=2,
            oracle_text="When Trophy Mage enters the battlefield, you may search your library for an artifact card with mana value 3, reveal it, put it into your hand, then shuffle."
        ),
        Card(
            id="trinket_mage",
            name="Trinket Mage",
            mana_cost=ManaCost(generic=2, blue=1),
            card_types=[CardType.CREATURE],
            colors=[Color.BLUE],
            power=2,
            toughness=2,
            oracle_text="When Trinket Mage enters the battlefield, you may search your library for an artifact card with mana value 1 or less, reveal it, put it into your hand, then shuffle."
        ),
        Card(
            id="acidic_ooze",
            name="Scavenging Ooze",
            mana_cost=ManaCost(generic=1, green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=2,
            toughness=2,
            oracle_text="{G}: Exile target card from a graveyard. If it was a creature card, put a +1/+1 counter on Scavenging Ooze and you gain 1 life."
        ),
        Card(
            id="spellseeker",
            name="Spellseeker",
            mana_cost=ManaCost(generic=2, blue=1),
            card_types=[CardType.CREATURE],
            colors=[Color.BLUE],
            power=1,
            toughness=1,
            oracle_text="When Spellseeker enters the battlefield, you may search your library for an instant or sorcery card with mana value 2 or less, reveal it, put it into your hand, then shuffle."
        ),
        Card(
            id="imperial_recruiter",
            name="Imperial Recruiter",
            mana_cost=ManaCost(generic=2, red=1),
            card_types=[CardType.CREATURE],
            colors=[Color.RED],
            power=1,
            toughness=1,
            oracle_text="When Imperial Recruiter enters the battlefield, search your library for a creature card with power 2 or less, reveal it, put it into your hand, then shuffle."
        ),
        Card(
            id="goblin_matron",
            name="Goblin Matron",
            mana_cost=ManaCost(generic=2, red=1),
            card_types=[CardType.CREATURE],
            colors=[Color.RED],
            power=1,
            toughness=1,
            oracle_text="When Goblin Matron enters the battlefield, you may search your library for a Goblin card, reveal it, put it into your hand, then shuffle."
        ),
    ])
    
    # ===== UTILITY LANDS =====
    cards.extend([
        Card(
            id="command_tower",
            name="Command Tower",
            card_types=[CardType.LAND],
            colors=[],
            oracle_text="T: Add one mana of any color in your commander's color identity."
        ),
        Card(
            id="reliquary_tower",
            name="Reliquary Tower",
            card_types=[CardType.LAND],
            colors=[],
            oracle_text="You have no maximum hand size. T: Add {C}."
        ),
        Card(
            id="rogue_s_passage",
            name="Rogue's Passage",
            card_types=[CardType.LAND],
            colors=[],
            oracle_text="T: Add {C}. {4}, T: Target creature can't be blocked this turn."
        ),
        Card(
            id="temple_of_the_false_god",
            name="Temple of the False God",
            card_types=[CardType.LAND],
            colors=[],
            oracle_text="T: Add {C}{C}. Activate only if you control five or more lands."
        ),
        Card(
            id="bojuka_bog",
            name="Bojuka Bog",
            card_types=[CardType.LAND],
            colors=[],
            oracle_text="Bojuka Bog enters the battlefield tapped. When Bojuka Bog enters the battlefield, exile target player's graveyard. T: Add {B}."
        ),
        Card(
            id="strip_mine",
            name="Strip Mine",
            card_types=[CardType.LAND],
            colors=[],
            oracle_text="T: Add {C}. T, Sacrifice Strip Mine: Destroy target land."
        ),
        Card(
            id="wasteland",
            name="Wasteland",
            card_types=[CardType.LAND],
            colors=[],
            oracle_text="T: Add {C}. T, Sacrifice Wasteland: Destroy target nonbasic land."
        ),
    ])
    
    # ===== ENCHANTMENTS & EQUIPMENT =====
    cards.extend([
        Card(
            id="smothering_tithe",
            name="Smothering Tithe",
            mana_cost=ManaCost(generic=3, white=1),
            card_types=[CardType.ENCHANTMENT],
            colors=[Color.WHITE],
            oracle_text="Whenever an opponent draws a card, that player may pay {2}. If the player doesn't, you create a Treasure token."
        ),
        Card(
            id="sylvan_library",
            name="Sylvan Library",
            mana_cost=ManaCost(generic=1, green=1),
            card_types=[CardType.ENCHANTMENT],
            colors=[Color.GREEN],
            oracle_text="At the beginning of your draw step, you may draw two additional cards. If you do, choose two cards in your hand drawn this turn. For each of those cards, pay 4 life or put the card on top of your library."
        ),
        Card(
            id="mystic_remora",
            name="Mystic Remora",
            mana_cost=ManaCost(blue=1),
            card_types=[CardType.ENCHANTMENT],
            colors=[Color.BLUE],
            oracle_text="Cumulative upkeep {1}. Whenever an opponent casts a noncreature spell, you may draw a card unless that player pays {4}."
        ),
        Card(
            id="animate_dead",
            name="Animate Dead",
            mana_cost=ManaCost(generic=1, black=1),
            card_types=[CardType.ENCHANTMENT],
            colors=[Color.BLACK],
            oracle_text="When Animate Dead enters the battlefield, if it's on the battlefield, it loses 'enchant creature card in a graveyard' and gains 'enchant creature put onto the battlefield with Animate Dead.' Return enchanted creature card to the battlefield under your control and attach Animate Dead to it. When Animate Dead leaves the battlefield, that creature's controller sacrifices it."
        ),
        Card(
            id="lightning_greaves",
            name="Lightning Greaves",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="Equipped creature has haste and shroud. Equip {0}"
        ),
        Card(
            id="swiftfoot_boots",
            name="Swiftfoot Boots",
            mana_cost=ManaCost(generic=2),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="Equipped creature has hexproof and haste. Equip {1}"
        ),
        Card(
            id="sword_of_feast_and_famine",
            name="Sword of Feast and Famine",
            mana_cost=ManaCost(generic=3),
            card_types=[CardType.ARTIFACT],
            colors=[],
            oracle_text="Equipped creature gets +2/+2 and has protection from black and from green. Whenever equipped creature deals combat damage to a player, that player discards a card and you untap all lands you control. Equip {2}"
        ),
    ])
    
    # ===== MORE STAPLES & COMMONS =====
    cards.extend([
        # More Creatures
        Card(
            id="knight_of_the_reliquary",
            name="Knight of the Reliquary",
            mana_cost=ManaCost(generic=1, green=1, white=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN, Color.WHITE],
            power=2,
            toughness=2,
            oracle_text="Knight of the Reliquary gets +1/+1 for each land card in your graveyard. {T}, Sacrifice a Forest or Plains: Search your library for a land card, put it onto the battlefield, then shuffle."
        ),
        Card(
            id="oracle_of_mul_daya",
            name="Oracle of Mul Daya",
            mana_cost=ManaCost(generic=3, green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=2,
            toughness=2,
            oracle_text="You may play an additional land on each of your turns. Play with the top card of your library revealed. You may play lands from the top of your library."
        ),
        Card(
            id="azusa_lost_but_seeking",
            name="Azusa, Lost but Seeking",
            mana_cost=ManaCost(generic=2, green=1),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=1,
            toughness=2,
            oracle_text="You may play two additional lands on each of your turns."
        ),
        Card(
            id="courser_of_kruphix",
            name="Courser of Kruphix",
            mana_cost=ManaCost(generic=1, green=2),
            card_types=[CardType.CREATURE],
            colors=[Color.GREEN],
            power=2,
            toughness=4,
            oracle_text="Play with the top card of your library revealed. You may play lands from the top of your library. Whenever a land enters the battlefield under your control, you gain 1 life."
        ),
        Card(
            id="fierce_guardianship",
            name="Fierce Guardianship",
            mana_cost=ManaCost(generic=2, blue=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="If you control a commander, you may cast this spell without paying its mana cost. Counter target noncreature spell."
        ),
        Card(
            id="deadly_rollick",
            name="Deadly Rollick",
            mana_cost=ManaCost(generic=3, black=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLACK],
            oracle_text="If you control a commander, you may cast this spell without paying its mana cost. Exile target creature."
        ),
        # More Removal
        Card(
            id="krosan_grip",
            name="Krosan Grip",
            mana_cost=ManaCost(generic=2, green=1),
            card_types=[CardType.INSTANT],
            colors=[Color.GREEN],
            oracle_text="Split second. Destroy target artifact or enchantment."
        ),
        Card(
            id="abrupt_decay",
            name="Abrupt Decay",
            mana_cost=ManaCost(black=1, green=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLACK, Color.GREEN],
            oracle_text="This spell can't be countered. Destroy target nonland permanent with mana value 3 or less."
        ),
        Card(
            id="putrefy",
            name="Putrefy",
            mana_cost=ManaCost(generic=1, black=1, green=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLACK, Color.GREEN],
            oracle_text="Destroy target artifact or creature. It can't be regenerated."
        ),
        # More Draw
        Card(
            id="fact_or_fiction",
            name="Fact or Fiction",
            mana_cost=ManaCost(generic=3, blue=1),
            card_types=[CardType.INSTANT],
            colors=[Color.BLUE],
            oracle_text="Reveal the top five cards of your library. An opponent separates those cards into two piles. Put one pile into your hand and the other into your graveyard."
        ),
        Card(
            id="jeska_s_will",
            name="Jeska's Will",
            mana_cost=ManaCost(generic=2, red=1),
            card_types=[CardType.SORCERY],
            colors=[Color.RED],
            oracle_text="Choose one. If you control a commander as you cast this spell, you may choose both: Add {R} for each card in target opponent's hand. Exile the top three cards of your library. You may play them this turn."
        ),
        Card(
            id="wheel_of_fortune",
            name="Wheel of Fortune",
            mana_cost=ManaCost(generic=2, red=1),
            card_types=[CardType.SORCERY],
            colors=[Color.RED],
            oracle_text="Each player discards their hand, then draws seven cards."
        ),
        Card(
            id="windfall",
            name="Windfall",
            mana_cost=ManaCost(generic=2, blue=1),
            card_types=[CardType.SORCERY],
            colors=[Color.BLUE],
            oracle_text="Each player discards their hand, then draws cards equal to the greatest number of cards a player discarded this way."
        ),
        # Utility
        Card(
            id="gilded_drake",
            name="Gilded Drake",
            mana_cost=ManaCost(generic=1, blue=1),
            card_types=[CardType.CREATURE],
            colors=[Color.BLUE],
            power=3,
            toughness=3,
            keywords=["flying"],
            oracle_text="Flying. When Gilded Drake enters the battlefield, exchange control of Gilded Drake and up to one target creature an opponent controls."
        ),
        Card(
            id="duplicant",
            name="Duplicant",
            mana_cost=ManaCost(generic=6),
            card_types=[CardType.ARTIFACT, CardType.CREATURE],
            colors=[],
            power=2,
            toughness=4,
            oracle_text="Imprint — When Duplicant enters the battlefield, you may exile target nontoken creature. As long as a card exiled with Duplicant is a creature card, Duplicant has the power, toughness, and creature types of the last creature card exiled with Duplicant."
        ),
        Card(
            id="meteor_golem",
            name="Meteor Golem",
            mana_cost=ManaCost(generic=7),
            card_types=[CardType.ARTIFACT, CardType.CREATURE],
            colors=[],
            power=3,
            toughness=3,
            oracle_text="When Meteor Golem enters the battlefield, destroy target nonland permanent."
        ),
    ])
    
    return {card.id: card for card in cards}


def create_ramp_deck(commander_card: Optional[Card] = None):
    """Create a green ramp deck with acceleration, card draw, and big threats."""
    cards = create_basic_cards()
    deck = []
    
    if commander_card:
        deck.append(commander_card)
    
    # Lands (36) - Ramp-heavy mana base
    for _ in range(25):
        deck.append(cards["forest_1"])
    for _ in range(5):
        deck.append(cards["plains_1"])
    for _ in range(3):
        deck.append(cards["island_1"])
    deck.append(cards["command_tower"])
    deck.append(cards["reliquary_tower"])
    deck.append(cards["temple_of_the_false_god"])
    
    # Ramp (15) - Mana acceleration
    deck.append(cards["sol_ring"])
    deck.append(cards["arcane_signet"])
    deck.append(cards["cultivate"])
    deck.append(cards["kodamas_reach"])
    deck.append(cards["rampant_growth"])
    deck.append(cards["natures_lore"])
    deck.append(cards["three_visits"])
    deck.append(cards["farseek"])
    deck.append(cards["explosive_vegetation"])
    deck.append(cards["skyshroud_claim"])
    deck.append(cards["llanowar_elves"])
    deck.append(cards["elvish_mystic"])
    deck.append(cards["fyndhorn_elves"])
    deck.append(cards["birds_of_paradise"])
    deck.append(cards["avacyns_pilgrim"])
    
    # Card Draw (8)
    deck.append(cards["harmonize"])
    deck.append(cards["rhystic_study"])
    deck.append(cards["sylvan_library"])
    deck.append(cards["mulldrifter"])
    deck.append(cards["solemn_simulacrum"])
    deck.append(cards["wall_of_blossoms"])
    deck.append(cards["consecrated_sphinx"])
    deck.append(cards["esper_sentinel"])
    
    # Creatures (20) - Value and threats
    deck.append(cards["wood_elves"])
    deck.append(cards["eternal_witness"])
    deck.append(cards["reclamation_sage"])
    deck.append(cards["acidic_slime"])
    deck.append(cards["avenger_of_zendikar"])
    deck.append(cards["craterhoof_behemoth"])
    deck.append(cards["sun_titan"])
    deck.append(cards["primeval_titan"])
    deck.append(cards["knight_of_the_reliquary"])
    deck.append(cards["oracle_of_mul_daya"])
    deck.append(cards["azusa_lost_but_seeking"])
    deck.append(cards["courser_of_kruphix"])
    deck.append(cards["dragonlord_dromoka"])
    deck.append(cards["steel_hellkite"])
    deck.append(cards["serra_angel"])
    deck.append(cards["wurmcoil_engine"])
    deck.append(cards["baleful_strix"])
    deck.append(cards["snapcaster_mage"])
    deck.append(cards["acidic_ooze"])
    deck.append(cards["spellseeker"])
    
    # Removal (10)
    deck.append(cards["swords_to_plowshares"])
    deck.append(cards["path_to_exile"])
    deck.append(cards["beast_within"])
    deck.append(cards["generous_gift"])
    deck.append(cards["krosan_grip"])
    deck.append(cards["natures_claim"])
    deck.append(cards["cyclonic_rift"])
    deck.append(cards["wrath_of_god"])
    deck.append(cards["return_to_dust"])
    deck.append(cards["abrupt_decay"])
    
    # Protection & Interaction (6)
    deck.append(cards["heroic_intervention"])
    deck.append(cards["teferi_s_protection"])
    deck.append(cards["counterspell"])
    deck.append(cards["swan_song"])
    deck.append(cards["arcane_denial"])
    deck.append(cards["fierce_guardianship"])
    
    # Tutors & Win Cons (4)
    deck.append(cards["worldly_tutor"])
    deck.append(cards["mystical_tutor"])
    deck.append(cards["green_suns_zenith"])
    deck.append(cards["chord_of_calling"])
    
    return deck


def create_control_deck(commander_card: Optional[Card] = None):
    """Create a blue/white control deck with counters, removal, and card draw."""
    cards = create_basic_cards()
    deck = []
    
    if commander_card:
        deck.append(commander_card)
    
    # Lands (37) - Control needs consistent mana
    for _ in range(15):
        deck.append(cards["island_1"])
    for _ in range(15):
        deck.append(cards["plains_1"])
    for _ in range(3):
        deck.append(cards["mountain_1"])
    deck.append(cards["command_tower"])
    deck.append(cards["reliquary_tower"])
    deck.append(cards["temple_of_the_false_god"])
    deck.append(cards["bojuka_bog"])
    
    # Mana Rocks (8)
    deck.append(cards["sol_ring"])
    deck.append(cards["arcane_signet"])
    deck.append(cards["azorius_signet"])
    deck.append(cards["commander_sphere"])
    deck.append(cards["mind_stone"])
    deck.append(cards["fellwar_stone"])
    deck.append(cards["thought_vessel"])
    deck.append(cards["talisman_of_progress"])
    
    # Card Draw (12) - Control needs cards
    deck.append(cards["rhystic_study"])
    deck.append(cards["esper_sentinel"])
    deck.append(cards["consecrated_sphinx"])
    deck.append(cards["mulldrifter"])
    deck.append(cards["blue_suns_zenith"])
    deck.append(cards["stroke_of_genius"])
    deck.append(cards["fact_or_fiction"])
    deck.append(cards["solemn_simulacrum"])
    deck.append(cards["baleful_strix"])
    deck.append(cards["snapcaster_mage"])
    deck.append(cards["wall_of_omens"])
    deck.append(cards["smothering_tithe"])
    
    # Counterspells (10)
    deck.append(cards["counterspell"])
    deck.append(cards["swan_song"])
    deck.append(cards["arcane_denial"])
    deck.append(cards["mana_drain"])
    deck.append(cards["force_of_will"])
    deck.append(cards["pact_of_negation"])
    deck.append(cards["mystical_dispute"])
    deck.append(cards["dovin_s_veto"])
    deck.append(cards["negate"])
    deck.append(cards["fierce_guardianship"])
    
    # Removal (14)
    deck.append(cards["swords_to_plowshares"])
    deck.append(cards["path_to_exile"])
    deck.append(cards["generous_gift"])
    deck.append(cards["anguished_unmaking"])
    deck.append(cards["vindicate"])
    deck.append(cards["return_to_dust"])
    deck.append(cards["cyclonic_rift"])
    deck.append(cards["wrath_of_god"])
    deck.append(cards["damnation"])
    deck.append(cards["toxic_deluge"])
    deck.append(cards["blasphemous_act"])
    deck.append(cards["chaos_warp"])
    deck.append(cards["terminate"])
    deck.append(cards["deflecting_swat"])
    
    # Win Conditions (8)
    deck.append(cards["sun_titan"])
    deck.append(cards["inferno_titan"])
    deck.append(cards["serra_angel"])
    deck.append(cards["thassas_oracle"])
    deck.append(cards["approach_of_the_second_sun"])
    deck.append(cards["aetherflux_reservoir"])
    deck.append(cards["exsanguinate"])
    deck.append(cards["torment_of_hailfire"])
    
    # Tutors & Utility (10)
    deck.append(cards["enlightened_tutor"])
    deck.append(cards["mystical_tutor"])
    deck.append(cards["vampiric_tutor"])
    deck.append(cards["demonic_tutor"])
    deck.append(cards["teferi_s_protection"])
    deck.append(cards["boros_charm"])
    deck.append(cards["flawless_maneuver"])
    deck.append(cards["lightning_greaves"])
    deck.append(cards["swiftfoot_boots"])
    deck.append(cards["gilded_drake"])
    
    return deck


def create_midrange_deck(commander_card: Optional[Card] = None):
    """Create a balanced midrange deck with creatures, removal, and value."""
    cards = create_basic_cards()
    deck = []
    
    if commander_card:
        deck.append(commander_card)
    
    # Lands (36)
    for _ in range(12):
        deck.append(cards["forest_1"])
    for _ in range(10):
        deck.append(cards["swamp_1"])
    for _ in range(8):
        deck.append(cards["plains_1"])
    for _ in range(3):
        deck.append(cards["mountain_1"])
    deck.append(cards["command_tower"])
    deck.append(cards["reliquary_tower"])
    deck.append(cards["bojuka_bog"])
    
    # Mana Acceleration (10)
    deck.append(cards["sol_ring"])
    deck.append(cards["arcane_signet"])
    deck.append(cards["selesnya_signet"])
    deck.append(cards["gruul_signet"])
    deck.append(cards["talisman_of_unity"])
    deck.append(cards["llanowar_elves"])
    deck.append(cards["birds_of_paradise"])
    deck.append(cards["cultivate"])
    deck.append(cards["rampant_growth"])
    deck.append(cards["farseek"])
    
    # Creatures (25) - Midrange creature base
    deck.append(cards["wood_elves"])
    deck.append(cards["eternal_witness"])
    deck.append(cards["reclamation_sage"])
    deck.append(cards["solemn_simulacrum"])
    deck.append(cards["acidic_slime"])
    deck.append(cards["mulldrifter"])
    deck.append(cards["baleful_strix"])
    deck.append(cards["snapcaster_mage"])
    deck.append(cards["acidic_ooze"])
    deck.append(cards["sun_titan"])
    deck.append(cards["primeval_titan"])
    deck.append(cards["avenger_of_zendikar"])
    deck.append(cards["serra_angel"])
    deck.append(cards["shivan_dragon"])
    deck.append(cards["grizzly_bears"])
    deck.append(cards["knight_of_the_reliquary"])
    deck.append(cards["oracle_of_mul_daya"])
    deck.append(cards["courser_of_kruphix"])
    deck.append(cards["wurmcoil_engine"])
    deck.append(cards["trophy_mage"])
    deck.append(cards["duplicant"])
    deck.append(cards["meteor_golem"])
    deck.append(cards["wall_of_blossoms"])
    deck.append(cards["wall_of_omens"])
    deck.append(cards["esper_sentinel"])
    
    # Removal (12)
    deck.append(cards["swords_to_plowshares"])
    deck.append(cards["path_to_exile"])
    deck.append(cards["beast_within"])
    deck.append(cards["assassins_trophy"])
    deck.append(cards["abrupt_decay"])
    deck.append(cards["putrefy"])
    deck.append(cards["murder"])
    deck.append(cards["terminate"])
    deck.append(cards["chaos_warp"])
    deck.append(cards["wrath_of_god"])
    deck.append(cards["blasphemous_act"])
    deck.append(cards["cyclonic_rift"])
    
    # Card Draw (6)
    deck.append(cards["harmonize"])
    deck.append(cards["nights_whisper"])
    deck.append(cards["sign_in_blood"])
    deck.append(cards["phyrexian_arena"])
    deck.append(cards["rhystic_study"])
    deck.append(cards["sylvan_library"])
    
    # Interaction (6)
    deck.append(cards["counterspell"])
    deck.append(cards["swan_song"])
    deck.append(cards["heroic_intervention"])
    deck.append(cards["teferi_s_protection"])
    deck.append(cards["boros_charm"])
    deck.append(cards["natures_claim"])
    
    # Tutors & Utility (4)
    deck.append(cards["demonic_tutor"])
    deck.append(cards["worldly_tutor"])
    deck.append(cards["lightning_greaves"])
    deck.append(cards["swiftfoot_boots"])
    
    return deck


def create_simple_deck(commander_card: Optional[Card] = None, archetype: str = "midrange"):
    """
    Create a 100-card Commander deck based on archetype.
    
    Args:
        commander_card: Optional commander card
        archetype: Deck archetype - "ramp", "control", or "midrange" (default)
    
    Returns:
        List of Card objects (100 cards total including commander)
    """
    if archetype == "ramp":
        return create_ramp_deck(commander_card)
    elif archetype == "control":
        return create_control_deck(commander_card)
    else:  # midrange or default
        return create_midrange_deck(commander_card)
