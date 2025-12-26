# Mobygames Scraping Dataset (dd)

Summary
-------

This folder contains scraped data and the scripts used to collect Mobygames information. It includes CSV datasets (per-game details, credits, contributors, prices, reviews, specs, and release dates) and Python scraper tools located in `src`.

Contents
--------

- `game_list_2020_2025.csv` — list of game names/IDs targeted for scraping (2020–2025).
- `games_data/` — CSV output files created by the scrapers:
  - `game.csv`
  - `credits.csv`
  - `contributors.csv`
  - `player_review.csv`
  - `prices.csv`
  - `release_date_per_platform.csv`
  - `specs.csv`
- `src/` — scraper and GUI scripts:
  - `APP_GUI.py` — GUI application (if present) for browsing or running scraping tasks.
  - `Crawl_games_names.py` — script to crawl and build `game_list_2020_2025.csv`.
  - `Scrape_All_Games_Data.py` — main script to scrape details for games in the list and save CSVs under `games_data/`.

Requirements
------------

- Python 3.8+ recommended.
- Common libraries often used by these scripts (install as needed):
  - `requests`
  - `beautifulsoup4`
  - `pandas`
  - `lxml`
  - `selenium` (only if a script depends on browser automation)

Install typical dependencies with:

```bash
python -m pip install requests beautifulsoup4 pandas lxml
```

Usage
-----

1. Inspect the scripts in `src/` to confirm exact dependencies and usage options. The scripts usually accept either command-line options or hard-coded settings near the top of the file.

2. To build or update the game list (if needed):

```bash
python src/Crawl_games_names.py
```

3. To run the full scraper and generate/update CSV files in `games_data/`:

```bash
python src/Scrape_All_Games_Data.py
```

4. If you prefer a GUI (if implemented):

```bash
python src/APP_GUI.py
```

Notes & Recommendations
-----------------------

- Open the scripts in `src/` and search their top sections or `if __name__ == '__main__'` blocks for required arguments and configuration (rate limits, output paths, or whether `selenium` is required).
- If scraping many pages, respect site robots/terms and add delays between requests to avoid being blocked.
- Back up the provided CSVs before re-running scrapers if you want to preserve historical data.

Want changes?
-------------

If you want, I can:

- Add exact dependency versions after inspecting the scripts.
- Add command-line examples based on the scripts' argument parsing.
- Create a `requirements.txt` automatically.

README created for: Mobygames_scrapping/dd
