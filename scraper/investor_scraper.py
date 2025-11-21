"""
News Scraper for investor.id
Scrapes financial/economics news articles including link, text, and category
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict
from datetime import datetime


class InvestorIDScraper:
    """Scraper for investor.id financial news"""

    BASE_URL = "https://investor.id"

    # Available categories on investor.id
    CATEGORIES = [
        "market",
        "finance",
        "business",
        "macroeconomy",
        "international",
        "national",
        "stock",
        "corporate-action",
    ]

    def __init__(self, delay: float = 1.0):
        """
        Initialize scraper

        Args:
            delay: Delay between requests in seconds (default: 1.0)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

    def scrape_homepage(self, max_articles: int = 50) -> List[Dict]:
        """
        Scrape articles from the homepage

        Args:
            max_articles: Maximum number of articles to scrape

        Returns:
            List of article dictionaries with link, text, and category
        """
        print(f"Scraping homepage: {self.BASE_URL}")

        try:
            response = self.session.get(self.BASE_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            articles = []

            # Find all article links
            article_links = soup.find_all("a", href=True)

            for link in article_links:
                if len(articles) >= max_articles:
                    break

                href = link.get("href", "")

                # Filter for article links
                if not href.startswith(self.BASE_URL):
                    if href.startswith("/"):
                        href = self.BASE_URL + href
                    else:
                        continue

                # Check if it's an article URL (has category and article ID)
                parts = href.replace(self.BASE_URL + "/", "").split("/")
                if len(parts) >= 3:
                    category = parts[0]

                    # Only process valid categories
                    if category in self.CATEGORIES:
                        # Get article title/text from link
                        title = link.get_text(strip=True)

                        if (
                            title and len(title) > 10
                        ):  # Filter out empty or very short titles
                            article_data = {
                                "link": href,
                                "title": title,
                                "category": category,
                                "scraped_at": datetime.now().isoformat(),
                            }

                            # Avoid duplicates
                            if not any(a["link"] == href for a in articles):
                                articles.append(article_data)
                                print(f"Found: [{category}] {title[:60]}...")

            print(f"\nScraped {len(articles)} articles from homepage")
            return articles

        except Exception as e:
            print(f"Error scraping homepage: {e}")
            return []

    def scrape_category(self, category: str, max_articles: int = 30) -> List[Dict]:
        """
        Scrape articles from a specific category

        Args:
            category: Category name (e.g., 'finance', 'market')
            max_articles: Maximum number of articles to scrape

        Returns:
            List of article dictionaries
        """
        if category not in self.CATEGORIES:
            print(f"Invalid category: {category}")
            print(f"Valid categories: {', '.join(self.CATEGORIES)}")
            return []

        url = f"{self.BASE_URL}/{category}"
        print(f"\nScraping category: {url}")

        try:
            time.sleep(self.delay)
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            articles = []

            # Find all article links
            article_links = soup.find_all("a", href=True)

            for link in article_links:
                if len(articles) >= max_articles:
                    break

                href = link.get("href", "")

                # Normalize URL
                if href.startswith("/"):
                    href = self.BASE_URL + href
                elif not href.startswith(self.BASE_URL):
                    continue

                # Check if it's an article from this category
                if f"/{category}/" in href:
                    title = link.get_text(strip=True)

                    if title and len(title) > 10:
                        article_data = {
                            "link": href,
                            "title": title,
                            "category": category,
                            "scraped_at": datetime.now().isoformat(),
                        }

                        if not any(a["link"] == href for a in articles):
                            articles.append(article_data)
                            print(f"Found: {title[:60]}...")

            print(f"Scraped {len(articles)} articles from {category}")
            return articles

        except Exception as e:
            print(f"Error scraping category {category}: {e}")
            return []

    def scrape_article_content(self, article_url: str) -> Dict:
        """
        Scrape full content of a specific article

        Args:
            article_url: URL of the article

        Returns:
            Dictionary with article details including full text
        """
        print(f"Scraping content: {article_url[:80]}...")

        try:
            time.sleep(self.delay)
            response = self.session.get(article_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract category from URL
            parts = article_url.replace(self.BASE_URL + "/", "").split("/")
            category = parts[0] if len(parts) > 0 else "unknown"

            # Try to find article title
            title = ""
            title_tag = soup.find("h1")
            if title_tag:
                title = title_tag.get_text(strip=True)

            # Extract article body text
            content = ""
            body_text = []

            # Get all paragraphs from the page
            all_paragraphs = soup.find_all("p")

            # Filter meaningful paragraphs (longer than 50 characters)
            for p in all_paragraphs:
                text = p.get_text(strip=True)
                # Skip very short paragraphs and navigation/UI text
                if (
                    len(text) > 50
                    and not text.startswith("Untuk")
                    and "Masuk" not in text[:20]
                ):
                    body_text.append(text)

            # Join paragraphs into content
            content = "\n\n".join(body_text)

            article_data = {
                "link": article_url,
                "title": title,
                "category": category,
                "body_text": content,
                "scraped_at": datetime.now().isoformat(),
            }

            return article_data

        except Exception as e:
            print(f"Error scraping article {article_url}: {e}")
            return {
                "link": article_url,
                "title": "",
                "category": "error",
                "body_text": "",
                "error": str(e),
                "scraped_at": datetime.now().isoformat(),
            }

    def scrape_all_categories(self, articles_per_category: int = 20) -> List[Dict]:
        """
        Scrape articles from all categories

        Args:
            articles_per_category: Number of articles to scrape per category

        Returns:
            List of all scraped articles
        """
        all_articles = []

        for category in self.CATEGORIES:
            articles = self.scrape_category(
                category, max_articles=articles_per_category
            )
            all_articles.extend(articles)
            time.sleep(self.delay)

        print(f"\n{'='*60}")
        print(f"Total articles scraped: {len(all_articles)}")
        print(f"{'='*60}")

        return all_articles

    def scrape_articles_with_content(
        self, article_links: List[Dict], max_articles: int = None
    ) -> List[Dict]:
        """
        Scrape full content for a list of articles

        Args:
            article_links: List of article dictionaries with 'link' key
            max_articles: Maximum number of articles to scrape (None for all)

        Returns:
            List of articles with full body text
        """
        articles_with_content = []
        total = (
            len(article_links)
            if max_articles is None
            else min(max_articles, len(article_links))
        )

        print(f"\nScraping full content for {total} articles...")
        print("=" * 60)

        for i, article in enumerate(article_links[:total]):
            print(f"[{i+1}/{total}] ", end="")
            full_article = self.scrape_article_content(article["link"])
            articles_with_content.append(full_article)

        print(f"\n{'='*60}")
        print(
            f"Successfully scraped {len(articles_with_content)} articles with full content"
        )
        print(f"{'='*60}")

        return articles_with_content

    def save_to_json(self, articles: List[Dict], filename: str):
        """
        Save scraped articles to JSON file

        Args:
            articles: List of article dictionaries
            filename: Output filename
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"\nSaved {len(articles)} articles to {filename}")
        except Exception as e:
            print(f"Error saving to file: {e}")

    def save_to_csv(self, articles: List[Dict], filename: str):
        """
        Save scraped articles to CSV file

        Args:
            articles: List of article dictionaries
            filename: Output filename
        """
        try:
            import csv

            if not articles:
                print("No articles to save")
                return

            # Get all unique keys
            keys = set()
            for article in articles:
                keys.update(article.keys())
            keys = sorted(keys)

            with open(filename, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(articles)

            print(f"\nSaved {len(articles)} articles to {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")


def main():
    """Main scraper - collects 100+ articles with full body text"""
    scraper = InvestorIDScraper(delay=1.0)

    print("=" * 60)
    print("SCRAPING 100+ ARTICLES WITH FULL BODY TEXT")
    print("=" * 60)

    all_article_links = []

    # Step 1: Collect article links from homepage
    print("\n[STEP 1] Scraping homepage for article links...")
    print("=" * 60)
    homepage_articles = scraper.scrape_homepage(max_articles=50)
    all_article_links.extend(homepage_articles)
    print(f"Collected {len(homepage_articles)} articles from homepage")

    # Step 2: Scrape additional articles from key categories
    print("\n[STEP 2] Scraping categories for more article links...")
    print("=" * 60)

    # Scrape more from each category to reach 100+
    for category in ["market", "finance", "business", "macroeconomy"]:
        print(f"\nScraping category: {category}")
        category_articles = scraper.scrape_category(category, max_articles=30)
        all_article_links.extend(category_articles)
        print(f"Total collected so far: {len(all_article_links)}")

        # Stop if we have enough
        if len(all_article_links) >= 120:
            break

    # Remove duplicates based on link
    seen_links = set()
    unique_articles = []
    for article in all_article_links:
        if article["link"] not in seen_links:
            seen_links.add(article["link"])
            unique_articles.append(article)

    print(f"\n{'='*60}")
    print(f"Total unique article links collected: {len(unique_articles)}")
    print(f"{'='*60}")

    # Step 3: Scrape full content (body text) for at least 100 articles
    print("\n[STEP 3] Scraping full body text for all articles...")
    print("=" * 60)
    print("This will take a few minutes. Please wait...")
    print("=" * 60)

    articles_with_content = scraper.scrape_articles_with_content(
        unique_articles,
        max_articles=min(
            100, len(unique_articles)
        ),  # Get at least 100 or all available
    )

    # Filter out articles that failed or have no body text
    valid_articles = [
        article
        for article in articles_with_content
        if article.get("body_text") and len(article.get("body_text", "")) > 100
    ]

    # Save results with body text
    if valid_articles:
        scraper.save_to_json(valid_articles, "investor_articles_full.json")
        scraper.save_to_csv(valid_articles, "investor_articles_full.csv")

    # Print summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Total article links collected: {len(unique_articles)}")
    print(f"Total articles scraped with content: {len(articles_with_content)}")
    print(f"Valid articles with body text (>100 chars): {len(valid_articles)}")

    # Show sample
    if valid_articles:
        sample = valid_articles[0]
        print(f"\n{'='*60}")
        print("SAMPLE ARTICLE:")
        print(f"{'='*60}")
        print(f"Title: {sample.get('title', 'N/A')}")
        print(f"Category: {sample.get('category', 'N/A')}")
        print(f"Link: {sample.get('link', 'N/A')}")
        print(f"\nBody text length: {len(sample.get('body_text', ''))} characters")
        print(f"\nBody text preview (first 400 chars):")
        print(f"{sample.get('body_text', 'N/A')[:400]}...")

    # Count by category
    categories = {}
    for article in valid_articles:
        cat = article.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    if categories:
        print(f"\n{'='*60}")
        print("Articles by category:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")

    print(f"\n{'='*60}")
    print("✓ Scraping complete!")
    print(f"✓ Files saved: investor_articles_full.json and investor_articles_full.csv")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
