"""
Exploratory Data Analysis (EDA) untuk Dataset Berita
Analisis distribusi kategori dan statistik panjang teks
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from collections import Counter
import warnings

warnings.filterwarnings("ignore")

# Set style untuk visualisasi
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")

# Category mapping configuration
MAIN_CATS = {
    "finance",
    "teknologi",
    "news",
    "otomotif",
    "tren",
    "bola",
    "lifestyle",
    "properti",
    "health",
    "edukasi",
    "travel",
    "lainnya",
}

CATEGORY_MAPPING = {
    # ---- HEALTH / MEDIS ----
    "berita-detikhealth": "health",
    "fotohealth": "health",
    "diet": "health",
    "info-sehat": "health",
    # ---- TRAVEL ----
    "travel-news": "travel",
    "fototravel": "travel",
    "cerita-perjalanan": "travel",
    "domestic-destination": "travel",
    # ---- LIFESTYLE / KULINER ----
    "mie-dan-pasta": "lifestyle",
    "resep-praktis": "lifestyle",
    "sayur": "lifestyle",
    "pengalaman-bersantap": "lifestyle",
    "daging": "lifestyle",
    "tempat-makan": "lifestyle",
    "foto-kuliner": "lifestyle",
    "resto-dan-kafe": "lifestyle",
    "warung-makan": "lifestyle",
    "info-kuliner": "lifestyle",
    "berita-boga": "lifestyle",
    # ---- TEKNOLOGI / GADGET ----
    "fotoinet": "teknologi",
    "telecommunication": "teknologi",
    "science": "teknologi",
    "cyberlife": "teknologi",
    "laptop-dan-pc": "teknologi",
    "smartphone": "teknologi",
    "lab-gadget": "teknologi",
    "games-news": "teknologi",
    "law-and-policy": "teknologi",
    "mobile-apps": "teknologi",
    "security": "teknologi",
    # ---- FINANCE / BISNIS ----
    "business": "finance",
    "consumer": "finance",
    # ---- SPORT ----
    "sport-lain": "bola",
    "sportstyle": "bola",
    "fotosport": "bola",
    "moto-gp": "otomotif",
    # ---- NEWS / UMUM ----
    "foto-news": "news",
    "berita": "news",
    "internasional": "news",
    "detiktv": "news",
    "true-story": "news",
    "melindungi-tuah-marwah": "news",
}


def map_category(cat: str) -> str:
    """Map raw category to main category"""
    cat = str(cat)
    if cat in CATEGORY_MAPPING:
        return CATEGORY_MAPPING[cat]
    if cat in MAIN_CATS:
        return cat
    return "lainnya"


def load_data(filepath):
    """Load dataset dari CSV"""
    print("=" * 80)
    print("LOADING DATA")
    print("=" * 80)
    df = pd.read_csv(filepath)

    # Map kategori ke main categories
    print("\nMapping categories to main categories...")
    df["category_original"] = df["category"]
    df["category"] = df["category"].apply(map_category)

    # Show mapping summary
    unique_mappings = df.groupby("category_original")["category"].first().to_dict()
    print(f"\n✓ Category mapping applied:")
    print(f"  Original categories: {df['category_original'].nunique()}")
    print(f"  Mapped to: {df['category'].nunique()} main categories")

    print(f"\n✓ Dataset loaded successfully")
    print(f"  Total records: {len(df):,}")
    print(f"  Columns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())
    return df


def analyze_category_distribution(df, category_col="category"):
    """
    Analisis 1: Distribusi Kategori Berita
    Mendeteksi class imbalance antara kategori
    """
    print("\n" + "=" * 80)
    print("ANALISIS 1: DISTRIBUSI KATEGORI BERITA")
    print("=" * 80)

    # Hitung distribusi
    category_counts = df[category_col].value_counts()
    category_pct = df[category_col].value_counts(normalize=True) * 100

    print("\nJumlah per Kategori:")
    for cat, count in category_counts.items():
        pct = category_pct[cat]
        print(f"  {cat}: {count:,} ({pct:.2f}%)")

    # Deteksi class imbalance
    max_pct = category_pct.max()
    min_pct = category_pct.min()
    imbalance_ratio = max_pct / min_pct

    print(f"\nImbalance Ratio: {imbalance_ratio:.2f}x")
    if imbalance_ratio > 2:
        print("⚠️  PERINGATAN: Class imbalance terdeteksi!")
        print("   Rekomendasi: Gunakan F1-Score (macro/weighted) untuk evaluasi")
    else:
        print("✓ Dataset relatif seimbang")

    # Visualisasi
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Bar plot
    category_counts.plot(
        kind="bar", ax=axes[0], color=sns.color_palette("husl", len(category_counts))
    )
    axes[0].set_title(
        "Distribusi Kategori Berita (Count)", fontsize=14, fontweight="bold"
    )
    axes[0].set_xlabel("Kategori", fontsize=12)
    axes[0].set_ylabel("Jumlah Artikel", fontsize=12)
    axes[0].tick_params(axis="x", rotation=45)

    # Tambahkan label persentase
    for i, (cat, count) in enumerate(category_counts.items()):
        pct = category_pct[cat]
        axes[0].text(
            i,
            count,
            f"{count:,}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    # Pie chart
    colors = sns.color_palette("husl", len(category_counts))
    axes[1].pie(
        category_counts,
        labels=category_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        textprops={"fontsize": 11, "fontweight": "bold"},
    )
    axes[1].set_title("Proporsi Kategori Berita", fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.savefig("gambar1_distribusi_kategori.png", dpi=300, bbox_inches="tight")
    print("\n✓ Visualisasi disimpan: gambar1_distribusi_kategori.png")
    plt.show()

    return category_counts, category_pct, imbalance_ratio


def analyze_text_length(df, text_col="body_text"):
    """
    Analisis 2: Statistik Panjang Teks
    Analisis panjang artikel dalam kata
    """
    print("\n" + "=" * 80)
    print("ANALISIS 2: STATISTIK PANJANG TEKS")
    print("=" * 80)

    # Hitung panjang dalam kata
    df["word_count"] = df[text_col].fillna("").str.split().str.len()

    # Statistik
    stats = {
        "mean_words": df["word_count"].mean(),
        "median_words": df["word_count"].median(),
        "std_words": df["word_count"].std(),
        "min_words": df["word_count"].min(),
        "max_words": df["word_count"].max(),
    }

    print("\nStatistik Panjang Kata:")
    print(f"  Rata-rata: {stats['mean_words']:.0f} kata")
    print(f"  Median: {stats['median_words']:.0f} kata")
    print(f"  Std Dev: {stats['std_words']:.0f} kata")
    print(f"  Min: {stats['min_words']:.0f} kata")
    print(f"  Max: {stats['max_words']:.0f} kata")

    # Visualisasi
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram kata
    axes[0].hist(
        df["word_count"], bins=50, edgecolor="black", alpha=0.7, color="skyblue"
    )
    axes[0].axvline(
        stats["mean_words"],
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Mean: {stats['mean_words']:.0f}",
    )
    axes[0].axvline(
        stats["median_words"],
        color="green",
        linestyle="--",
        linewidth=2,
        label=f"Median: {stats['median_words']:.0f}",
    )
    axes[0].set_title(
        "Distribusi Panjang Artikel (Kata)", fontsize=12, fontweight="bold"
    )
    axes[0].set_xlabel("Jumlah Kata", fontsize=10)
    axes[0].set_ylabel("Frekuensi", fontsize=10)
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Box plot kata
    axes[1].boxplot(df["word_count"], vert=False)
    axes[1].set_title("Box Plot - Panjang Kata", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Jumlah Kata", fontsize=10)
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("gambar2_statistik_panjang_teks.png", dpi=300, bbox_inches="tight")
    print("\n✓ Visualisasi disimpan: gambar2_statistik_panjang_teks.png")
    plt.show()

    return stats


def analyze_ner_entities(df, ner_col="ner"):
    """
    Analisis 3: Named Entity Recognition (NER)
    Analisis distribusi entitas yang diekstrak dari artikel
    """
    print("\n" + "=" * 80)
    print("ANALISIS 3: NAMED ENTITY RECOGNITION (NER)")
    print("=" * 80)

    print(f"\nTotal artikel untuk analisis NER: {len(df):,}")
    print(f"Total artikel dengan data NER: {df[ner_col].notna().sum():,}")

    # Parse NER data (assume JSON or string format)
    all_entities = []
    entity_types = Counter()
    entity_names = Counter()
    articles_with_entities = 0

    print(f"\nMemproses entitas NER dari kolom '{ner_col}'...")

    parse_errors = 0
    entities_per_article = []
    for idx, ner_data in enumerate(df[ner_col].fillna("[]")):
        try:
            # Handle both JSON string and already-parsed list
            if isinstance(ner_data, str):
                # Clean and fix common JSON issues
                ner_data_clean = ner_data.strip()

                # Try standard JSON first
                try:
                    entities = json.loads(ner_data_clean)
                except json.JSONDecodeError:
                    # Try fixing single quotes to double quotes
                    try:
                        import ast

                        entities = ast.literal_eval(ner_data_clean)
                    except:
                        entities = []
                        parse_errors += 1
            elif isinstance(ner_data, list):
                entities = ner_data
            else:
                entities = []

            entities_per_article.append(len(entities))

            if entities:
                articles_with_entities += 1
                for entity in entities:
                    if (
                        isinstance(entity, dict)
                        and "type" in entity
                        and "entity" in entity
                    ):
                        entity_type = entity["type"]
                        entity_name = entity["entity"]
                        entity_types[entity_type] += 1
                        entity_names[entity_name] += 1
                        all_entities.append(entity)
        except (json.JSONDecodeError, TypeError, ValueError, SyntaxError) as e:
            entities_per_article.append(0)
            parse_errors += 1
            if parse_errors <= 5:  # Only show first 5 errors
                print(f"  Warning: Could not parse NER data for article {idx+1}")
            continue

    if parse_errors > 0:
        print(f"\n⚠️  Total parsing errors: {parse_errors} artikel (akan dilewati)")

    print(f"\nStatistik NER:")
    print(
        f"  Total artikel dengan entitas: {articles_with_entities:,} ({articles_with_entities/len(df)*100:.1f}%)"
    )
    print(f"  Total entitas diekstrak: {sum(entity_types.values()):,}")
    print(f"  Rata-rata entitas per artikel: {sum(entity_types.values())/len(df):.2f}")
    print(f"  Jumlah tipe entitas unik: {len(entity_types)}")
    print(f"  Jumlah entitas unik: {len(entity_names)}")

    # Top entity types
    print(f"\nTop 10 Tipe Entitas:")
    for entity_type, count in entity_types.most_common(10):
        pct = count / sum(entity_types.values()) * 100
        print(f"  {entity_type}: {count:,} ({pct:.1f}%)")

    # Top entities
    print(f"\nTop 15 Entitas Paling Sering:")
    for entity_name, count in entity_names.most_common(15):
        print(f"  {entity_name}: {count:,}")

    # Visualisasi
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Plot 1: Top entity types
    top_types = entity_types.most_common(15)
    types_df = pd.DataFrame(top_types, columns=["Type", "Count"])
    axes[0, 0].barh(
        types_df["Type"],
        types_df["Count"],
        color=sns.color_palette("viridis", len(types_df)),
    )
    axes[0, 0].set_xlabel("Jumlah", fontsize=10)
    axes[0, 0].set_title("Top 15 Tipe Entitas", fontsize=12, fontweight="bold")
    axes[0, 0].invert_yaxis()
    axes[0, 0].grid(alpha=0.3)

    # Plot 2: Top entities
    top_entities = entity_names.most_common(15)
    entities_df = pd.DataFrame(top_entities, columns=["Entity", "Count"])
    axes[0, 1].barh(
        entities_df["Entity"],
        entities_df["Count"],
        color=sns.color_palette("magma", len(entities_df)),
    )
    axes[0, 1].set_xlabel("Frekuensi", fontsize=10)
    axes[0, 1].set_title("Top 15 Entitas Paling Sering", fontsize=12, fontweight="bold")
    axes[0, 1].invert_yaxis()
    axes[0, 1].grid(alpha=0.3)

    # Plot 3: Distribution of entities per article
    axes[1, 0].hist(
        entities_per_article, bins=50, edgecolor="black", alpha=0.7, color="coral"
    )
    axes[1, 0].axvline(
        np.mean(entities_per_article),
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Mean: {np.mean(entities_per_article):.1f}",
    )
    axes[1, 0].set_xlabel("Jumlah Entitas per Artikel", fontsize=10)
    axes[1, 0].set_ylabel("Frekuensi", fontsize=10)
    axes[1, 0].set_title(
        "Distribusi Jumlah Entitas per Artikel", fontsize=12, fontweight="bold"
    )
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    # Plot 4: Pie chart of top entity types
    top_5_types = entity_types.most_common(5)
    other_count = sum(entity_types.values()) - sum([count for _, count in top_5_types])
    pie_data = [(name, count) for name, count in top_5_types]
    if other_count > 0:
        pie_data.append(("Others", other_count))

    labels = [name for name, _ in pie_data]
    sizes = [count for _, count in pie_data]
    colors = sns.color_palette("Set2", len(pie_data))

    axes[1, 1].pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        textprops={"fontsize": 10},
    )
    axes[1, 1].set_title("Proporsi Top 5 Tipe Entitas", fontsize=12, fontweight="bold")

    plt.tight_layout()
    plt.savefig("gambar3_analisis_ner.png", dpi=300, bbox_inches="tight")
    print("\n✓ Visualisasi disimpan: gambar3_analisis_ner.png")
    plt.show()

    return {
        "total_entities": sum(entity_types.values()),
        "unique_types": len(entity_types),
        "unique_entities": len(entity_names),
        "articles_with_entities": articles_with_entities,
        "avg_entities_per_article": sum(entity_types.values()) / len(df),
        "top_types": entity_types.most_common(10),
        "top_entities": entity_names.most_common(10),
    }


def analyze_summary(df, summary_col="summary", body_col="body_text"):
    """
    Analisis 4: Summary Analysis
    Analisis ringkasan artikel
    """
    print("\n" + "=" * 80)
    print("ANALISIS 4: SUMMARY ANALYSIS")
    print("=" * 80)

    # Hitung panjang summary dan compression ratio
    df["summary_length"] = df[summary_col].fillna("").str.split().str.len()
    df["body_length"] = df[body_col].fillna("").str.split().str.len()
    df["compression_ratio"] = (df["summary_length"] / df["body_length"] * 100).replace(
        [np.inf, -np.inf], np.nan
    )

    stats = {
        "mean_summary_length": df["summary_length"].mean(),
        "median_summary_length": df["summary_length"].median(),
        "mean_compression_ratio": df["compression_ratio"].mean(),
        "median_compression_ratio": df["compression_ratio"].median(),
    }

    print(f"\nStatistik Summary:")
    print(f"  Rata-rata panjang summary: {stats['mean_summary_length']:.0f} kata")
    print(f"  Median panjang summary: {stats['median_summary_length']:.0f} kata")
    print(f"  Rata-rata compression ratio: {stats['mean_compression_ratio']:.1f}%")
    print(f"  Median compression ratio: {stats['median_compression_ratio']:.1f}%")

    # Visualisasi
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram summary length
    axes[0].hist(
        df["summary_length"].dropna(),
        bins=50,
        edgecolor="black",
        alpha=0.7,
        color="lightgreen",
    )
    axes[0].axvline(
        stats["mean_summary_length"],
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Mean: {stats['mean_summary_length']:.0f}",
    )
    axes[0].set_xlabel("Panjang Summary (kata)", fontsize=10)
    axes[0].set_ylabel("Frekuensi", fontsize=10)
    axes[0].set_title("Distribusi Panjang Summary", fontsize=12, fontweight="bold")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Histogram compression ratio
    axes[1].hist(
        df["compression_ratio"].dropna(),
        bins=50,
        edgecolor="black",
        alpha=0.7,
        color="plum",
    )
    axes[1].axvline(
        stats["mean_compression_ratio"],
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Mean: {stats['mean_compression_ratio']:.1f}%",
    )
    axes[1].set_xlabel("Compression Ratio (%)", fontsize=10)
    axes[1].set_ylabel("Frekuensi", fontsize=10)
    axes[1].set_title("Distribusi Compression Ratio", fontsize=12, fontweight="bold")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("gambar4_analisis_summary.png", dpi=300, bbox_inches="tight")
    print("\n✓ Visualisasi disimpan: gambar4_analisis_summary.png")
    plt.show()

    return stats


def analyze_channel_temporal(df, channel_col="channel", date_col="published_date"):
    """
    Analisis 5: Channel & Temporal Distribution
    Analisis distribusi channel dan temporal
    """
    print("\n" + "=" * 80)
    print("ANALISIS 5: CHANNEL & TEMPORAL DISTRIBUTION")
    print("=" * 80)

    # Channel distribution
    channel_counts = df[channel_col].value_counts()
    print(f"\nDistribusi Channel:")
    for channel, count in channel_counts.items():
        pct = count / len(df) * 100
        print(f"  {channel}: {count:,} ({pct:.1f}%)")

    # Parse dates
    df["published_date_parsed"] = pd.to_datetime(df[date_col], errors="coerce")
    df["year"] = df["published_date_parsed"].dt.year
    df["month"] = df["published_date_parsed"].dt.month
    df["year_month"] = df["published_date_parsed"].dt.to_period("M")

    # Temporal stats
    valid_dates = df["published_date_parsed"].dropna()
    has_valid_dates = len(valid_dates) > 0

    print(f"\nStatistik Temporal:")
    if has_valid_dates:
        print(f"  Tanggal tertua: {valid_dates.min()}")
        print(f"  Tanggal terbaru: {valid_dates.max()}")
        print(f"  Rentang waktu: {(valid_dates.max() - valid_dates.min()).days} hari")
    else:
        print(f"  ⚠️  Tidak ada data tanggal yang valid")

    # Visualisasi
    if has_valid_dates:
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    else:
        # Only 2 plots if no date data
        fig, axes = plt.subplots(1, 2, figsize=(16, 5))
        axes = axes.reshape(1, 2)

    # Plot 1: Channel distribution
    channel_counts.plot(
        kind="bar", ax=axes[0, 0], color=sns.color_palette("Set3", len(channel_counts))
    )
    axes[0, 0].set_title(
        "Distribusi Artikel per Channel", fontsize=12, fontweight="bold"
    )
    axes[0, 0].set_xlabel("Channel", fontsize=10)
    axes[0, 0].set_ylabel("Jumlah Artikel", fontsize=10)
    axes[0, 0].tick_params(axis="x", rotation=45)
    axes[0, 0].grid(alpha=0.3)

    # Plot 2: Category by channel
    category_channel = pd.crosstab(df["category"], df[channel_col])
    category_channel.plot(
        kind="bar",
        stacked=True,
        ax=axes[0, 1],
        color=sns.color_palette("Pastel1", len(category_channel.columns)),
    )
    axes[0, 1].set_title(
        "Distribusi Kategori per Channel", fontsize=12, fontweight="bold"
    )
    axes[0, 1].set_xlabel("Kategori", fontsize=10)
    axes[0, 1].set_ylabel("Jumlah Artikel", fontsize=10)
    axes[0, 1].tick_params(axis="x", rotation=45)
    axes[0, 1].legend(title="Channel", bbox_to_anchor=(1.05, 1), loc="upper left")
    axes[0, 1].grid(alpha=0.3)

    # Plot 3 & 4: Temporal plots (only if valid dates exist)
    if has_valid_dates:
        # Plot 3: Articles over time
        articles_per_month = df.groupby("year_month").size()
        if len(articles_per_month) > 0:
            articles_per_month.plot(
                ax=axes[1, 0], color="steelblue", linewidth=2, marker="o"
            )
            axes[1, 0].set_title(
                "Jumlah Artikel per Bulan", fontsize=12, fontweight="bold"
            )
            axes[1, 0].set_xlabel("Bulan", fontsize=10)
            axes[1, 0].set_ylabel("Jumlah Artikel", fontsize=10)
            axes[1, 0].tick_params(axis="x", rotation=45)
            axes[1, 0].grid(alpha=0.3)

        # Plot 4: Heatmap of articles by year and month
        year_month_data = df.groupby(["year", "month"]).size().reset_index(name="count")
        if len(year_month_data) > 0:
            heatmap_data = year_month_data.pivot(
                index="month", columns="year", values="count"
            )
            sns.heatmap(
                heatmap_data,
                annot=True,
                fmt="g",
                cmap="YlOrRd",
                ax=axes[1, 1],
                cbar_kws={"label": "Jumlah Artikel"},
            )
            axes[1, 1].set_title(
                "Heatmap Artikel per Tahun-Bulan", fontsize=12, fontweight="bold"
            )
            axes[1, 1].set_xlabel("Tahun", fontsize=10)
            axes[1, 1].set_ylabel("Bulan", fontsize=10)

    plt.tight_layout()
    plt.savefig("gambar5_channel_temporal.png", dpi=300, bbox_inches="tight")
    print("\n✓ Visualisasi disimpan: gambar5_channel_temporal.png")
    plt.show()

    return {
        "channel_distribution": channel_counts.to_dict(),
        "date_range": (
            f"{valid_dates.min()} to {valid_dates.max()}"
            if has_valid_dates
            else "No valid dates"
        ),
        "total_days": (
            (valid_dates.max() - valid_dates.min()).days if has_valid_dates else 0
        ),
    }


def generate_summary_report(
    category_stats,
    text_stats,
    category_pct,
    imbalance_ratio,
    ner_stats=None,
    summary_stats=None,
    channel_stats=None,
):
    """Generate summary report untuk paper"""
    print("\n" + "=" * 80)
    print("SUMMARY REPORT - UNTUK PAPER")
    print("=" * 80)

    # Template untuk paper
    report = f"""
TEMUAN ANALISIS EDA:

1) Distribusi Kategori Berita:
   
   Analisis distribusi kategori dilakukan untuk mendeteksi adanya ketidakseimbangan 
   kelas (class imbalance) antara kategori berita. Ketidakseimbangan yang ekstrem 
   dapat menyebabkan model bias terhadap kelas mayoritas.
   
   Seperti terlihat pada Gambar 1, proporsi data menunjukkan:
"""

    # Tambahkan info distribusi
    for cat, pct in category_pct.items():
        count = category_stats[cat]
        report += f"   - {cat}: {count:,} artikel ({pct:.1f}%)\n"

    # Analisis imbalance
    dominant_cat = category_pct.idxmax()
    dominant_pct = category_pct.max()

    if imbalance_ratio > 2:
        report += f"""
   Dataset menunjukkan ketidakseimbangan dengan kategori "{dominant_cat}" mendominasi 
   sebesar {dominant_pct:.1f}% dari total data (rasio ketidakseimbangan: {imbalance_ratio:.2f}x).
   
   Hal ini mengindikasikan perlunya strategi evaluasi menggunakan metrik F1-Score 
   (macro atau weighted) daripada sekadar akurasi, untuk menghindari bias terhadap 
   kelas mayoritas dalam evaluasi performa model.
"""
    else:
        report += f"""
   Dataset menunjukkan distribusi yang relatif seimbang dengan rasio ketidakseimbangan 
   sebesar {imbalance_ratio:.2f}x. Namun tetap disarankan menggunakan F1-Score untuk 
   evaluasi yang lebih komprehensif.
"""

    report += f"""
2) Statistik Panjang Teks:
   
   Analisis panjang teks dilakukan untuk memahami karakteristik artikel dalam dataset.
   
   Berdasarkan histogram pada Gambar 2, karakteristik panjang artikel adalah:
   - Rata-rata panjang artikel: {text_stats['mean_words']:.0f} kata
   - Median panjang artikel: {text_stats['median_words']:.0f} kata
   - Standar deviasi: {text_stats['std_words']:.0f} kata
   - Range: {text_stats['min_words']:.0f} - {text_stats['max_words']:.0f} kata
   
   Distribusi panjang artikel menunjukkan variasi yang cukup signifikan, dengan
   sebagian besar artikel berada di sekitar median {text_stats['median_words']:.0f} kata.
   Informasi ini penting untuk preprocessing dan strategi model training.
"""

    # Tambahkan analisis NER jika ada
    if ner_stats:
        report += f"""
3) Analisis Named Entity Recognition (NER):
   
   Analisis entitas menunjukkan bahwa dari {ner_stats['articles_with_entities']:,} artikel 
   yang memiliki entitas (coverage: {ner_stats['articles_with_entities']/len(category_stats)*100:.1f}%), 
   berhasil diekstrak total {ner_stats['total_entities']:,} entitas dengan 
   {ner_stats['unique_types']} tipe entitas berbeda.
   
   Rata-rata setiap artikel mengandung {ner_stats['avg_entities_per_article']:.1f} entitas.
   
   Top 5 Tipe Entitas yang paling sering muncul:
"""
        for entity_type, count in ner_stats["top_types"][:5]:
            pct = count / ner_stats["total_entities"] * 100
            report += f"   - {entity_type}: {count:,} ({pct:.1f}%)\n"

        report += f"""
   Entitas yang paling sering disebutkan (Top 5):
"""
        for entity_name, count in ner_stats["top_entities"][:5]:
            report += f"   - {entity_name}: {count:,} kali\n"

    # Tambahkan analisis Summary jika ada
    if summary_stats:
        report += f"""
4) Analisis Ringkasan (Summary):
   
   Analisis ringkasan artikel menunjukkan:
   - Rata-rata panjang summary: {summary_stats['mean_summary_length']:.0f} kata
   - Median panjang summary: {summary_stats['median_summary_length']:.0f} kata
   - Rata-rata compression ratio: {summary_stats['mean_compression_ratio']:.1f}%
   - Median compression ratio: {summary_stats['median_compression_ratio']:.1f}%
   
   Compression ratio menunjukkan bahwa ringkasan rata-rata sekitar 
   {summary_stats['mean_compression_ratio']:.1f}% dari panjang artikel asli, 
   yang mengindikasikan kompresi informasi yang efektif dalam proses summarization.
"""

    # Tambahkan analisis Channel & Temporal jika ada
    if channel_stats:
        report += f"""
5) Distribusi Channel & Temporal:
   
   Dataset berasal dari {len(channel_stats['channel_distribution'])} sumber channel:
"""
        for channel, count in sorted(
            channel_stats["channel_distribution"].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            pct = count / sum(channel_stats["channel_distribution"].values()) * 100
            report += f"   - {channel}: {count:,} artikel ({pct:.1f}%)\n"

        report += f"""
   Rentang waktu publikasi: {channel_stats['date_range']}
   Total periode: {channel_stats['total_days']} hari
   
   Distribusi temporal artikel menunjukkan pola publikasi berita dari berbagai channel
   sepanjang periode observasi, yang penting untuk memahami representasi temporal dataset.
"""

    print(report)

    # Simpan ke file
    with open("eda_summary_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n✓ Summary report disimpan: eda_summary_report.txt")

    return report


def main():
    """Main function untuk menjalankan seluruh analisis EDA"""

    # Path ke dataset
    dataset_path = "../column_adder/final_processed_dataset_nona.csv"

    # Load data
    df = load_data(dataset_path)

    # Analisis 1: Distribusi Kategori
    category_counts, category_pct, imbalance_ratio = analyze_category_distribution(df)

    # Analisis 2: Statistik Panjang Teks
    text_stats = analyze_text_length(df)

    # Analisis 3: NER Analysis (jika kolom ner ada)
    ner_stats = None
    if "ner" in df.columns:
        ner_stats = analyze_ner_entities(df)

    # Analisis 4: Summary Analysis (jika kolom summary ada)
    summary_stats = None
    if "summary" in df.columns:
        summary_stats = analyze_summary(df)

    # Analisis 5: Channel & Temporal (jika kolom tersedia)
    channel_stats = None
    if "channel" in df.columns and "published_date" in df.columns:
        channel_stats = analyze_channel_temporal(df)

    # Generate summary report
    report = generate_summary_report(
        category_counts,
        text_stats,
        category_pct,
        imbalance_ratio,
        ner_stats,
        summary_stats,
        channel_stats,
    )

    print("\n" + "=" * 80)
    print("ANALISIS EDA SELESAI!")
    print("=" * 80)
    print("\nFile yang dihasilkan:")
    print("  1. gambar1_distribusi_kategori.png")
    print("  2. gambar2_statistik_panjang_teks.png")
    if "ner" in df.columns:
        print("  3. gambar3_analisis_ner.png")
    if "summary" in df.columns:
        print("  4. gambar4_analisis_summary.png")
    if "channel" in df.columns and "published_date" in df.columns:
        print("  5. gambar5_channel_temporal.png")
    print("  6. eda_summary_report.txt")
    print("\nGunakan hasil analisis ini untuk paper Anda.")


if __name__ == "__main__":
    main()
