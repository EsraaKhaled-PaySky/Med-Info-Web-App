from flask import Blueprint, request, render_template, current_app
from . import mongo
from app.utils.api_clients import search_drug_info

medicine_bp = Blueprint("medicine", __name__, url_prefix="/medicine")

@medicine_bp.route('/search', methods=["GET", "POST"])
def search():
    query = ""
    if request.method == "POST":
        query = request.form.get("query", "").strip()
    else:
        query = request.args.get("query", "").strip()
    
    if not query:
        return render_template("search_results.html", error="Please enter a drug name.", query=query)

    # Convert to lowercase for consistent database storage
    query_lower = query.lower()

    # Try to find in MongoDB first
    cached = mongo.db.medicines.find_one({"name": query_lower})
    if cached:
        current_app.logger.info(f"Using cached result from MongoDB for: {query}")
        print(f"📦 Using cached data for: {query}")
        return render_template("search_results.html", 
                             fda=cached.get("fda_data"), 
                             interactions=cached.get("interactions"), 
                             query=query)

    # Fetch from APIs using comprehensive search
    current_app.logger.info(f"Fetching new data for: {query}")
    print(f"🌐 Fetching new data from APIs for: {query}")
    
    result = search_drug_info(query)
    
    fda_data = result.get('fda_data', {})
    interactions = result.get('interactions', [])
    rxcui = result.get('rxcui')

    # Save to DB if we got any results
    if fda_data or interactions:
        try:
            mongo.db.medicines.insert_one({
                "name": query_lower,
                "original_query": query,
                "fda_data": fda_data,
                "interactions": interactions,
                "rxcui": rxcui
            })
            current_app.logger.info(f"Saved data to MongoDB for: {query}")
            print(f"💾 Saved data to MongoDB for: {query}")
        except Exception as e:
            current_app.logger.error(f"Error saving to MongoDB: {e}")
            print(f"❌ Error saving to MongoDB: {e}")

    # If no results found, provide helpful message
    if not fda_data and not interactions:
        error_message = f"No information found for '{query}'. Please check the spelling or try a different drug name."
        print(f"❌ No results found for: {query}")
        return render_template("search_results.html", error=error_message, query=query)

    print(f"✅ Returning results for: {query}")
    return render_template("search_results.html", 
                         fda=fda_data, 
                         interactions=interactions, 
                         query=query)
