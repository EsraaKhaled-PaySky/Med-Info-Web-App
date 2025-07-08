# openfda_import.py

import requests
from app.db import drug_collection  # adjust if your db.py is elsewhere

def fetch_openfda_data(search_term, limit=10):
    base_url = "https://api.fda.gov/drug/label.json"
    params = {
        "search": f"openfda.brand_name:{search_term}",
        "limit": limit
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        print("Error:", e)
        return []

def store_data_in_mongo(drug_name):
    results = fetch_openfda_data(drug_name)
    if results:
        for doc in results:
            # Avoid duplicates
            if not drug_collection.find_one({"id": doc.get("id")}):
                drug_collection.insert_one(doc)
                print(f"Inserted: {doc.get('id')}")
            else:
                print(f"Duplicate skipped: {doc.get('id')}")
    else:
        print("No results found or error occurred.")

