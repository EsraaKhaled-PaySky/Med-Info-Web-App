# utils/api_clients.py

import os
import requests
from dotenv import load_dotenv
from app.db import drug_collection  # Make sure db.py is in app/

# Load environment variables (e.g. from .env in local or Replit secrets)
load_dotenv()
FDA_API_KEY = os.getenv("FDA_API_KEY")

# ✅ Fetch drug label data from the FDA API
def get_fda_data(drug_name):
    url = f"https://api.fda.gov/drug/label.json?search=generic_name:{drug_name}&api_key={FDA_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])[0] if data.get("results") else {}
    except Exception as e:
        print(f"FDA API error: {e}")
        return {}

# ✅ Insert FDA drug data into MongoDB
def store_fda_data_in_mongo(drug_name):
    drug_data = get_fda_data(drug_name)
    if drug_data:
        drug_id = drug_data.get("id")
        if not drug_collection.find_one({"id": drug_id}):
            drug_collection.insert_one(drug_data)
            print(f"✅ Inserted drug data for '{drug_name}' with ID {drug_id}")
        else:
            print(f"⚠️ Drug '{drug_name}' already exists in database.")
    else:
        print(f"❌ No FDA data found for '{drug_name}'")

# ✅ Get the RxNorm Concept Unique Identifier (RxCUI) from drug name
def get_rxcui(drug_name):
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("idGroup", {}).get("rxnormId", [None])[0]
    except Exception as e:
        print(f"RxNorm API error: {e}")
        return None

# ✅ Get drug interactions using the RxCUI
def get_interactions(rxcui):
    if not rxcui:
        return []
    url = f"https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui={rxcui}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        interaction_groups = data.get("interactionTypeGroup", [])
        interactions = []
        for group in interaction_groups:
            for interaction_type in group.get("interactionType", []):
                for interaction in interaction_type.get("interactionPair", []):
                    interactions.append(interaction.get("description"))
        return interactions
    except Exception as e:
        print(f"Interaction API error: {e}")
        return []

