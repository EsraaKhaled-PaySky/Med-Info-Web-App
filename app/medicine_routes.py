from flask import Blueprint, request, render_template, current_app, redirect, url_for, flash
from flask_login import login_required
from . import mongo
from app.utils.api_clients import get_fda_data, get_rxcui, get_interactions

medicine_bp = Blueprint("medicine", __name__, url_prefix="/medicine")

@medicine_bp.route('/search', methods=["GET", "POST"])
@login_required
def search():
    # Handle both GET (from redirect) and POST (from form submission)
    query = request.args.get("query", "").strip().lower()
    if not query and request.method == "POST":
        query = request.form.get("query", "").strip().lower()
    
    if not query:
        flash("Please enter a drug name.", "warning")
        return redirect(url_for('main.dashboard'))

    # Try to find in MongoDB first
    cached = mongo.db.medicines.find_one({"name": query})
    if cached:
        current_app.logger.info("Using cached result from MongoDB.")
        return render_template("search_results.html", 
                             fda=cached["fda"], 
                             interactions=cached["interactions"],
                             query=query)

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
        current_app.logger.info(f"Saved new drug data for: {query}")

    return render_template("search_results.html", 
                         fda=fda_data, 
                         interactions=interactions,
                         query=query)



# from flask import Blueprint, request, render_template, current_app
# from . import mongo
# from app.utils.api_clients import get_fda_data, get_rxcui, get_interactions

# medicine_bp = Blueprint("medicine", __name__, url_prefix="/medicine")

# @medicine_bp.route('/search', methods=["GET"])
# def search():
#     query = request.args.get("query", "").strip().lower()
#     if not query:
#         return render_template("search_results.html", error="Please enter a drug name.")

#     # Try to find in MongoDB first
#     cached = mongo.db.medicines.find_one({"name": query})
#     if cached:
#         current_app.logger.info("Using cached result from MongoDB.")
#         return render_template("search_results.html", fda=cached["fda"], interactions=cached["interactions"])

#     # Fetch from APIs
#     fda_data = get_fda_data(query)
#     rxcui = get_rxcui(query)
#     interactions = get_interactions(rxcui)

#     # Save to DB if successful
#     if fda_data or interactions:
#         mongo.db.medicines.insert_one({
#             "name": query,
#             "fda": fda_data,
#             "interactions": interactions
#         })

#     return render_template("search_results.html", fda=fda_data, interactions=interactions)

