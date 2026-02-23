"""
HospitalsDBTool - LangChain tool for querying Bangladesh hospitals database
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import sqlite3
import re
import time
from utils.database import DatabaseManager
from utils.config import Config

class HospitalsInput(BaseModel):
    """Input schema for HospitalsDBTool"""
    query: str = Field(description="Natural language query about Bangladesh hospitals")

class HospitalsDBTool(BaseTool):
    """Tool for querying Bangladesh hospitals database"""
    
    name = "HospitalsDBTool"
    description = """Use this tool for queries about Bangladesh hospitals and healthcare facilities.
    Handles hospital names, bed capacity, location, facilities, and hospital statistics.
    
    Examples:
    - "How many hospitals are in Dhaka?"
    - "List top 10 hospitals by bed capacity"
    - "Which hospitals have emergency services?"
    - "Show private hospitals in Dhaka"
    - "What hospitals offer cardiology services?"
    - "Find teaching hospitals"
    - "Hospitals established after 2000"
    
    Database schema:
    - name: Hospital name
    - location: City/District
    - bed_capacity: Number of beds
    - type: Hospital type (Teaching Hospital, Private Hospital, General Hospital)
    - public_private: Public or Private
    - emergency_services: Has emergency services (True/False)
    - specialties: Medical specialties available
    - established: Year established
    """
    
    args_schema = HospitalsInput
    
    def __init__(self):
        super().__init__()
        # Store configuration as instance attributes that don't conflict with Pydantic
        object.__setattr__(self, '_db_path', Config.HOSPITALS_DB)
        object.__setattr__(self, '_table_name', "hospitals")
        object.__setattr__(self, '_schema_info', self._get_schema_info())
    
    @property
    def db_path(self):
        return self._db_path
    
    @property
    def table_name(self):
        return self._table_name
    
    @property
    def schema_info(self):
        return self._schema_info
    
    def _get_schema_info(self) -> str:
        """Get database schema information for SQL generation"""
        conn = DatabaseManager.create_connection(self.db_path)
        try:
            schema = DatabaseManager.validate_schema(conn, self.table_name)
            return f"Table: {self.table_name}\nColumns: {', '.join(schema)}"
        finally:
            conn.close()
    
    def _validate_sql(self, sql: str) -> bool:
        """Validate SQL to prevent destructive operations"""
        sql_upper = sql.upper().strip()
        
        # Only allow SELECT queries
        if not sql_upper.startswith('SELECT'):
            return False
        
        # Block dangerous keywords
        dangerous_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER',
            'TRUNCATE', 'EXEC', 'EXECUTE', 'UNION', 'MERGE'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False
        
        return True
    
    def _generate_sql(self, natural_query: str) -> str:
        """Generate SQL from natural language query"""
        
        # Common query patterns and their SQL equivalents
        query_patterns = [
            # Count queries
            (r'how many.*hospitals?', lambda m: "SELECT COUNT(*) as total FROM hospitals"),
            (r'how many.*hospitals?.*in\s+(\w+)', lambda m: f"SELECT COUNT(*) as total FROM hospitals WHERE location LIKE '%{m.group(1)}%'"),
            (r'how many.*public.*hospitals?', lambda m: "SELECT COUNT(*) as total FROM hospitals WHERE public_private = 'Public'"),
            (r'how many.*private.*hospitals?', lambda m: "SELECT COUNT(*) as total FROM hospitals WHERE public_private = 'Private'"),
            (r'how many.*teaching.*hospitals?', lambda m: "SELECT COUNT(*) as total FROM hospitals WHERE type LIKE '%Teaching%'"),
            
            # Location-based queries
            (r'hospitals?.*in\s+(\w+)', lambda m: f"SELECT name, type, bed_capacity, location FROM hospitals WHERE location LIKE '%{m.group(1)}%'"),
            (r'public.*hospitals?.*in\s+(\w+)', lambda m: f"SELECT name, bed_capacity, type FROM hospitals WHERE public_private = 'Public' AND location LIKE '%{m.group(1)}%'"),
            (r'private.*hospitals?.*in\s+(\w+)', lambda m: f"SELECT name, bed_capacity, type FROM hospitals WHERE public_private = 'Private' AND location LIKE '%{m.group(1)}%'"),
            
            # Bed capacity queries
            (r'.*largest.*by.*bed.*capacity?', lambda m: "SELECT name, location, bed_capacity, type FROM hospitals ORDER BY bed_capacity DESC LIMIT 10"),
            (r'.*smallest.*by.*bed.*capacity?', lambda m: "SELECT name, location, bed_capacity, type FROM hospitals ORDER BY bed_capacity ASC LIMIT 10"),
            (r'.*more than\s+(\d+)\s*beds?', lambda m: f"SELECT name, location, bed_capacity FROM hospitals WHERE bed_capacity > {m.group(1)} ORDER BY bed_capacity DESC"),
            (r'.*at least\s+(\d+)\s*beds?', lambda m: f"SELECT name, location, bed_capacity FROM hospitals WHERE bed_capacity >= {m.group(1)} ORDER BY bed_capacity DESC"),
            (r'.*less than\s+(\d+)\s*beds?', lambda m: f"SELECT name, location, bed_capacity FROM hospitals WHERE bed_capacity < {m.group(1)} ORDER BY bed_capacity DESC"),
            
            # Emergency services queries
            (r'.*emergency.*services?', lambda m: "SELECT name, location, bed_capacity, type FROM hospitals WHERE emergency_services = 1"),
            (r'hospitals?.*with.*emergency', lambda m: "SELECT name, location, bed_capacity, type FROM hospitals WHERE emergency_services = 1"),
            (r'hospitals?.*without.*emergency', lambda m: "SELECT name, location, bed_capacity, type FROM hospitals WHERE emergency_services = 0"),
            
            # Specialty queries
            (r'.*cardiology.*services?', lambda m: "SELECT name, location, specialties FROM hospitals WHERE specialties LIKE '%Cardiology%'"),
            (r'.*neurology.*services?', lambda m: "SELECT name, location, specialties FROM hospitals WHERE specialties LIKE '%Neurology%'"),
            (r'.*oncology.*services?', lambda m: "SELECT name, location, specialties FROM hospitals WHERE specialties LIKE '%Oncology%'"),
            (r'.*orthopedics?.*services?', lambda m: "SELECT name, location, specialties FROM hospitals WHERE specialties LIKE '%Orthopedics%'"),
            (r'.*pediatrics?.*services?', lambda m: "SELECT name, location, specialties FROM hospitals WHERE specialties LIKE '%Pediatrics%'"),
            
            # Hospital type queries
            (r'teaching.*hospitals?', lambda m: "SELECT name, location, bed_capacity, established FROM hospitals WHERE type LIKE '%Teaching%' ORDER BY name"),
            (r'private.*hospitals?', lambda m: "SELECT name, location, bed_capacity, type FROM hospitals WHERE public_private = 'Private' ORDER BY name"),
            (r'public.*hospitals?', lambda m: "SELECT name, location, bed_capacity, type FROM hospitals WHERE public_private = 'Public' ORDER BY name"),
            (r'general.*hospitals?', lambda m: "SELECT name, location, bed_capacity, type FROM hospitals WHERE type LIKE '%General%' ORDER BY name"),
            
            # Establishment year queries
            (r'.*established.*after\s+(\d{4})', lambda m: f"SELECT name, type, location, established FROM hospitals WHERE established > {m.group(1)} ORDER BY established"),
            (r'.*established.*before\s+(\d{4})', lambda m: f"SELECT name, type, location, established FROM hospitals WHERE established < {m.group(1)} ORDER BY established DESC"),
            (r'.*established.*in\s+(\d{4})', lambda m: f"SELECT name, type, location, established FROM hospitals WHERE established = {m.group(1)}"),
            
            # General listing queries
            (r'list.*all.*hospitals?', lambda m: "SELECT name, type, location, bed_capacity FROM hospitals ORDER BY name"),
            (r'show.*all.*hospitals?', lambda m: "SELECT name, type, location, bed_capacity FROM hospitals ORDER BY name"),
        ]
        
        # Try to match patterns
        for pattern, sql_generator in query_patterns:
            match = re.search(pattern, natural_query, re.IGNORECASE)
            if match:
                sql = sql_generator(match)
                if self._validate_sql(sql):
                    return sql
        
        # Default fallback for general queries
        if 'hospital' in natural_query.lower():
            return "SELECT name, type, location, bed_capacity FROM hospitals LIMIT 10"
        
        return None
    
    def _format_results(self, results: list, query: str) -> str:
        """Format query results into natural language"""
        if not results:
            return "No hospitals found matching your query."
        
        # Count queries
        if 'COUNT' in query.upper():
            count = results[0]['total']
            return f"Found {count} hospitals matching your criteria."
        
        # Single hospital
        if len(results) == 1:
            hospital = results[0]
            response = f"Found 1 hospital:\n"
            response += f"• {hospital.get('name', 'Unknown')} - {hospital.get('type', 'Unknown')} in {hospital.get('location', 'Unknown')}"
            if 'bed_capacity' in hospital and hospital['bed_capacity']:
                response += f" ({hospital['bed_capacity']} beds)"
            if 'established' in hospital and hospital['established']:
                response += f", Est. {hospital['established']}"
            return response
        
        # Multiple hospitals
        response = f"Found {len(results)} hospitals:\n"
        for i, hospital in enumerate(results[:10], 1):  # Limit to 10 results
            response += f"{i}. {hospital.get('name', 'Unknown')} - {hospital.get('type', 'Unknown')}"
            if 'location' in hospital and hospital['location']:
                response += f" in {hospital['location']}"
            if 'bed_capacity' in hospital and hospital['bed_capacity']:
                response += f" ({hospital['bed_capacity']} beds)"
            if 'established' in hospital and hospital['established']:
                response += f", Est. {hospital['established']}"
            response += "\n"
        
        if len(results) > 10:
            response += f"... and {len(results) - 10} more hospitals."
        
        return response
    
    def _run(self, query: str) -> str:
        """Execute the tool"""
        start_time = time.time()
        
        try:
            # Generate SQL
            sql = self._generate_sql(query)
            if not sql:
                return "I couldn't understand your query about hospitals. Please try rephrasing it."
            
            # Validate SQL
            if not self._validate_sql(sql):
                return "Invalid query detected. Only SELECT queries are allowed."
            
            # Execute query
            conn = DatabaseManager.create_connection(getattr(self, '_db_path'))
            try:
                results = DatabaseManager.execute_query(conn, sql)
                response = self._format_results(results, sql)
                
                # Add metadata
                execution_time = time.time() - start_time
                response += f"\n\n[Query executed in {execution_time:.2f} seconds]"
                
                return response
                
            finally:
                conn.close()
                
        except Exception as e:
            return f"Error querying hospitals database: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version (not implemented)"""
        return self._run(query)
