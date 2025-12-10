from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time, random, re

BASE_URL = "https://www.mobygames.com"
USERNAME = "cherif04444"
PASSWORD = "'X=YdNMhha895KM"  # replace with your real password if needed

# --------------------------- Setup ---------------------------

def start_browser():
    opts = Options()
    # opts.add_argument("--headless=new")  # uncomment for headless mode
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=opts)

# --------------------------- Login ---------------------------

def login(driver, username, password, timeout=40):
    print("🔐 Logging in to MobyGames...")
    driver.get(f"{BASE_URL}/user/login/")

    # Handle cookie banner if present
    try:
        consent = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Accept') or contains(.,'Agree')]"))
        )
        consent.click()
        print("🍪 Accepted cookie banner.")
    except:
        pass

    # Fill the login form
    login_input = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input#login[name='login']"))
    )
    pass_input = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input#password[name='password']"))
    )

    login_input.clear(); login_input.send_keys(username)
    pass_input.clear(); pass_input.send_keys(password)

    # Click "Login"
    submit_btn = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn-primary') and normalize-space()='Login']"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
    submit_btn.click()

    # Wait for redirect and confirmation
    WebDriverWait(driver, timeout).until_not(EC.url_contains("/user/login"))
    WebDriverWait(driver, timeout).until(
        EC.any_of(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/user/logout']")),
            EC.presence_of_element_located((By.CSS_SELECTOR, ".dropdown-profile"))
        )
    )
    print("✅ Login successful!")

# --------------------------- Helpers ---------------------------

def wait_for_initial_games(driver):
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/game/']"))
    )

def parse_games_from_dom(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    games = []
    for a in soup.select("a[href*='/game/']"):
        href = a.get("href", "")
        if re.search(r"/game/\d+/", href):
            title = a.get_text(strip=True)
            if title:
                full_url = href if href.startswith("http") else BASE_URL + href
                games.append({"title": title, "url": full_url})
    return games

def find_next_button_standard(driver):
    xpaths = [
        "//button[normalize-space()='Next']",
        "//a[normalize-space()='Next']",
        "//button[@aria-label='Next']",
        "//a[@aria-label='Next']",
        "//div[contains(@class,'pagination')]//button[normalize-space()='Next']",
        "//div[contains(@class,'pagination')]//a[normalize-space()='Next']",
    ]
    for xp in xpaths:
        try:
            btn = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, xp)))
            return btn
        except:
            pass
    return None

def find_next_button_shadow(driver):
    script = """
    const host = document.querySelector('game-browser, moby-game-browser, moby-game-list, [data-component="game-browser"]');
    if (!host) return null;
    const root = host.shadowRoot || host;
    if (!root) return null;
    const candidates = [
      "button[aria-label='Next']",
      "a[aria-label='Next']",
      ".pagination button[aria-label='Next']",
      ".pagination a[aria-label='Next']",
      "button.next, a.next"
    ];
    for (const sel of candidates) {
      const el = root.querySelector(sel);
      if (el) return el;
    }
    for (const el of root.querySelectorAll('button,a')) {
      const t = (el.innerText || el.textContent || '').trim();
      if (/^next$/i.test(t)) return el;
    }
    return null;
    """
    try:
        return driver.execute_script(script)
    except:
        return None

def click_next_until_end(driver, max_clicks=50):
    """Scrolls/clicks through game pages, limited to max_clicks (pages)."""
    seen = set()
    all_games = []

    # Start with first page
    current = parse_games_from_dom(driver)
    for g in current:
        if g["url"] not in seen:
            seen.add(g["url"])
            all_games.append(g)

    for i in range(max_clicks):
        btn = find_next_button_standard(driver) or find_next_button_shadow(driver)
        if not btn:
            print(f"🛑 No Next button found after {i} clicks — stopping.")
            break

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        time.sleep(random.uniform(0.3, 0.6))
        try:
            btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", btn)

        # Wait for new content
        start = time.time()
        new_found = False
        while time.time() - start < 15:
            time.sleep(0.5)
            cur = parse_games_from_dom(driver)
            added = 0
            for g in cur:
                if g["url"] not in seen:
                    seen.add(g["url"])
                    all_games.append(g)
                    added += 1
            if added > 0:
                print(f"➡️ Click {i+1}: {added} new games (total {len(all_games)})")
                new_found = True
                break

        if not new_found:
            again = find_next_button_standard(driver) or find_next_button_shadow(driver)
            if again is None:
                print("✅ Reached last page — stopping.")
                break
            print("⏳ No new items after click; retrying once more.")
            time.sleep(1.0)

    return all_games

# --------------------------- Scraping ---------------------------

def scrape_range(driver, start_year=2020, end_year=2025, max_pages=50, out_name=None):
    """Open one combined browser view for 2020..2025 and paginate up to max_pages."""
    if out_name is None:
        out_name = f"game_list_{start_year}_{end_year}.csv"

    print(f"\n🕹️ Scraping combined range {start_year}–{end_year} (logged-in pagination)...")
    # Single filter URL using from: and until: in one query
    url = (
        f"{BASE_URL}/game/"
        f"from:{start_year}/until:{end_year}/"
        f"include_dlc:false/include_nsfw:false/release_status:all/"
        f"sort:moby_score/"
    )
    driver.get(url)
    wait_for_initial_games(driver)

    all_games = click_next_until_end(driver, max_clicks=max_pages)

    # Deduplicate and write once
    df = pd.DataFrame(all_games).drop_duplicates(subset=["url"])
    df.to_csv(out_name, index=False)
    print(f"🎯 Combined range {start_year}–{end_year}: scraped {len(df)} total games into {out_name}.")
    return df

def main():
    driver = start_browser()
    try:
        login(driver, USERNAME, PASSWORD)
        scrape_range(driver, start_year=2020, end_year=2025, max_pages=50, out_name="game_list_2020_2025_onepage.csv")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
