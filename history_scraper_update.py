import requests
from lxml import html
import csv
import re
from datetime import datetime, date
import os

HEADERS = {"User-Agent": "Mozilla/5.0"}
BASE_URL = "https://www.beatlottery.co.uk/eurojackpot/draw-history"
CSV_FILE = "history.csv"

def get_latest_year_from_website():
    """Findet das aktuellste verfügbare Jahr direkt auf der Website."""
    print(f"Ermittle aktuellstes Jahr von {BASE_URL} …")
    resp = requests.get(BASE_URL, headers=HEADERS)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    tree = html.fromstring(resp.text)
    # XPath laut Vorgabe:
    year_text = tree.xpath('/html/body/section/div/div/div/div/div[1]/div/div/div/div/article/div/div[2]/div[1]/div/div/a[1]/text()')
    if not year_text:
        raise RuntimeError("Konnte aktuelles Jahr nicht auf der Website finden.")
    year = int(re.search(r"\d{4}", year_text[0]).group())
    print(f"Aktuellstes Jahr laut Website: {year}")
    return year


def scrape_year(year):
    url = f"{BASE_URL}/year/{year}"
    print(f"Lade Jahr {year} … ({url})")
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    tree = html.fromstring(resp.text)
    
    rows = tree.xpath('//tr[td/div[@class="results-ball-box"]]')
    print(f"  Gefundene Ziehungen Jahr {year}: {len(rows)}")
    
    results = []
    for row in rows:
        try:
            date_text = row.xpath('./td[2]/text()')[0].strip()
            spans = row.xpath('./td[4]/div/span')
            numbers = [int(s.text.strip()) for s in spans if s.text and s.text.strip().isdigit()]
            main_numbers = numbers[:5]
            euro_numbers = numbers[5:7]
            results.append([date_text] + main_numbers + euro_numbers)
        except Exception as e:
            print(f"  Fehler beim Parsen einer Zeile: {e}")
    return results


def parse_date(date_text):
    if not date_text:
        return None
    s = date_text.strip().replace('.', '/').replace('-', '/')
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except Exception:
        pass
    fmts = ["%d %B %Y", "%d %b %Y", "%Y/%m/%d", "%Y-%m-%d"]
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue
    m = re.search(r"(\d{1,2})\D+(\d{1,2})\D+(\d{4})", s)
    if m:
        d, mth, y = m.group(1), m.group(2), m.group(3)
        try:
            return date(int(y), int(mth), int(d))
        except Exception:
            return None
    return None


def load_existing_results():
    """Lade vorhandene history.csv, falls vorhanden."""
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if len(rows) <= 1:
        return []
    return rows[1:]  # Header überspringen


def main():
    # Vorhandene Daten laden
    existing = load_existing_results()
    existing_dates = {r[0].strip() for r in existing}
    print(f"Vorhandene Einträge: {len(existing_dates)}")

    # Aktuellstes Jahr von Website abrufen
    try:
        latest_year = get_latest_year_from_website()
    except Exception as e:
        print(f"Fehler beim Ermitteln des aktuellen Jahres: {e}")
        return

    # Nur dieses Jahr scrapen
    try:
        year_results = scrape_year(latest_year)
        new_entries = []
        for r in year_results:
            if r[0].strip() not in existing_dates:
                new_entries.append(r)
                print(f"  ➕ Neuer Eintrag: {r[0]}")
    except Exception as e:
        print(f"Fehler beim Scrapen von Jahr {latest_year}: {e}")
        return

    if not new_entries:
        print("Keine neuen Einträge gefunden.")
        return

    # Alles zusammenführen
    all_results = existing + new_entries

    # Nach Datum sortieren
    all_results.sort(key=lambda r: parse_date(r[0]) or date.min)

    # CSV schreiben
    header = ["Date", "Main1", "Main2", "Main3", "Main4", "Main5", "Euro1", "Euro2"]
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(all_results)

    print(f"CSV '{CSV_FILE}' aktualisiert. Gesamt: {len(all_results)} Einträge.")
    print(f"Neu hinzugefügt: {len(new_entries)} Ziehungen.")

if __name__ == "__main__":
    main()
