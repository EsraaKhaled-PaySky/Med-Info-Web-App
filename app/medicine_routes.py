# app/medicine_routes.py

from flask import Blueprint, request, render_template, current_app
from . import mongo
from app.utils.api_clients import get_fda_data, get_rxcui, get_interactions

medicine_bp = Blueprint("medicine", __name__, url_prefix="/medicine")

@medicine_bp.route('/search', methods=["GET"])
def search():
    query = request.args.get("query", "").strip().lower()
    if not query:
        return render_template("search_results.html", error="Please enter a drug name.")

    # Try to find in MongoDB first
    cached = mongo.db.medicines.find_one({"name": query})
    if cached:
        current_app.logger.info("Using cached result from MongoDB.")
        return render_template("search_results.html", fda=cached["fda"], interactions=cached["interactions"])

    # Fetch from APIs
    fda_data = get_fda_data(query)
    rxcui = get_rxcui(query)
    interactions = get_interactions(rxcui)

    # Save to DB if successful
    if fda_data or interactions:
        mongo.db.medicines.insert_one({
            "name": query,
            "fda": fda_data,
            "interactions": interactions
        })

    return render_template("search_results.html", fda=fda_data, interactions=interactions)

