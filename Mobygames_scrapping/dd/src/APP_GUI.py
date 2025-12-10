import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
import hashlib
import traceback
import math
import secrets   
import string    
import re        
import re

def print_table(text_widget, title, rows, headers=None, col_widths=None):
    text_widget.insert(tk.END, f"\n{'='*100}\n")
    text_widget.insert(tk.END, f"{title.center(100)}\n")
    text_widget.insert(tk.END, f"{'='*100}\n\n")

    if not rows:
        text_widget.insert(tk.END, "No data available.\n\n")
        return

    if headers is None:
        headers = rows[0].keys() if isinstance(rows[0], dict) else [f"Col {i+1}" for i in range(len(rows[0]))]
    headers = list(headers)

    if col_widths is None:
        col_widths = {}
        for i, h in enumerate(headers):
            col_widths[i] = max(len(h), 12)

        for row in rows:
            values = row.values() if isinstance(row, dict) else row
            for i, val in enumerate(values):
                col_widths[i] = max(col_widths[i], len(str(val or "")))

    line = ""
    for i, h in enumerate(headers):
        line += f"{h:<{col_widths[i]}}  "
    text_widget.insert(tk.END, line.rstrip() + "\n")
    text_widget.insert(tk.END, "-" * (sum(col_widths.values()) + 2*(len(headers)-1)) + "\n")

    for row in rows:
        values = row.values() if isinstance(row, dict) else row
        line = ""
        for i, val in enumerate(values):
            line += f"{str(val or 'N/A'):<{col_widths[i]}}  "
        text_widget.insert(tk.END, line.rstrip() + "\n")
    text_widget.insert(tk.END, "\n")

def validate_password_strength(password):
    """
    Returns True if password is strong:
    - >=8 characters
    - at least one uppercase, one lowercase, one digit, one special char
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r'[A-Z]', password):
        return False, "Password must include at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must include at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must include at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must include at least one special character."
    return True, ""

DB_CONFIG = {
    'host': 'sql7.freesqldatabase.com',
    'database': 'sql7808703',
    'user': 'sql7808703',
    'password': 'suxTffYt4t',
    'port': 3306,
    'autocommit': True
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(plain):
    return hashlib.sha256(plain.encode('utf-8')).hexdigest()

def generate_random_password(length=16):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def extract_username_from_url(url):
    if not url:
        return None
    s = url.strip().rstrip('/')
    match = re.search(r'/user/\d+/([^/]+)', s)
    if match:
        return match.group(1)
    return s.split('/')[-1].split('?')[0] if '/' in s else s

def consume_cursor(cursor):
    while cursor.with_rows:
        try:
            cursor.fetchall()
        except:
            break

def fetch_to_table(cursor):
    cols = [d[0] for d in cursor.description] if cursor.description else []
    rows = cursor.fetchall()
    return cols, rows

def reset_and_populate_users_table():
    con = get_db_connection()
    cur = con.cursor()
    try:
        cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cur.execute("DROP TABLE IF EXISTS users;")
        cur.execute("""
            CREATE TABLE users (
                username VARCHAR(100) NOT NULL PRIMARY KEY,
                password_hash VARCHAR(256) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.execute("SELECT DISTINCT username_pk FROM player_reviews WHERE username_pk IS NOT NULL")
        rows = cur.fetchall()
        usernames = set()

        for (url,) in rows:
            uname = extract_username_from_url(url)
            if uname and len(uname) <= 100:
                usernames.add(uname)

        for uname in usernames:
            cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                        (uname, hash_password(generate_random_password())))

        con.commit()
        messagebox.showinfo("Success", f"Users table reset & populated with {len(usernames)} users from reviews.")
    except Exception as e:
        con.rollback()
        messagebox.showerror("Error", f"Failed to populate users table:\n{e}")
    finally:
        consume_cursor(cur)
        cur.close()
        con.close()

def register_user(username, password):
    if not username or not password:
        messagebox.showerror("Validation", "Username and password are required.")
        return

    username = username.strip()
    if len(username) > 100:
        messagebox.showerror("Validation", "Username too long (max 100 chars).")
        return

    valid, msg = validate_password_strength(password)
    if not valid:
        messagebox.showerror("Weak Password", msg)
        return

    con = get_db_connection()
    cur = con.cursor()
    try:
        cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            messagebox.showwarning("User Exists", f"Username '{username}' is already taken.")
            return

        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hash_password(password))
        )
        con.commit()
        messagebox.showinfo("Success", f"User '{username}' registered successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Registration failed:\n{e}\n{traceback.format_exc()}")
    finally:
        cur.close()
        con.close()

def add_player_rating(username, password, moby_id, platform, score, title, body):
    if not all([username, password, moby_id, platform]):
        messagebox.showerror("Validation", "Username, password, moby_id, and platform are required.")
        return

    username = username.strip()
    moby_id = moby_id.strip()
    platform = platform.strip()
    title = title or ""
    body = body or ""

    try:
        score_val = float(score)
        if not (0 <= score_val <= 5):
            messagebox.showerror("Validation", "Score must be between 0 and 5.")
            return
    except (ValueError, TypeError):
        messagebox.showerror("Validation", f"Score must be a number. Got '{score}'")
        return

    con = get_db_connection()
    cur = con.cursor()
    try:

        cur.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        if not row or row[0] != hash_password(password):
            messagebox.showerror("Authentication Failed", "Incorrect username or password.")
            return

        cur.execute("SELECT 1 FROM game WHERE moby_id = %s", (moby_id,))
        if not cur.fetchone():
            messagebox.showerror("Error", f"Game with moby_id '{moby_id}' not found.")
            return

        cur.execute("SELECT 1 FROM release_date_per_platform WHERE moby_id=%s AND release_platform=%s",
                    (moby_id, platform))
        if not cur.fetchone():
            messagebox.showerror("Error", f"Platform '{platform}' not valid for game '{moby_id}'.")
            return

        try:
            cur.execute("""
                INSERT INTO player_reviews (username_pk, title, body, score, platform, date, moby_id)
                VALUES (%s, %s, %s, %s, %s, CURDATE(), %s)
            """, (username, title, body, score_val, platform, moby_id))
            con.commit()
            messagebox.showinfo("Success", f"Review for game '{moby_id}' on platform '{platform}' added!")

        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "You already reviewed this game on this platform.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to add review:\n{e}\n{traceback.format_exc()}")
    finally:
        cur.close()
        con.close()

def get_filter_options(filter_type):
    con = get_db_connection()
    cur = con.cursor()
    options = []
    try:
        if filter_type == 'genre':
            cur.execute("SELECT DISTINCT genre_name FROM game_genre ORDER BY genre_name")
        elif filter_type == 'platform':
            cur.execute("SELECT DISTINCT release_platform FROM release_date_per_platform ORDER BY release_platform")
        elif filter_type == 'publisher':
            cur.execute("SELECT DISTINCT publisher_name FROM game_publishers ORDER BY publisher_name")
        elif filter_type == 'developer':
            cur.execute("SELECT DISTINCT developer_name FROM game_developers ORDER BY developer_name")
        else:
            return []
        options = [row[0] for row in cur.fetchall()]
    finally:
        cur.close()
        con.close()
    return options

def view_user_ratings(username):
    """
    Return user ratings as (columns, rows) safely. Works with URL usernames.
    """
    if not username:
        return [], []

    username = username.strip()
    con = get_db_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT pr.moby_id, g.name_ AS game_name, pr.platform, pr.score, pr.title, pr.body, pr.date
            FROM player_reviews pr
            LEFT JOIN game g ON g.moby_id = pr.moby_id
            WHERE pr.username_pk LIKE %s
               OR pr.username_pk LIKE %s
               OR pr.username_pk = %s
            ORDER BY pr.date DESC
        """, (f'%/{username}/', f'%/{username}', username))
        rows = cur.fetchall()
        if not rows:
            return [], []

        cols = list(rows[0].keys())
        return cols, [list(r.values()) for r in rows]

    except Exception as e:
        messagebox.showerror("Error", f"Query failed:\n{e}\n{traceback.format_exc()}")
        return [], []
    finally:
        cur.close()
        con.close()

def top_rated_by_genre_and_year(limit_per_group=10):
    con = get_db_connection()
    cur = con.cursor(dictionary=True)
    try:

        cur.execute("""
            SELECT 
                gg.genre_name AS genre,
                COALESCE(
                    YEAR(STR_TO_DATE(g.releasedate, '%M %d, %Y')),
                    YEAR(STR_TO_DATE(g.releasedate, '%B %d, %Y')),
                    9999
                ) AS year,
                g.moby_id,
                g.name_ AS name,
                CAST(NULLIF(g.mobyscore, '') AS DECIMAL(5,2)) AS moby_score
            FROM game_genre gg
            JOIN game g ON g.moby_id = gg.game_moby_id
            WHERE g.mobyscore REGEXP '^[0-9]+\\.?[0-9]*$'
              AND g.mobyscore IS NOT NULL
              AND g.mobyscore <> ''
              AND g.releasedate IS NOT NULL
              AND g.releasedate <> ''
        """)
        critics = cur.fetchall()

        cur.execute("""
            SELECT 
                gg.genre_name AS genre,
                COALESCE(
                    YEAR(STR_TO_DATE(g.releasedate, '%M %d, %Y')),
                    YEAR(STR_TO_DATE(g.releasedate, '%B %d, %Y')),
                    9999
                ) AS year,
                pr.moby_id,
                g.name_ AS name,
                ROUND(AVG(CAST(NULLIF(pr.score, '') AS DECIMAL(5,2))), 2) AS avg_player_score
            FROM game_genre gg
            JOIN game g ON g.moby_id = gg.game_moby_id
            JOIN player_reviews pr ON pr.moby_id = g.moby_id
            WHERE pr.score REGEXP '^[0-9]+\\.?[0-9]*$'
              AND g.releasedate IS NOT NULL
              AND g.releasedate <> ''
            GROUP BY gg.genre_name, year, pr.moby_id, g.name_
            HAVING avg_player_score IS NOT NULL
        """)
        players = cur.fetchall()

        from collections import defaultdict

        def get_top_n(data, score_key, n):
            groups = defaultdict(list)
            for row in data:
                genre = row['genre'] or 'Unknown'
                year = row['year']
                if year == 9999 or year is None:
                    year = 'No Year'
                groups[(genre, year)].append(row)

            result = []
            for items in groups.values():
                items.sort(key=lambda x: float(x[score_key] or 0), reverse=True)
                result.extend(items[:n])
            return result

        return (
            get_top_n(critics, 'moby_score', limit_per_group),
            get_top_n(players, 'avg_player_score', limit_per_group)
        )

    except Exception as e:
        messagebox.showerror("Error", f"Top rated query failed:\n{e}")
        return [], []
    finally:
        cur.close()
        con.close()

def games_for_filter(filter_type, filter_value):
    """
    Show all games for a specific genre / platform / publisher / developer.
    filter_type: 'genre' | 'platform' | 'publisher' | 'developer'
    """
    con = get_db_connection()
    cur = con.cursor()
    try:
        if filter_type == 'genre':
            sql = """
                SELECT g.moby_id, g.name_, gg.genre_name
                FROM game_genre gg
                JOIN game g ON g.moby_id = gg.game_moby_id
                WHERE gg.genre_name = %s
                ORDER BY g.name_;
            """
            cur.execute(sql, (filter_value,))
        elif filter_type == 'platform':

            sql = """
                SELECT DISTINCT g.moby_id, g.name_, r.release_platform
                FROM release_date_per_platform r
                JOIN game g ON g.moby_id = r.moby_id
                WHERE r.release_platform = %s
                ORDER BY g.name_;
            """
            cur.execute(sql, (filter_value,))
        elif filter_type == 'publisher':
            sql = """
                SELECT g.moby_id, g.name_, gp.publisher_name
                FROM game_publishers gp
                JOIN game g ON g.moby_id = gp.game_moby_id
                WHERE gp.publisher_name = %s
                ORDER BY g.name_;
            """
            cur.execute(sql, (filter_value,))
        elif filter_type == 'developer':
            sql = """
                SELECT g.moby_id, g.name_, gd.developer_name
                FROM game_developers gd
                JOIN game g ON g.moby_id = gd.game_moby_id
                WHERE gd.developer_name = %s
                ORDER BY g.name_;
            """
            cur.execute(sql, (filter_value,))
        else:
            return [], []
        cols, rows = fetch_to_table(cur)
        return cols, rows
    except Exception as e:
        messagebox.showerror("DB Error", f"Error fetching games for {filter_type} '{filter_value}':\n{e}")
        return [], []
    finally:
        cur.close()
        con.close()

def top5_games_by_genre_setting():
    con = get_db_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT 
                COALESCE(gg.genre_name, 'Unknown Genre') AS genre_name,
                COALESCE(gs.setting_name, 'Unknown Setting') AS setting_name,
                g.moby_id,
                g.name_,
                CAST(NULLIF(g.mobyscore, '') AS DECIMAL(5,2)) AS moby_score
            FROM game g
            LEFT JOIN game_genre gg ON gg.game_moby_id = g.moby_id
            LEFT JOIN game_setting gs ON gs.game_moby_id = g.moby_id
            WHERE g.mobyscore IS NOT NULL AND g.mobyscore <> '' AND g.mobyscore REGEXP '^[0-9]+\\.?[0-9]*$'
            ORDER BY gg.genre_name, gs.setting_name, moby_score DESC
        """)
        rows = cur.fetchall()

        groups = {}
        for r in rows:
            key = (r['genre_name'], r['setting_name'])
            groups.setdefault(key, []).append(r)

        result = []
        for items in groups.values():
            result.extend(sorted(items, key=lambda x: x['moby_score'] or 0, reverse=True)[:5])
        return result
    finally:
        cur.close()
        con.close()

def top5_dev_companies_by_critics_in_genre():
    con = get_db_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT 
                gg.genre_name AS genre,
                gd.developer_name AS developer,
                ROUND(AVG(CAST(NULLIF(g.mobyscore, '') AS DECIMAL(6,2))), 3) AS avg_critic_score,
                COUNT(DISTINCT g.moby_id) AS games_count
            FROM game_developers gd
            JOIN game_genre gg ON gg.game_moby_id = gd.game_moby_id
            JOIN game g ON g.moby_id = gd.game_moby_id
            WHERE g.mobyscore IS NOT NULL AND g.mobyscore <> '' AND g.mobyscore REGEXP '^[0-9]+\\.?[0-9]*$'
            GROUP BY gg.genre_name, gd.developer_name
            HAVING avg_critic_score IS NOT NULL
            ORDER BY gg.genre_name, avg_critic_score DESC
        """)
        rows = cur.fetchall()

        groups = {}
        for r in rows:
            key = r['genre'] or 'Unknown'
            groups.setdefault(key, []).append(r)

        result = []
        for items in groups.values():
            result.extend(sorted(items, key=lambda x: x['avg_critic_score'] or 0, reverse=True)[:5])
        return result
    finally:
        cur.close()
        con.close()

def dream_game_from_players(top_n_specs=1):
    """
    Dream game: create the 'perfect' game specs based on player ratings.
    Strategy:
      - Find games with highest average player ratings.
      - For top games, aggregate the most common developer, publisher, genre, setting, perspective, visual, interface.
      - Return an aggregated "spec" suggestion.
    """
    con = get_db_connection()
    cur = con.cursor(dictionary=True)
    try:

        cur.execute("""
            SELECT pr.moby_id, AVG(CAST(NULLIF(pr.score, '') AS DECIMAL(6,2))) AS avg_player_score
            FROM player_reviews pr
            WHERE pr.score IS NOT NULL AND pr.score <> ''
            GROUP BY pr.moby_id
            ORDER BY avg_player_score DESC
            LIMIT 200;
        """)
        top_games = cur.fetchall()
        if not top_games:
            return {"error": "No player-rated games found."}

        top_ids = [g['moby_id'] for g in top_games[:50]]  
        format_ids = ",".join(["%s"] * len(top_ids))

        cur.execute(f"""
            SELECT gd.developer_name, COUNT(*) AS cnt
            FROM game_developers gd
            WHERE gd.game_moby_id IN ({format_ids})
            GROUP BY gd.developer_name
            ORDER BY cnt DESC
            LIMIT 10;
        """, tuple(top_ids))
        devs = cur.fetchall()

        cur.execute(f"""
            SELECT gp.publisher_name, COUNT(*) AS cnt
            FROM game_publishers gp
            WHERE gp.game_moby_id IN ({format_ids})
            GROUP BY gp.publisher_name
            ORDER BY cnt DESC
            LIMIT 10;
        """, tuple(top_ids))
        pubs = cur.fetchall()

        cur.execute(f"""
            SELECT gg.genre_name, COUNT(*) AS cnt
            FROM game_genre gg
            WHERE gg.game_moby_id IN ({format_ids})
            GROUP BY gg.genre_name
            ORDER BY cnt DESC
            LIMIT 10;
        """, tuple(top_ids))
        genres = cur.fetchall()

        cur.execute(f"""
            SELECT gs.setting_name, COUNT(*) AS cnt
            FROM game_setting gs
            WHERE gs.game_moby_id IN ({format_ids})
            GROUP BY gs.setting_name
            ORDER BY cnt DESC
            LIMIT 10;
        """, tuple(top_ids))
        settings = cur.fetchall()

        dream = {
            'developer': devs[0]['developer_name'] if devs else None,
            'publisher': pubs[0]['publisher_name'] if pubs else None,
            'genre': genres[0]['genre_name'] if genres else None,
            'setting': settings[0]['setting_name'] if settings else None,
            'developer_top_list': [d['developer_name'] for d in devs],
            'publisher_top_list': [p['publisher_name'] for p in pubs],
            'genre_top_list': [g['genre_name'] for g in genres],
            'setting_top_list': [s['setting_name'] for s in settings],
            'recommended_based_on': f"Top {len(top_ids)} player-rated games aggregated"
        }
        return dream
    except Exception as e:
        messagebox.showerror("DB Error", f"Error generating Dream Game:\n{e}\n\n{traceback.format_exc()}")
        return {}
    finally:
        cur.close()
        con.close()

def top5_directors_by_volume():
    """Return top 5 directors by number of games (volume)."""
    con = get_db_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT c.director AS director_name, COUNT(DISTINCT c.moby_id) AS games_count
            FROM credits c
            WHERE c.director IS NOT NULL AND c.director <> ''
            GROUP BY c.director
            ORDER BY games_count DESC
            LIMIT 5;
        """)
        return cur.fetchall()
    except Exception as e:
        messagebox.showerror("DB Error", f"Error computing top directors:\n{e}")
        return []
    finally:
        cur.close()
        con.close()

def top5_director_dev_collaborations():
    con = get_db_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT 
                TRIM(c.director) AS director,
                TRIM(c.developer) AS developer,
                COUNT(DISTINCT c.moby_id) AS games_count
            FROM credits c
            WHERE c.director IS NOT NULL 
              AND c.director <> '' 
              AND c.director <> 'N/A'
              AND c.developer IS NOT NULL 
              AND c.developer <> '' 
              AND c.developer <> 'N/A'
            GROUP BY c.director, c.developer
            HAVING games_count >= 2
            ORDER BY games_count DESC
            LIMIT 10
        """)
        return cur.fetchall()
    finally:
        cur.close()
        con.close()

def games_count_by_platform_and_avg_ratings():
    """
    Number of games available on each platform and their average critics and player ratings.
    Uses release_date_per_platform to list platforms.
    """
    con = get_db_connection()
    cur = con.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT r.release_platform AS platform,
                   COUNT(DISTINCT r.moby_id) AS games_count,
                   AVG(CAST(NULLIF(g.mobyscore,'') AS DECIMAL(6,2))) AS avg_critic_score,
                   AVG(sub.avg_player_score) AS avg_player_score_over_games
            FROM release_date_per_platform r
            LEFT JOIN game g ON g.moby_id = r.moby_id
            LEFT JOIN (
                SELECT pr.moby_id, AVG(CAST(NULLIF(pr.score,'') AS DECIMAL(6,2))) AS avg_player_score
                FROM player_reviews pr
                WHERE pr.score IS NOT NULL AND pr.score <> ''
                GROUP BY pr.moby_id
            ) sub ON sub.moby_id = r.moby_id
            GROUP BY r.release_platform
            ORDER BY games_count DESC;
        """)
        return cur.fetchall()
    except Exception as e:
        messagebox.showerror("DB Error", f"Error computing platform counts and averages:\n{e}")
        return []
    finally:
        cur.close()
        con.close()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mobygames DB GUI - Fully Fixed")
        self.geometry("1200x750")

        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)
        ttk.Button(top_frame, text="RESET & POPULATE USERS FROM REVIEWS",
                  command=reset_and_populate_users_table).pack(side=tk.LEFT, padx=4)

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        frm_reg = ttk.Frame(nb)
        nb.add(frm_reg, text="Register User")
        ttk.Label(frm_reg, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=6, pady=6)
        self.reg_username = ttk.Entry(frm_reg, width=30); self.reg_username.grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(frm_reg, text="Password:").grid(row=1, column=0, sticky=tk.W, padx=6, pady=6)
        self.reg_password = ttk.Entry(frm_reg, show='*', width=30); self.reg_password.grid(row=1, column=1, padx=6, pady=6)
        ttk.Button(frm_reg, text="Register", command=self._on_register).grid(row=2, column=0, columnspan=2, pady=8)

        frm_add = ttk.Frame(nb)
        nb.add(frm_add, text="Add Player Rating")
        ttk.Label(frm_add, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=6, pady=4)
        self.add_username = ttk.Entry(frm_add, width=30); self.add_username.grid(row=0, column=1, padx=6, pady=4)
        ttk.Label(frm_add, text="Password:").grid(row=1, column=0, sticky=tk.W, padx=6, pady=4)
        self.add_password = ttk.Entry(frm_add, show='*', width=30); self.add_password.grid(row=1, column=1, padx=6, pady=4)
        ttk.Label(frm_add, text="Game moby_id:").grid(row=2, column=0, sticky=tk.W, padx=6, pady=4)
        self.add_mobyid = ttk.Entry(frm_add, width=30); self.add_mobyid.grid(row=2, column=1, padx=6, pady=4)
        ttk.Label(frm_add, text="Platform:").grid(row=3, column=0, sticky=tk.W, padx=6, pady=4)
        self.add_platform = ttk.Entry(frm_add, width=30); self.add_platform.grid(row=3, column=1, padx=6, pady=4)
        ttk.Label(frm_add, text="Score:").grid(row=4, column=0, sticky=tk.W, padx=6, pady=4)
        self.add_score = ttk.Entry(frm_add, width=10); self.add_score.grid(row=4, column=1, sticky=tk.W, padx=6, pady=4)
        ttk.Label(frm_add, text="Title:").grid(row=5, column=0, sticky=tk.W, padx=6, pady=4)
        self.add_title = ttk.Entry(frm_add, width=50); self.add_title.grid(row=5, column=1, padx=6, pady=4)
        ttk.Label(frm_add, text="Body:").grid(row=6, column=0, sticky=tk.NW, padx=6, pady=4)
        self.add_body = tk.Text(frm_add, width=60, height=6); self.add_body.grid(row=6, column=1, padx=6, pady=4)
        ttk.Button(frm_add, text="Add Rating", command=self._on_add_rating).grid(row=7, column=0, columnspan=2, pady=8)

        frm_view = ttk.Frame(nb)
        nb.add(frm_view, text="View User Ratings")
        ttk.Label(frm_view, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=6, pady=6)
        self.view_username = ttk.Entry(frm_view, width=30); self.view_username.grid(row=0, column=1, padx=6, pady=6)
        ttk.Button(frm_view, text="Show Ratings", command=self._on_view_ratings).grid(row=0, column=2, padx=6)
        self.tree_view = ttk.Treeview(frm_view)
        self.tree_view.grid(row=1, column=0, columnspan=4, sticky='nsew', padx=6, pady=6)
        frm_view.grid_rowconfigure(1, weight=1)
        frm_view.grid_columnconfigure(3, weight=1)

        frm_reports = ttk.Frame(nb)
        nb.add(frm_reports, text="Reports & Analysis")
        btns = [
            ("Top rated (critics & players) by genre/year", self._on_top_rated_by_genre_year),
            ("Games for filter (genre/platform/publisher/developer)", self._on_games_for_filter),
            ("Top 5 games per genre/setting (moby score)", self._on_top5_games_genre_setting),
            ("Top 5 dev companies by critics per genre", self._on_top5_dev_by_genre),
            ("Dream Game (from player ratings)", self._on_dream_game),
            ("Top 5 directors by volume", self._on_top5_directors),
            ("Top 5 director-dev collaborations", self._on_top5_collabs),
            ("Games per platform & avg ratings", self._on_platform_stats)
        ]
        r = 0
        for (txt, cmd) in btns:
            ttk.Button(frm_reports, text=txt, command=cmd, width=45).grid(row=r, column=0, padx=6, pady=4, sticky=tk.W)
            r += 1
        self.report_text = tk.Text(frm_reports, wrap='none', height=25, font=("Courier", 10))
        self.report_text.grid(row=0, column=1, rowspan=12, sticky='nsew', padx=6, pady=6)
        frm_reports.grid_columnconfigure(1, weight=1)
        frm_reports.grid_rowconfigure(11, weight=1)

    def _on_register(self):
        u = self.reg_username.get().strip()
        p = self.reg_password.get()
        if u and p:
            register_user(u, p)
            self.reg_username.delete(0, tk.END)
            self.reg_password.delete(0, tk.END)

    def _on_add_rating(self):
        u = self.add_username.get().strip()
        p = self.add_password.get()
        mid = self.add_mobyid.get().strip()
        plat = self.add_platform.get().strip()
        score = self.add_score.get().strip()
        title = self.add_title.get().strip()
        body = self.add_body.get("1.0", tk.END).strip()
        if u and p and mid and plat:
            add_player_rating(u, p, mid, plat, score, title, body)
        else:
            messagebox.showerror("Error", "Please fill username, password, moby_id, and platform.")

    def _on_view_ratings(self):
        username = self.view_username.get().strip()
        if not username:
            return
        cols, rows = view_user_ratings(username)
        for i in self.tree_view.get_children():
            self.tree_view.delete(i)
        if not cols:
            messagebox.showinfo("Result", f"No reviews found for '{username}'")
            return
        self.tree_view["columns"] = cols
        self.tree_view["show"] = "headings"
        for c in cols:
            self.tree_view.heading(c, text=c)
            self.tree_view.column(c, width=130)
        for row in rows:
            self.tree_view.insert("", tk.END, values=row)

    def _on_top_rated_by_genre_year(self):
        self.report_text.delete('1.0', tk.END)
        critics, players = top_rated_by_genre_and_year(5)

        print_table(self.report_text,
                    "CRITICS - TOP GAMES BY GENRE/YEAR",
                    critics,
                    headers=["Genre", "Year", "Moby ID", "Game Name", "Score"],
                    col_widths={0:20, 1:6, 2:10, 3:45, 4:8})

        print_table(self.report_text,
                    "PLAYERS - TOP GAMES BY GENRE/YEAR",
                    players,
                    headers=["Genre", "Year", "Moby ID", "Game Name", "Avg Score"],
                    col_widths={0:20, 1:6, 2:10, 3:45, 4:10})

    def _on_games_for_filter(self):
        filter_type = simpledialog.askstring("Filter", "Enter type (genre/platform/publisher/developer):")
        if not filter_type: return
        filter_type = filter_type.strip().lower()
        options = get_filter_options(filter_type)
        if not options:
            messagebox.showinfo("Info", f"No values for {filter_type}")
            return

        top = tk.Toplevel(self)
        top.title("Select value")
        ttk.Label(top, text=f"Choose {filter_type}:").pack(padx=10, pady=10)
        var = tk.StringVar(value=options[0])
        combo = ttk.Combobox(top, values=options, textvariable=var, state="readonly", width=50)
        combo.pack(padx=10, pady=5)

        def run():
            value = var.get()
            cols, rows = games_for_filter(filter_type, value)
            self.report_text.delete('1.0', tk.END)
            print_table(self.report_text,
                        f"GAMES WHERE {filter_type.upper()} = {value}",
                        rows,
                        headers=cols)
            top.destroy()

        ttk.Button(top, text="Show", command=run).pack(pady=10)

    def _on_top5_games_genre_setting(self):
        rows = top5_games_by_genre_setting()
        self.report_text.delete('1.0', tk.END)
        print_table(self.report_text,
                    "TOP 5 GAMES PER (GENRE × SETTING) BY MOBYSCORE",
                    rows,
                    headers=["Genre", "Setting", "Moby ID", "Game Name", "Score"],
                    col_widths={0:22, 1:25, 2:10, 3:42, 4:8})

    def _on_top5_dev_by_genre(self):
        rows = top5_dev_companies_by_critics_in_genre()
        self.report_text.delete('1.0', tk.END)
        print_table(self.report_text,
                    "TOP 5 DEVELOPMENT COMPANIES BY CRITIC SCORE PER GENRE",
                    rows,
                    headers=["Genre", "Developer", "Avg Score", "Games"],
                    col_widths={0:20, 1:35, 2:10, 3:8})

    def _on_dream_game(self):
        dream = dream_game_from_players()
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert(tk.END, "="*80 + "\n")
        self.report_text.insert(tk.END, "DREAM GAME RECOMMENDATION (based on highest player-rated games)\n".center(80))
        self.report_text.insert(tk.END, "="*80 + "\n\n")

        self.report_text.insert(tk.END, "RECOMMENDED SPEC:\n")
        self.report_text.insert(tk.END, f"   Developer : {dream.get('developer', 'N/A')}\n")
        self.report_text.insert(tk.END, f"   Publisher : {dream.get('publisher', 'N/A')}\n")
        self.report_text.insert(tk.END, f"   Genre     : {dream.get('genre', 'N/A')}\n")
        self.report_text.insert(tk.END, f"   Setting   : {dream.get('setting', 'N/A')}\n\n")

        self.report_text.insert(tk.END, "TOP CANDIDATES:\n")
        self.report_text.insert(tk.END, f"   Developers : {', '.join(dream.get('developer_top_list', [])[:5])}\n")
        self.report_text.insert(tk.END, f"   Publishers : {', '.join(dream.get('publisher_top_list', [])[:5])}\n")
        self.report_text.insert(tk.END, f"   Genres     : {', '.join(dream.get('genre_top_list', [])[:5])}\n")
        self.report_text.insert(tk.END, f"   Settings   : {', '.join(dream.get('setting_top_list', [])[:5])}\n\n")
        self.report_text.insert(tk.END, f"Based on top {len(dream.get('developer_top_list', []))} player-loved games.\n")

    def _on_top5_directors(self):
        rows = top5_directors_by_volume()
        self.report_text.delete('1.0', tk.END)
        print_table(self.report_text,
                    "TOP 5 DIRECTORS BY NUMBER OF GAMES",
                    rows,
                    headers=["Director", "Games Directed"],
                    col_widths={0:40, 1:15})

    def _on_top5_collabs(self):
        rows = top5_director_dev_collaborations()
        self.report_text.delete('1.0', tk.END)
        print_table(self.report_text,
                    "TOP 5 DIRECTOR × DEVELOPER COLLABORATIONS (REAL NAMES ONLY)",
                    rows,
                    headers=["Director", "Developer", "Games Together"],
                    col_widths={0:30, 1:30, 2:14})

    def _on_platform_stats(self):
        rows = games_count_by_platform_and_avg_ratings()
        self.report_text.delete('1.0', tk.END)
        print_table(self.report_text,
                    "GAMES PER PLATFORM + AVERAGE RATINGS",
                    rows,
                    headers=["Platform", "Games", "Avg Critic", "Avg Player"],
                    col_widths={0:25, 1:10, 2:12, 3:12})
if __name__ == "__main__":
    reset_and_populate_users_table()
    app = App()
    app.mainloop()