import requests

def get_fda_data(drug_name):
    """Fetch drug label data from OpenFDA."""
    url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug_name}&limit=1"
    res = requests.get(url)
    return res.json() if res.ok else {}

def get_rxcui(drug_name):
    """Get RxCUI (RxNorm ID) from RxNav."""
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
    res = requests.get(url).json()
    return res.get("idGroup", {}).get("rxnormId", [None])[0]

def get_interactions(rxcui):
    """Get drug interaction data using RxNav API."""
    if not rxcui:
        return {}
    url = f"https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui={rxcui}"
    res = requests.get(url)
    return res.json() if res.ok else {}
