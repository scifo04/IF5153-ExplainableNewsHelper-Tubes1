"""
News Scraper for detik.com
Scrapes financial and general news articles including link, text, and category
Focuses on finance.detik.com for financial news, but can also scrape other detik.com channels
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict
from datetime import datetime
import re


class DetikScraper:
    """Scraper for detik.com news (finance and general)"""

    BASE_URL = "https://www.detik.com"
    FINANCE_URL = "https://finance.detik.com"

    # Financial news categories
    FINANCE_CATEGORIES = [
        "berita-ekonomi-bisnis",
        "finansial",
        "infrastruktur",
        "energi",
        "industri",
        "fintech",
        "moneter",
        "bursa-dan-valas",
    ]

    # General news channels
    GENERAL_CHANNELS = [
        ("https://news.detik.com", "news"),
        ("https://inet.detik.com", "tech"),
        ("https://sport.detik.com", "sport"),
        ("https://travel.detik.com", "travel"),
        ("https://food.detik.com", "food"),
        ("https://health.detik.com", "health"),
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

    def scrape_finance_homepage(self, max_articles: int = 50) -> List[Dict]:
        """
        Scrape articles from finance.detik.com homepage

        Args:
            max_articles: Maximum number of articles to scrape

        Returns:
            List of article dictionaries
        """
        print(f"Scraping finance homepage: {self.FINANCE_URL}")

        try:
            response = self.session.get(self.FINANCE_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            articles = []

            # Find all article links
            article_links = soup.find_all("a", href=True)

            for link in article_links:
                if len(articles) >= max_articles:
                    break

                href = link.get("href", "")

                # Check if it's a finance article (contains /d- which is article ID pattern)
                if "/d-" in href and "finance.detik.com" in href:
                    # Extract category from URL
                    category_match = re.search(r"finance\.detik\.com/([^/]+)/d-", href)
                    category = category_match.group(1) if category_match else "finance"

                    # Get article title
                    title = link.get_text(strip=True)

                    if title and len(title) > 10:
                        article_data = {
                            "link": href,
                            "title": title,
                            "category": category,
                            "channel": "finance",
                            "scraped_at": datetime.now().isoformat(),
                        }

                        # Avoid duplicates
                        if not any(a["link"] == href for a in articles):
                            articles.append(article_data)
                            print(f"Found: [{category}] {title[:60]}...")

            print(f"\nScraped {len(articles)} articles from finance homepage")
            return articles

        except Exception as e:
            print(f"Error scraping finance homepage: {e}")
            return []

    def scrape_finance_category(
        self, category: str, max_articles: int = 30
    ) -> List[Dict]:
        """
        Scrape articles from a specific finance category

        Args:
            category: Category name (e.g., 'berita-ekonomi-bisnis', 'moneter')
            max_articles: Maximum number of articles to scrape

        Returns:
            List of article dictionaries
        """
        if category not in self.FINANCE_CATEGORIES:
            print(f"Invalid finance category: {category}")
            print(f"Valid categories: {', '.join(self.FINANCE_CATEGORIES)}")
            return []

        url = f"{self.FINANCE_URL}/{category}"
        print(f"\nScraping finance category: {url}")

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

                # Check if it's an article from this category
                if f"/{category}/d-" in href:
                    title = link.get_text(strip=True)

                    if title and len(title) > 10:
                        article_data = {
                            "link": href,
                            "title": title,
                            "category": category,
                            "channel": "finance",
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

    def scrape_general_channel(
        self, channel_url: str, channel_name: str, max_articles: int = 30
    ) -> List[Dict]:
        """
        Scrape articles from a general detik.com channel

        Args:
            channel_url: URL of the channel (e.g., 'https://news.detik.com')
            channel_name: Name of the channel (e.g., 'news')
            max_articles: Maximum number of articles to scrape

        Returns:
            List of article dictionaries
        """
        print(f"\nScraping {channel_name} channel: {channel_url}")

        try:
            time.sleep(self.delay)
            response = self.session.get(channel_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            articles = []

            # Find all article links
            article_links = soup.find_all("a", href=True)

            for link in article_links:
                if len(articles) >= max_articles:
                    break

                href = link.get("href", "")

                # Check if it's an article (contains /d- pattern)
                if "/d-" in href and channel_url in href:
                    # Extract category from URL
                    category_match = re.search(
                        rf"{channel_name}\.detik\.com/([^/]+)/d-", href
                    )
                    category = (
                        category_match.group(1) if category_match else channel_name
                    )

                    title = link.get_text(strip=True)

                    if title and len(title) > 10:
                        article_data = {
                            "link": href,
                            "title": title,
                            "category": category,
                            "channel": channel_name,
                            "scraped_at": datetime.now().isoformat(),
                        }

                        if not any(a["link"] == href for a in articles):
                            articles.append(article_data)
                            print(f"Found: [{category}] {title[:60]}...")

            print(f"Scraped {len(articles)} articles from {channel_name}")
            return articles

        except Exception as e:
            print(f"Error scraping {channel_name} channel: {e}")
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

            # Extract channel and category from URL
            channel_match = re.search(r"//([^.]+)\.detik\.com", article_url)
            channel = channel_match.group(1) if channel_match else "detik"

            category_match = re.search(r"detik\.com/([^/]+)/d-", article_url)
            category = category_match.group(1) if category_match else "general"

            # Find article title
            title = ""
            title_tag = soup.find("h1", class_="detail__title")
            if not title_tag:
                title_tag = soup.find("h1")
            if title_tag:
                title = title_tag.get_text(strip=True)

            # Find article body text
            body_text = []

            # Try to find the main article content div
            detail_div = soup.find("div", class_="detail__body-text")

            if detail_div:
                # Get all paragraphs from detail div
                paragraphs = detail_div.find_all("p")
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    # Filter out ads and irrelevant text
                    if (
                        text
                        and len(text) > 30
                        and "ADVERTISEMENT" not in text
                        and "SCROLL TO CONTINUE" not in text
                    ):
                        body_text.append(text)
            else:
                # Fallback: get all paragraphs
                all_p = soup.find_all("p")
                for p in all_p:
                    text = p.get_text(strip=True)
                    if (
                        text
                        and len(text) > 50
                        and "ADVERTISEMENT" not in text
                        and "SCROLL TO CONTINUE" not in text
                    ):
                        body_text.append(text)

            # Find published date
            published_date = ""
            date_elem = soup.find("div", class_="detail__date")
            if date_elem:
                published_date = date_elem.get_text(strip=True)

            # Find author
            author = ""
            author_elem = soup.find("div", class_="detail__author")
            if author_elem:
                author = author_elem.get_text(strip=True)

            article_data = {
                "link": article_url,
                "title": title,
                "category": category,
                "channel": channel,
                "body_text": "\n\n".join(body_text),
                "published_date": published_date,
                "author": author,
                "scraped_at": datetime.now().isoformat(),
            }

            return article_data

        except Exception as e:
            print(f"Error scraping article {article_url}: {e}")
            return {
                "link": article_url,
                "title": "",
                "category": "error",
                "channel": "error",
                "body_text": "",
                "published_date": "",
                "author": "",
                "error": str(e),
                "scraped_at": datetime.now().isoformat(),
            }

    def scrape_all_finance_categories(
        self, articles_per_category: int = 20
    ) -> List[Dict]:
        """
        Scrape articles from all finance categories

        Args:
            articles_per_category: Number of articles to scrape per category

        Returns:
            List of all scraped articles
        """
        all_articles = []

        for category in self.FINANCE_CATEGORIES:
            articles = self.scrape_finance_category(
                category, max_articles=articles_per_category
            )
            all_articles.extend(articles)
            time.sleep(self.delay)

        print(f"\n{'='*60}")
        print(f"Total finance articles scraped: {len(all_articles)}")
        print(f"{'='*60}")

        return all_articles

    def scrape_all_general_channels(self, articles_per_channel: int = 20) -> List[Dict]:
        """
        Scrape articles from all general news channels

        Args:
            articles_per_channel: Number of articles to scrape per channel

        Returns:
            List of all scraped articles
        """
        all_articles = []

        for channel_url, channel_name in self.GENERAL_CHANNELS:
            articles = self.scrape_general_channel(
                channel_url, channel_name, max_articles=articles_per_channel
            )
            all_articles.extend(articles)
            time.sleep(self.delay)

        print(f"\n{'='*60}")
        print(f"Total general articles scraped: {len(all_articles)}")
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
    """Example usage"""
    scraper = DetikScraper(delay=1.0)

    finance_articles = scraper.scrape_all_finance_categories(articles_per_category=1000)
    general_articles = scraper.scrape_all_general_channels(articles_per_channel=1000)

    # Combine all article links
    all_article_links = finance_articles + general_articles

    # Example 4: Scrape full content for articles
    print("\n" + "=" * 60)
    print("SCRAPING FULL ARTICLE CONTENT WITH BODY TEXT")
    print("=" * 60)
    articles_with_content = scraper.scrape_articles_with_content(
        all_article_links, max_articles=2000
    )

    # Save results
    if articles_with_content:
        scraper.save_to_json(articles_with_content, "detik_articles_full.json")
        scraper.save_to_csv(articles_with_content, "detik_articles_full.csv")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total article links collected: {len(all_article_links)}")
    print(f"Total articles with full content: {len(articles_with_content)}")

    # Show sample
    if articles_with_content:
        sample = articles_with_content[0]
        print(f"\n{'='*60}")
        print("SAMPLE ARTICLE:")
        print(f"{'='*60}")
        print(f"Title: {sample.get('title', 'N/A')}")
        print(f"Channel: {sample.get('channel', 'N/A')}")
        print(f"Category: {sample.get('category', 'N/A')}")
        print(f"Link: {sample.get('link', 'N/A')}")
        print(f"Published: {sample.get('published_date', 'N/A')}")
        print(f"Author: {sample.get('author', 'N/A')}")
        print(f"\nBody text preview (first 300 chars):")
        print(f"{sample.get('body_text', 'N/A')[:300]}...")

    # Count by channel and category
    channels = {}
    categories = {}
    for article in articles_with_content:
        ch = article.get("channel", "unknown")
        cat = article.get("category", "unknown")
        channels[ch] = channels.get(ch, 0) + 1
        categories[cat] = categories.get(cat, 0) + 1

    if channels:
        print(f"\n{'='*60}")
        print("Articles by channel:")
        for ch, count in sorted(channels.items()):
            print(f"  {ch}: {count}")

    if categories:
        print(f"\n{'='*60}")
        print("Articles by category:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
