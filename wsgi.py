import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from core.database import init_db, get_db
try:
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM wheels").fetchone()[0]
    db.close()
    if count == 0:
        init_db()
except:
    init_db()

from app import app

if __name__ == '__main__':
    app.run()
