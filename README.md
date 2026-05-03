# YouTube ELT Pipeline (Airflow + Docker + PostgreSQL)

## Overview

This project implements an end-to-end ELT (Extract, Load, Transform) data pipeline using modern data engineering tools.

The pipeline extracts video data from the YouTube API, loads it into a PostgreSQL data warehouse using a staging/core architecture, and applies automated data quality checks.

The project is fully containerized with Docker and orchestrated using Apache Airflow.

---

## Motivation

The goal of this project is to gain hands-on experience with real-world data engineering workflows, including:

- Building orchestrated pipelines with Airflow
- Working with containerized environments (Docker)
- Designing a simple data warehouse (staging → core)
- Implementing unit tests and data quality checks
- Understanding CI/CD concepts (GitHub Actions)

---

## Data Source

The data is retrieved from the YouTube Data API.

Current implementation uses:

- Channel: **MrBeast**

The pipeline can be easily adapted to any other channel by modifying the channel handle.

---

## Architecture

The pipeline follows this structure:

### Steps:

1. **Extract**
   - Data is pulled from the YouTube API using Python
   - Saved as JSON files

2. **Load (staging)**
   - Raw data is inserted into the `staging` schema

3. **Transform (core)**
   - Data is cleaned and transformed
   - Loaded into the `core` schema

4. **Data Quality**
   - Validations are applied using Soda

---

## Orchestration (Airflow)

The pipeline is orchestrated using Airflow and consists of three DAGs:

- `produce_json`  
  Extracts data from the API and stores it as JSON

- `update_db`  
  Loads data into staging and transforms it into core

- `data_quality_checks`  
  Runs data quality checks on the database

Airflow UI:

---

## Data Model

Two-layer architecture:

- **staging**
  - Raw, unprocessed data

- **core**
  - Cleaned and transformed data ready for analysis

---

## Data Extracted

The following fields are retrieved:

- video_id
- title
- upload_date
- duration
- video_views
- like_count
- comment_count

---

## Tech Stack

- **Python**
- **Apache Airflow**
- **PostgreSQL**
- **Docker & Docker Compose**
- **Pytest** (unit testing)
- **Soda Core** (data quality checks)

---

## Testing

### Unit Tests (pytest)

- Airflow variables
- Database connection
- DAG integrity (structure, tasks, loading)

### Data Quality (Soda)

Checks include:

- No null `video_id`
- No duplicate `video_id`
- Logical consistency (likes ≤ views, comments ≤ views)

---

## How to Run

```bash
docker compose up -d


http://localhost:8080
```
