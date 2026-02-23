"""
InstitutionsDBTool - LangChain tool for querying Bangladesh institutions database
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import sqlite3
import re
import time
from utils.database import DatabaseManager
from utils.config import Config

class InstitutionsInput(BaseModel):
    """Input schema for InstitutionsDBTool"""
    query: str = Field(description="Natural language query about Bangladesh educational institutions")

class InstitutionsDBTool(BaseTool):
    """Tool for querying Bangladesh institutions database"""
    
    name = "InstitutionsDBTool"
    description = """Use this tool for queries about Bangladesh educational institutions.
    Handles universities, colleges, government institutions, degree offerings, and institution counts.
    
    Examples:
    - "How many universities are in Dhaka?"
    - "Which institutions offer medical degrees?"
    - "List all colleges in Dhaka"
    - "What are the government institutions?"
    - "Show institutions established after 1950"
    
    Database schema:
    - name: Institution name
    - type: University, College, Government Institution
    - location: City/District
    - established: Year established
    - degrees_offered: Types of degrees available
    - students_count: Number of students
    - public_private: Public or Private
    - specialization: Field of specialization
    """
    
    args_schema = InstitutionsInput
    
    def __init__(self):
        super().__init__()
        # Store configuration as instance attributes that don't conflict with Pydantic
        object.__setattr__(self, '_db_path', Config.INSTITUTIONS_DB)
        object.__setattr__(self, '_table_name', "institutions")
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
            (r'how many.*institutions?', lambda m: "SELECT COUNT(*) as total FROM institutions"),
            (r'how many.*universities?', lambda m: "SELECT COUNT(*) as total FROM institutions WHERE type LIKE '%University%'"),
            (r'how many.*colleges?', lambda m: "SELECT COUNT(*) as total FROM institutions WHERE type LIKE '%College%'"),
            (r'how many.*government.*institutions?', lambda m: "SELECT COUNT(*) as total FROM institutions WHERE public_private = 'Public' AND type LIKE '%Government%'"),
            
            # Location-based queries
            (r'institutions?.*in\s+(\w+)', lambda m: f"SELECT name, type, location FROM institutions WHERE location LIKE '%{m.group(1)}%'"),
            (r'universities?.*in\s+(\w+)', lambda m: f"SELECT name, established, students_count FROM institutions WHERE type LIKE '%University%' AND location LIKE '%{m.group(1)}%'"),
            (r'colleges?.*in\s+(\w+)', lambda m: f"SELECT name, established, students_count FROM institutions WHERE type LIKE '%College%' AND location LIKE '%{m.group(1)}%'"),
            
            # Degree/specialization queries
            (r'.*offer.*medical.*degrees?', lambda m: "SELECT name, location, degrees_offered FROM institutions WHERE degrees_offered LIKE '%Medical%' OR specialization LIKE '%Medical%'"),
            (r'.*offer.*engineering.*degrees?', lambda m: "SELECT name, location, degrees_offered FROM institutions WHERE degrees_offered LIKE '%Engineering%' OR specialization LIKE '%Engineering%'"),
            (r'.*specialization.*(\w+)', lambda m: f"SELECT name, type, specialization FROM institutions WHERE specialization LIKE '%{m.group(1)}%'"),
            
            # Establishment year queries
            (r'.*established.*after\s+(\d{4})', lambda m: f"SELECT name, type, established FROM institutions WHERE established > {m.group(1)}"),
            (r'.*established.*before\s+(\d{4})', lambda m: f"SELECT name, type, established FROM institutions WHERE established < {m.group(1)}"),
            (r'.*established.*in\s+(\d{4})', lambda m: f"SELECT name, type, established FROM institutions WHERE established = {m.group(1)}"),
            
            # General listing queries
            (r'list.*all.*institutions?', lambda m: "SELECT name, type, location FROM institutions ORDER BY name"),
            (r'list.*all.*universities?', lambda m: "SELECT name, location, established, students_count FROM institutions WHERE type LIKE '%University%' ORDER BY name"),
            (r'list.*all.*colleges?', lambda m: "SELECT name, location, established, students_count FROM institutions WHERE type LIKE '%College%' ORDER BY name"),
            (r'government.*institutions?', lambda m: "SELECT name, type, location FROM institutions WHERE public_private = 'Public' ORDER BY name"),
            (r'private.*institutions?', lambda m: "SELECT name, type, location FROM institutions WHERE public_private = 'Private' ORDER BY name"),
            
            # Student count queries
            (r'.*largest.*by.*students?', lambda m: "SELECT name, type, students_count FROM institutions ORDER BY students_count DESC LIMIT 5"),
            (r'.*smallest.*by.*students?', lambda m: "SELECT name, type, students_count FROM institutions ORDER BY students_count ASC LIMIT 5"),
        ]
        
        # Try to match patterns
        for pattern, sql_generator in query_patterns:
            match = re.search(pattern, natural_query, re.IGNORECASE)
            if match:
                sql = sql_generator(match)
                if self._validate_sql(sql):
                    return sql
        
        # Default fallback for general queries
        if 'institution' in natural_query.lower():
            return "SELECT name, type, location FROM institutions LIMIT 10"
        
        return None
    
    def _format_results(self, results: list, query: str) -> str:
        """Format query results into natural language"""
        if not results:
            return "No institutions found matching your query."
        
        # Count queries - check if the query is a COUNT query
        if 'COUNT' in query.upper():
            # The result should be a single row with a count column
            if results and len(results) > 0:
                # Try different possible column names for count
                count = None
                row = results[0]
                for key in ['total', 'COUNT(*)', 'count']:
                    if key in row:
                        count = row[key]
                        break
                
                if count is not None:
                    return f"Found {count} institutions matching your criteria."
                else:
                    # If no count column found, use the number of rows
                    return f"Found {len(results)} institutions matching your criteria."
        
        # Single institution
        if len(results) == 1:
            inst = results[0]
            response = f"Found 1 institution:\n"
            response += f"• {inst.get('name', 'Unknown')} - {inst.get('type', 'Unknown')} in {inst.get('location', 'Unknown')}"
            if 'established' in inst and inst['established']:
                response += f" (Established: {inst['established']})"
            if 'students_count' in inst and inst['students_count']:
                response += f", Students: {inst['students_count']}"
            return response
        
        # Multiple institutions
        response = f"Found {len(results)} institutions:\n"
        for i, inst in enumerate(results[:10], 1):  # Limit to 10 results
            response += f"{i}. {inst.get('name', 'Unknown')} - {inst.get('type', 'Unknown')}"
            if 'location' in inst and inst['location']:
                response += f" in {inst['location']}"
            if 'established' in inst and inst['established']:
                response += f" (Est. {inst['established']})"
            response += "\n"
        
        if len(results) > 10:
            response += f"... and {len(results) - 10} more institutions."
        
        return response
    
    def _run(self, query: str) -> str:
        """Execute the tool"""
        start_time = time.time()
        
        try:
            # Generate SQL
            sql = self._generate_sql(query)
            if not sql:
                return "I couldn't understand your query about institutions. Please try rephrasing it."
            
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
            return f"Error querying institutions database: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version (not implemented)"""
        return self._run(query)
