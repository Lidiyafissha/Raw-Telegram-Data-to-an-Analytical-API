# pipeline.py

from dagster import op, job, ScheduleDefinition
import subprocess
import os

# ---------------------------
# CONFIG
# ---------------------------

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------
# OPS
# ---------------------------


@op
def scrape_telegram_data():
    result = subprocess.run(
        ["python", "src/scraper.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise Exception(f"Scraping failed:\n{result.stderr}")
    return "Scraping completed"


@op
def load_raw_to_postgres():
    result = subprocess.run(
        ["python", "src/load_raw_to_postgres.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise Exception(f"Load failed:\n{result.stderr}")
    return "Raw data loaded"


@op
def run_dbt_transformations():
    result = subprocess.run(
        ["dbt", "run"],
        cwd=os.path.join(PROJECT_ROOT, "medical_warehouse"),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise Exception(f"dbt failed:\n{result.stderr}")
    return "dbt transformations completed"


@op
def run_yolo_enrichment():
    result = subprocess.run(
        ["python", "src/yolo_detect.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise Exception(f"YOLO failed:\n{result.stderr}")
    return "YOLO enrichment completed"


# ---------------------------
# JOB (PIPELINE GRAPH)
# ---------------------------


@job
def medical_telegram_pipeline():
    scrape_telegram_data()
    load_raw_to_postgres()
    run_dbt_transformations()
    run_yolo_enrichment()


# ---------------------------
# SCHEDULE (DAILY RUN)
# ---------------------------

daily_schedule = ScheduleDefinition(
    job=medical_telegram_pipeline,
    cron_schedule="0 2 * * *",  # runs daily at 2 AM
)

