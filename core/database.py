import sqlite3, os

DB_PATH = os.environ.get('DB_PATH', '/app/data/envy.db')

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    c = db.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS wheels (
        id INTEGER PRIMARY KEY,
        sku TEXT UNIQUE,
        name TEXT,
        construction TEXT,
        sizes TEXT,
        description TEXT,
        market_ref TEXT,
        popular INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS finishes (
        id INTEGER PRIMARY KEY,
        name TEXT,
        code TEXT,
        tier TEXT
    );
    CREATE TABLE IF NOT EXISTS pricing (
        id INTEGER PRIMARY KEY,
        construction TEXT,
        size_inch INTEGER,
        finish_tier TEXT,
        base_usd INTEGER,
        retail_usd INTEGER,
        processing_fee INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        name TEXT, email TEXT, phone TEXT,
        vehicle TEXT, wheel_sku TEXT, size_inch INTEGER,
        finish TEXT, qty INTEGER, fitment TEXT,
        notes TEXT, status TEXT DEFAULT 'new',
        country TEXT, referral_code TEXT
    );
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        quote_id INTEGER,
        name TEXT, email TEXT,
        wheel_sku TEXT, wheel_name TEXT,
        size_inch INTEGER, finish TEXT, qty INTEGER,
        country TEXT, status TEXT DEFAULT 'received',
        tracking TEXT, notes TEXT,
        referral_code TEXT
    );
    """)

    c.execute("DELETE FROM finishes")
    c.executemany("INSERT INTO finishes(name,code,tier) VALUES(?,?,?)", [
        ('Gloss Black','gloss-black','standard'),
        ('Matte Black','matte-black','standard'),
        ('Silver','silver','standard'),
        ('White','white','standard'),
        ('Bronze','bronze','standard'),
        ('Gunmetal','gunmetal','standard'),
        ('Brushed','brushed','premium'),
        ('Polished Bright','polished','premium'),
        ('Chrome','chrome','premium'),
    ])

    def retail(cost):
        return int((cost * 1.5 / 50 + 1) * 50)

    c.execute("DELETE FROM pricing")
    for size, cost in [(17,195),(18,205),(19,220),(20,250),(21,280),(22,310),(23,350),(24,395)]:
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,retail_usd,processing_fee) VALUES(?,?,?,?,?,?)",('one-piece',size,'standard',cost,retail(cost),0))
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,retail_usd,processing_fee) VALUES(?,?,?,?,?,?)",('one-piece',size,'premium',cost+50,retail(cost+50),0))
    for size, cost in [(17,340),(18,350),(19,380),(20,410),(21,440),(22,480),(23,520),(24,595),(26,680)]:
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,retail_usd,processing_fee) VALUES(?,?,?,?,?,?)",('two-piece',size,'standard',cost,retail(cost),50))
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,retail_usd,processing_fee) VALUES(?,?,?,?,?,?)",('two-piece',size,'premium',cost+50,retail(cost+50),50))
    for size, cost in [(17,410),(18,420),(19,450),(20,480),(21,510),(22,550),(23,595),(24,670),(26,750)]:
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,retail_usd,processing_fee) VALUES(?,?,?,?,?,?)",('three-piece',size,'standard',cost,retail(cost),50))
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,retail_usd,processing_fee) VALUES(?,?,?,?,?,?)",('three-piece',size,'premium',cost+50,retail(cost+50),50))
    for size, cost in [(17,350),(18,395),(19,450),(20,595)]:
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,retail_usd,processing_fee) VALUES(?,?,?,?,?,?)",('beadlock',size,'standard',cost,retail(cost),0))
    for size, cost in [(20,440),(22,480),(24,520),(26,595),(28,770),(30,1020)]:
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,retail_usd,processing_fee) VALUES(?,?,?,?,?,?)",('htype',size,'standard',cost,retail(cost),0))
    for size, cost in [(19,850),(20,950),(21,1050),(22,1150)]:
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,retail_usd,processing_fee) VALUES(?,?,?,?,?,?)",('carbon',size,'standard',cost,retail(cost),0))

    c.execute("DELETE FROM wheels")
    wheels = [
        ('GS001','Mono Seven','one-piece','17-24"','Deep concave 7-spoke monoblock. Universally fitment-friendly, the most requested spoke pattern in the Euro scene.','Vossen HF-2 / Rohana RFX7'),
        ('GS002','Mesh Ten','one-piece','17-24"','10-spoke mesh face. High visual complexity, clean from any angle. Works staggered or square.','HRE FF01 / Forgeline GA1R'),
        ('GS004','Split Eight','one-piece','18-24"','Split
