import pandas as pd


def concatenate_scrapers(
    kompas_csv="kompas_articles_full.csv",
    detik_csv="detik_articles_full.csv",
    output_csv="combined_kompas_detik.csv",
):
    """
    Concatenate kompas and detik scraper results (only articles with body text)

    Args:
      kompas_csv: Path to kompas scraper output CSV
      detik_csv: Path to detik scraper output CSV
      output_csv: Path to save combined CSV

    Returns:
      DataFrame with combined results
    """
    print("=" * 60)
    print("CONCATENATING KOMPAS AND DETIK RESULTS")
    print("=" * 60)

    try:
        # Read both CSVs
        print(f"\nReading {kompas_csv}...")
        df_kompas = pd.read_csv(kompas_csv)
        print(f"  Kompas articles: {len(df_kompas)}")

        print(f"\nReading {detik_csv}...")
        df_detik = pd.read_csv(detik_csv)
        print(f"  Detik articles: {len(df_detik)}")

        # Filter out articles without body text
        print("\nFiltering articles with body text...")
        df_kompas = df_kompas[
            df_kompas["body_text"].notna() & (df_kompas["body_text"].str.strip() != "")
        ]
        df_detik = df_detik[
            df_detik["body_text"].notna() & (df_detik["body_text"].str.strip() != "")
        ]
        print(f"  Kompas with body: {len(df_kompas)}")
        print(f"  Detik with body: {len(df_detik)}")

        # Concatenate
        print("\nConcatenating dataframes...")
        df_combined = pd.concat([df_kompas, df_detik], ignore_index=True)

        # Remove duplicates based on link
        print("Removing duplicates...")
        df_combined = df_combined.drop_duplicates(subset=["link"], keep="first")

        # Swap category and channel for finance articles
        df_combined = swap_category_channel_for_finance(df_combined)

        # Save combined results
        print(f"\nSaving to {output_csv}...")
        df_combined.to_csv(output_csv, index=False, encoding="utf-8")

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Kompas articles (with body): {len(df_kompas)}")
        print(f"Detik articles (with body): {len(df_detik)}")
        print(f"Combined (after deduplication): {len(df_combined)}")

        # Show stats by source
        print("\n" + "=" * 60)
        print("ARTICLES BY CHANNEL")
        print("=" * 60)
        channel_counts = df_combined["channel"].value_counts()
        for channel, count in channel_counts.items():
            print(f"  {channel}: {count}")

        # Show stats by category
        print("\n" + "=" * 60)
        print("ARTICLES BY CATEGORY (Top 10)")
        print("=" * 60)
        category_counts = df_combined["category"].value_counts().head(10)
        for category, count in category_counts.items():
            print(f"  {category}: {count}")

        return df_combined

    except FileNotFoundError as e:
        print(f"\nError: File not found - {e}")
        print("\nMake sure you have run both scrapers first:")
        print("  uv run kompas_scraper.py")
        print("  uv run detik_scraper.py")
        return None
    except Exception as e:
        print(f"\nError: {e}")
        return None


def swap_category_channel_for_finance(df):
    """
    Swap category and channel columns for rows where channel='finance'

    Args:
      df: DataFrame with 'channel' and 'category' columns

    Returns:
      DataFrame with swapped values for finance channel rows
    """
    # Create a copy to avoid modifying original
    df_copy = df.copy()

    # Find rows where channel is 'finance'
    finance_mask = df_copy["channel"] == "finance"

    # Swap category and channel for these rows
    df_copy.loc[finance_mask, ["channel", "category"]] = df_copy.loc[
        finance_mask, ["category", "channel"]
    ].values

    print(
        f"\nSwapped category and channel for {finance_mask.sum()} rows with channel='finance'"
    )

    return df_copy


if __name__ == "__main__":
    concatenate_scrapers()
