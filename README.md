# Raw-Telegram-Data-to-an-Analytical-API
# Medical Telegram Warehouse

## 📌 Project Overview

This project builds an **end-to-end data engineering pipeline** for collecting, transforming, and modeling data from **Telegram channels related to Ethiopian medical businesses**. The goal is to turn raw, unstructured Telegram messages into a **clean, trusted, analytics-ready data warehouse** using modern data engineering tools.

The pipeline follows a classic **ELT architecture**:

1. **Extract & Load** – Scrape raw Telegram data and load it into PostgreSQL
2. **Transform** – Use dbt to clean, test, and model the data
3. **Serve** – Provide a star schema optimized for analytics and reporting

---

## 🏗️ Project Structure

```
medical-telegram-warehouse/
├── .env                        # Secrets (API keys, DB credentials) – NOT COMMITTED
├── requirements.txt
├── README.md
├── data/
│   └── raw/
│       ├── telegram_messages/
│       │   └── YYYY-MM-DD/
│       │       ├── lobelia4cosmetics.json
│       │       ├── tikvahpharma.json
│       │       └── chemed123.json
│       └── images/
│           └── channel_name/
│               └── message_id.jpg
├── logs/
│   └── scraper.log
├── src/
│   ├── scraper.py              # Telegram scraping pipeline
│   └── config.py               # Centralized configuration
├── notebooks/
│   └── telegram_scraping.ipynb # Reproducible execution notebook
├── medical_warehouse/          # dbt project
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   └── tests/
└── scripts/
```

---

## 🧩 Task 1 – Data Scraping and Collection (Extract & Load)

### 🎯 Objective

Extract messages and images from selected Telegram channels and store them in a **raw data lake**, preserving the original structure.

### 📡 Telegram Channels Scraped

* `@lobelia4cosmetics`
* `@tikvahpharma`
* `@chemed123`

### 🔐 Authentication

* Telegram API credentials (`api_id`, `api_hash`) are stored in `.env`
* Loaded securely using **python-dotenv**

### ⚙️ Scraping Logic

* Built using **Telethon (async)**
* Scrapes a **limited number of recent messages per channel** (configurable)
* Each channel can have a different message limit

### 📥 Extracted Fields

For each message:

* `message_id`
* `date` (ISO format)
* `text`
* `views`
* `forwards`
* `media metadata`

### 🖼️ Image Handling

* If a message contains a photo:

  * Downloaded to:

    ```
    data/raw/images/{channel_name}/{message_id}.jpg
    ```
  * Directories are created automatically

### 🗂️ Data Lake Storage

* Raw data stored as JSON
* Partitioned by **date and channel**:

  ```
  data/raw/telegram_messages/YYYY-MM-DD/{channel_name}.json
  ```
* Uses `json.dump(..., default=str)` to handle datetime serialization

### 📊 Progress Tracking

* Scraping progress is displayed as a **percentage** while messages are being collected

### 🧾 Logging & Error Handling

* Logs saved to `logs/scraper.log`
* Captures:

  * Start/end of each channel scrape
  * Errors (network issues, rate limits, unexpected failures)
* Designed to fail gracefully without crashing the pipeline

---

## 🧱 Task 2 – Data Modeling and Transformation (Transform)

### 🎯 Objective

Transform messy raw Telegram data into a **clean, trusted star schema** using **dbt**.

---

## 🐘 PostgreSQL Layer

### ✅ What Is Created Manually

Only **one table** is created manually:

```sql
raw.telegram_messages
```

This table:

* Stores raw scraped data
* Is append-only
* Never modified or cleaned

Schemas created:

```sql
raw
staging
marts
```

All other tables are created by **dbt**.

---

## 🧼 Staging Models (models/staging)

### Purpose

* Clean and standardize raw data
* Prepare data for dimensional modeling

### Key Transformations

* Cast data types correctly (dates, integers)
* Rename columns using consistent naming conventions
* Remove invalid records (null or empty messages)
* Add derived fields:

  * `message_length`
  * `has_image`

### Example Model

```text
stg_telegram_messages.sql
```

---

## ⭐ Star Schema Design (models/marts)

### 📐 Design Choice

A **star schema** was chosen for:

* Fast analytical queries
* Clear separation of facts and dimensions
* BI and dashboard friendliness

---

### 📊 Fact Table

#### `fct_messages`

One row per Telegram message

| Column         | Description        |
| -------------- | ------------------ |
| message_id     | Natural message ID |
| channel_key    | FK to dim_channels |
| date_key       | FK to dim_dates    |
| message_text   | Message content    |
| message_length | Character count    |
| view_count     | Views              |
| forward_count  | Forwards           |
| has_image      | Image indicator    |

---

### 🧩 Dimension Tables

#### `dim_channels`

Stores channel-level information

* channel_key (surrogate key)
* channel_name
* channel_type (Pharmaceutical, Cosmetics, Medical)
* first_post_date
* last_post_date
* total_posts
* avg_views

#### `dim_dates`

Standard date dimension

* date_key
* full_date
* day_name, month_name, year
* week_of_year, quarter
* is_weekend

---

## ✅ Data Testing with dbt

### Built-in Tests (schema.yml)

* `unique` and `not_null` tests on primary keys
* `relationships` tests on foreign keys

### Custom Tests (tests/)

#### Examples:

* `assert_no_future_messages.sql`

  * Ensures no message has a future date

* `assert_positive_views.sql`

  * Ensures view counts are non-negative

> All tests must return **0 rows** to pass

---

## 📚 Documentation

* Generated using:

  ```bash
  dbt docs generate
  dbt docs serve
  ```
* Includes:

  * Model descriptions
  * Column-level metadata
  * Lineage graph

---

## 🔁 Reproducibility

### Achieved Through:

* Centralized configuration (`config.py`)
* Environment-based secrets (`.env`)
* Deterministic dbt models
* Notebook-based execution for transparency

### Final Execution Entry Point

All steps can be **re-run reproducibly** from:

```text
notebooks/telegram_scraping.ipynb
```

---

## 🌟 Final Outcome

This project delivers:

* A reliable Telegram data ingestion pipeline
* A clean, tested PostgreSQL data warehouse
* A star schema optimized for analytics
* Fully documented, reproducible transformations

Raw chaos becomes trusted insight — gently, clearly, and at scale 🌿
