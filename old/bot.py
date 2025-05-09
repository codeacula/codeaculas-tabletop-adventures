import random
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import unicodedata
import json # For an internal method to demonstrate JSON string export/import
import os

class DnDBot:
    """
    DnDBot provides utility methods for running a Dungeons & Dragons 5e campaign.
    Features include dice rolling, initiative tracking, HP and status effect management,
    in-game time tracking, and campaign state persistence.
    """

    def __init__(self):
        """
        Initializes the DnDBot with an empty state.
        """
        self.initiative_order: List[Dict[str, Any]] = []  # List of combatant dicts
        self.current_turn_idx: int = 0  # Index in initiative_order
        self.combat_round: int = 0

        # In-game time
        self.game_time: Dict[str, int] = {
            "year": 1491, # Default starting year in FR
            "day": 1,
            "hour": 12, # Noon
            "minute": 0
        }
        # Standard D&D dice
        self.allowed_dice = {4, 6, 8, 10, 12, 20, 100}

    # --- Dice Rolling ---
    def _roll_individual_dice(self, num: int, die: int) -> List[int]:
        """Helper to roll individual dice."""
        return [random.randint(1, die) for _ in range(num)]

    def roll(self, dice_str: str, advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """
        Rolls dice in NdM[+/-X] format (e.g., '2d6+3', '1d20-1').
        Supports advantage and disadvantage for d20 rolls.
        Only standard D&D dice (d4, d6, d8, d10, d12, d20, d100) are allowed.

        Args:
            dice_str (str): Dice string in NdM[+/-X] format.
            advantage (bool): If true, roll 2d20 and take the higher for the primary die.
            disadvantage (bool): If true, roll 2d20 and take the lower for the primary die.

        Returns:
            Dict[str, Any]: Dictionary with 'rolls', 'modifier', 'total', 'final_d20_roll' (if applicable),
                            or 'error' if invalid.
        """
        dice_str = dice_str.replace(' ', '').lower()
        match = re.fullmatch(r"(\d*)d(\d+)([+-]\d+)?", dice_str)
        if not match:
            return {"error": "Invalid dice format. Expected NdM[+/-X] (e.g., '2d6+3', 'd20-1')."}

        num_str, die_str, mod_str = match.groups()
        num = int(num_str) if num_str else 1
        die = int(die_str)
        mod = int(mod_str) if mod_str else 0

        if die not in self.allowed_dice:
            return {"error": f"Invalid die size. Allowed dice: {sorted(list(self.allowed_dice))}"}
        if advantage and disadvantage:
            return {"error": "Cannot roll with both advantage and disadvantage."}

        rolls = []
        final_d20_roll = None

        if die == 20 and num == 1 and (advantage or disadvantage):
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            if advantage:
                final_d20_roll = max(roll1, roll2)
            else: # disadvantage
                final_d20_roll = min(roll1, roll2)
            rolls = [final_d20_roll] # The chosen d20 roll
            # Store original rolls for transparency
            result = {
                "rolls": rolls,
                "modifier": mod,
                "total": final_d20_roll + mod,
                "d20_outcomes": sorted([roll1, roll2]),
                "final_d20_roll": final_d20_roll,
                "type": "advantage" if advantage else "disadvantage"
            }
            return result
        elif die == 20 and num > 1 and (advantage or disadvantage):
            return {"error": "Advantage/disadvantage typically applies to a single d20 roll, not multiple d20s in one command like '2d20'."}


        rolls = self._roll_individual_dice(num, die)
        total = sum(rolls) + mod
        return {"rolls": rolls, "modifier": mod, "total": total}

    # --- Initiative and Combat ---
    def add_combatant(self, name: str, initiative: int, max_hp: int, current_hp: Optional[int] = None, npc: bool = False, player_controlled: bool = False) -> bool:
        """
        Adds a combatant to the initiative order. Re-sorts the order.
        Args:
            name (str): Name of the combatant.
            initiative (int): Initiative score.
            max_hp (int): Maximum hit points.
            current_hp (Optional[int]): Current HP. Defaults to max_hp.
            npc (bool): True if this combatant is an NPC.
            player_controlled (bool): True if this is a player character or an NPC directly controlled by a player.
        Returns:
            bool: True if successful, False if combatant name already exists.
        """
        if any(c["name"] == name for c in self.initiative_order):
            return False # Name already exists

        combatant = {
            "name": name,
            "initiative": initiative,
            "max_hp": max_hp,
            "current_hp": current_hp if current_hp is not None else max_hp,
            "status_effects": [], # List of {"name": str, "duration_rounds": Optional[int], "notes": str}
            "npc": npc,
            "player_controlled": player_controlled,
        }
        self.initiative_order.append(combatant)
        self.initiative_order.sort(key=lambda x: x["initiative"], reverse=True)
        # If this is the first combatant, set turn and round
        if len(self.initiative_order) == 1:
            self.current_turn_idx = 0
            self.combat_round = 1 
        return True

    def remove_combatant(self, name: str) -> bool:
        """
        Removes a combatant from the initiative order by name.
        Adjusts current_turn_idx if necessary.
        Returns:
            bool: True if successful, False if combatant not found.
        """
        original_len = len(self.initiative_order)
        if original_len == 0:
            return False

        idx_to_remove = -1
        for i, c in enumerate(self.initiative_order):
            if c["name"] == name:
                idx_to_remove = i
                break
        
        if idx_to_remove == -1:
            return False # Not found

        self.initiative_order.pop(idx_to_remove)

        if not self.initiative_order: # List became empty
            self.current_turn_idx = 0
            self.combat_round = 0 # Reset combat round
            return True

        # Adjust current_turn_idx
        if idx_to_remove < self.current_turn_idx:
            self.current_turn_idx -= 1
        elif idx_to_remove == self.current_turn_idx:
            # If the current combatant was removed, the index now effectively points to the next one,
            # or is out of bounds if it was the last one.
            # We ensure it's within bounds for the next `next_turn` call.
            if self.current_turn_idx >= len(self.initiative_order):
                self.current_turn_idx = 0 # Wrap around for the next `next_turn` call which will advance it
                # This also means a round likely passed if we were at the end.
                # However, round increment is handled by next_turn.
        
        # Ensure current_turn_idx is always valid
        if self.current_turn_idx < 0: # Should not happen with above logic but as a safeguard
            self.current_turn_idx = 0
        if self.current_turn_idx >= len(self.initiative_order): # If it was last and list shrunk
            self.current_turn_idx = 0

        return True

    def next_turn(self) -> Optional[str]:
        """
        Advances to the next combatant. Increments round if it cycles.
        Returns:
            Optional[str]: Name of the next combatant, or None if no combatants.
        """
        if not self.initiative_order:
            return None
        
        self.current_turn_idx = (self.current_turn_idx + 1)
        if self.current_turn_idx >= len(self.initiative_order):
            self.current_turn_idx = 0
            self.combat_round += 1
            # Tick down status effect durations
            for combatant in self.initiative_order:
                active_effects = []
                for effect in combatant.get("status_effects", []):
                    if effect.get("duration_rounds") is not None:
                        effect["duration_rounds"] -= 1
                        if effect["duration_rounds"] > 0:
                            active_effects.append(effect)
                    else: # Permanent or indefinite until removed
                        active_effects.append(effect)
                combatant["status_effects"] = active_effects
        
        return self.initiative_order[self.current_turn_idx]["name"]

    def get_initiative_order_details(self) -> List[Dict[str, Any]]:
        """Returns the full details of combatants in initiative order."""
        return self.initiative_order

    def get_current_combatant_details(self) -> Optional[Dict[str, Any]]:
        """Returns the details of the current combatant."""
        if self.initiative_order:
            return self.initiative_order[self.current_turn_idx]
        return None

    def get_combatant(self, name: str) -> Optional[Dict[str, Any]]:
        """Gets details for a specific combatant by name."""
        for c in self.initiative_order:
            if c["name"] == name:
                return c
        return None

    # --- HP Management ---
    def _modify_hp(self, name: str, amount: int) -> Optional[Dict[str, Any]]:
        """Helper to modify HP, ensuring it stays within 0 and max_hp."""
        combatant = self.get_combatant(name)
        if not combatant:
            return None
        
        combatant["current_hp"] = max(0, min(combatant["max_hp"], combatant["current_hp"] + amount))
        return combatant

    def deal_damage(self, name: str, damage: int) -> Optional[Dict[str, Any]]:
        """Deals damage to a combatant."""
        if damage < 0: damage = 0 # Damage cannot be negative
        return self._modify_hp(name, -damage)

    def heal(self, name: str, healing: int) -> Optional[Dict[str, Any]]:
        """Heals a combatant."""
        if healing < 0: healing = 0 # Healing cannot be negative
        return self._modify_hp(name, healing)

    def set_hp(self, name: str, hp: int, set_max_too: bool = False) -> Optional[Dict[str, Any]]:
        """Sets current HP. Optionally also sets max_hp."""
        combatant = self.get_combatant(name)
        if not combatant:
            return None
        
        if set_max_too:
            combatant["max_hp"] = max(0,hp) # Max HP shouldn't be negative
        combatant["current_hp"] = max(0, min(combatant["max_hp"], hp))
        return combatant
    
    def set_max_hp(self, name: str, max_hp: int, adjust_current_hp: bool = True) -> Optional[Dict[str, Any]]:
        """Sets max HP for a combatant. Optionally adjusts current HP to match if it exceeds new max."""
        combatant = self.get_combatant(name)
        if not combatant:
            return None
        combatant["max_hp"] = max(0, max_hp) # Max HP shouldn't be negative
        if adjust_current_hp:
            combatant["current_hp"] = min(combatant["current_hp"], combatant["max_hp"])
        return combatant


    # --- Status Effects ---
    def add_status_effect(self, name: str, effect_name: str, duration_rounds: Optional[int] = None, notes: str = "") -> bool:
        """Adds a status effect to a combatant."""
        combatant = self.get_combatant(name)
        if not combatant:
            return False
        # Avoid duplicate effects by name; could be extended to allow stacking with different rules
        if any(e["name"] == effect_name for e in combatant["status_effects"]):
            # Optionally, refresh duration here if desired, or just return False/True
            return True # Or False if strict no duplicates allowed
            
        combatant["status_effects"].append({
            "name": effect_name,
            "duration_rounds": duration_rounds,
            "notes": notes,
            "applied_round": self.combat_round 
        })
        return True

    def remove_status_effect(self, name: str, effect_name: str) -> bool:
        """Removes a status effect from a combatant."""
        combatant = self.get_combatant(name)
        if not combatant:
            return False
        
        initial_len = len(combatant["status_effects"])
        combatant["status_effects"] = [e for e in combatant["status_effects"] if e["name"] != effect_name]
        return len(combatant["status_effects"]) < initial_len

    # --- In-Game Time ---
    def get_in_game_datetime_str(self) -> str:
        """Returns the current in-game date and time as a string."""
        gt = self.game_time
        return f"Year {gt['year']}, Day {gt['day']}, {gt['hour']:02d}:{gt['minute']:02d}"

    def advance_time(self, years: int = 0, days: int = 0, hours: int = 0, minutes: int = 0) -> None:
        """Advances the in-game time."""
        # Rough calculation, assumes 30 days/month, 365 days/year for simplicity.
        # D&D calendars can be more complex (e.g., Harptos). This is a basic version.
        self.game_time["minute"] += minutes
        self.game_time["hour"] += self.game_time["minute"] // 60
        self.game_time["minute"] %= 60

        self.game_time["hour"] += hours
        self.game_time["day"] += self.game_time["hour"] // 24
        self.game_time["hour"] %= 24

        self.game_time["day"] += days
        # Simple year progression
        self.game_time["year"] += self.game_time["day"] // 365 # Approximation
        self.game_time["day"] = (self.game_time["day"] -1) % 365 + 1 # Keep day between 1-365

        self.game_time["year"] += years

    # --- State Persistence (for GPT interaction) ---
    def get_full_state(self) -> Dict[str, Any]:
        """
        Returns the entire current state of the bot as a dictionary.
        This can be serialized to JSON by the calling application (e.g., the GPT).
        """
        return {
            "initiative_order": self.initiative_order,
            "current_turn_idx": self.current_turn_idx,
            "combat_round": self.combat_round,
            "game_time": self.game_time,
        }

    def load_full_state(self, state: Dict[str, Any]) -> bool:
        """
        Loads the bot's state from a dictionary (e.g., from a deserialized JSON).
        Returns:
            bool: True if loading was successful (basic check), False otherwise.
        """
        try:
            self.initiative_order = state.get("initiative_order", [])
            self.current_turn_idx = state.get("current_turn_idx", 0)
            self.combat_round = state.get("combat_round", 0)
            self.game_time = state.get("game_time", {"year": 1491, "day": 1, "hour": 12, "minute": 0})
            
            # Basic validation
            if not isinstance(self.initiative_order, list) or \
               not isinstance(self.current_turn_idx, int) or \
               not isinstance(self.combat_round, int) or \
               not isinstance(self.game_time, dict):
                raise ValueError("Invalid state structure.")

            # Further ensure current_turn_idx is valid for the loaded initiative_order
            if self.initiative_order and self.current_turn_idx >= len(self.initiative_order):
                self.current_turn_idx = 0
            elif not self.initiative_order:
                 self.current_turn_idx = 0


        except Exception as e:
            print(f"Error loading state: {e}") # Or log this appropriately
            # Optionally, reset to a default state or re-raise
            self.__init__() # Reset to default if loading fails critically
            return False
        return True

    # --- Utility Functions (from original script) ---
    def get_current_real_datetime(self) -> str:
        """Returns the current real-world date and time."""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_ascii(self, text: str) -> str:
        """Converts UTF-8 to ASCII, ignoring/replacing non-ASCII characters."""
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

    def clean_filename(self, text: str) -> str:
        """Cleans a string to make it safe for use as a filename."""
        text = self.to_ascii(text) # First, convert to ASCII to handle unicode better
        text = text.replace(' ', '_')
        return re.sub(r'[^A-Za-z0-9._-]', '', text)

    # --- Local File/Folder Helpers ---
    def ensure_base_folder(self) -> str:
        """Ensures the 'ChatGPT Table Top' folder exists locally. Returns its path."""
        base_folder = os.path.join(os.getcwd(), "ChatGPT Table Top")
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)
        return base_folder

    def create_campaign_folders(self, campaign_name: str) -> str:
        """Creates a campaign folder with /state/, /lore/, and /archive/ subfolders. Returns campaign path."""
        base_folder = self.ensure_base_folder()
        campaign_path = os.path.join(base_folder, campaign_name)
        for sub in ["state", "lore", "archive"]:
            os.makedirs(os.path.join(campaign_path, sub), exist_ok=True)
        return campaign_path

    def save_json(self, file_path: str, data: Dict[str, Any]) -> bool:
        """Saves a dictionary as a minified JSON file. Returns True if successful."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, separators=(",", ":"))
            return True
        except Exception as e:
            print(f"Error saving JSON to {file_path}: {e}")
            return False

    def load_json(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Loads a JSON file and returns its contents as a dictionary, or None if error."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON from {file_path}: {e}")
            return None

    def validate_character_name(self, name: str, existing_names: List[str]) -> bool:
        """Ensures the character name is unique and valid (alphanumeric, not empty, not already used)."""
        if not name or not name.strip():
            return False
        if name in existing_names:
            return False
        # Only allow letters, numbers, spaces, dashes, and underscores
        if not re.match(r'^[A-Za-z0-9 _-]+$', name):
            return False
        return True

    def archive_session(self, campaign_name: str, session_data: Dict[str, Any]) -> bool:
        """Archives the current session data into the /archive/ folder. Returns True if successful."""
        campaign_path = self.create_campaign_folders(campaign_name)
        archive_path = os.path.join(campaign_path, "archive")
        # Find next available session number
        existing = [f for f in os.listdir(archive_path) if f.startswith("session_") and f.endswith(".json")]
        session_nums = [int(f.split("_")[1].split(".")[0]) for f in existing if f.split("_")[1].split(".")[0].isdigit()]
        next_num = max(session_nums, default=0) + 1
        archive_file = os.path.join(archive_path, f"session_{next_num}.json")
        return self.save_json(archive_file, session_data)

    def reset_live_session(self, campaign_name: str) -> bool:
        """Resets the live session file for the campaign (empties or recreates session_live.json)."""
        campaign_path = self.create_campaign_folders(campaign_name)
        state_path = os.path.join(campaign_path, "state", "session_live.json")
        try:
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return True
        except Exception as e:
            print(f"Error resetting live session: {e}")
            return False

    def fail_soft_narration(self, message: str) -> None:
        """Prints or logs a fail-soft message (e.g., 'the record crystal flickers')."""
        print(f"the record crystal flickers: {message}")

    def retry_operation(self, operation, *args, **kwargs) -> bool:
        """Retries a failed operation once. Returns True if successful, False otherwise."""
        try:
            operation(*args, **kwargs)
            return True
        except Exception as e:
            self.fail_soft_narration(str(e))
            return False