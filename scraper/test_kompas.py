import requests
from bs4 import BeautifulSoup

url = "https://money.kompas.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

print("Kompas Money Homepage Structure")
print("=" * 60)

# Find article links
article_links = soup.find_all("a", href=True)
print(f"\nTotal links found: {len(article_links)}")

# Print sample URLs to see the pattern
print("\nSample URLs:")
count = 0
for link in article_links:
    href = link.get("href", "")
    title = link.get_text(strip=True)
    if href and href.startswith("http") and "money.kompas.com" in href:
        count += 1
        print(f"{count}. URL: {href[:100]}")
        if title and len(title) > 10:
            print(f"   Title: {title[:80]}")
        # if count >= 20:
        # break
