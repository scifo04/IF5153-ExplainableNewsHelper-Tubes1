"""
News Scraper for kompas.com
Scrapes financial and general news articles including link, text, and category
Focuses on money.kompas.com for financial news, but can also scrape other kompas.com channels
Output format matches detik_scraper for easy concatenation
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock


class KompasScraper:
    """Scraper for kompas.com news (finance and general)"""

    BASE_URL = "https://www.kompas.com"
    MONEY_URL = "https://money.kompas.com"

    # Financial news categories on money.kompas.com
    MONEY_CATEGORIES = [
        {"url": "https://money.kompas.com/ekbis", "name": "Ekbis"},
        {"url": "https://money.kompas.com/keuangan", "name": "Keuangan"},
        {"url": "https://money.kompas.com/syariah", "name": "Syariah"},
        {"url": "https://money.kompas.com/industri", "name": "Industri"},
        {"url": "https://money.kompas.com/energi", "name": "Energi"},
        {"url": "https://money.kompas.com/karier", "name": "Karier"},
        {"url": "https://money.kompas.com/cuan", "name": "Cuan"},
        {"url": "https://money.kompas.com/belanja", "name": "Belanja"},
        {"url": "https://kolom.kompas.com/Tanya.Pajak", "name": "Tanya Pajak"},
        {"url": "https://indeks.kompas.com?site=money", "name": "Indeks"},
        {"url": "https://kilasbadan.kompas.com/", "name": "Kilas Badan"},
        {"url": "https://kilastransportasi.kompas.com/", "name": "Kilas Transportasi"},
        {"url": "https://kilasfintech.kompas.com/", "name": "Kilas Fintech"},
        {"url": "https://kilasperbankan.kompas.com/", "name": "Kilas Perbankan"},
        {"url": "https://kilasinvestasi.kompas.com/", "name": "Kilas Investasi"},
        {
            "url": "https://indeks.kompas.com/topik-pilihan/list/9076/bukan-dompet-biasa",
            "name": "Transaksi Digital",
        },
        {
            "url": "https://www.kompas.com/topik-pilihan/list/9635/jejak-umkm",
            "name": "Jejak UMKM",
        },
    ]

    # General news channels
    GENERAL_CHANNELS = [
        {
            "category": "News",
            "channel": [
                {"url": "https://nasional.kompas.com", "name": "Nasional"},
                {"url": "https://www.kompas.com/global", "name": "Global"},
                {"url": "https://megapolitan.kompas.com", "name": "Megapolitan"},
                {"url": "https://regional.kompas.com", "name": "Regional"},
                {"url": "https://pemilu.kompas.com", "name": "Pemilu"},
                {"url": "https://www.kompas.com/hype", "name": "Hype"},
                {
                    "url": "https://www.kompas.com/konsultasihukum",
                    "name": "Konsultasi Hukum",
                },
                {"url": "https://www.kompas.com/cekfakta", "name": "Cek Fakta"},
                {"url": "https://kilasdaerah.kompas.com", "name": "Kilas Daerah"},
                {"url": "https://kilaskorporasi.kompas.com", "name": "Kilas Korporasi"},
                {
                    "url": "https://kilaskementerian.kompas.com",
                    "name": "Kilas Kementerian",
                },
                {"url": "https://sorotpolitik.kompas.com", "name": "Sorot Politik"},
                {
                    "url": "https://kilasbadannegara.kompas.com",
                    "name": "Kilas Badan Negara",
                },
                {
                    "url": "https://kelanaindonesia.kompas.com",
                    "name": "Kelana Indonesia",
                },
                {"url": "https://kilasparlemen.kompas.com", "name": "Kilas Parlemen"},
                {"url": "https://kilasbumn.kompas.com", "name": "Kilas BUMN"},
            ],
        },
        # {
        #     "category": "Nusaraya",
        #     "channel": [
        #         {
        #             "url": "https://www.kompas.com/sumatera-utara",
        #             "name": "Sumatera Utara",
        #         },
        #         {
        #             "url": "https://www.kompas.com/sumatera-selatan",
        #             "name": "Sumatera Selatan",
        #         },
        #         {
        #             "url": "https://www.kompas.com/sumatera-barat",
        #             "name": "Sumatera Barat",
        #         },
        #         {"url": "https://www.kompas.com/riau", "name": "Riau"},
        #         {"url": "https://www.kompas.com/lampung", "name": "Lampung"},
        #         {"url": "https://www.kompas.com/banten", "name": "Banten"},
        #         {"url": "https://yogyakarta.kompas.com", "name": "Yogyakarta"},
        #         {"url": "https://www.kompas.com/jawa-barat", "name": "Jawa Barat"},
        #         {"url": "https://www.kompas.com/jawa-tengah", "name": "Jawa Tengah"},
        #         {"url": "https://www.kompas.com/jawa-timur", "name": "Jawa Timur"},
        #         {
        #             "url": "https://www.kompas.com/kalimantan-barat",
        #             "name": "Kalimantan Barat",
        #         },
        #         {
        #             "url": "https://www.kompas.com/kalimantan-timur",
        #             "name": "Kalimantan Timur",
        #         },
        #         {
        #             "url": "https://www.kompas.com/sulawesi-selatan",
        #             "name": "Sulawesi Selatan",
        #         },
        #         {"url": "https://denpasar.kompas.com", "name": "Bali"},
        #     ],
        # },
        {
            "category": "Teknologi",
            "channel": [
                {"url": "https://tekno.kompas.com/apps-os", "name": "Apps & OS"},
                {"url": "https://tekno.kompas.com/gadget", "name": "Gadget"},
                {"url": "https://tekno.kompas.com/internet", "name": "Internet"},
                {"url": "https://tekno.kompas.com/hardware", "name": "Hardware"},
                {"url": "https://tekno.kompas.com/business", "name": "Business"},
                {"url": "https://tekno.kompas.com/game", "name": "Game"},
                {"url": "https://tekno.kompas.com/galeri", "name": "Galeri"},
                {"url": "https://kilasinternet.kompas.com/", "name": "Kilas Internet"},
            ],
        },
        {
            "category": "Otomotif",
            "channel": [
                {"url": "https://otomotif.kompas.com/news", "name": "News"},
                {"url": "https://otomotif.kompas.com/mobil", "name": "Mobil"},
                {"url": "https://otomotif.kompas.com/motor", "name": "Motor"},
                {"url": "https://otomotif.kompas.com/sport", "name": "Sport"},
                {"url": "https://otomotif.kompas.com/feature", "name": "Feature"},
                {"url": "https://otomotif.kompas.com/niaga", "name": "Niaga"},
                {"url": "https://otomotif.kompas.com/komunitas", "name": "Komunitas"},
                {"url": "https://otomotif.kompas.com/otopedia", "name": "Otopedia"},
                {"url": "https://otomotif.kompas.com/galeri", "name": "Galeri"},
                {"url": "https://otomotif.kompas.com/merapah", "name": "Merapah"},
                {
                    "url": "https://otomotif.kompas.com/ev-leadership",
                    "name": "EV Leadership",
                },
                {
                    "url": "https://otomotif.kompas.com/elektrifikasi",
                    "name": "Elektrifikasi",
                },
            ],
        },
        {
            "category": "Bola",
            "channel": [
                {
                    "url": "https://bola.kompas.com/timnas-indonesia",
                    "name": "Timnas Indonesia",
                },
                {
                    "url": "https://bola.kompas.com/liga-indonesia",
                    "name": "Liga Indonesia",
                },
                {"url": "https://bola.kompas.com/liga-inggris", "name": "Liga Inggris"},
                {"url": "https://bola.kompas.com/liga-italia", "name": "Liga Italia"},
                {
                    "url": "https://bola.kompas.com/liga-champions",
                    "name": "Liga Champions",
                },
                {
                    "url": "https://bola.kompas.com/internasional",
                    "name": "Internasional",
                },
                {"url": "https://bola.kompas.com/liga-lain", "name": "Liga Lain"},
                {"url": "https://bola.kompas.com/klasemen", "name": "Klasemen"},
                {"url": "https://www.kompas.com/sports", "name": "Sports"},
                {"url": "https://www.kompas.com/motogp", "name": "Motogp"},
                {"url": "https://www.kompas.com/badminton", "name": "Badminton"},
            ],
        },
        {
            "category": "Lifestyle",
            "channel": [
                {"url": "https://lifestyle.kompas.com/wellness", "name": "Wellness"},
                {"url": "https://lifestyle.kompas.com/fashion", "name": "Fashion"},
                {
                    "url": "https://lifestyle.kompas.com/relationship",
                    "name": "Relationship",
                },
                {"url": "https://lifestyle.kompas.com/parenting", "name": "Parenting"},
                {
                    "url": "https://lifestyle.kompas.com/beauty",
                    "name": "Beauty & Grooming",
                },
                {"url": "https://buku.kompas.com", "name": "Buku"},
                {"url": "https://genbest.kompas.com", "name": "Sadar Stunting"},
                {"url": "https://kilaslifestyle.kompas.com", "name": "Kilas Lifestyle"},
            ],
        },
        {
            "category": "Tren",
            "channel": [
                {"url": "https://www.kompas.com/tren", "name": "Tren"},
            ],
        },
        {
            "category": "Health",
            "channel": [
                {"url": "https://health.kompas.com/penyakit", "name": "Penyakit"},
                {"url": "https://kilaskesehatan.kompas.com", "name": "Kilas Kesehatan"},
            ],
        },
        {
            "category": "Properti",
            "channel": [
                {"url": "https://www.kompas.com/properti", "name": "Properti"},
                {
                    "url": "https://properti.kompas.com/listing-properti",
                    "name": "Listing Properti",
                },
                {"url": "https://properti.kompas.com/arsitektur", "name": "Arsitektur"},
                {"url": "https://properti.kompas.com/konstruksi", "name": "Konstruksi"},
                {
                    "url": "https://properti.kompas.com/tips-properti",
                    "name": "Tips Properti",
                },
                {"url": "https://ikn.kompas.com/", "name": "IKN"},
                {"url": "https://www.kompas.com/homey", "name": "Homey"},
                {"url": "https://sorot.kompas.com", "name": "Sorot Properti"},
            ],
        },
        {
            "category": "Edukasi",
            "channel": [
                {"url": "https://edukasi.kompas.com/sekolah", "name": "Sekolah"},
                {"url": "https://www.kompas.com/edu", "name": "Edu News"},
                {
                    "url": "https://edukasi.kompas.com/perguruan-tinggi",
                    "name": "Perguruan Tinggi",
                },
                {
                    "url": "https://edukasi.kompas.com/pendidikan-khusus",
                    "name": "Pendidikan Khusus",
                },
                {"url": "https://edukasi.kompas.com/beasiswa", "name": "Beasiswa"},
                {"url": "https://edukasi.kompas.com/literasi", "name": "Literasi"},
                {"url": "https://www.kompas.com/skola", "name": "Skola"},
                {
                    "url": "https://kilaspendidikan.kompas.com",
                    "name": "Kilas Pendidikan",
                },
                {"url": "https://edukasi.kompas.com/ideaksi", "name": "IdeAksi"},
            ],
        },
        {
            "category": "Travel",
            "channel": [
                {"url": "https://travel.kompas.com/travel-news", "name": "Travel News"},
                {
                    "url": "https://travel.kompas.com/travel-ideas",
                    "name": "Travel Ideas",
                },
                {"url": "https://travel.kompas.com/hotel-story", "name": "Hotel Story"},
                {"url": "https://travel.kompas.com/travelpedia", "name": "Travelpedia"},
                {"url": "https://www.kompas.com/food", "name": "Food"},
                {"url": "https://ohayojepang.kompas.com", "name": "Ohayo Jepang"},
            ],
        },
        {
            "category": "Lainnya",
            "channel": [
                {"url": "https://video.kompas.com", "name": "Video"},
                {"url": "https://www.kompas.com/parapuan", "name": "Parapuan"},
                {"url": "https://kolom.kompas.com/", "name": "Kolom"},
                {"url": "https://www.kompas.com/sains", "name": "Sains"},
                {"url": "https://jeo.kompas.com/", "name": "JEO"},
                {"url": "https://foto.kompas.com/photo", "name": "Foto"},
                {"url": "https://vik.kompas.com/", "name": "VIK"},
                {"url": "https://katanetizen.kompas.com/", "name": "Kata Netizen"},
                {"url": "https://warta.kompas.com/", "name": "Warta"},
            ],
        },
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
        self.print_lock = Lock()  # Thread-safe printing

    def scrape_money_category(
        self, category_url: str, category_name: str, max_articles: int = 50
    ) -> List[Dict]:
        """
        Scrape articles from a specific money.kompas.com category

        Args:
            category_url: Full URL of the category
            category_name: Category name (e.g., 'Ekbis', 'Keuangan', etc.)
            max_articles: Maximum number of articles to scrape

        Returns:
            List of article dictionaries
        """
        print(f"\nScraping category: {category_name} ({category_url})")

        try:
            response = self.session.get(category_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            articles = []

            # Find all article links
            article_links = soup.find_all("a", href=True)

            for link in article_links:
                if len(articles) >= max_articles:
                    break

                href = link.get("href", "")

                # Check if it's a /read/ article link
                if "/read/" in href and "kompas.com" in href:
                    # Get article title
                    title = link.get_text(strip=True)

                    if title and len(title) > 10:
                        article_data = {
                            "link": href,
                            "title": title,
                            "category": category_name.lower(),
                            "channel": "finance",
                            "scraped_at": datetime.now().isoformat(),
                        }

                        # Avoid duplicates
                        if not any(a["link"] == href for a in articles):
                            articles.append(article_data)
                            print(f"Found: [{category_name}] {title[:60]}...")

            print(f"Scraped {len(articles)} articles from {category_name}")
            return articles

        except Exception as e:
            print(f"Error scraping category {category_name}: {e}")
            return []

    def scrape_all_money_categories(
        self, articles_per_category: int = 50, max_workers: int = 20
    ) -> List[Dict]:
        """
        Scrape articles from all money.kompas.com categories using multithreading

        Args:
            articles_per_category: Number of articles to scrape per category
            max_workers: Number of concurrent threads (default: 10)

        Returns:
            List of all scraped articles
        """
        all_articles = []

        print(f"\n{'='*60}")
        print(f"SCRAPING ALL MONEY.KOMPAS.COM CATEGORIES (using {max_workers} threads)")
        print(f"{'='*60}")

        # Use ThreadPoolExecutor for concurrent scraping
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_category = {
                executor.submit(
                    self.scrape_money_category,
                    category_info["url"],
                    category_info["name"],
                    articles_per_category,
                ): category_info["name"]
                for category_info in self.MONEY_CATEGORIES
            }

            # Process completed tasks
            completed = 0
            total_categories = len(self.MONEY_CATEGORIES)
            for future in as_completed(future_to_category):
                completed += 1
                category_name = future_to_category[future]

                try:
                    articles = future.result()
                    all_articles.extend(articles)

                    with self.print_lock:
                        print(
                            f"[{completed}/{total_categories}] Completed {category_name}: {len(articles)} articles"
                        )
                except Exception as e:
                    with self.print_lock:
                        print(
                            f"[{completed}/{total_categories}] Error scraping {category_name}: {e}"
                        )

        print(f"\n{'='*60}")
        print(f"Total money articles scraped: {len(all_articles)}")
        print(f"{'='*60}")

        return all_articles

    def scrape_general_channel(
        self, channel_url: str, channel_name: str, category: str, max_articles: int = 30
    ) -> List[Dict]:
        """
        Scrape articles from a general kompas.com channel

        Args:
            channel_url: URL of the channel
            channel_name: Name of the channel
            category: Main category (e.g., 'News', 'Tekno', etc.)
            max_articles: Maximum number of articles to scrape

        Returns:
            List of article dictionaries
        """
        print(f"\nScraping {channel_name} ({channel_url})")

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

                # Check if it's an article (contains /read/ pattern)
                if "/read/" in href and "kompas.com" in href:
                    title = link.get_text(strip=True)

                    if title and len(title) > 10:
                        article_data = {
                            "link": href,
                            "title": title,
                            "category": category.lower(),
                            "channel": channel_name.lower().replace(" ", "_"),
                            "scraped_at": datetime.now().isoformat(),
                        }

                        if not any(a["link"] == href for a in articles):
                            articles.append(article_data)
                            print(f"Found: [{channel_name}] {title[:60]}...")

            print(f"Scraped {len(articles)} articles from {channel_name}")
            return articles

        except Exception as e:
            print(f"Error scraping {channel_name} channel: {e}")
            return []

    def scrape_all_general_channels(
        self, articles_per_channel: int = 20, max_workers: int = 30
    ) -> List[Dict]:
        """
        Scrape articles from all general news channels using multithreading

        Args:
            articles_per_channel: Number of articles to scrape per channel
            max_workers: Number of concurrent threads (default: 5)

        Returns:
            List of all scraped articles
        """
        all_articles = []

        print(f"\n{'='*60}")
        print(f"SCRAPING ALL GENERAL CHANNELS (using {max_workers} threads)")
        print(f"{'='*60}")

        # Prepare all channel tasks
        channel_tasks = []
        for category_group in self.GENERAL_CHANNELS:
            category = category_group["category"]
            channels = category_group["channel"]

            for channel_info in channels:
                channel_url = channel_info["url"]
                channel_name = channel_info["name"]
                channel_tasks.append((channel_url, channel_name, category))

        # Use ThreadPoolExecutor for concurrent scraping
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_channel = {
                executor.submit(
                    self.scrape_general_channel,
                    channel_url,
                    channel_name,
                    category,
                    articles_per_channel,
                ): (channel_name, category)
                for channel_url, channel_name, category in channel_tasks
            }

            # Process completed tasks
            completed = 0
            total_channels = len(channel_tasks)
            for future in as_completed(future_to_channel):
                completed += 1
                channel_name, category = future_to_channel[future]

                try:
                    articles = future.result()
                    all_articles.extend(articles)

                    with self.print_lock:
                        print(
                            f"[{completed}/{total_channels}] Completed {channel_name} ({category}): {len(articles)} articles"
                        )
                except Exception as e:
                    with self.print_lock:
                        print(
                            f"[{completed}/{total_channels}] Error scraping {channel_name}: {e}"
                        )

        print(f"\n{'='*60}")
        print(f"Total general articles scraped: {len(all_articles)}")
        print(f"{'='*60}")

        return all_articles

    def scrape_article_content(self, article_dict: Dict) -> Dict:
        """
        Scrape full content of a specific article

        Args:
            article_dict: Dictionary containing article metadata including 'link', 'category', 'channel'

        Returns:
            Dictionary with article details including full text (matching detik format)
        """
        article_url = (
            article_dict.get("link", article_dict)
            if isinstance(article_dict, dict)
            else article_dict
        )

        with self.print_lock:
            print(f"Scraping content: {article_url[:80]}...")

        try:
            time.sleep(self.delay)
            response = self.session.get(article_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Use provided category and channel from article metadata if available
            if isinstance(article_dict, dict):
                category = article_dict.get("category", "unknown")
                channel = article_dict.get("channel", "unknown")
            else:
                # Fallback: Extract channel and category from URL
                if "money.kompas.com" in article_url:
                    channel = "finance"
                    category = "money"
                elif "news.kompas.com" in article_url:
                    channel = "news"
                    category = "news"
                else:
                    # Try to extract from URL
                    channel_match = re.search(r"//([^.]+)\.kompas\.com", article_url)
                    channel = channel_match.group(1) if channel_match else "kompas"
                    category = channel

            # Find article title
            title = ""
            # Try multiple title selectors
            title_tag = soup.find("h1", class_="read__title")
            if not title_tag:
                title_tag = soup.find("h1")
            if title_tag:
                title = title_tag.get_text(strip=True)

            # Find article body text
            body_text = []

            # Try to find the main article content div
            detail_div = soup.find("div", class_="read__content")

            if detail_div:
                # Get all paragraphs from detail div
                paragraphs = detail_div.find_all("p")
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    # Filter out ads and irrelevant text
                    if (
                        text
                        and len(text) > 30
                        and "ADVERTISEMENT" not in text.upper()
                        and "Baca juga:" not in text
                        and "Dapatkan update" not in text
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
                        and "ADVERTISEMENT" not in text.upper()
                        and "Baca juga:" not in text
                    ):
                        body_text.append(text)

            # Find published date
            published_date = ""
            # Try multiple date selectors
            date_elem = soup.find("div", class_="read__time")
            if not date_elem:
                date_elem = soup.find("div", class_="read__date")
            if date_elem:
                published_date = date_elem.get_text(strip=True)

            # Find author
            author = ""
            author_elem = soup.find("div", class_="credit-title-nameEditor")
            if not author_elem:
                author_elem = soup.find("div", class_="author")
            if author_elem:
                author = author_elem.get_text(strip=True)

            # Match detik scraper output format
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
            with self.print_lock:
                print(f"Error scraping article {article_url}: {e}")

            # Preserve category and channel even in error case
            if isinstance(article_dict, dict):
                category = article_dict.get("category", "error")
                channel = article_dict.get("channel", "error")
            else:
                category = "error"
                channel = "error"

            return {
                "link": article_url,
                "title": "",
                "category": category,
                "channel": channel,
                "body_text": "",
                "published_date": "",
                "author": "",
                "error": str(e),
                "scraped_at": datetime.now().isoformat(),
            }

    def scrape_articles_with_content(
        self, article_links: List[Dict], max_articles: int = None, max_workers: int = 100
    ) -> List[Dict]:
        """
        Scrape full content for a list of articles using multithreading

        Args:
            article_links: List of article dictionaries with 'link' key
            max_articles: Maximum number of articles to scrape (None for all)
            max_workers: Number of concurrent threads (default: 5)

        Returns:
            List of articles with full body text
        """
        articles_with_content = []
        total = (
            len(article_links)
            if max_articles is None
            else min(max_articles, len(article_links))
        )

        print(
            f"\nScraping full content for {total} articles using {max_workers} threads..."
        )
        print("=" * 60)

        # Use ThreadPoolExecutor for concurrent scraping
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks - pass the full article dict to preserve metadata
            future_to_article = {
                executor.submit(self.scrape_article_content, article): i
                for i, article in enumerate(article_links[:total])
            }

            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_article):
                completed += 1
                article_index = future_to_article[future]

                try:
                    full_article = future.result()
                    articles_with_content.append(full_article)

                    with self.print_lock:
                        print(
                            f"[{completed}/{total}] Completed: {full_article.get('title', 'N/A')[:60]}..."
                        )
                except Exception as e:
                    with self.print_lock:
                        print(f"[{completed}/{total}] Error processing article: {e}")

        # Sort articles to maintain original order
        link_order = {
            article["link"]: i for i, article in enumerate(article_links[:total])
        }
        articles_with_content.sort(
            key=lambda x: link_order.get(x["link"], float("inf"))
        )

        print(f"\n{'='*60}")
        print(
            f"Successfully scraped {len(articles_with_content)} articles with full content"
        )
        print(f"{'='*60}")

        return articles_with_content

    def save_to_json(self, articles: List[Dict], filename: str):
        """Save scraped articles to JSON file"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"\nSaved {len(articles)} articles to {filename}")
        except Exception as e:
            print(f"Error saving to file: {e}")

    def save_to_csv(self, articles: List[Dict], filename: str):
        """Save scraped articles to CSV file"""
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
    scraper = KompasScraper(delay=1.0)

    # Example 1: Scrape all money.kompas.com categories
    print("=" * 60)
    print("SCRAPING MONEY.KOMPAS.COM CATEGORIES")
    print("=" * 60)
    money_articles = scraper.scrape_all_money_categories(articles_per_category=1000)

    # Example 2: Scrape all general channels (optional - uncomment to use)
    print("\n" + "=" * 60)
    print("SCRAPING ALL GENERAL CHANNELS")
    print("=" * 60)
    general_articles = scraper.scrape_all_general_channels(articles_per_channel=1000)

    all_article_links = money_articles + general_articles

    # Example 3: Scrape full content for articles
    print("\n" + "=" * 60)
    print("SCRAPING FULL ARTICLE CONTENT WITH BODY TEXT")
    print("=" * 60)
    articles_with_content = scraper.scrape_articles_with_content(
        all_article_links, max_articles=None
    )

    # Save results
    if articles_with_content:
        scraper.save_to_json(articles_with_content, "kompas_articles_full.json")
        scraper.save_to_csv(articles_with_content, "kompas_articles_full.csv")

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
