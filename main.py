import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json

BASE_URL = "https://toolkit.rescuegroups.org/iframe/fb/v3.0/"
TOTAL_PAGES = 6
OUTPUT_FILE = "rabbits.json"

def get_soup(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def collect_all_detail_links():
    detail_links = []
    for page in range(1, TOTAL_PAGES + 1):
        url = f"{BASE_URL}?breed=&age=&sex=&page={page}&ids=925&locationid=&species=Rabbit"
        print(f"\nCollecting links from page {page}: {url}")
        soup = get_soup(url)
        cells = soup.find_all("td", class_="searchResultsCell")
        print(f"  Found {len(cells)} searchResultsCell tds")
        for cell in cells:
            a_tag = cell.find("a", class_="petName", href=True)
            if a_tag:
                full_url = urljoin(BASE_URL, a_tag['href'])
                print(f"    Found rabbit link: {full_url}")
                detail_links.append(full_url)
            else:
                print("    No rabbit link found in this cell.")
    print(f"\nCollected {len(detail_links)} rabbit links total.")
    return detail_links

def extract_rabbit_data(detail_url):
    print(f"  Scraping rabbit detail: {detail_url}")
    soup = get_soup(detail_url)

    # Name
    name_tag = soup.find("div", class_="pageCenterTitle")
    name = name_tag.text.strip() if name_tag else ""

    # Type
    type_tag = soup.find("span", id="rgPetDetailsBreed")
    pet_type = type_tag.text.strip() if type_tag else ""

    # Gender
    gender_tag = soup.find("span", id="rgPetDetailsSex")
    gender = gender_tag.text.replace("::", "").strip() if gender_tag else ""

    # Age
    age_tag = soup.find("span", id="rgPetDetailsAge")
    age = age_tag.text.replace("::", "").strip() if age_tag else ""

    # Description
    desc_div = soup.find("div", class_="rgDescription")
    description = desc_div.get_text(strip=True) if desc_div else ""
    print(f"    Name: {name}, Type: {pet_type}, Age: {age}, Gender: {gender}")
    return {
        "name": name,
        "type": pet_type,
        "age": age,
        "gender": gender,
        "description": description,
        "detail_url": detail_url
    }

def main():
    all_rabbits = []
    detail_links = collect_all_detail_links()
    for i, link in enumerate(detail_links, 1):
        print(f"\nScraping rabbit {i}/{len(detail_links)}")
        rabbit_data = extract_rabbit_data(link)
        all_rabbits.append(rabbit_data)
        time.sleep(0.5)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_rabbits, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(all_rabbits)} rabbits to {OUTPUT_FILE}")
    print("\nSample data:")
    for r in all_rabbits[:3]:
        print(json.dumps(r, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
