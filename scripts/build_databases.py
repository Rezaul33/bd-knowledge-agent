#!/usr/bin/env python3
"""
Database Builder Script for Bangladesh Knowledge Agent

This script creates and initializes the SQLite databases for the Bangladesh Knowledge Agent.
It creates the database schema and populates them with sample data for testing.

Usage:
    python scripts/build_databases.py [--recreate] [--sample-data]

Options:
    --recreate    Drop and recreate existing databases
    --sample-data Populate with sample data for testing
"""

import sqlite3
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config

class DatabaseBuilder:
    """Builds and initializes SQLite databases for the Bangladesh Knowledge Agent"""
    
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"Created directory: {self.data_dir}")
    
    def create_institutions_database(self, recreate: bool = False, sample_data: bool = False):
        """Create and populate institutions database"""
        db_path = os.path.join(self.data_dir, "institutions.db")
        
        if recreate and os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing institutions database")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create institutions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS institutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                location TEXT NOT NULL,
                established INTEGER,
                degrees_offered TEXT,
                students_count INTEGER,
                public_private TEXT,
                specialization TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_institutions_name ON institutions(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_institutions_type ON institutions(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_institutions_location ON institutions(location)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_institutions_established ON institutions(established)')
        
        if sample_data:
            self._populate_institutions_sample_data(cursor)
        
        conn.commit()
        conn.close()
        print(f"✅ Institutions database created: {db_path}")
    
    def create_hospitals_database(self, recreate: bool = False, sample_data: bool = False):
        """Create and populate hospitals database"""
        db_path = os.path.join(self.data_dir, "hospitals.db")
        
        if recreate and os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing hospitals database")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create hospitals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hospitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                location TEXT NOT NULL,
                bed_capacity INTEGER,
                emergency_services TEXT,
                specialties TEXT,
                public_private TEXT,
                established INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hospitals_name ON hospitals(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hospitals_type ON hospitals(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hospitals_location ON hospitals(location)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hospitals_bed_capacity ON hospitals(bed_capacity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hospitals_emergency ON hospitals(emergency_services)')
        
        if sample_data:
            self._populate_hospitals_sample_data(cursor)
        
        conn.commit()
        conn.close()
        print(f"✅ Hospitals database created: {db_path}")
    
    def create_restaurants_database(self, recreate: bool = False, sample_data: bool = False):
        """Create and populate restaurants database"""
        db_path = os.path.join(self.data_dir, "restaurants.db")
        
        if recreate and os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing restaurants database")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create restaurants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cuisine TEXT NOT NULL,
                location TEXT NOT NULL,
                rating REAL,
                price_range TEXT,
                specialties TEXT,
                established INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_restaurants_name ON restaurants(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_restaurants_cuisine ON restaurants(cuisine)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_restaurants_location ON restaurants(location)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_restaurants_rating ON restaurants(rating)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_restaurants_price_range ON restaurants(price_range)')
        
        if sample_data:
            self._populate_restaurants_sample_data(cursor)
        
        conn.commit()
        conn.close()
        print(f"✅ Restaurants database created: {db_path}")
    
    def _populate_institutions_sample_data(self, cursor):
        """Populate institutions database with sample data"""
        sample_institutions = [
            ("University of Dhaka", "University", "Dhaka", 1921, "Undergraduate, Graduate, PhD", 35000, "Public", "General"),
            ("Bangladesh University of Engineering and Technology", "University", "Dhaka", 1962, "Undergraduate, Graduate, PhD", 8000, "Public", "Engineering"),
            ("Bangabandhu Sheikh Mujib Medical University", "University", "Dhaka", 1998, "Undergraduate, Graduate, PhD", 12000, "Public", "Medical"),
            ("Dhaka Medical College", "College", "Dhaka", 1946, "Undergraduate", 2500, "Public", "Medical"),
            ("Chittagong University", "University", "Chattogram", 1966, "Undergraduate, Graduate, PhD", 22000, "Public", "General"),
            ("Rajshahi University", "University", "Rajshahi", 1953, "Undergraduate, Graduate, PhD", 25000, "Public", "General"),
            ("Khulna University", "University", "Khulna", 1991, "Undergraduate, Graduate", 8000, "Public", "General"),
            ("Jahangirnagar University", "University", "Savar", 1970, "Undergraduate, Graduate, PhD", 15000, "Public", "General"),
            ("North South University", "University", "Dhaka", 1992, "Undergraduate, Graduate", 12000, "Private", "General"),
            ("BRAC University", "University", "Dhaka", 2001, "Undergraduate, Graduate, PhD", 6000, "Private", "General"),
            ("American International University-Bangladesh", "University", "Dhaka", 2002, "Undergraduate, Graduate", 10000, "Private", "General"),
            ("East West University", "University", "Dhaka", 1996, "Undergraduate, Graduate", 8000, "Private", "General"),
            ("Bangladesh University of Business & Technology", "University", "Dhaka", 2003, "Undergraduate, Graduate", 5000, "Private", "Business"),
            ("Independent University Bangladesh", "University", "Dhaka", 1993, "Undergraduate, Graduate", 7000, "Private", "General"),
            ("United International University", "University", "Dhaka", 2003, "Undergraduate, Graduate", 6000, "Private", "General")
        ]
        
        cursor.executemany('''
            INSERT INTO institutions (name, type, location, established, degrees_offered, students_count, public_private, specialization)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_institutions)
        
        print(f"📊 Inserted {len(sample_institutions)} sample institutions")
    
    def _populate_hospitals_sample_data(self, cursor):
        """Populate hospitals database with sample data"""
        sample_hospitals = [
            ("Bangabandhu Sheikh Mujib Medical University Hospital", "Teaching Hospital", "Dhaka", 1500, "Yes", "General, Cardiology, Neurology", "Public", 1998),
            ("Dhaka Medical College Hospital", "Teaching Hospital", "Dhaka", 2300, "Yes", "General, Surgery, Medicine", "Public", 1946),
            ("Sir Salimullah Medical College Hospital", "Teaching Hospital", "Dhaka", 1200, "Yes", "General, Pediatrics", "Public", 1963),
            ("Chittagong Medical College Hospital", "Teaching Hospital", "Chattogram", 1300, "Yes", "General, Surgery", "Public", 1957),
            ("Rajshahi Medical College Hospital", "Teaching Hospital", "Rajshahi", 1000, "Yes", "General, Medicine", "Public", 1958),
            ("Khulna Medical College Hospital", "Teaching Hospital", "Khulna", 800, "Yes", "General, Surgery", "Public", 1962),
            ("Apollo Hospitals Dhaka", "Private Hospital", "Dhaka", 450, "Yes", "Cardiology, Neurology, Oncology", "Private", 2005),
            ("United Hospital Limited", "Private Hospital", "Dhaka", 500, "Yes", "Cardiology, Surgery, ICU", "Private", 2006),
            ("Kurmitola General Hospital", "General Hospital", "Dhaka", 250, "Yes", "General, Emergency", "Public", 1965),
            ("Ibrahim Cardiac Hospital & Research Institute", "Specialized Hospital", "Dhaka", 350, "Yes", "Cardiology, Cardiac Surgery", "Private", 2003),
            ("National Institute of Neurosciences", "Specialized Hospital", "Dhaka", 400, "Yes", "Neurology, Neurosurgery", "Public", 2012),
            ("Bangabandhu Sheikh Mujib Medical University", "Teaching Hospital", "Dhaka", 1200, "Yes", "Medical Education, Research", "Public", 1998),
            ("Shaheed Suhrawardy Medical College Hospital", "Teaching Hospital", "Dhaka", 900, "Yes", "General, Medicine", "Public", 2006),
            ("Mymensingh Medical College Hospital", "Teaching Hospital", "Mymensingh", 750, "Yes", "General, Surgery", "Public", 1968),
            ("Sylhet MAG Osmani Medical College Hospital", "Teaching Hospital", "Sylhet", 600, "Yes", "General, Medicine", "Public", 1969)
        ]
        
        cursor.executemany('''
            INSERT INTO hospitals (name, type, location, bed_capacity, emergency_services, specialties, public_private, established)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_hospitals)
        
        print(f"📊 Inserted {len(sample_hospitals)} sample hospitals")
    
    def _populate_restaurants_sample_data(self, cursor):
        """Populate restaurants database with sample data"""
        sample_restaurants = [
            ("Pizza Hut", "Italian", "Dhaka", 3.8, "Medium", "Pizza, Pasta", 2003),
            ("KFC", "American", "Dhaka", 3.7, "Medium", "Fried Chicken, Burgers", 2006),
            ("Starbucks", "Coffee", "Dhaka", 4.2, "Expensive", "Coffee, Pastries", 2013),
            ("Burger King", "American", "Dhaka", 3.9, "Medium", "Burgers, Fries", 2016),
            ("Subway", "American", "Dhaka", 4.0, "Medium", "Sandwiches, Salads", 2003),
            ("Domino's Pizza", "Italian", "Dhaka", 3.6, "Medium", "Pizza, Garlic Bread", 2015),
            ("Nando's", "Portuguese", "Dhaka", 4.1, "Medium", "Peri-Peri Chicken", 2011),
            ("The Coffee House", "Coffee", "Dhaka", 4.3, "Medium", "Coffee, Desserts", 2014),
            ("Barista", "Coffee", "Dhaka", 4.0, "Medium", "Coffee, Snacks", 2010),
            ("Gloria Jean's Coffees", "Coffee", "Dhaka", 3.9, "Medium", "Coffee, Cake", 2012),
            ("Le Méridien Dhaka", "International", "Dhaka", 4.5, "Expensive", "Fine Dining, International", 2015),
            ("Westin Dhaka", "International", "Dhaka", 4.4, "Expensive", "Fine Dining, Asian", 2006),
            ("Pan Pacific Dhaka", "International", "Dhaka", 4.3, "Expensive", "Fine Dining, Chinese", 2014),
            ("Radisson Blu Dhaka", "International", "Dhaka", 4.2, "Expensive", "Buffet, International", 2011),
            ("Sheraton Dhaka", "International", "Dhaka", 4.1, "Expensive", "Fine Dining, Continental", 2018)
        ]
        
        cursor.executemany('''
            INSERT INTO restaurants (name, cuisine, location, rating, price_range, specialties, established)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_restaurants)
        
        print(f"📊 Inserted {len(sample_restaurants)} sample restaurants")
    
    def create_all_databases(self, recreate: bool = False, sample_data: bool = False):
        """Create all databases"""
        print("🏗️  Building Bangladesh Knowledge Agent databases...")
        print("=" * 50)
        
        self.create_institutions_database(recreate, sample_data)
        self.create_hospitals_database(recreate, sample_data)
        self.create_restaurants_database(recreate, sample_data)
        
        print("=" * 50)
        print("✅ All databases created successfully!")
        
        # Verify databases
        self.verify_databases()
    
    def verify_databases(self):
        """Verify that all databases were created and have data"""
        databases = {
            "institutions.db": "institutions",
            "hospitals.db": "hospitals", 
            "restaurants.db": "restaurants"
        }
        
        print("\n🔍 Verifying databases...")
        
        for db_file, table_name in databases.items():
            db_path = os.path.join(self.data_dir, db_file)
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                conn.close()
                print(f"✅ {db_file}: {count} records in {table_name} table")
            else:
                print(f"❌ {db_file}: Database not found")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Build databases for Bangladesh Knowledge Agent")
    parser.add_argument("--recreate", action="store_true", help="Drop and recreate existing databases")
    parser.add_argument("--sample-data", action="store_true", help="Populate with sample data")
    
    args = parser.parse_args()
    
    try:
        builder = DatabaseBuilder()
        builder.create_all_databases(recreate=args.recreate, sample_data=args.sample_data)
        
        print("\n🎉 Database building completed successfully!")
        print("You can now run the Bangladesh Knowledge Agent.")
        
    except Exception as e:
        print(f"❌ Error building databases: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
