# Codeacula's Tabletop Adventures – Product Specification

## Overview

**Product Name:** Codeacula's Tabletop Adventures
**Repository:** [codeacula/codeaculas-tabletop-adventures](https://github.com/codeacula/codeaculas-tabletop-adventures)
**Purpose:** A CustomGPT-powered Dungeons & Dragons assistant that can guide users through game setup, character creation, and active session management, with Discord integration, in-browser visual aids, and local game state logic via SQLite.

**GPT Persona Name:** Nyrae
**Persona Description:** Nyrae is a witty and unflinching digital Dungeon Mistress. She guides players with sharp clarity and playful provocation, balancing strict adherence to the rules with dynamic improvisation when story demands. She avoids coddling, encourages curiosity, and values player agency. Her voice is feminine, direct, and a touch theatrical — like a stage performer with dice behind her eyes. She supports mature themes when users opt in, including NSFW content within private sessions, but this capability is never advertised or prompted publicly.

## MVP Feature Set

### 1. Character Creation Mode

* **Purpose:** Walk a player through a complete D\&D 5e character creation process.
* **Details:**

  * Guided prompts to choose race, class, background, stats, and equipment
  * Enforces RAW (Rules As Written) with fallback to story overrides if allowed
  * Saves final character sheet to a designated Google Drive folder (e.g., `/characters/{player_name}_{date}.json`)
  * Associates characters with Discord handles when known, allowing reuse across campaigns

### 2. Campaign Setup Mode

* **Purpose:** Help a Dungeon Master define campaign details
* **Details:**

  * Asks for setting, theme, session zero topics, house rules
  * Creates a folder structure on Google Drive (e.g., `/campaigns/{campaign_name}/`)
  * Generates initial documents: `overview.md`, `npcs.json`, `world_notes.md`
  * Tracks which characters (by Discord handle or name) are involved in the campaign

### 3. Session Management Mode

* **Purpose:** Assist the DM during active sessions
* **Details:**

  * Reads Discord channel user list to infer active players
  * Handles initiative tracking and combat order
  * Manages NPC actions and narrates scenes when prompted
  * Records session summaries, logs rolls, and stores state to `/campaigns/{campaign_name}/sessions/session_{n}.json`
  * Uses the Discord API to list channels in the server, allowing the user to confirm which channel maps to which campaign context. GPT can guide this selection or infer based on activity patterns.

### 4. Google Drive Integration

* **Purpose:** Store and organize campaign and character data
* **Details:**

  * Reads and writes JSON or Markdown files
  * Enforces structured naming and folder hierarchy
  * Requires user authentication to access their Drive securely

### 5. Discord Integration

* **Purpose:** Enhance session experience and track players dynamically
* **Details:**

  * Lists users in channels and links them to characters
  * Supports multiple campaign channels
  * Planned slash command extensions for runtime interaction

### 6. SQLite Game State Engine

* **Purpose:** Support local rule lookup and persistent game state
* **Details:**

  * Custom-uploaded SQLite database used for content and logic queries
  * Python scripts handle in-GPT data parsing and interaction
  * Expected to be updated with Open5e and user content

### 7. Visual Aids and Initiative Tracker

* **Purpose:** Provide UI-based game management for DMs and players
* **Details:**

  * In-browser view (optional) for turn order, character sheets, and session status
  * Syncs state from GPT or campaign files stored in Google Drive

## Stretch Features (Post-MVP)

* Slash commands to retrieve character stats or trigger scene prompts
* Companion web UI for easier DM tools access
* KV database for storing ephemeral player state
* Open5e JSON parser or conversion script to populate SQLite database with official D\&D rules/content
* Support for character portability across campaigns and persistent character data
* GPT-driven generation of combat encounters, NPC interactions, and story events based on active session and player context

## Technical Stack (Planned)

* **CustomGPT Actions** to interface with Google Drive and Discord (via secure proxy server)
* **GitHub Repo** as public documentation and hosting source for CustomGPT manifest, persona, schema definitions
* **External Node.js Server** to handle Discord webhooks and forward to GPT API (future)
* **Open5e API / SRD Content** for rules and mechanics
* **Python Environment** in CustomGPT for interacting with uploaded SQLite databases to manage game data dynamically

## Notes

* Ensure all user data stored externally complies with Google and Discord data policies
* Consider later migration to a full backend once usage expands
* Aim for transparency: All capabilities and actions clearly documented in-repo
* NSFW support is opt-in only and handled respectfully, never advertised or enabled by default
* Player data is separate from campaign/session data to allow for reusable characters and cross-campaign continuity
* Campaign context selection via Discord channel detection ensures proper association across parallel games

---

## Next Steps

* [ ] Create CustomGPT manifest with scoped Actions for Google Drive
* [ ] Build first script to write JSON character sheet to Drive
* [ ] Draft sample interaction logs for each mode
* [ ] Prepare Discord bot invite link and basic webhook relay stub
* [ ] Define SQLite schema for rules and game state support
* [ ] Write parser or converter for Open5e JSON into SQLite
* [ ] Update OpenAPI spec with Discord endpoints for message reading, channel listing, and member detection
* [ ] Prototype in-browser initiative tracker UI

---

## License & Contributions

MIT License. Open to community contributions after MVP.

---

## Maintainer

Codeacula
