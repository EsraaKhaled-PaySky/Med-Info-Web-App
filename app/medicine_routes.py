from flask import Blueprint, request, render_template
from app.utils.api_clients import get_fda_data, get_rxcui, get_interactions

medicine_bp = Blueprint('medicine', __name__)

@medicine_bp.route('/search')
def search():
    drug = request.args.get("query")
    fda_data = get_fda_data(drug)
    rxcui = get_rxcui(drug)
    interactions = get_interactions(rxcui)
    return render_template("search_results.html", fda=fda_data, interactions=interactions)
