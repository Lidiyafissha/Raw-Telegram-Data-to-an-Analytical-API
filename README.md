# Raw-Telegram-Data-to-an-Analytical-API
🏥 Shipping a Data Product: From Raw Telegram Data to an Analytical API
📌 Project Overview

This project builds an end-to-end, production-ready data pipeline that transforms raw, unstructured Telegram data into a clean, enriched, and queryable analytical API.

The system focuses on Ethiopian medical and pharmaceutical Telegram channels, extracting insights about products, prices, posting behavior, and visual content. It follows modern data engineering best practices, including ELT architecture, dimensional modeling, data validation, enrichment with computer vision, and pipeline orchestration.

The final result is not just data — but a reliable data product.

🎯 Business Problem

Medical businesses in Ethiopia actively use Telegram to advertise products, prices, and availability. However:

The data is scattered across channels

Messages are unstructured and inconsistent

Images contain valuable signals that are often ignored

Manual analysis does not scale

This project answers questions such as:

What are the most frequently mentioned medical products?

How does activity vary across channels and time?

Which channels rely more on visual promotion?

Do posts with people or product images attract more attention?

🏗️ Architecture Overview

The project follows a layered ELT architecture:

Telegram → Data Lake → PostgreSQL (Raw) → dbt (Staging & Marts)
        → YOLO Image Enrichment → Analytical API → Orchestration (Dagster)


Each layer has a clear responsibility, making the system robust, scalable, and reproducible.

📁 Project Structure
medical-telegram-warehouse/
│
├── src/                    # Core pipeline scripts
│   ├── scraper.py          # Telegram scraping
│   ├── load_raw_to_postgres.py
│   └── yolo_detect.py      # Image enrichment
│
├── api/                    # FastAPI application
│   ├── main.py
│   ├── database.py
│   └── schemas.py
│
├── medical_warehouse/      # dbt project
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   └── tests/
│
├── data/
│   ├── raw/                # JSON + images
│   └── processed/          # YOLO outputs
│
├── pipeline.py             # Dagster orchestration
├── requirements.txt
├── docker-compose.yml
├── .env                    # Secrets (not committed)
└── README.md

✅ Task Breakdown
🔹 Task 1 – Data Scraping & Loading (Extract & Load)
What was done

Connected securely to the Telegram API using Telethon

Scraped a controlled number of messages from public medical channels

Extracted:

Message ID, timestamp, text

Views and forwards

Media metadata

Downloaded images into a structured folder hierarchy

Stored raw data as partitioned JSON files

Implemented logging for observability

Loaded raw JSON data into PostgreSQL without modification

Result

A trustworthy raw data lake and a raw.telegram_messages table preserving original truth.

🔹 Task 2 – Data Modeling & Transformation (Transform)
What was done

Initialized a dbt project connected to PostgreSQL

Created schemas:

raw → original data

staging → cleaned data

marts → analytics-ready models

Built staging models to:

Cast data types

Standardize column names

Remove invalid records

Add derived fields

Designed a star schema:

dim_channels

dim_dates

fct_messages

Implemented dbt tests:

not_null, unique

Foreign key relationships

Custom business rule tests

Generated dbt documentation

Result

A clean, tested, and documented data warehouse optimized for analytics and APIs.

🔹 Task 3 – Data Enrichment with YOLOv8 (Enrich)
What was done

Used YOLOv8 nano for efficient object detection

Scanned downloaded Telegram images

Detected objects and confidence scores

Classified images into:

promotional

product_display

lifestyle

other

Stored results in a CSV

Integrated image data into the warehouse via dbt

Result

Unstructured images were transformed into structured analytical signals, enabling visual-content insights.

🔹 Task 4 – Analytical API (Serve)
What was done

Built a FastAPI application

Connected to PostgreSQL via SQLAlchemy

Implemented analytical endpoints:

Top mentioned products

Channel activity trends

Message keyword search

Visual content statistics

Added Pydantic schemas for validation

Enabled automatic OpenAPI documentation

Result

A self-documenting analytical API that exposes warehouse insights to dashboards and users.

🔹 Task 5 – Pipeline Orchestration with Dagster (Automate)
What was done

Converted each pipeline step into Dagster ops

Defined a job enforcing execution order

Enabled logging, retries, and observability

Configured daily scheduling

Verified execution via Dagster UI

Result

The pipeline became a fully automated, observable workflow, no longer a collection of scripts.

🔁 Reproducibility & Reliability

Reproducibility is ensured through:

.env for secrets and credentials

requirements.txt for dependency control

dbt for deterministic transformations

Dagster for execution guarantees

Clear module boundaries

To reproduce the system:

Set environment variables

Install dependencies

Run Dagster or individual components

🚀 How to Run
pip install -r requirements.txt
dagster dev -f pipeline.py


Access:

Dagster UI → http://localhost:3000

API Docs → http://localhost:8000/docs

🔮 Future Extensions

Product-level entity recognition (NER)

Price extraction using NLP

Alerting on product availability changes

Dashboard integration (Superset / Power BI)

Domain-specific computer vision models