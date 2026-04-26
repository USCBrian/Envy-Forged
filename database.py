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
        processing_fee INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        name TEXT, email TEXT, phone TEXT,
        vehicle TEXT, wheel_sku TEXT, size_inch INTEGER,
        finish TEXT, qty INTEGER, fitment TEXT,
        notes TEXT, status TEXT DEFAULT 'new'
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

    c.execute("DELETE FROM pricing")
    for size, price in [(17,195),(18,205),(19,220),(20,250),(21,280),(22,310),(23,350),(24,395)]:
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,processing_fee) VALUES(?,?,?,?,?)",('one-piece',size,'standard',price,0))
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,processing_fee) VALUES(?,?,?,?,?)",('one-piece',size,'premium',price+50,0))
    for size, price in [(17,340),(18,350),(19,380),(20,410),(21,440),(22,480),(23,520),(24,595),(26,680)]:
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,processing_fee) VALUES(?,?,?,?,?)",('two-piece',size,'standard',price,50))
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,processing_fee) VALUES(?,?,?,?,?)",('two-piece',size,'premium',price+50,50))
    for size, price in [(17,410),(18,420),(19,450),(20,480),(21,510),(22,550),(23,595),(24,670),(26,750)]:
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,processing_fee) VALUES(?,?,?,?,?)",('three-piece',size,'standard',price,50))
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,processing_fee) VALUES(?,?,?,?,?)",('three-piece',size,'premium',price+50,50))
    for size, price in [(17,350),(18,395),(19,450),(20,595)]:
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,processing_fee) VALUES(?,?,?,?,?)",('beadlock',size,'standard',price,0))
    for size, price in [(20,440),(22,480),(24,520),(26,595),(28,770),(30,1020)]:
        c.execute("INSERT INTO pricing(construction,size_inch,finish_tier,base_usd,processing_fee) VALUES(?,?,?,?,?)",('htype',size,'standard',price,0))

    c.execute("DELETE FROM wheels")
    wheels = [
        ('GS001','Mono Seven','one-piece','17-24"','Deep concave 7-spoke monoblock. Universally fitment-friendly, the most requested spoke pattern in the Euro scene.','Vossen HF-2 / Rohana RFX7'),
        ('GS002','Mesh Ten','one-piece','17-24"','10-spoke mesh face. High visual complexity, clean from any angle. Works staggered or square.','HRE FF01 / Forgeline GA1R'),
        ('GS004','Split Eight','one-piece','18-24"','Split 8-spoke with stepped face. Modern luxury aesthetic, dominant on BMW G-series and Mercedes AMG.','Vossen CVT / AG Luxury AGL67'),
        ('GS007','Spyder Six','one-piece','18-22"','Open 6-spoke spider design. Lightweight visual weight, motorsport DNA on the road.','BBS CH-R / Rays G025'),
        ('GS012','Concave Six','one-piece','18-24"','Deep concave 6-spoke monoblock. Maximum dish. Built for stance and aggressive fitment.','Vossen S17-01 / Strasse SV10'),
        ('GS016','Y-Spoke','one-piece','18-22"','Wide Y-spoke face. One of the most searched designs on BMW and Porsche forums globally.','Forgeline GS1R / BC Forged HB'),
        ('GS021','Multi Mesh','one-piece','18-24"','Dense multi-spoke mesh. OEM-upgrade look at a fraction of OEM pricing.','HRE FlowForm FF21 / Vossen HF-4'),
        ('GS022','Flow Ten','one-piece','18-24"','Ten flowing curved spokes. Dynamic and modern, dominant on sedans and sport coupes.','AG Luxury AGL67 / Savini SV-F2'),
        ('GS026','Track Six','one-piece','17-20"','TE37-reference 6-spoke. JDM royalty. Track-proven face that moves across every car culture.','Rays Volk TE37 ref'),
        ('GS027','Classic Six','one-piece','17-22"','Straightforward 6-spoke with deep face. Bronze, matte black, and gunmetal are top sellers.','Work Emotion / Enkei RPF1 ref'),
        ('GS029','Star Five','one-piece','18-24"','Wide 5-spoke star. Rolls-Royce and G-wagon energy. Luxury SUV and sedan crossover.','Forgiato Autonomo / Vossen VPS-306'),
        ('GS034','Interlaced','one-piece','19-24"','Woven spoke pattern. Complex face geometry with deep concave. Stops people mid-scroll.','HRE P200 / Strasse R10'),
        ('GS041','Directional Nine','one-piece','18-22"','9 directional spokes. High visual rotation at speed. Sport applications.','Vossen VFS-2 / Rohana RFX9'),
        ('GS042','Twisted Ten','one-piece','19-24"','Ten twisted spokes with dramatic concave. Maximum presence on lowered builds.','Savini SV-F5 / Forgiato Flow'),
        ('GS051','Wide Five','one-piece','20-24"','Massive 5-spoke with wide face. Built for performance SUVs and luxury sedans.','Vossen VPS-315T / HRE S201'),
        ('GS052','Turbine Thirty','one-piece','20-24"','30-blade turbine face. Rolls-Royce-inspired. The highest-spec visual in the 1-piece lineup.','Forgiato Turbina / OEM Rolls ref'),
        ('GS071','Sport Mesh','one-piece','18-22"','Mesh-face monoblock with motorsport proportions. Clean, fast, purposeful.','BBS FI-R / OEM AMG ref'),
        ('GS093','Aero Five','one-piece','20-24"','Wide-body 5-spoke aero face. Track-inspired GT car aesthetic.','HRE R101 / Forgeline VX3C'),
        ('GS098','Gold Mesh','one-piece','19-22"','Open mesh in satin gold. Trending hard in the Euro scene, color-forward statement.','BC Forged EH series / AG Luxury'),
        ('GS103','Split Flow','one-piece','19-22"','Split flowing spokes with high concave. Modern and aggressive.','Vossen HF-7 / BC Forged MLE'),
        ('GS1001','2P Classic Five','two-piece','18-24"','Classic 5-spoke two-piece with polished lip. The original statement wheel.','TSW Aileron / ADV.1 ADV5.0'),
        ('GS1003','2P Deep Mesh','two-piece','18-26"','Deep-dish two-piece mesh face with stepped outer lip. Euro show staple.','BBS E88 / Rotiform BLQ'),
        ('GS1004','2P Split Five','two-piece','18-24"','Split 5-spoke two-piece. Adjustable lip width, custom fitment on every order.','HRE 540M / Vossen M-X4'),
        ('GS1009','2P Bronze Five','two-piece','18-24"','5-spoke two-piece in dark bronze. Most requested finish/style combo in BMW performance.','Vossen M-X3 / HRE FlowForm'),
        ('GS1013','2P Silver Step','two-piece','18-26"','Stepped lip two-piece with brushed center. Timeless. Concours and street.','BBS CI-R / Forgeline DE3C'),
        ('GS1019','2P Wide Five','two-piece','20-26"','Massive 5-spoke two-piece for wide-body fitment. SUV and stance builds.','Forgiato 2.0 / AG Luxury AGL44'),
        ('GS1021','2P Bronze Mesh','two-piece','18-24"','Mesh center two-piece in satin bronze. High demand in BMW M and Porsche 911 market.','Vossen VPS-303 / HRE 543M'),
        ('GS1035','2P Ten Spoke','two-piece','19-24"','Ten-spoke two-piece with deep outer barrel. Sport sedan standard.','Strasse SV10M / ADV.1 ADV10.2'),
        ('GS1036','2P Copper Mesh','two-piece','18-22"','Open mesh two-piece in satin copper. Rising trend across Euro and JDM scenes.','Forgeline GA3R / BC Forged HCA'),
        ('GS1008','2P Polished','two-piece','18-26"','Two-piece with mirror polished outer barrel. Show and concours spec.','BBS E92 / HRE 843M'),
        ('GS1003-3P','3P Classic','three-piece','18-26"','Fully adjustable three-piece. Your offset, your lip, your spec.','HRE 300M / Vossen M-X2'),
        ('GS1008-3P','3P Polished','three-piece','18-26"','Three-piece with mirror polished outer barrel. Show-level finish.','Forgeline GX3 / BBS E92'),
        ('GS1022','3P Wide Silver','three-piece','20-26"','Wide-lip three-piece. Complete custom spec per order.','ADV.1 ADV5.0 TS / HRE P104'),
        ('GS1037','3P Dark Eight','three-piece','19-24"','Eight-spoke three-piece in matte dark. Motorsport-derived, road-tuned.','Strasse R8M / BC Forged MLE'),
        ('GS1039','3P Polished Five','three-piece','18-24"','Five-spoke three-piece with contrasting polished barrel.','Vossen M-X5 / Rotiform TMB'),
        ('GS-BL01','Track Beadlock','beadlock','17-20"','Forged center with FIA-style beadlock ring. Track, drag, and high-power street.','Enkei RPT1M / Method 105'),
        ('GS-BL02','Off-Road Beadlock','beadlock','17-20"','Heavy-duty beadlock for rock crawl and off-road. Maximum bead retention.','Method Race 105 / Fuel Anza'),
        ('GS-HT01','Off-Road Six','htype','20-30"','Six-spoke off-road rim. High load rating for lifted trucks and SUVs.','Fuel Assault / XD Series XD820'),
        ('GS-HT02','Off-Road Mesh','htype','20-28"','Mesh face off-road rim. Top seller for F-150, Ram, and Silverado builds.','American Force / Fuel Maverick'),
        ('GS2001','Carbon Mesh','carbon','19-22"','Carbon fiber composite wheel. Lightest option at ~6kg per corner. Built-to-order only.','HRE Carbon / Carbon Revolution CR-9'),
    ]
    for i, w in enumerate(wheels):
        sku,name,construction,sizes,desc,market_ref = w
        c.execute("INSERT OR REPLACE INTO wheels(sku,name,construction,sizes,description,market_ref,popular,sort_order) VALUES(?,?,?,?,?,?,?,?)",
                  (sku,name,construction,sizes,desc,market_ref,1,i+1))

    db.commit()
    db.close()

if __name__ == '__main__':
    init_db()
    print('done')
