import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Helper class for SQLite database operations"""
    
    @staticmethod
    def create_connection(db_path: str) -> sqlite3.Connection:
        """Create database connection"""
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
            return conn
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database {db_path}: {e}")
            raise
    
    @staticmethod
    def execute_query(conn: sqlite3.Connection, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results"""
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except sqlite3.Error as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            raise
    
    @staticmethod
    def validate_schema(conn: sqlite3.Connection, table_name: str) -> List[str]:
        """Get table schema information"""
        try:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema = cursor.fetchall()
            return [f"{row[1]} {row[2]}" for row in schema]
        except sqlite3.Error as e:
            logger.error(f"Error getting schema for {table_name}: {e}")
            raise
    
    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Clean column names: lowercase, snake_case, remove special chars"""
        df.columns = df.columns.str.lower()
        df.columns = df.columns.str.replace(' ', '_')
        df.columns = df.columns.str.replace('-', '_')
        df.columns = df.columns.str.replace('[^a-zA-Z0-9_]', '', regex=True)
        return df
    
    @staticmethod
    def infer_sql_types(df: pd.DataFrame) -> Dict[str, str]:
        """Infer SQLite data types from pandas DataFrame"""
        type_mapping = {
            'int64': 'INTEGER',
            'float64': 'REAL',
            'bool': 'INTEGER',
            'object': 'TEXT',
            'datetime64[ns]': 'TEXT',
            'category': 'TEXT'
        }
        
        sql_types = {}
        for col in df.columns:
            pandas_type = str(df[col].dtype)
            sql_types[col] = type_mapping.get(pandas_type, 'TEXT')
        
        return sql_types
    
    @staticmethod
    def create_table_from_df(conn: sqlite3.Connection, df: pd.DataFrame, table_name: str) -> None:
        """Create table and insert data from DataFrame"""
        # Clean column names
        df = DatabaseManager.clean_column_names(df)
        
        # Infer SQL types
        sql_types = DatabaseManager.infer_sql_types(df)
        
        # Create table SQL
        columns_def = ', '.join([f"{col} {sql_types[col]}" for col in df.columns])
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        
        # Insert data
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        logger.info(f"Created table {table_name} with {len(df)} rows")
