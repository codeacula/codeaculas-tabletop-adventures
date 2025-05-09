"""
Open5e API Client
A Python client for accessing the Open5e API based on the OpenAPI schema.
"""
import requests
from typing import Dict, List, Optional, Union, Any, TypeVar
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("open5e_client")

# Type aliases for clearer typing
T = TypeVar('T')
JSONDict = Dict[str, Any]
JSONList = List[JSONDict]
JSONResponse = Union[JSONDict, JSONList]

class Open5eClient:
    """Client for accessing the Open5e API."""
    
    BASE_URL = "https://api.open5e.com"
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the Open5e API client.
        
        Args:
            base_url: Optional override for the API base URL
        """
        self.base_url = base_url or self.BASE_URL
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str, params: Optional[JSONDict] = None) -> JSONDict:
        """
        Make a GET request to the API.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters to include
            
        Returns:
            JSON response as a dictionary
            
        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def _is_paginated_response(self, response: JSONResponse) -> bool:
        """
        Check if a response is a paginated response.
        
        Args:
            response: The API response
            
        Returns:
            True if the response is paginated
        """
        return isinstance(response, dict) and "results" in response
    
    def _paginate_results(self, endpoint: str, params: Optional[JSONDict] = None) -> List[JSONDict]:
        """
        Fetch all pages of results for a paginated endpoint.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters to include
            
        Returns:
            List of all results from all pages
        """
        all_results = []
        params = params or {}
        
        # Get first page
        response = self._make_request(endpoint, params)
        
        if "results" in response:
            all_results.extend(response["results"])
            
            # Continue fetching pages if there are more
            while response.get("next"):
                # Parse the 'next' URL to get the page parameter
                next_url = response["next"]
                if "page=" in next_url:
                    page_num = int(next_url.split("page=")[1].split("&")[0])
                    params["page"] = page_num
                    response = self._make_request(endpoint, params)
                    all_results.extend(response["results"])
                else:
                    break
            
            return all_results
        else:
            # Not a paginated response
            return [response]
    
    # ============== API ENDPOINTS ==============
      # === ABILITIES ===
    def get_abilities(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """
        Get a list of abilities.
        
        Args:
            params: Query parameters for filtering
            paginate: If True, fetch all pages
            
        Returns:
            List of abilities or paginated response
        """
        endpoint = "/v2/abilities/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_ability(self, key: str) -> JSONDict:
        """
        Get a specific ability by key.
        
        Args:
            key: The ability key
            
        Returns:
            Ability details
        """
        endpoint = f"/v2/abilities/{key}/"
        return self._make_request(endpoint)
    
    # === ALIGNMENTS ===
    def get_alignments(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of alignments."""
        endpoint = "/v2/alignments/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_alignment(self, key: str) -> JSONDict:
        """Get a specific alignment by key."""
        endpoint = f"/v2/alignments/{key}/"
        return self._make_request(endpoint)
    
    # === ARMOR ===
    def get_armor(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of armor."""
        endpoint = "/v2/armor/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_armor_item(self, key: str) -> JSONDict:
        """Get a specific armor by key."""
        endpoint = f"/v2/armor/{key}/"
        return self._make_request(endpoint)
    
    # === BACKGROUNDS ===
    def get_backgrounds(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of backgrounds."""
        endpoint = "/v2/backgrounds/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_background(self, key: str) -> JSONDict:
        """Get a specific background by key."""
        endpoint = f"/v2/backgrounds/{key}/"
        return self._make_request(endpoint)
    
    # === CLASSES ===
    def get_classes(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of classes."""
        endpoint = "/v2/classes/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_class(self, key: str) -> JSONDict:
        """Get a specific class by key."""
        endpoint = f"/v2/classes/{key}/"
        return self._make_request(endpoint)
    
    # === CONDITIONS ===
    def get_conditions(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of conditions."""
        endpoint = "/v2/conditions/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_condition(self, key: str) -> JSONDict:
        """Get a specific condition by key."""
        endpoint = f"/v2/conditions/{key}/"
        return self._make_request(endpoint)
    
    # === CREATURES ===
    def get_creatures(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of creatures (monsters)."""
        endpoint = "/v2/creatures/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_creature(self, key: str) -> JSONDict:
        """Get a specific creature by key."""
        endpoint = f"/v2/creatures/{key}/"
        return self._make_request(endpoint)
    
    # === CREATURE SETS ===
    def get_creature_sets(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of creature sets."""
        endpoint = "/v2/creaturesets/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_creature_set(self, key: str) -> JSONDict:
        """Get a specific creature set by key."""
        endpoint = f"/v2/creaturesets/{key}/"
        return self._make_request(endpoint)
    
    # === CREATURE TYPES ===
    def get_creature_types(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of creature types."""
        endpoint = "/v2/creaturetypes/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_creature_type(self, key: str) -> JSONDict:
        """Get a specific creature type by key."""
        endpoint = f"/v2/creaturetypes/{key}/"
        return self._make_request(endpoint)
    
    # === DAMAGE TYPES ===
    def get_damage_types(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of damage types."""
        endpoint = "/v2/damagetypes/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_damage_type(self, key: str) -> JSONDict:
        """Get a specific damage type by key."""
        endpoint = f"/v2/damagetypes/{key}/"
        return self._make_request(endpoint)
    
    # === DOCUMENTS ===
    def get_documents(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of documents."""
        endpoint = "/v2/documents/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_document(self, key: str) -> JSONDict:
        """Get a specific document by key."""
        endpoint = f"/v2/documents/{key}/"
        return self._make_request(endpoint)
    
    # === ENVIRONMENTS ===
    def get_environments(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of environments."""
        endpoint = "/v2/environments/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_environment(self, key: str) -> JSONDict:
        """Get a specific environment by key."""
        endpoint = f"/v2/environments/{key}/"
        return self._make_request(endpoint)
    
    # === FEATS ===
    def get_feats(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of feats."""
        endpoint = "/v2/feats/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_feat(self, key: str) -> JSONDict:
        """Get a specific feat by key."""
        endpoint = f"/v2/feats/{key}/"
        return self._make_request(endpoint)
    
    # === GAME SYSTEMS ===
    def get_game_systems(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of game systems."""
        endpoint = "/v2/gamesystems/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_game_system(self, key: str) -> JSONDict:
        """Get a specific game system by key."""
        endpoint = f"/v2/gamesystems/{key}/"
        return self._make_request(endpoint)
    
    # === ITEMS ===
    def get_items(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of items."""
        endpoint = "/v2/items/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_item(self, key: str) -> JSONDict:
        """Get a specific item by key."""
        endpoint = f"/v2/items/{key}/"
        return self._make_request(endpoint)
    
    # === ITEM CATEGORIES ===
    def get_item_categories(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of item categories."""
        endpoint = "/v2/itemcategories/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_item_category(self, key: str) -> JSONDict:
        """Get a specific item category by key."""
        endpoint = f"/v2/itemcategories/{key}/"
        return self._make_request(endpoint)
    
    # === ITEM RARITIES ===
    def get_item_rarities(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of item rarities."""
        endpoint = "/v2/itemrarities/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_item_rarity(self, key: str) -> JSONDict:
        """Get a specific item rarity by key."""
        endpoint = f"/v2/itemrarities/{key}/"
        return self._make_request(endpoint)
    
    # === ITEM SETS ===
    def get_item_sets(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of item sets."""
        endpoint = "/v2/itemsets/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_item_set(self, key: str) -> JSONDict:
        """Get a specific item set by key."""
        endpoint = f"/v2/itemsets/{key}/"
        return self._make_request(endpoint)
    
    # === LANGUAGES ===
    def get_languages(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of languages."""
        endpoint = "/v2/languages/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_language(self, key: str) -> JSONDict:
        """Get a specific language by key."""
        endpoint = f"/v2/languages/{key}/"
        return self._make_request(endpoint)
    
    # === SIZES ===
    def get_sizes(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of creature sizes."""
        endpoint = "/v2/sizes/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_size(self, key: str) -> JSONDict:
        """Get a specific size by key."""
        endpoint = f"/v2/sizes/{key}/"
        return self._make_request(endpoint)
    
    # === SKILLS ===
    def get_skills(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of skills."""
        endpoint = "/v2/skills/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_skill(self, key: str) -> JSONDict:
        """Get a specific skill by key."""
        endpoint = f"/v2/skills/{key}/"
        return self._make_request(endpoint)
    
    # === SPECIES ===
    def get_species(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of species (races)."""
        endpoint = "/v2/species/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_species_item(self, key: str) -> JSONDict:
        """Get a specific species by key."""
        endpoint = f"/v2/species/{key}/"
        return self._make_request(endpoint)
    
    # === SPELLS ===
    def get_spells(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of spells."""
        endpoint = "/v2/spells/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_spell(self, key: str) -> JSONDict:
        """Get a specific spell by key."""
        endpoint = f"/v2/spells/{key}/"
        return self._make_request(endpoint)
    
    # === SPELL SCHOOLS ===
    def get_spell_schools(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of spell schools."""
        endpoint = "/v2/spellschools/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_spell_school(self, key: str) -> JSONDict:
        """Get a specific spell school by key."""
        endpoint = f"/v2/spellschools/{key}/"
        return self._make_request(endpoint)
    
    # === WEAPONS ===
    def get_weapons(self, params: Optional[JSONDict] = None, paginate: bool = False) -> JSONResponse:
        """Get a list of weapons."""
        endpoint = "/v2/weapons/"
        if paginate:
            return self._paginate_results(endpoint, params)
        return self._make_request(endpoint, params)
    
    def get_weapon(self, key: str) -> JSONDict:
        """Get a specific weapon by key."""
        endpoint = f"/v2/weapons/{key}/"
        return self._make_request(endpoint)
      # === SEARCH ===
    def search(self, query: str, params: Optional[JSONDict] = None) -> JSONDict:
        """
        Search across all resources.
        
        Args:
            query: Search term
            params: Additional query parameters
            
        Returns:
            Search results
        """
        endpoint = "/v2/search/"
        params = params or {}
        params["search"] = query
        return self._make_request(endpoint, params)


# Example usage
if __name__ == "__main__":
    client = Open5eClient()
    
    # Get a list of spells
    try:
        # The API returns a paginated response unless paginate=True
        spell_results = client.get_spells({"level": 1, "school__name": "Evocation"})
        
        # Type checking to handle the union return type
        if isinstance(spell_results, dict):
            print(f"Found {spell_results.get('count', 0)} level 1 evocation spells")
        else:
            print(f"Retrieved {len(spell_results)} level 1 evocation spells")
        
        # Get details of a specific monster
        dragon = client.get_creature("adult-black-dragon")
        print(f"Dragon CR: {dragon.get('challenge_rating_text')}")
        
        # Search for items containing "sword"
        search_results = client.search("sword")
        print(f"Found {search_results.get('count', 0)} items containing 'sword'")
        
        # If you want all results (paginated):
        all_spells = client.get_spells({"level": 0}, paginate=True)
        print(f"Retrieved {len(all_spells)} cantrips")
        
    except requests.RequestException as e:
        print(f"Error accessing the API: {e}")