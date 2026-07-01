from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import get_db, init_db

app = Flask(__name__)

init_db()


@app.route("/")
def menu():
    return render_template("menu.html")


@app.route("/sports")
def sports_report():
    conn = get_db()
    cursor = conn.cursor()

    sports = cursor.execute("SELECT * FROM sports ORDER BY name").fetchall()
    levels = cursor.execute("SELECT * FROM sport_levels ORDER BY name").fetchall()
    teams = cursor.execute("SELECT * FROM teams ORDER BY name").fetchall()

    selected_iacid = request.args.get("iacid", "")
    selected_scid = request.args.get("scid", "")
    selected_sport = request.args.get("sport", "")
    selected_gender = request.args.get("gender", "")
    selected_level = request.args.get("level", "")
    selected_team = request.args.get("team", "")
    selected_opponent = request.args.get("opponent", "")
    sort1 = request.args.get("sort1", "game_date")
    sort2 = request.args.get("sort2", "sport_name")

    query = """
        SELECT
            g.id AS game_id,
            g.iacid,
            g.scid,
            g.season,
            g.sport_id,
            g.school_id,
            g.opponent_id,
            g.game_date,
            g.location,
            g.your_team_score,
            g.opponent_score,
            g.pdf_link,
            g.gender,
            s.name AS sport_name,
            sl.name AS level_name,
            yt.name AS your_team,
            yt.town_id,
            yt.school_id AS your_school_id,
            yt.team_id AS your_team_id,
            ot.name AS opponent_team
        FROM games g
        LEFT JOIN sports s ON g.sport_id = s.id
        LEFT JOIN sport_levels sl ON g.level_id = sl.id
        LEFT JOIN teams yt ON g.school_id = yt.id
        LEFT JOIN teams ot ON g.opponent_id = ot.id
        WHERE 1=1
    """

    params = []

    if selected_iacid:
        query += " AND g.iacid = ?"
        params.append(selected_iacid)

    if selected_scid:
        query += " AND g.scid = ?"
        params.append(selected_scid)

    if selected_sport:
        query += " AND g.sport_id = ?"
        params.append(selected_sport)

    if selected_gender:
        query += " AND g.gender = ?"
        params.append(selected_gender)

    if selected_level:
        query += " AND g.level_id = ?"
        params.append(selected_level)

    if selected_team:
        query += " AND g.school_id = ?"
        params.append(selected_team)

    if selected_opponent:
        query += " AND g.opponent_id = ?"
        params.append(selected_opponent)

    allowed_sorts = {
        "game_date": "g.game_date",
        "season": "g.season",
        "sport_name": "s.name",
        "your_team": "yt.name",
        "opponent_team": "ot.name",
        "level_name": "sl.name",
        "gender": "g.gender",
        "your_team_score": "g.your_team_score",
        "opponent_score": "g.opponent_score"
    }

    order1 = allowed_sorts.get(sort1, "g.game_date")
    order2 = allowed_sorts.get(sort2, "s.name")

    query += f" ORDER BY {order1}, {order2}"

    games = cursor.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "sports.html",
        sports=sports,
        levels=levels,
        teams=teams,
        games=games,
        selected_iacid=selected_iacid,
        selected_scid=selected_scid,
        selected_sport=selected_sport,
        selected_gender=selected_gender,
        selected_level=selected_level,
        selected_team=selected_team,
        selected_opponent=selected_opponent,
        sort1=sort1,
        sort2=sort2
    )


@app.route("/setup", methods=["GET", "POST"])
def setup():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        iacid = request.form["iacid"]
        scid = request.form["scid"]
        season = request.form["season"]
        sport_id = request.form["sport_id"]
        school_id = request.form["school_id"]
        opponent_id = request.form["opponent_id"]
        level_id = request.form["level_id"]
        game_date = request.form["game_date"]
        location = request.form["location"]
        your_team_score = request.form["your_team_score"]
        opponent_score = request.form["opponent_score"]
        pdf_link = request.form["pdf_link"]
        gender = request.form["gender"]

        cursor.execute("""
            INSERT INTO games (
                iacid, scid, season, sport_id, school_id, opponent_id,
                level_id, game_date, location, your_team_score,
                opponent_score, pdf_link, gender
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            iacid, scid, season, sport_id, school_id, opponent_id,
            level_id, game_date, location, your_team_score,
            opponent_score, pdf_link, gender
        ))

        conn.commit()
        conn.close()
        return redirect(url_for("sports_report"))

    sports = cursor.execute("SELECT * FROM sports ORDER BY name").fetchall()
    levels = cursor.execute("SELECT * FROM sport_levels ORDER BY name").fetchall()
    teams = cursor.execute("SELECT * FROM teams ORDER BY name").fetchall()
    conn.close()

    return render_template("setup.html", sports=sports, levels=levels, teams=teams)


@app.route("/summary")
def summary():
    conn = get_db()
    cursor = conn.cursor()

    sport_summary = cursor.execute("""
        SELECT
            s.name AS sport_name,
            COUNT(g.id) AS games_played,
            AVG(g.your_team_score) AS avg_score
        FROM games g
        JOIN sports s ON g.sport_id = s.id
        GROUP BY s.name
        ORDER BY s.name
    """).fetchall()

    team_summary = cursor.execute("""
        SELECT
            t.name AS team_name,
            COUNT(g.id) AS games_played,
            SUM(CASE WHEN g.your_team_score > g.opponent_score THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN g.your_team_score < g.opponent_score THEN 1 ELSE 0 END) AS losses,
            SUM(CASE WHEN g.your_team_score = g.opponent_score THEN 1 ELSE 0 END) AS ties
        FROM games g
        JOIN teams t ON g.school_id = t.id
        GROUP BY t.name
        ORDER BY wins DESC
    """).fetchall()

    conn.close()

    return render_template(
        "summary.html",
        sport_summary=sport_summary,
        team_summary=team_summary
    )


@app.route("/api/sports")
def api_sports():
    conn = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT
            g.id AS game_id,
            g.iacid,
            g.scid,
            g.season,
            s.name AS sport,
            yt.name AS your_team,
            ot.name AS opponent_team,
            sl.name AS level,
            g.game_date,
            g.location,
            g.your_team_score,
            g.opponent_score,
            g.pdf_link,
            g.gender
        FROM games g
        JOIN sports s ON g.sport_id = s.id
        JOIN teams yt ON g.school_id = yt.id
        JOIN teams ot ON g.opponent_id = ot.id
        JOIN sport_levels sl ON g.level_id = sl.id
        ORDER BY g.game_date DESC
    """).fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    app.run(debug=True, port=5004)