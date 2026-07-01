import sqlite3

DB_NAME = "sports.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS games")
    cursor.execute("DROP TABLE IF EXISTS teams")
    cursor.execute("DROP TABLE IF EXISTS sport_levels")
    cursor.execute("DROP TABLE IF EXISTS sports")

    cursor.execute("""
        CREATE TABLE sports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE sport_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            town_id INTEGER NOT NULL,
            school_id INTEGER NOT NULL,
            team_id INTEGER NOT NULL,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            iacid INTEGER NOT NULL,
            scid INTEGER NOT NULL,
            season TEXT NOT NULL,
            sport_id INTEGER NOT NULL,
            school_id INTEGER NOT NULL,
            opponent_id INTEGER NOT NULL,
            level_id INTEGER NOT NULL,
            game_date TEXT NOT NULL,
            location TEXT NOT NULL,
            your_team_score INTEGER,
            opponent_score INTEGER,
            pdf_link TEXT,
            gender TEXT NOT NULL,
            FOREIGN KEY (sport_id) REFERENCES sports(id),
            FOREIGN KEY (school_id) REFERENCES teams(id),
            FOREIGN KEY (opponent_id) REFERENCES teams(id),
            FOREIGN KEY (level_id) REFERENCES sport_levels(id)
        )
    """)

    cursor.executemany("INSERT INTO sports (name) VALUES (?)", [
        ("Track",),
        ("Basketball",),
        ("Skeet",),
        ("Volleyball",),
        ("Swimming",),
        ("Football",),
        ("Soccer",),
        ("Baseball",),
        ("Softball",)
    ])

    cursor.executemany("INSERT INTO sport_levels (name) VALUES (?)", [
        ("Tournament",),
        ("Post Season",),
        ("Regular Season",),
        ("Past Seasons",),
        ("Rivalry",)
    ])

    cursor.executemany("""
        INSERT INTO teams (town_id, school_id, team_id, name)
        VALUES (?, ?, ?, ?)
    """, [
        (10, 101, 1001, "IAC Tigers"),
        (10, 102, 1002, "SC Falcons"),
        (20, 201, 2001, "River Hawks"),
        (20, 202, 2002, "Lake Wolves"),
        (30, 301, 3001, "Valley Knights"),
        (30, 302, 3002, "North Bears"),
        (40, 401, 4001, "South Eagles"),
        (40, 402, 4002, "West Panthers")
    ])

    sports = {r["name"]: r["id"] for r in cursor.execute("SELECT * FROM sports")}
    levels = {r["name"]: r["id"] for r in cursor.execute("SELECT * FROM sport_levels")}
    teams = {r["name"]: r["id"] for r in cursor.execute("SELECT * FROM teams")}

    games = [
        (1, 100, "2026 Spring", sports["Basketball"], teams["IAC Tigers"], teams["SC Falcons"], levels["Regular Season"], "2026-04-01", "IAC Gym", 68, 61, "reports/basketball_iac_sc.pdf", "Boys"),
        (1, 100, "2026 Spring", sports["Soccer"], teams["River Hawks"], teams["Lake Wolves"], levels["Tournament"], "2026-03-28", "River Field", 3, 2, "reports/soccer_river_lake.pdf", "Girls"),
        (1, 100, "2026 Spring", sports["Volleyball"], teams["SC Falcons"], teams["Valley Knights"], levels["Regular Season"], "2026-03-24", "SC Gym", 3, 1, "reports/volleyball_sc_valley.pdf", "Girls"),
        (2, 200, "2026 Winter", sports["Swimming"], teams["Lake Wolves"], teams["IAC Tigers"], levels["Post Season"], "2026-02-18", "Community Pool", 92, 88, "reports/swimming_lake_iac.pdf", "Girls"),
        (2, 200, "2026 Winter", sports["Football"], teams["North Bears"], teams["South Eagles"], levels["Rivalry"], "2026-02-10", "North Stadium", 28, 24, "reports/football_north_south.pdf", "Boys"),
        (3, 300, "2025 Fall", sports["Track"], teams["West Panthers"], teams["River Hawks"], levels["Past Seasons"], "2025-11-12", "West Track", 76, 70, "reports/track_west_river.pdf", "Girls"),
        (3, 300, "2025 Fall", sports["Basketball"], teams["Valley Knights"], teams["North Bears"], levels["Tournament"], "2025-10-30", "Valley Gym", 59, 63, "reports/basketball_valley_north.pdf", "Boys"),
        (4, 400, "2025 Fall", sports["Skeet"], teams["South Eagles"], teams["SC Falcons"], levels["Regular Season"], "2025-10-15", "Outdoor Range", 44, 41, "reports/skeet_south_sc.pdf", "Male"),
        (4, 400, "2025 Summer", sports["Baseball"], teams["IAC Tigers"], teams["West Panthers"], levels["Regular Season"], "2025-08-20", "IAC Field", 7, 5, "reports/baseball_iac_west.pdf", "Boys"),
        (5, 500, "2025 Summer", sports["Soccer"], teams["SC Falcons"], teams["IAC Tigers"], levels["Rivalry"], "2025-07-18", "SC Field", 1, 1, "reports/soccer_sc_iac.pdf", "Girls"),
        (5, 500, "2025 Summer", sports["Softball"], teams["Lake Wolves"], teams["South Eagles"], levels["Post Season"], "2025-06-30", "Lake Field", 9, 6, "reports/softball_lake_south.pdf", "Female"),
        (6, 600, "2025 Spring", sports["Basketball"], teams["River Hawks"], teams["IAC Tigers"], levels["Regular Season"], "2025-05-12", "River Gym", 72, 70, "reports/basketball_river_iac.pdf", "Boys")
    ]

    cursor.executemany("""
        INSERT INTO games (
            iacid, scid, season, sport_id, school_id, opponent_id,
            level_id, game_date, location, your_team_score,
            opponent_score, pdf_link, gender
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, games)

    conn.commit()
    conn.close()