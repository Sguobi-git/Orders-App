# Show Order Management

A Streamlit app for tracking exhibitor orders during a trade show, built for Expo Convention Contractors (Miami) to replace a paper-based order process on the show floor.

## What it does

- Multi-user login, scoped to a specific show
- Order creation, editing, and status tracking (In Process / Delivered / Cancelled), backed by a live Google Sheet so multiple staff see the same data at once
- A simple feedback/message board for exhibitors, stored as local JSON

Google Sheets is the database: `data/direct_sheets_operations.py` and `data/test_data_manager.py` handle reads and writes through the Sheets API, with `st.cache_data` to avoid hammering the API on every page load.

## Stack

Python, Streamlit, gspread (Google Sheets API), pandas.

## Running it

```
pip install -r requirements.txt
# add a Google Cloud service account under st.secrets["gcp_service_account"]
streamlit run app/Home.py
```

## Honest limitations

This was built fast for a specific show and iterated on through several internal versions rather than designed up front, so it has the rough edges you'd expect: no automated tests, and the Google Sheets calls aren't batched, so a busy show floor with many concurrent edits would need a proper database or at least request batching before this scaled past a single-show, few-dozen-user use case.
