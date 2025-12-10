import os, re, time, random, glob, hashlib, json
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------- CONFIG ----------------
OUTPUT_DIR = "mobygames_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

USERNAME = "cherif04444"
PASSWORD = "'X=YdNMhha895KM"

BASE_URL = "https://www.mobygames.com"
HEADLESS = False  # set to True after testing if you want headless Chrome
# ----------------------------------------

def start_browser():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1600,1000")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    prefs = {"profile.managed_default_content_settings.images": 2}
    opts.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=opts)
    return driver

def login(driver, username, password, timeout=25):
    driver.get(f"{BASE_URL}/user/login/")
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='login']")))
        driver.find_element(By.CSS_SELECTOR, "input[name='login']").clear()
        driver.find_element(By.CSS_SELECTOR, "input[name='login']").send_keys(username)
        driver.find_element(By.CSS_SELECTOR, "input[name='password']").clear()
        driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys(password)
        btns = driver.find_elements(By.XPATH, "//button[contains(.,'Login') or contains(.,'Log in')]")
        if btns:
            btns[0].click()
        else:
            driver.find_element(By.CSS_SELECTOR, "form").submit()
        WebDriverWait(driver, timeout).until_not(EC.url_contains("/user/login"))
        print("Login done.")
    except Exception as e:
        print("Login may have failed or timed out:", e)

# ------------------ Utilities ------------------

def safe_text(el):
    try:
        return el.get_text(" ", strip=True)
    except Exception:
        return ""

def get_moby_id_from_url(url: str) -> str:
    m = re.search(r"/game/(\d+)/", str(url))
    return m.group(1) if m else ""

def stable_synt_id(prefix, value):
    h = hashlib.md5(value.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}{h}"

def extract_id_from_href(href):
    if not href:
        return None
    m = re.search(r'/company/(\d+)', href)
    if m: return m.group(1)
    m = re.search(r'/person/(\d+)', href)
    if m: return m.group(1)
    m = re.search(r'/user/(\d+)', href)
    if m: return m.group(1)
    return None

# Atomic write with retry to avoid Windows lock issues
import time as _time
def write_csv_dedupe(name, rows, cols, index_cols=None, retries=3, sleep_sec=0.6):
    path = os.path.join(OUTPUT_DIR, f"{name}.csv")
    if not rows:
        if not os.path.exists(path):
            pd.DataFrame(columns=cols).to_csv(path, index=False)
        print(f"[{name}] (0 rows) -> {path}")
        return
    df = pd.DataFrame(rows).fillna("")
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df = df[cols]
    if os.path.exists(path):
        try:
            old = pd.read_csv(path, dtype=str).fillna("")
            combined = pd.concat([old, df], ignore_index=True, sort=False).fillna("")
            if index_cols:
                combined = combined.drop_duplicates(subset=index_cols)
            else:
                combined = combined.drop_duplicates()
        except Exception:
            combined = df
    else:
        combined = df
    for attempt in range(1, retries + 1):
        tmp = path + f".tmp{attempt}"
        try:
            combined.to_csv(tmp, index=False)
            os.replace(tmp, path)
            print(f"[{name}] {len(df)} rows -> {path}")
            return
        except PermissionError as e:
            try:
                if os.path.exists(tmp): os.remove(tmp)
            except Exception:
                pass
            if attempt == retries:
                print(f"write_csv_dedupe failed: {e}")
                raise
            _time.sleep(sleep_sec)

# ------------------ Parsers ------------------

def parse_overview_html(html, url):
    soup = BeautifulSoup(html, "html.parser")
    moby_id = get_moby_id_from_url(url)

    def txt(el): return el.get_text(" ", strip=True) if el else ""
    def join_links(scope):
        return "; ".join(a.get_text(strip=True) for a in scope.select("a")) if scope else ""

    # Name
    name = txt(soup.select_one("h1.mb-0"))

    # Released: first dd in .info-release
    releasedate, releaseplatform = "", ""
    rel_dd = soup.select_one(".info-release dl.metadata dd")
    if rel_dd:
        anchors = rel_dd.select("a")
        if anchors:
            releasedate = txt(anchors[0])
            releaseplatform = txt(anchors[-1])

    # Fallback platforms list
    if not releaseplatform:
        plats = []
        for li in soup.select("#platformLinks li"):
            p = txt(li.select_one("span a")) or txt(li.select_one("a[href*='/platform/']"))
            if p: plats.append(p)
        if plats:
            releaseplatform = "; ".join(dict.fromkeys(plats))

    # Publishers and Developers
    publishers = "; ".join(a.get_text(strip=True) for a in soup.select("#publisherLinks a"))
    developers = "; ".join(a.get_text(strip=True) for a in soup.select("#developerLinks a"))

    # Scores and ranking
    mobyscore = txt(soup.select_one(".info-score .mobyscore"))
    rank, total = "", ""
    small_node = soup.select_one(".info-score dd small.text-muted")
    small = txt(small_node)
    if small and "#" in small and "of" in small:
        try:
            rank = small.split("#",1)[1].split("of",1)[0].strip()
            total = small.split("of",1)[1].strip()
        except Exception:
            pass

    # Per-platform rankings
    ranking_windows = ranking_ps5 = ranking_xbox = ""
    for li in soup.select("#platformRankings li"):
        n = txt(li.select_one("span"))
        plat = txt(li.select_one("a[href*='/platform/']"))
        if not n or not plat:
            continue
        if "Windows" in plat:
            ranking_windows = n
        elif "PlayStation 5" in plat:
            ranking_ps5 = n
        elif "Xbox Series" in plat:
            ranking_xbox = n

    # Collected by
    collectedby = ""
    for dt in soup.select(".info-score dt"):
        if txt(dt).lower() == "collected by":
            dd = dt.find_next_sibling("dd")
            collectedby = txt(dd)
            if collectedby.endswith("players"):
                collectedby = collectedby.replace("players","").strip()
            break

    # Facets
    def facet_value(label):
        for dt in soup.select(".info-genres dt"):
            if label.lower() == dt.get_text(strip=True).lower():
                dd = dt.find_next_sibling("dd")
                return "; ".join(a.get_text(strip=True) for a in dd.select("a")) if dd else ""
        return ""

    genre_main  = facet_value("Genre")
    perspective = facet_value("Perspective")
    visual      = facet_value("Visual")
    pacing      = facet_value("Pacing")
    interface   = facet_value("Interface")
    setting     = facet_value("Setting")
    misc        = facet_value("Misc")

    # Overview specs
    def dd_after(label):
        for dt in soup.select(".info-specs dt"):
            if label.lower() == dt.get_text(strip=True).lower():
                return dt.find_next_sibling("dd")
        return None

    esrb = txt(dd_after("ESRB Rating"))
    business_model = join_links(dd_after("Business Model"))
    media_type = join_links(dd_after("Media Type"))

    return {
        "moby_id": moby_id,
        "name": name,
        "releasedate": releasedate,
        "releaseplatform": releaseplatform,
        "publishers": publishers,
        "developers": developers,
        "mobyscore": mobyscore,
        "rank": rank,
        "total": total,
        "collectedby": collectedby,
        "ranking_windows": ranking_windows,
        "ranking_ps5": ranking_ps5,
        "ranking_xbox": ranking_xbox,
        "ranking_macintosh": "",
        "ranking_nintendo": "",
        "genre": genre_main,
        "Genre": "",
        "Perspective": perspective,
        "Visual": visual,
        "Pacing": pacing,
        "Interface": interface,
        "Setting": setting,
        "Misc": misc,
        "ESRB Rating": esrb,
        "Business Model": business_model,
        "Media Type": media_type
    }

import re

# Accept: director, directors, directed, directing, direction, directorial, co-director, co directed
RE_DIRECT  = re.compile(r'\b(?:co-?\s*)?direct\w*\b', re.IGNORECASE)   # [attached_file:1]
# Accept producer, producers, produced, producing, production, productions; exclude product/products
RE_PRODUCE = re.compile(r'\b(?:co-?\s*)?produc(?!t)\w*\b', re.IGNORECASE)  # [attached_file:1]
# Accept developer, developers, developed, developing, development, developments; allow co-develop
RE_DEVELOP = re.compile(r'\b(?:co-?\s*)?develop\w*\b', re.IGNORECASE)  # [attached_file:1]

def first_verb_like(pattern: re.Pattern, *texts: str) -> bool:
    return any(t and pattern.search(t) for t in texts)  # [attached_file:1]

def parse_credits_html(html, url):
    soup = BeautifulSoup(html, "html.parser")
    moby_game_id = get_moby_id_from_url(url)

    credits = {
        "moby_id": moby_game_id,
        "platform": "",
        "director": "", "director_ID": "",
        "producer": "", "producer_ID": "",
        "developer": "", "developer_ID": ""
    }

    # platform header
    h2 = soup.find("h2", string=re.compile("credits", re.IGNORECASE))   # [attached_file:1]
    if h2:
        m = re.search(r"^([A-Za-z0-9 \-+]+)\s+credits", h2.get_text(strip=True))
        if m:
            credits["platform"] = m.group(1).strip()

    found = {"director": False, "producer": False, "developer": False}

    for tr in soup.select("table.table-credits tr"):  # [attached_file:1]
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue

        role_text  = tds[0].get_text(" ", strip=True)
        right_text = tds[1].get_text(" ", strip=True)

        a = tds[1].find("a", href=True)
        if not a:
            continue

        name = a.get_text(strip=True)
        pid_match = re.search(r"/person/(\d+)/", a["href"])
        pid = pid_match.group(1) if pid_match else ""

        if not found["director"] and first_verb_like(RE_DIRECT, role_text, right_text):
            credits["director"] = name
            credits["director_ID"] = pid
            found["director"] = True
        elif not found["producer"] and first_verb_like(RE_PRODUCE, role_text, right_text):
            credits["producer"] = name
            credits["producer_ID"] = pid
            found["producer"] = True
        elif not found["developer"] and first_verb_like(RE_DEVELOP, role_text, right_text):
            credits["developer"] = name
            credits["developer_ID"] = pid
            found["developer"] = True

        if all(found.values()):
            break

    return credits

def parse_contributor_html(html, url):
    soup = BeautifulSoup(html, "html.parser")
    m = re.search(r"/person/(\d+)/", url)
    person_id = m.group(1) if m else ""

    name = ""
    name_el = soup.select_one("h1, .page-title")
    if name_el:
        name = name_el.get_text(strip=True)

    overview = ""
    bio_section = soup.select_one("#developerBiography #description-text")
    if bio_section:
        overview = bio_section.get_text(" ", strip=True)

    related_sites = []
    for li in soup.select("#relatedSites li a[href]"):
        href = li["href"].strip()
        label = li.get_text(strip=True)
        related_sites.append(f"{label}: {href}")
    related_sites_str = "; ".join(related_sites)

    return {
        "moby_id": person_id,
        "name": name,
        "overview": overview,
        "Related Sites": related_sites_str,
    }

def parse_specs_html(html, url):
    soup = BeautifulSoup(html, "html.parser")
    moby_id = get_moby_id_from_url(url)

    base_row = {
        "moby_id": moby_id,
        "platform": "",
        "Business Model": "",
        "min_os": "",
        "supported_system": "",
        "min_ram": "",
        "supported_drivers": "",
        "media_type": "",
        "gamepads_Supported": "",
    }

    label_map = {
        "business model": "Business Model",
        "minimum os class required": "min_os",
        "supported systems/models": "supported_system",
        "minimum ram required": "min_ram",
        "drivers/apis supported": "supported_drivers",
        "media type": "media_type",
        "gamepads supported": "gamepads_Supported",
    }

    def cell_links(td):
        links = [a.get_text(strip=True) for a in td.select("a")]
        return "; ".join([x for x in links if x]) or td.get_text(" ", strip=True)

    out = []
    current = dict(base_row)

    for tr in soup.select("table tr"):
        header = tr.select_one("h4")
        if header:
            if any(current.get(k) for k in base_row if k not in ("moby_id", "platform")):
                out.append(current)
            current = dict(base_row)
            current["platform"] = header.get_text(strip=True)
            continue

        tds = tr.find_all("td")
        if len(tds) != 2:
            continue

        label = tds[0].get_text(" ", strip=True)
        norm = label.rstrip(":").strip().lower()
        key = label_map.get(norm)
        if not key:
            continue

        current[key] = cell_links(tds[1])

    if any(current.get(k) for k in base_row if k not in ("moby_id", "platform")):
        out.append(current)

    return out

def parse_prices_html(html, url):
    soup = BeautifulSoup(html, "html.parser")
    moby_id = get_moby_id_from_url(url)
    price_rows = []

    table = soup.select_one("main table") or soup.select_one("table")
    if not table:
        return price_rows

    for tr in table.select("tr"):
        tds = tr.find_all("td")
        if len(tds) < 6:
            continue

        store_a = tds[0].find("a")
        store = store_a.get_text(strip=True) if store_a else tds[0].get_text(strip=True)

        platform = tds[1].get_text(strip=True)
        fmt = tds[2].get_text(strip=True)

        used_a = tds[3].find("a")
        used_price_url = used_a["href"].strip() if used_a and used_a.has_attr("href") else ""
        used_price_text = used_a.get_text(strip=True) if used_a else ""

        new_a = tds[4].find("a")
        new_price_url = new_a["href"].strip() if new_a and new_a.has_attr("href") else ""
        new_price_text = new_a.get_text(strip=True) if new_a else ""

        updated_date = tds[-1].get_text(strip=True)

        price_rows.append({
            "moby_id": moby_id,
            "store": store,
            "platform": platform,
            "format": fmt,
            "used_price_url": used_price_url or used_price_text,
            "new_price_url": new_price_url or new_price_text,
            "updated_date": updated_date,
        })

    return price_rows

def parse_release_dates_html(html, url):
    soup = BeautifulSoup(html, "html.parser")
    moby_id = get_moby_id_from_url(url)
    game_name = safe_text(soup.select_one("h1")) or ""
    rows = []

    for block in soup.select("section#releaseInfo, div#releaseInfo, table.release-info, div.release-info"):
        for tr in block.select("tr"):
            tds = tr.find_all(["td", "th"])
            if len(tds) >= 2:
                platform = safe_text(tds[0])
                date = safe_text(tds[1])
                if platform and date:
                    rows.append({
                        "moby_id": moby_id,
                        "game_name": game_name,
                        "release_platform": platform,
                        "release_date": date
                    })

    if not rows:
        for row in soup.select("div.release, li.release, p:has(time)"):
            platform = safe_text(row.select_one("b, strong, .platform"))
            date = safe_text(row.select_one("time, .date"))
            if platform and date:
                rows.append({
                    "moby_id": moby_id,
                    "game_name": game_name,
                    "release_platform": platform,
                    "release_date": date
                })

    if not rows:
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and "gamePlatform" in data:
                    platforms = data.get("gamePlatform", [])
                    if isinstance(platforms, str):
                        platforms = [platforms]
                    date = data.get("datePublished", "")
                    for p in platforms:
                        rows.append({
                            "moby_id": moby_id,
                            "game_name": data.get("name", game_name),
                            "release_platform": p,
                            "release_date": date
                        })
            except Exception:
                pass

    return rows

# -------- Reviews helpers --------

def _get_moby_id(url: str) -> str:
    m = re.search(r"/game/(\d+)/", url)
    return m.group(1) if m else ""

def _platform_from_reviews(url, soup):
    m = re.search(r"/reviews/([^/?#]+)/?", url)
    if m:
        slug = m.group(1).replace("-", " ").strip().lower()
        return {
            "windows": "Windows",
            "macintosh": "Macintosh",
            "stadia": "Stadia",
            "playstation 5": "PlayStation 5",
            "xbox series": "Xbox Series",
            "nintendo switch": "Nintendo Switch",
            "playstation 4": "PlayStation 4",
            "xbox one": "Xbox One",
            "ios": "iOS",
            "android": "Android",
        }.get(slug, slug.title())
    if soup.title:
        t = soup.title.get_text(strip=True)
        mm = re.search(r"reviews?\s*\(([^,]+)", t, re.I)
        if mm:
            return mm.group(1).strip()
    return ""

import random

def parse_reviews_dynamic(driver, url):
    moby_id = _get_moby_id(url)
    platform = _platform_from_reviews(url, BeautifulSoup(driver.page_source, "html.parser"))

    critic_rows, player_rows = [], []

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#critics table tbody tr"))
        )
        all_rows = driver.find_elements(By.CSS_SELECTOR, "#critics table tbody tr")

        if not all_rows:
            print("⚠️ No critic rows found.")
        else:
            sample = random.sample(all_rows, min(15, len(all_rows)))
            for tr in sample:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", tr)
                    time.sleep(0.3)
                    tr.click()

                    WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal.show, .critic-review-text"))
                    )

                    modal = None
                    try:
                        modal = driver.find_element(By.CSS_SELECTOR, ".modal.show")
                    except Exception:
                        pass

                    if modal:
                        text = modal.find_element(By.CSS_SELECTOR, ".modal-body").text
                        links = modal.find_elements(By.CSS_SELECTOR, "a[href^='http']")
                        review_url = links[0].get_attribute("href") if links else ""
                        date_el = modal.find_elements(By.CSS_SELECTOR, "time, .text-muted")
                        date = date_el[0].text if date_el else ""
                        modal.find_element(By.CSS_SELECTOR, "button.close, .btn-close").click()
                    else:
                        text_el = driver.find_elements(By.CSS_SELECTOR, ".critic-review-text")
                        text = text_el[-1].text if text_el else ""
                        links = tr.find_elements(By.CSS_SELECTOR, "a[href^='http']")
                        review_url = links[-1].get_attribute("href") if links else ""
                        date = ""

                    tds = tr.find_elements(By.CSS_SELECTOR, "td")
                    source = tds[0].text.strip() if len(tds) >= 1 else ""
                    platform_text = tds[1].text.strip() if len(tds) >= 2 else platform
                    score = tds[2].text.strip() if len(tds) >= 3 else ""

                    critic_rows.append({
                        "text": text.strip(),
                        "pk url": review_url.strip(),
                        "score": score,
                        "date": date.strip(),
                        "source": source,
                        "platform": platform_text,
                        "moby_id": moby_id
                    })
                    time.sleep(0.5)

                except Exception as e:
                    print(f"❌ Failed to extract one critic review: {e}")
                    continue

    except Exception as e:
        print("⚠️ Critic section not found:", e)

    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for block in soup.select("#players .border.mb"):
            title_el = block.select_one("b a")
            title = title_el.get_text(strip=True) if title_el else ""

            user_el = block.find("a", href=re.compile(r"/user/"))
            username = user_el.get_text(strip=True) if user_el else ""
            user_url = urljoin(BASE_URL, user_el["href"]) if user_el else ""

            score_el = block.select_one(".stars")
            score = score_el["data-tooltip"].replace("stars", "").strip() if score_el and score_el.has_attr("data-tooltip") else ""

            body = safe_text(block.select_one(".toggle-text-review"))

            player_rows.append({
                "username": username,
                "username pk": user_url,
                "title": title,
                "body": body,
                "score": score,
                "platform": platform,
                "date": "",
                "moby_id": moby_id
            })
    except Exception as e:
        print("⚠️ Player review extraction failed:", e)

    return critic_rows, player_rows

def collect_urls_from_lists():
    target = "game_list_2020_2025_onepage.csv"
    all_urls = []
    try:
        df = pd.read_csv(target)
        if "url" in df.columns:
            all_urls = df["url"].dropna().astype(str).tolist()
        else:
            print(f"{target} exists but has no 'url' column.")
    except FileNotFoundError:
        print(f"{target} not found. Make sure it is in the working directory.")
        return []
    except Exception as e:
        print(f"Error reading {target}: {e}")
        return []
    seen = set()
    uniq = []
    for u in all_urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq

# ---------------- Columns Definitions ------------------

game_cols = [
    "moby_id", "name", "releasedate", "releaseplatform", "publishers", "developers", 
    "mobyscore", "rank", "total", "collectedby", "ranking_windows", "ranking_ps5", 
    "ranking_xbox", "ranking_macintosh", "ranking_nintendo", "genre", "Genre", 
    "Perspective", "Visual", "Pacing", "Interface", "Setting", "Misc", "ESRB Rating", 
    "Business Model", "Media Type"
]
credits_cols = [
    "platform", "moby_id",
    "director", "director_ID",
    "producer", "producer_ID",
    "developer", "developer_ID"
]
contributors_cols = ["moby_id", "name", "overview", "Related Sites"]
specs_cols = [
    "moby_id", "platform", "Business Model", "min_os", "supported_system", "min_ram", 
    "supported_drivers", "media_type", "gamepads_Supported"
]
price_cols = [
    "moby_id", "store", "platform", "format", "used_price_url", "new_price_url", "updated_date"
]
critic_cols = ["text", "pk url", "score", "date", "source", "platform", "moby_id"]
player_cols = ["username pk", "title", "body", "score", "platform", "date", "moby_id"]

def parse_player_reviews_static(driver, url):
    moby_id = _get_moby_id(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    platform = _platform_from_reviews(url, soup)

    player_rows = []
    for block in soup.select("#players .border.mb"):
        title_el = block.select_one("b a")
        title = title_el.get_text(strip=True) if title_el else ""

        user_el = block.find("a", href=re.compile(r"/user/"))
        username = user_el.get_text(strip=True) if user_el else ""
        user_url = urljoin(BASE_URL, user_el["href"]) if user_el else ""

        score_el = block.select_one(".stars")
        score = score_el["data-tooltip"].replace("stars", "").strip() if score_el and score_el.has_attr("data-tooltip") else ""

        body = safe_text(block.select_one(".toggle-text-review"))

        player_rows.append({
            "username": username,
            "username pk": user_url,
            "title": title,
            "body": body,
            "score": score,
            "platform": platform,
            "date": "",
            "moby_id": moby_id
        })

    return player_rows

# -------- Credits platform discovery and crawl --------

PLATFORM_SLUGS_PRIORITY = [
    "windows",
    "macintosh",
    "playstation-5",
    "playstation-4",
    "nintendo-switch",
    "ios",
    "iphone",
]

def build_platform_credit_urls(base_game_url):
    base = base_game_url.rstrip("/")
    return [f"{base}/credits/{slug}/" for slug in PLATFORM_SLUGS_PRIORITY]

def find_platform_credit_links_in_page(html, current_url):
    """
    Parse the <p class="mb"> platform switcher in the credits page.
    - Includes the current platform (bold, no link)
    - Includes all other platform links (<a href="/game/.../credits/.../">)
    - Ignores 'add' or rel="nofollow" links
    Returns absolute URLs.
    """
    soup = BeautifulSoup(html, "html.parser")
    urls = set()
    base = current_url.split("?")[0].rstrip("/") + "/"

    p_block = soup.select_one("p.mb")
    if not p_block:
        return [base]

    for span in p_block.select("span.text-nowrap"):
        a = span.find("a", href=True)
        if a:
            href = a["href"].strip()
            # Skip 'add' or rel="nofollow" links
            if a.get("rel") and "nofollow" in a.get("rel", []):
                continue
            if "/credits/" in href:
                urls.add(urljoin(current_url, href.split("?")[0].rstrip("/") + "/"))
        else:
            # Handle bold (current platform)
            b = span.find("b")
            if b and "credits" not in base:
                urls.add(base)

    if not urls:
        urls.add(base)

    return sorted(urls)




def scrape_all_platform_credits(driver, base_game_url):
    """
    Discover and scrape all platform credits dynamically based on the <p class="mb"> block.
    Handles both current and linked platform pages.
    """
    all_credit_rows = []
    seen_urls = set()

    # The initial (current) credits page — typically "Windows" or whatever exists first
    initial_credits_url = base_game_url.rstrip("/") + "/credits/"
    print(" → Checking credits root:", initial_credits_url)

    try:
        driver.get(initial_credits_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(random.uniform(0.8, 1.5))
    except Exception as e:
        print(f"⚠️ Failed to load initial credits: {e}")
        return all_credit_rows

    # Discover all available platform credit URLs from the <p class="mb"> element
    platform_urls = find_platform_credit_links_in_page(driver.page_source, initial_credits_url)
    print(f"   → Found {len(platform_urls)} platform credit URLs:")
    for u in platform_urls:
        print("     ", u)

    # Crawl each discovered platform credit page
    for cu in platform_urls:
        if cu in seen_urls:
            continue
        seen_urls.add(cu)

        try:
            print("   → Visiting credits page:", cu)
            driver.get(cu)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(random.uniform(0.8, 1.8))

            row = parse_credits_html(driver.page_source, cu)
            if row and any([row.get("director"), row.get("producer"), row.get("developer")]):
                all_credit_rows.append(row)

            # Optional: discover any new URLs (the other platform may link back)
            new_urls = find_platform_credit_links_in_page(driver.page_source, cu)
            for n in new_urls:
                if n not in seen_urls:
                    platform_urls.append(n)

        except Exception as e:
            print(f"   ⚠️ Failed credits page {cu}: {e}")
            continue

    return all_credit_rows

# ---------------- Main ----------------

def main(max_games=None):
    urls = collect_urls_from_lists()
    print(f"Found {len(urls)} unique URLs to scrape.")
    if max_games:
        urls = urls[:max_games]

    driver = start_browser()
    try:
        try:
            login(driver, USERNAME, PASSWORD)
        except Exception:
            pass

        bucket = {
            "game": [],
            "credits": [],
            "specs": [],
            "prices": [],
            "player_review": [],
            "contributors": [],
            "release_date_per_platform": []
        }

        for i, url in enumerate(urls, start=1):
            if i % 80 == 0:
                print("♻️ Restarting browser to prevent timeouts...")
                driver.quit()
                time.sleep(3)
                driver = start_browser()
                login(driver, USERNAME, PASSWORD)
            try:
                print(f"\n[{i}/{len(urls)}] Overview -> {url}")
                driver.get(url)
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                game_row = parse_overview_html(driver.page_source, url) or {}

                # Release dates
                release_rows = parse_release_dates_html(driver.page_source, url)
                if release_rows:
                    bucket.setdefault("release_date_per_platform", []).extend(release_rows)

                # Credits across requested platforms + discovered
                credit_rows = scrape_all_platform_credits(driver, url)
                if credit_rows:
                    bucket.setdefault("credits", []).extend(credit_rows)

                    # Collect contributor IDs across all platforms for this game
                    contributor_ids = set()
                    for r in credit_rows:
                        for k, v in r.items():
                            if isinstance(k, str) and k.endswith("_ID") and v:
                                contributor_ids.add(str(v).strip())

                    for pid in sorted(contributor_ids):
                        contrib_url = f"{BASE_URL}/person/{pid}/"
                        print(f"   → Contributor profile: {contrib_url}")
                        try:
                            driver.get(contrib_url)
                            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                            time.sleep(random.uniform(1.0, 1.8))
                            contrib_data = parse_contributor_html(driver.page_source, contrib_url)
                            if contrib_data:
                                bucket.setdefault("contributors", []).append(contrib_data)
                        except Exception as e:
                            print(f"   ⚠️ Failed to extract contributor {pid}: {e}")
                            continue

                # Specs
                specs_url = url.rstrip("/") + "/specs/"
                print(" → Specs:", specs_url)
                driver.get(specs_url)
                time.sleep(random.uniform(0.8, 1.8))
                specs_rows = parse_specs_html(driver.page_source, specs_url)
                for s in specs_rows:
                    bucket.setdefault("specs", []).append(s)

                # Prices
                stores_url = url.rstrip("/") + "/stores/"
                print(" → Stores:", stores_url)
                driver.get(stores_url)
                time.sleep(random.uniform(0.8, 1.8))
                price_rows = parse_prices_html(driver.page_source, stores_url)
                for pr in price_rows:
                    bucket.setdefault("prices", []).append(pr)

                # Reviews summary
                reviews_url = url.rstrip("/") + "/reviews/"
                print(" → Reviews:", reviews_url)
                driver.get(reviews_url)
                time.sleep(4)

                html_rendered = driver.execute_script("return document.body.innerHTML;")
                with open("mobygames_reviews_rendered.html", "w", encoding="utf-8") as f:
                    f.write(html_rendered)
                soup = BeautifulSoup(html_rendered, "html.parser")

                critics_overall_rating = ""
                critics_total_reviews = ""
                players_overall_rating = ""
                players_total_reviews = ""

                critics_section = soup.select_one("#critics p")
                if critics_section:
                    text = critics_section.get_text(" ", strip=True)
                    m1 = re.search(r"Average score[:\s]*([0-9.]+%?)", text)
                    m2 = re.search(r"based on\s+(\d+)\s+ratings?", text)
                    if m1:
                        critics_overall_rating = m1.group(1)
                    if m2:
                        critics_total_reviews = m2.group(1)

                players_section = soup.select_one("#players p")
                if players_section:
                    text = players_section.get_text(" ", strip=True)
                    m3 = re.search(r"Average score[:\s]*([0-9.]+)", text)
                    m4 = re.search(r"based on\s+(\d+)\s+ratings", text)
                    if m3:
                        players_overall_rating = m3.group(1)
                    if m4:
                        players_total_reviews = m4.group(1)

                game_row.update({
                    "critics_overall_rating": critics_overall_rating,
                    "critics_total_reviews": critics_total_reviews,
                    "players_overall_rating": players_overall_rating,
                    "players_total_reviews": players_total_reviews
                })
                bucket["game"].append(game_row)

                # Player reviews (static)
                print(" → Extracting player reviews...")
                player_rows = parse_player_reviews_static(driver, reviews_url)
                print(f"   -> Found {len(player_rows)} player reviews.")
                bucket["player_review"].extend(player_rows)

                time.sleep(random.uniform(0.8, 1.5))

            except Exception as e:
                print("Error scraping", url, ":", e)
                continue

        # --- Write CSVs ---
        write_csv_dedupe("game", bucket["game"], game_cols + [
            "critics_overall_rating", "critics_total_reviews",
            "players_overall_rating", "players_total_reviews"
        ], index_cols=["moby_id"])
        write_csv_dedupe("credits", bucket["credits"], credits_cols, index_cols=["platform", "moby_id"])
        write_csv_dedupe("specs", bucket["specs"], specs_cols, index_cols=["moby_id", "platform"])
        write_csv_dedupe("prices", bucket["prices"], price_cols, index_cols=["moby_id", "store", "platform", "format", "updated_date"])
        write_csv_dedupe("player_review", bucket["player_review"], player_cols, index_cols=["username pk", "moby_id", "date"])
        release_cols = ["moby_id", "game_name", "release_platform", "release_date"]
        write_csv_dedupe("release_date_per_platform", bucket.get("release_date_per_platform", []),
                        release_cols, index_cols=["moby_id", "release_platform"])
        write_csv_dedupe("contributors", bucket.get("contributors", []), ["moby_id", "name", "overview", "Related Sites"], index_cols=["moby_id"])

        print("\n✅ Scraping finished. CSVs in:", OUTPUT_DIR)

    finally:
        driver.quit()

if __name__ == "__main__":
    main(max_games=306)
