import os
import requests
from dotenv import load_dotenv
from flask import current_app

# Load environment variables (e.g. from .env in local or Replit secrets)
load_dotenv()
FDA_API_KEY = os.getenv("FDA_API_KEY")

# ✅ Fetch drug label data from the FDA API with correct search syntax
def get_fda_data(drug_name):
    if not FDA_API_KEY:
        print("❌ FDA_API_KEY not found in environment variables")
        return {}
    
    base_url = "https://api.fda.gov/drug/label.json"
    
    # Different search field strategies for FDA API
    search_strategies = [
        f"openfda.generic_name:{drug_name}",
        f"openfda.brand_name:{drug_name}", 
        f"openfda.substance_name:{drug_name}",
        f"openfda.generic_name.exact:{drug_name}",
        f"openfda.brand_name.exact:{drug_name}",
        f"generic_name:{drug_name}",
        f"brand_name:{drug_name}",
        f"substance_name:{drug_name}",
        # Try broader searches
        f"openfda.generic_name:*{drug_name}*",
        f"openfda.brand_name:*{drug_name}*",
        # Try without field specification (general search)
        drug_name
    ]
    
    for search_term in search_strategies:
        try:
            print(f"🔍 Trying FDA search: {search_term}")
            
            # Build the URL with proper parameters
            params = {
                'search': search_term,
                'api_key': FDA_API_KEY,
                'limit': 1
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    print(f"✅ Found FDA data for '{drug_name}' using search: {search_term}")
                    return data.get("results", [])[0]
            else:
                print(f"⚠️ FDA API returned {response.status_code} for {search_term}")
                
        except requests.exceptions.RequestException as e:
            print(f"FDA API request error for {search_term}: {e}")
            continue
        except Exception as e:
            print(f"FDA API unexpected error for {search_term}: {e}")
            continue
    
    print(f"❌ No FDA data found for '{drug_name}' after trying all search strategies")
    return {}

# ✅ Get the RxNorm Concept Unique Identifier (RxCUI) from drug name
def get_rxcui(drug_name):
    # Try multiple RxNorm API endpoints
    endpoints = [
        f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}",
        f"https://rxnav.nlm.nih.gov/REST/approximateTerm.json?term={drug_name}",
        f"https://rxnav.nlm.nih.gov/REST/spellingsuggestions.json?name={drug_name}"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"🔍 Getting RxCUI from: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Handle different response formats
            if "rxcui" in endpoint:
                rxcui = data.get("idGroup", {}).get("rxnormId", [None])[0]
            elif "approximateTerm" in endpoint:
                candidates = data.get("approximateGroup", {}).get("candidate", [])
                if candidates:
                    rxcui = candidates[0].get("rxcui")
                else:
                    continue
            elif "spellingsuggestions" in endpoint:
                suggestions = data.get("suggestionGroup", {}).get("suggestionList", {}).get("suggestion", [])
                if suggestions:
                    # Try the first suggestion to get RxCUI
                    suggestion = suggestions[0] if isinstance(suggestions, list) else suggestions
                    return get_rxcui(suggestion)
                else:
                    continue
            
            if rxcui:
                print(f"✅ Found RxCUI for '{drug_name}': {rxcui}")
                return rxcui
                
        except requests.exceptions.RequestException as e:
            print(f"RxNorm API request error: {e}")
            continue
        except Exception as e:
            print(f"RxNorm API unexpected error: {e}")
            continue
    
    print(f"❌ No RxCUI found for '{drug_name}'")
    return None

# ✅ Get drug interactions using the RxCUI with better error handling
def get_interactions(rxcui):
    if not rxcui:
        print("❌ No RxCUI provided for interaction search")
        return []
    
    # Try multiple interaction endpoints
    endpoints = [
        f"https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui={rxcui}",
        f"https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={rxcui}"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"🔍 Getting interactions from: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                interactions = []
                
                # Handle different response formats
                if "interaction.json" in endpoint:
                    interaction_groups = data.get("interactionTypeGroup", [])
                    for group in interaction_groups:
                        for interaction_type in group.get("interactionType", []):
                            for interaction in interaction_type.get("interactionPair", []):
                                description = interaction.get("description", "No description available")
                                severity = interaction.get("severity", "Unknown")
                                interactions.append({
                                    "description": description,
                                    "severity": severity
                                })
                                
                elif "list.json" in endpoint:
                    full_interaction_list = data.get("fullInteractionTypeGroup", [])
                    for group in full_interaction_list:
                        for interaction_type in group.get("fullInteractionType", []):
                            for interaction in interaction_type.get("interactionPair", []):
                                description = interaction.get("description", "No description available")
                                severity = interaction.get("severity", "Unknown")
                                interactions.append({
                                    "description": description,
                                    "severity": severity
                                })
                
                if interactions:
                    print(f"✅ Found {len(interactions)} interactions for RxCUI: {rxcui}")
                    return interactions
                else:
                    print(f"ℹ️ No interactions found for RxCUI: {rxcui} using {endpoint}")
                    continue
                    
            else:
                print(f"⚠️ Interaction API returned {response.status_code} for {endpoint}")
                continue
                
        except requests.exceptions.RequestException as e:
            print(f"Interaction API request error: {e}")
            continue
        except Exception as e:
            print(f"Interaction API unexpected error: {e}")
            continue
    
    print(f"❌ No interactions found for RxCUI: {rxcui}")
    return []

# ✅ Try common drug name variations
def get_drug_name_variations(drug_name):
    """Generate common variations of drug names"""
    variations = [drug_name.strip()]
    
    # Basic variations
    variations.extend([
        drug_name.lower(),
        drug_name.upper(), 
        drug_name.capitalize(),
        drug_name.title()
    ])
    
    # Common drug name mappings (generic to brand names)
    name_mappings = {
        'aspirin': ['acetylsalicylic acid', 'Bayer', 'Bufferin', 'Ecotrin'],
        'ibuprofen': ['Advil', 'Motrin', 'Nuprin'],
        'acetaminophen': ['Tylenol', 'Panadol', 'paracetamol'],
        'naproxen': ['Aleve', 'Naprosyn'],
        'omeprazole': ['Prilosec', 'Zegerid'],
        'metformin': ['Glucophage', 'Fortamet', 'Glumetza'],
        'lisinopril': ['Prinivil', 'Zestril'],
        'amlodipine': ['Norvasc', 'Katerzia'],
        'atorvastatin': ['Lipitor'],
        'simvastatin': ['Zocor']
    }
    
    drug_lower = drug_name.lower()
    if drug_lower in name_mappings:
        variations.extend(name_mappings[drug_lower])
    
    # Reverse lookup - if brand name provided, try generic
    for generic, brands in name_mappings.items():
        if drug_lower in [brand.lower() for brand in brands]:
            variations.append(generic)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_variations = []
    for var in variations:
        if var.lower() not in seen:
            seen.add(var.lower())
            unique_variations.append(var)
    
    return unique_variations

# ✅ Comprehensive drug search function with better drug name handling
def search_drug_info(drug_name):
    """
    Comprehensive search that gets both FDA data and interactions
    Returns a dictionary with all available information
    """
    print(f"🔍 Starting comprehensive search for: {drug_name}")
    
    # Get drug name variations
    variations = get_drug_name_variations(drug_name)
    print(f"🔄 Will try these variations: {variations}")
    
    fda_data = {}
    interactions = []
    rxcui = None
    
    # Try each variation until we find results
    for variation in variations:
        print(f"🔍 Trying variation: {variation}")
        
        # Get FDA data
        if not fda_data:
            fda_data = get_fda_data(variation)
        
        # Get RxCUI and interactions
        if not rxcui:
            rxcui = get_rxcui(variation)
            
        if rxcui and not interactions:
            interactions = get_interactions(rxcui)
        
        # If we found something, we can stop
        if fda_data or interactions:
            print(f"✅ Found results using variation: {variation}")
            break
    
    result = {
        "fda_data": fda_data,
        "interactions": interactions,
        "rxcui": rxcui,
        "search_term": drug_name,
        "successful_variation": variation if (fda_data or interactions) else None
    }
    
    print(f"📊 Search complete for '{drug_name}': FDA={bool(fda_data)}, Interactions={len(interactions) if interactions else 0}")
    return result

