import pandas as pd
import json
import os
from datetime import datetime, timedelta
import streamlit as st

# Database simulation using session state and local files
DATA_DIR = "data"


def init_database():
    """Initialize database tables in session state"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Initialize session state tables if they don't exist
    tables = [
        'families', 'workers', 'collections', 'vehicles',
        'community_reports', 'rewards_fines', 'training_records.json',
        'safety_kits', 'treatment_reports', 'collection_routes'
    ]

    for table in tables:
        if table not in st.session_state:
            st.session_state[table] = load_data(table)


def load_data(table_name):
    """Load data from JSON file"""
    file_path = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return []
    except:
        return []


def save_data(table_name, data):
    """Save data to JSON file"""
    file_path = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        st.session_state[table_name] = data
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")


def add_record(table_name, record):
    """Add a new record to the specified table"""
    if table_name not in st.session_state:
        st.session_state[table_name] = []

    # Add timestamp and unique ID
    record['id'] = len(st.session_state[table_name]) + 1
    record['created_at'] = datetime.now().isoformat()

    st.session_state[table_name].append(record)
    save_data(table_name, st.session_state[table_name])

    return record


def update_record(table_name, record_id, updates):
    """Update an existing record"""
    if table_name in st.session_state:
        for i, record in enumerate(st.session_state[table_name]):
            if record.get('id') == record_id:
                st.session_state[table_name][i].update(updates)
                st.session_state[table_name][i]['updated_at'] = datetime.now().isoformat()
                save_data(table_name, st.session_state[table_name])
                return True
    return False


def get_records(table_name, filters=None):
    """Get records from the specified table with optional filters"""
    if table_name not in st.session_state:
        return []

    records = st.session_state[table_name]

    if filters:
        filtered_records = []
        for record in records:
            match = True
            for key, value in filters.items():
                if key not in record or record[key] != value:
                    match = False
                    break
            if match:
                filtered_records.append(record)
        return filtered_records

    return records


def get_dashboard_stats():
    """Get statistics for the dashboard"""
    stats = {}

    # Count families
    families = get_records('families')
    stats['families'] = len(families)

    # Count workers
    workers = get_records('workers')
    stats['workers'] = len([w for w in workers if w.get('status') == 'active'])

    # Count today's collections
    today = datetime.now().date().isoformat()
    collections = get_records('collections')
    stats['collections_today'] = len([c for c in collections if c.get('date', '').startswith(today)])

    # Count community reports
    reports = get_records('community_reports')
    stats['community_reports'] = len(reports)

    # Training completion rate
    training_records = get_records('training_records.json')
    completed = len([t for t in training_records if t.get('status') == 'completed'])
    pending = len([t for t in training_records if t.get('status') == 'pending'])
    stats['training_completion'] = {'completed': completed, 'pending': pending}

    # Segregation quality
    good_segregation = len([c for c in collections if c.get('segregation_quality') == 'good'])
    poor_segregation = len([c for c in collections if c.get('segregation_quality') == 'poor'])
    stats['segregation_quality'] = {'good': good_segregation, 'poor': poor_segregation}

    # Recent alerts (mock for now)
    stats['recent_alerts'] = []

    return stats
