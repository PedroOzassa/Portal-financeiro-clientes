from flask import Blueprint
from .relat_dupl_liquid import relat_dupl_liquid_bp
from .relat_dupl_receb import relat_dupl_receb_bp
from .relat_geral import relat_geral_bp

reports_bp = Blueprint("reports_bp", __name__)

reports_bp.register_blueprint(relat_dupl_liquid_bp)
reports_bp.register_blueprint(relat_dupl_receb_bp)
reports_bp.register_blueprint(relat_geral_bp)
