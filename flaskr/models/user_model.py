from flask_login import UserMixin
from flaskr.db.connection import get_connection

# Flask-Login automatically exposes `current_user` inside all Jinja templates.
# It does this through a context processor added by LoginManager, which injects
# "current_user" into the template context on every jinja generated page.
# Because of that, any attribute defined on this User class (rasoc, cgccpf, etc.)
# becomes directly accessible in templates like: {{ current_user.rasoc }}.

class User(UserMixin):
    def __init__(self, numct, rasoc, inter, digdup, digche, vencolet, situa, cgccpf):
        self.id = numct  # Flask-Login expects 'id'
        self.type = 1 # User type in this system is always 1
        self.rasoc = rasoc
        self.inter = inter
        self.digdup = digdup
        self.digche = digche
        self.vencolet = vencolet
        self.situa = situa
        self.cgccpf = cgccpf

    @staticmethod
    def from_db_row(row):
        return User(
            numct=row[0],
            rasoc=row[1],
            inter=row[2],
            digdup=row[3],
            digche=row[4],
            vencolet=row[5],
            situa=row[6],
            cgccpf=row[7],
        )

    @staticmethod
    def get(user_id):
        """Rebuild user from DB using its ID."""
        query = """
            SELECT CE_NUMCT, CE_RASOC, CE_INTER, CE_DIGDUP, CE_DIGCHE, CE_VENCOLET, CE_SITUA, CE_CGCCE
            FROM DESENPUC.CE_CEDEN
            WHERE CE_NUMCT = :numct
        """
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, {"numct": user_id})
                row = cursor.fetchone()
                if row:
                    return User.from_db_row(row)
        return None
