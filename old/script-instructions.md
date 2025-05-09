# DnDBot Python Script: Usage Guide for Custom GPT

You have access to a Python helper script, `DnDBot`, which manages the mechanics of a Dungeons & Dragons game. You will interact with an *instance* of this `DnDBot` class. Remember that this bot is stateful, meaning changes made in one call (like adding a combatant or dealing damage) persist for subsequent calls within the same session or loaded state.

**Note:** These instructions refer to the enhanced version of `DnDBot` that includes HP and status effect tracking, in-game time, and state persistence methods (`get_full_state`, `load_full_state`).

## Super Important First Thing: The Bot Has Memory (State)

1. When the game starts, or you load a saved game, an instance of `DnDBot` is created or restored.
2. Everything you tell it to do (add a player, deal damage, whose turn it is) is remembered *by that specific bot instance* for the current session.
3. **To save the game across sessions:** You'll ask the bot for its entire current memory (we call this its "state"), and then you'll use your Google Drive helper functions (like `create_json` from your `drive_helpers.py` script) to save this state.
4. **To load a game:** You'll use your Drive helpers to load the saved state, then tell the bot to load this state into its memory.

## Core DnDBot Actions

First, ensure an instance of the bot is ready. Let's assume your Python environment makes an instance named `dnd_session_bot` available to your actions.

*(Conceptual initialization in Python environment)*

```python
# This happens on your end, Custom GPT, when a game session begins.
# from dnd_bot_module import DnDBot # Assuming the class is in dnd_bot_module.py
# dnd_session_bot = DnDBot()
# Or, if loading a game, you'd load its state right after creating it.
```

---

### 1. Dice Rolling

**Action: `dnd_session_bot.roll`**

* **Description:** Rolls dice based on standard D&D notation (e.g., "2d6+3"). Can also handle advantage or disadvantage for single d20 rolls.
* **Parameters:**
  * `dice_str` (string): The dice to roll, like "1d20", "3d6+4", "1d10-1".
  * `advantage` (boolean, optional, default: `False`): Set to `True` if the roll is made with advantage (only applies if `dice_str` is a single d20, like "1d20" or "1d20+5").
  * `disadvantage` (boolean, optional, default: `False`): Set to `True` if the roll is made with disadvantage (similar conditions to advantage).
* **Returns:**
  * **On Success:** A dictionary with details.
    * For standard rolls: `{"rolls": [list_of_individual_die_results], "modifier": integer_modifier, "total": integer_total_result}`
    * For d20 advantage/disadvantage: `{"rolls": [chosen_d20_roll], "modifier": integer_modifier, "total": integer_total_result, "d20_outcomes": [list_of_the_two_d20_rolls], "final_d20_roll": chosen_d20_roll, "type": "advantage" or "disadvantage"}`
  * **On Error:** `{"error": "description_of_error"}` (e.g., invalid dice string, rolling with both advantage and disadvantage).
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    result = dnd_session_bot.roll(dice_str="2d8+3")
    result = dnd_session_bot.roll(dice_str="1d20", advantage=True)
    result = dnd_session_bot.roll(dice_str="1d20-2", disadvantage=True)
    ```

---

### 2. Combat Management (Initiative)

**Action: `dnd_session_bot.add_combatant`**

* **Description:** Adds a participant (player character, monster, NPC) to the combat encounter. The initiative order is automatically sorted from highest to lowest initiative. If it's the first combatant added, the combat round will be set to 1.
* **Parameters:**
  * `name` (string): Unique name for the combatant.
  * `initiative` (integer): The combatant's rolled initiative score.
  * `max_hp` (integer): The combatant's maximum hit points.
  * `current_hp` (integer, optional): Current HP. If not provided, defaults to `max_hp`.
  * `npc` (boolean, optional, default: `False`): Set to `True` if this is a non-player character.
  * `player_controlled` (boolean, optional, default: `False`): Set to `True` if this combatant is a player character or an NPC actively controlled by a player.
* **Returns:**
  * `True` if the combatant was added successfully.
  * `False` if a combatant with that name already exists in the current initiative order.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    dnd_session_bot.add_combatant(name="Player1_Arin", initiative=18, max_hp=35, player_controlled=True)
    dnd_session_bot.add_combatant(name="Goblin_A", initiative=12, max_hp=7, npc=True)
    ```

**Action: `dnd_session_bot.remove_combatant`**

* **Description:** Removes a combatant from the initiative order (e.g., if they are defeated or flee).
* **Parameters:**
  * `name` (string): The name of the combatant to remove.
* **Returns:**
  * `True` if successful.
  * `False` if the combatant was not found.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    dnd_session_bot.remove_combatant(name="Goblin_A")
    ```

**Action: `dnd_session_bot.next_turn`**

* **Description:** Advances to the next combatant in the initiative order. If it cycles through all combatants, the combat round number increases by 1, and status effect durations are ticked down.
* **Returns:**
  * The `name` (string) of the combatant whose turn it is now.
  * `None` if there are no combatants in the initiative order.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    current_player_name = dnd_session_bot.next_turn()
    ```

**Action: `dnd_session_bot.get_initiative_order_details`**

* **Description:** Gets the current list of all combatants in their initiative order, along with their full details.
* **Returns:**
  * A list of dictionaries. Each dictionary represents a combatant and contains their `name`, `initiative`, `current_hp`, `max_hp`, `status_effects`, `npc`, `player_controlled`.
  * Example: `[{"name": "Arin", "initiative": 18, ...}, {"name": "Goblin_B", "initiative": 10, ...}]`
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    order_list = dnd_session_bot.get_initiative_order_details()
    ```

**Action: `dnd_session_bot.get_current_combatant_details`**

* **Description:** Gets the full details of the combatant whose turn it currently is.
* **Returns:**
  * A dictionary containing the current combatant's details (same structure as elements in `get_initiative_order_details`).
  * `None` if combat is not active or no combatants exist.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    active_combatant = dnd_session_bot.get_current_combatant_details()
    # if active_combatant: print(f"It's {active_combatant['name']}'s turn!")
    ```

**Action: `dnd_session_bot.get_combatant`**

* **Description:** Retrieves the details of a specific combatant by their name, whether it's their turn or not.
* **Parameters:**
  * `name` (string): The name of the combatant.
* **Returns:**
  * A dictionary with the combatant's details if found.
  * `None` if not found.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    goblin_stats = dnd_session_bot.get_combatant(name="Goblin_C")
    ```

---

### 3. HP Management

**Action: `dnd_session_bot.deal_damage`**

* **Description:** Reduces a combatant's `current_hp`. HP cannot go below 0.
* **Parameters:**
  * `name` (string): Name of the target combatant.
  * `damage` (integer): Amount of damage to deal (should be non-negative).
* **Returns:**
  * The updated combatant dictionary if found (includes new HP).
  * `None` if combatant not found.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    updated_goblin = dnd_session_bot.deal_damage(name="Goblin_B", damage=5)
    # if updated_goblin and updated_goblin['current_hp'] == 0: print(f"{updated_goblin['name']} is down!")
    ```

**Action: `dnd_session_bot.heal`**

* **Description:** Increases a combatant's `current_hp`. HP cannot exceed `max_hp`.
* **Parameters:**
  * `name` (string): Name of the target combatant.
  * `healing` (integer): Amount of HP to restore (should be non-negative).
* **Returns:**
  * The updated combatant dictionary if found (includes new HP).
  * `None` if combatant not found.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    dnd_session_bot.heal(name="Player1_Arin", healing=10)
    ```

**Action: `dnd_session_bot.set_hp`**

* **Description:** Directly sets a combatant's `current_hp`. Can also set `max_hp` at the same time.
* **Parameters:**
  * `name` (string): Name of the combatant.
  * `hp` (integer): The value to set `current_hp` to (clamped between 0 and `max_hp`).
  * `set_max_too` (boolean, optional, default: `False`): If `True`, also sets `max_hp` to the `hp` value.
* **Returns:**
  * The updated combatant dictionary if found.
  * `None` if combatant not found.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    dnd_session_bot.set_hp(name="Player1_Arin", hp=15)
    dnd_session_bot.set_hp(name="BigBoss", hp=100, set_max_too=True)
    ```

**Action: `dnd_session_bot.set_max_hp`**

* **Description:** Sets the maximum HP for a combatant. Can optionally adjust current HP if it exceeds the new maximum.
* **Parameters:**
  * `name` (string): Name of the combatant.
  * `max_hp` (integer): The new maximum HP value.
  * `adjust_current_hp` (boolean, optional, default: `True`): If `True` and current HP is greater than the new `max_hp`, current HP is set to the new `max_hp`.
* **Returns:**
  * The updated combatant dictionary if found.
  * `None` if combatant not found.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    dnd_session_bot.set_max_hp(name="Player1_Arin", max_hp=40)
    ```

---

### 4. Status Effect Management

**Action: `dnd_session_bot.add_status_effect`**

* **Description:** Adds a status effect (e.g., "Poisoned", "Blinded") to a combatant.
* **Parameters:**
  * `name` (string): Name of the target combatant.
  * `effect_name` (string): Name of the status effect (e.g., "Poisoned").
  * `duration_rounds` (integer, optional): How many rounds the effect lasts. If `None`, it's indefinite until removed manually. Decremented at the end of each full combat round (via `next_turn`).
  * `notes` (string, optional): Any additional notes about this specific instance of the effect.
* **Returns:**
  * `True` if successful.
  * `False` if combatant not found.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    dnd_session_bot.add_status_effect(name="Goblin_C", effect_name="Frightened", duration_rounds=3, notes="Frightened by Arin's roar")
    dnd_session_bot.add_status_effect(name="Player1_Arin", effect_name="Blessed")
    ```

**Action: `dnd_session_bot.remove_status_effect`**

* **Description:** Removes a specific status effect from a combatant.
* **Parameters:**
  * `name` (string): Name of the target combatant.
  * `effect_name` (string): Name of the status effect to remove.
* **Returns:**
  * `True` if the effect was found and removed.
  * `False` if combatant not found or effect not present on the combatant.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    dnd_session_bot.remove_status_effect(name="Goblin_C", effect_name="Frightened")
    ```

---

### 5. In-Game Time Management

**Action: `dnd_session_bot.get_in_game_datetime_str`**

* **Description:** Returns the current in-game date and time as a formatted string.
* **Returns:**
  * A string, e.g., "Year 1491, Day 1, 12:00".
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    current_time_str = dnd_session_bot.get_in_game_datetime_str()
    ```

**Action: `dnd_session_bot.advance_time`**

* **Description:** Moves the in-game clock forward by the specified amount. (Note: Day/year progression is simplified).
* **Parameters:**
  * `years` (integer, optional, default: 0)
  * `days` (integer, optional, default: 0)
  * `hours` (integer, optional, default: 0)
  * `minutes` (integer, optional, default: 0)
* **Returns:**
  * None. (This action modifies the bot's internal state).
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    dnd_session_bot.advance_time(days=1, hours=6)
    # After a long rest
    dnd_session_bot.advance_time(hours=8)
    ```

---

### 6. State Persistence (Crucial for Saving/Loading Games!)

**Action: `dnd_session_bot.get_full_state`**

* **Description:** This is how you get the bot's entire memory! It returns a dictionary containing everything the bot is currently tracking (initiative order with all combatant details, current turn index, combat round number, and in-game time).
* **Returns:**
  * A dictionary representing the bot's complete current state.
* **Example Usage by GPT (Conceptual Workflow):**
    1. Call `bot_memory_dict = dnd_session_bot.get_full_state()`.
    2. Take `bot_memory_dict` and use your Google Drive helper (like `create_json` or `patch_json` from your `drive_helpers.py` script) to save this dictionary as a JSON file to Google Drive (e.g., `save_to_drive("my_campaign_active_state.json", bot_memory_dict)`).

**Action: `dnd_session_bot.load_full_state`**

* **Description:** This is how you restore the bot's memory from a previously saved state. You'll provide a dictionary (which you would have loaded from a JSON file from Google Drive).
* **Parameters:**
  * `state` (dictionary): A dictionary matching the structure provided by `get_full_state`.
* **Returns:**
  * `True` if the state was loaded successfully (basic validation passed).
  * `False` if there was an error loading the state (e.g., invalid structure), in which case the bot might reset to a default initial state.
* **Example Usage by GPT (Conceptual Workflow):**
    1. Use your Google Drive helper (like `load_json` from `drive_helpers.py`) to load the saved state from a JSON file into a dictionary (e.g., `loaded_state_dict = load_from_drive("my_campaign_active_state.json")`).
    2. Call `success = dnd_session_bot.load_full_state(state=loaded_state_dict)`.
    3. Respond based on `success` value: `if success: print("Game state loaded!") else: print("Failed to load game state.")`.

---

### 7. Utility Functions

**Action: `dnd_session_bot.get_current_real_datetime`**

* **Description:** Gets the current *real-world* date and time (not the in-game time).
* **Returns:**
  * A string in 'YYYY-MM-DD HH:MM:SS' format.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    real_timestamp = dnd_session_bot.get_current_real_datetime()
    ```

**Action: `dnd_session_bot.to_ascii`**

* **Description:** Converts a string with potentially non-ASCII characters (like fancy quotes or accents) into a plain ASCII string. Useful for sanitizing input or before creating filenames.
* **Parameters:**
  * `text` (string): The input string.
* **Returns:**
  * An ASCII-only version of the string.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    ascii_name = dnd_session_bot.to_ascii(text="Voilà le Café") # Expected result: "Voila le Cafe"
    ```

**Action: `dnd_session_bot.clean_filename`**

* **Description:** Takes any string and makes it safe to use as a filename (replaces spaces with underscores, removes most special characters, converts to ASCII).
* **Parameters:**
  * `text` (string): The string to clean.
* **Returns:**
  * A cleaned, filename-safe string.
* **Example Usage by GPT (Conceptual Python Call):**

    ```python
    safe_name = dnd_session_bot.clean_filename(text="My Awesome D&D Session! Part 1") # Expected result: "My_Awesome_DD_Session_Part_1"
    ```
