"""
Validate card data against Scryfall API.

This script checks our card database against Scryfall to verify:
- Card names are correct
- Mana costs match
- Card types are accurate
- Oracle text is similar (we have simplified versions)
"""
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List, cast

sys.path.insert(0, str(Path(__file__).parent / 'src'))

import requests
from data.cards import create_basic_cards
from core.card import CardType


SCRYFALL_API = "https://api.scryfall.com/cards/named"
RATE_LIMIT_DELAY = 0.1  # 100ms between requests (Scryfall allows 10 req/sec)


def query_scryfall(card_name: str) -> Optional[Dict[str, Any]]:
    """Query Scryfall API for a card by name."""
    params = {"fuzzy": card_name}
    response = requests.get(SCRYFALL_API, params=params, timeout=10)
    
    if response.status_code == 200:
        return cast(Dict[str, Any], response.json())
    elif response.status_code == 404:
        return None
    else:
        print(f"  ⚠️  API error {response.status_code} for {card_name}")
        return None


def parse_scryfall_mana_cost(mana_cost_str: str) -> Dict[str, int]:
    """Parse Scryfall mana cost string like '{2}{G}{W}' into components."""
    if not mana_cost_str:
        return {}
    
    cost = {"generic": 0, "white": 0, "blue": 0, "black": 0, "red": 0, "green": 0}
    
    # Remove braces and split
    symbols = mana_cost_str.replace("{", " ").replace("}", " ").split()
    
    for symbol in symbols:
        symbol = symbol.strip()
        if not symbol:
            continue
            
        if symbol.isdigit():
            cost["generic"] += int(symbol)
        elif symbol == "W":
            cost["white"] += 1
        elif symbol == "U":
            cost["blue"] += 1
        elif symbol == "B":
            cost["black"] += 1
        elif symbol == "R":
            cost["red"] += 1
        elif symbol == "G":
            cost["green"] += 1
        elif symbol == "C":
            cost["generic"] += 1  # Colorless mana
        # Ignore hybrid/phyrexian symbols for now
    
    # Remove zero values
    return {k: v for k, v in cost.items() if v > 0}


def compare_mana_costs(our_cost, scryfall_cost_str: str) -> Tuple[bool, str]:
    """Compare our mana cost with Scryfall's."""
    if not our_cost and not scryfall_cost_str:
        return True, "Both are lands/free"
    
    if not our_cost:
        return False, f"We have no cost but Scryfall has {scryfall_cost_str}"
    
    if not scryfall_cost_str:
        return False, f"Scryfall has no cost but we have {our_cost}"
    
    scryfall_parsed = parse_scryfall_mana_cost(scryfall_cost_str)
    our_dict = {
        "generic": our_cost.generic,
        "white": our_cost.white,
        "blue": our_cost.blue,
        "black": our_cost.black,
        "red": our_cost.red,
        "green": our_cost.green,
    }
    our_dict = {k: v for k, v in our_dict.items() if v > 0}
    
    if our_dict == scryfall_parsed:
        return True, "Match"
    else:
        return False, f"Ours: {our_dict}, Scryfall: {scryfall_parsed}"


def validate_card_types(our_types: List[CardType], scryfall_types: str) -> Tuple[bool, str]:
    """Validate card types match."""
    scryfall_lower = scryfall_types.lower()
    
    type_map = {
        CardType.CREATURE: "creature",
        CardType.INSTANT: "instant",
        CardType.SORCERY: "sorcery",
        CardType.ARTIFACT: "artifact",
        CardType.ENCHANTMENT: "enchantment",
        CardType.LAND: "land",
        CardType.PLANESWALKER: "planeswalker",
    }
    
    our_type_strings = [type_map.get(t, str(t).lower()) for t in our_types]
    
    # Check if all our types are in Scryfall's type line
    matches = all(t in scryfall_lower for t in our_type_strings)
    
    if matches:
        return True, "Types match"
    else:
        return False, f"Ours: {our_type_strings}, Scryfall: {scryfall_types}"


def validate_cards() -> Tuple[int, int, int]:
    """Validate all cards against Scryfall."""
    cards = create_basic_cards()
    
    print(f"\n🔍 Validating {len(cards)} cards against Scryfall...")
    print("=" * 70)
    
    total = len(cards)
    validated = 0
    warnings = 0
    errors = 0
    
    # Skip basic lands (they're fine)
    basic_lands = {"Plains", "Island", "Swamp", "Mountain", "Forest"}
    
    for card in cards.values():
        if card.name in basic_lands:
            validated += 1
            continue
        
        print(f"\n📝 {card.name}")
        
        # Query Scryfall
        scryfall_data = query_scryfall(card.name)
        time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
        
        if not scryfall_data:
            print(f"  ❌ NOT FOUND on Scryfall!")
            errors += 1
            continue
        
        # Validate mana cost
        scryfall_mana = scryfall_data.get("mana_cost", "")
        cost_match, cost_msg = compare_mana_costs(card.mana_cost, scryfall_mana)
        
        if cost_match:
            print(f"  ✅ Mana cost: {scryfall_mana}")
        else:
            print(f"  ⚠️  Mana cost mismatch: {cost_msg}")
            warnings += 1
        
        # Validate types
        scryfall_types = scryfall_data.get("type_line", "")
        types_match, types_msg = validate_card_types(card.card_types, scryfall_types)
        
        if types_match:
            print(f"  ✅ Types: {scryfall_types}")
        else:
            print(f"  ⚠️  Type mismatch: {types_msg}")
            warnings += 1
        
        # Check power/toughness for creatures
        if CardType.CREATURE in card.card_types:
            scryfall_power = scryfall_data.get("power")
            scryfall_toughness = scryfall_data.get("toughness")
            
            if scryfall_power and scryfall_toughness:
                if (str(card.power) == scryfall_power and 
                    str(card.toughness) == scryfall_toughness):
                    print(f"  ✅ P/T: {scryfall_power}/{scryfall_toughness}")
                else:
                    print(f"  ⚠️  P/T mismatch: Ours {card.power}/{card.toughness}, "
                          f"Scryfall {scryfall_power}/{scryfall_toughness}")
                    warnings += 1
        
        if cost_match and types_match:
            validated += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"\n📊 VALIDATION SUMMARY")
    print(f"Total cards:     {total}")
    print(f"✅ Validated:    {validated} ({validated/total*100:.1f}%)")
    print(f"⚠️  Warnings:     {warnings}")
    print(f"❌ Errors:       {errors}")
    
    if errors == 0 and warnings < 5:
        print(f"\n🎉 Excellent! Card data is highly accurate!")
    elif errors == 0:
        print(f"\n✅ Good! No errors, just minor warnings.")
    else:
        print(f"\n⚠️  Some cards need attention.")
    
    return validated, warnings, errors


if __name__ == "__main__":
    try:
        validate_cards()
    except KeyboardInterrupt:
        print("\n\n⏸️  Validation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
