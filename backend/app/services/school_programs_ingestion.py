"""
School Programs Data Ingestion Service

This module handles data ingestion from various sources including CEGEP and university databases.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import json

from app.utils.database import get_db_connection

logger = logging.getLogger(__name__)


@dataclass
class ProgramData:
    """Data structure for program information"""
    title: str
    institution_name: str
    institution_type: str  # 'cegep', 'university', 'college'
    program_type: str
    level: str
    duration_months: Optional[int] = None
    language: List[str] = None
    description: Optional[str] = None
    field_of_study: Optional[str] = None
    admission_requirements: List[str] = None
    tuition_domestic: Optional[float] = None
    employment_rate: Optional[float] = None
    source_system: str = "unknown"
    source_id: str = ""
    source_url: Optional[str] = None
    
    def __post_init__(self):
        if self.language is None:
            self.language = ['en']
        if self.admission_requirements is None:
            self.admission_requirements = []


@dataclass
class InstitutionData:
    """Data structure for institution information"""
    name: str
    institution_type: str
    country: str = "CA"
    province_state: Optional[str] = None
    city: Optional[str] = None
    website_url: Optional[str] = None
    source_system: str = "unknown"
    source_id: str = ""


@dataclass
class IngestionResult:
    """Result of data ingestion operation"""
    source: str
    success: bool
    programs_processed: int = 0
    institutions_processed: int = 0
    errors: List[str] = None
    duration_seconds: float = 0.0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def __aenter__(self):
        now = datetime.utcnow()
        # Remove requests older than time window
        self.requests = [req_time for req_time in self.requests 
                        if (now - req_time).total_seconds() < self.time_window]
        
        # Wait if we've hit the limit
        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = self.time_window - (now - oldest_request).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.requests.append(now)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class DataSource:
    """Base class for data sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
        self.rate_limiter = RateLimiter(
            max_requests=config.get('rate_limit', 60),
            time_window=60
        )
    
    async def initialize(self):
        """Initialize the data source"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> bool:
        """Check if the data source is accessible"""
        raise NotImplementedError
    
    async def fetch_institutions(self) -> List[InstitutionData]:
        """Fetch institution data"""
        raise NotImplementedError
    
    async def fetch_programs(self) -> List[ProgramData]:
        """Fetch program data"""
        raise NotImplementedError


class SRAMCEGEPSource(DataSource):
    """Data source for SRAM CEGEP data"""
    
    BASE_URL = "https://www.sram.qc.ca"
    
    async def health_check(self) -> bool:
        """Check SRAM website accessibility"""
        try:
            async with self.rate_limiter:
                async with self.session.get(f"{self.BASE_URL}/", timeout=10) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"SRAM health check failed: {e}")
            return False
    
    async def fetch_institutions(self) -> List[InstitutionData]:
        """Fetch CEGEP institutions from SRAM"""
        institutions = []
        
        try:
            async with self.rate_limiter:
                async with self.session.get(f"{self.BASE_URL}/en/cegeps") as response:
                    html_content = await response.text()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Parse institution listings
            institution_links = soup.find_all('a', class_='institution-link')
            
            for link in institution_links:
                institution_data = InstitutionData(
                    name=link.get_text(strip=True),
                    institution_type='cegep',
                    country='CA',
                    province_state='QC',
                    source_system='sram',
                    source_id=link.get('href', '').split('/')[-1]
                )
                institutions.append(institution_data)
                
        except Exception as e:
            logger.error(f"Error fetching SRAM institutions: {e}")
        
        return institutions
    
    async def fetch_programs(self) -> List[ProgramData]:
        """Fetch CEGEP programs from SRAM"""
        programs = []
        
        try:
            # Fetch programs page
            async with self.rate_limiter:
                async with self.session.get(f"{self.BASE_URL}/en/programs") as response:
                    html_content = await response.text()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Parse program listings
            program_cards = soup.find_all('div', class_='program-card')
            
            for card in program_cards:
                title_elem = card.find('h3', class_='program-title')
                institution_elem = card.find('span', class_='institution-name')
                
                if title_elem and institution_elem:
                    program_data = ProgramData(
                        title=title_elem.get_text(strip=True),
                        institution_name=institution_elem.get_text(strip=True),
                        institution_type='cegep',
                        program_type='technical',  # Most CEGEP programs are technical
                        level='diploma',
                        duration_months=36,  # Standard CEGEP technical program duration
                        language=['fr', 'en'],  # Quebec programs often bilingual
                        source_system='sram',
                        source_id=card.get('data-program-id', ''),
                        source_url=f"{self.BASE_URL}/en/programs/{card.get('data-program-id', '')}"
                    )
                    programs.append(program_data)
                    
        except Exception as e:
            logger.error(f"Error fetching SRAM programs: {e}")
        
        return programs


class DonneesQuebecSource(DataSource):
    """Data source for Données Québec open data"""
    
    BASE_URL = "https://www.donneesquebec.ca/recherche/api/3/action"
    
    async def health_check(self) -> bool:
        """Check Données Québec API accessibility"""
        try:
            async with self.rate_limiter:
                async with self.session.get(f"{self.BASE_URL}/site_read", timeout=10) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Données Québec health check failed: {e}")
            return False
    
    async def fetch_institutions(self) -> List[InstitutionData]:
        """Fetch institutions from Données Québec"""
        institutions = []
        
        try:
            # Search for education datasets
            params = {
                'q': 'établissements éducation',
                'rows': 100
            }
            
            async with self.rate_limiter:
                async with self.session.get(f"{self.BASE_URL}/package_search", params=params) as response:
                    data = await response.json()
            
            # Process datasets
            for dataset in data.get('result', {}).get('results', []):
                # Extract institution data from dataset metadata
                # This would require specific parsing based on dataset format
                pass
                
        except Exception as e:
            logger.error(f"Error fetching Données Québec institutions: {e}")
        
        return institutions
    
    async def fetch_programs(self) -> List[ProgramData]:
        """Fetch programs from Données Québec"""
        programs = []
        
        try:
            # Search for program datasets
            params = {
                'q': 'programmes études',
                'rows': 100
            }
            
            async with self.rate_limiter:
                async with self.session.get(f"{self.BASE_URL}/package_search", params=params) as response:
                    data = await response.json()
            
            # Process program datasets
            for dataset in data.get('result', {}).get('results', []):
                # Extract program data from dataset
                # This would require specific parsing based on dataset format
                pass
                
        except Exception as e:
            logger.error(f"Error fetching Données Québec programs: {e}")
        
        return programs


class CollegeScorecardSource(DataSource):
    """Data source for US College Scorecard API"""
    
    BASE_URL = "https://api.data.gov/ed/collegescorecard/v1"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
    
    async def health_check(self) -> bool:
        """Check College Scorecard API accessibility"""
        if not self.api_key:
            return False
        
        try:
            params = {'api_key': self.api_key, 'per_page': 1}
            async with self.rate_limiter:
                async with self.session.get(f"{self.BASE_URL}/schools", params=params, timeout=10) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"College Scorecard health check failed: {e}")
            return False
    
    async def fetch_institutions(self) -> List[InstitutionData]:
        """Fetch US institutions from College Scorecard"""
        institutions = []
        
        try:
            params = {
                'api_key': self.api_key,
                'fields': 'school.name,school.state,school.city,school.school_url',
                'per_page': 100
            }
            
            async with self.rate_limiter:
                async with self.session.get(f"{self.BASE_URL}/schools", params=params) as response:
                    data = await response.json()
            
            for school in data.get('results', []):
                institution_data = InstitutionData(
                    name=school.get('school.name', ''),
                    institution_type='university',
                    country='US',
                    province_state=school.get('school.state'),
                    city=school.get('school.city'),
                    website_url=school.get('school.school_url'),
                    source_system='college_scorecard',
                    source_id=str(school.get('id', ''))
                )
                institutions.append(institution_data)
                
        except Exception as e:
            logger.error(f"Error fetching College Scorecard institutions: {e}")
        
        return institutions
    
    async def fetch_programs(self) -> List[ProgramData]:
        """Fetch programs from College Scorecard"""
        # College Scorecard doesn't provide detailed program data
        # This would need to be supplemented with other sources
        return []


class SchoolProgramsIngestionPipeline:
    """Main pipeline for ingesting school program data"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_sources: List[DataSource] = []
        self.db_connection = None
    
    def add_data_source(self, source_class, source_config: Dict[str, Any]):
        """Add a data source to the pipeline"""
        source = source_class(source_config)
        self.data_sources.append(source)
    
    async def run_ingestion(self) -> List[IngestionResult]:
        """Run the complete ingestion pipeline"""
        results = []
        
        try:
            # Initialize database connection
            self.db_connection = await get_db_connection(self.config['database_url'])
            
            # Initialize all data sources
            for source in self.data_sources:
                await source.initialize()
            
            # Run ingestion for each source
            for source in self.data_sources:
                result = await self._ingest_from_source(source)
                results.append(result)
            
            # Cleanup
            for source in self.data_sources:
                await source.cleanup()
            
            if self.db_connection:
                await self.db_connection.close()
                
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            # Return error results for all sources
            for source in self.data_sources:
                results.append(IngestionResult(
                    source=source.__class__.__name__,
                    success=False,
                    errors=[str(e)]
                ))
        
        return results
    
    async def _ingest_from_source(self, source: DataSource) -> IngestionResult:
        """Ingest data from a single source"""
        start_time = datetime.utcnow()
        source_name = source.__class__.__name__
        
        try:
            # Health check
            if not await source.health_check():
                return IngestionResult(
                    source=source_name,
                    success=False,
                    errors=["Health check failed"]
                )
            
            # Fetch institutions
            institutions = await source.fetch_institutions()
            institutions_processed = await self._save_institutions(institutions)
            
            # Fetch programs
            programs = await source.fetch_programs()
            programs_processed = await self._save_programs(programs)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return IngestionResult(
                source=source_name,
                success=True,
                programs_processed=programs_processed,
                institutions_processed=institutions_processed,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Error ingesting from {source_name}: {e}")
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return IngestionResult(
                source=source_name,
                success=False,
                errors=[str(e)],
                duration_seconds=duration
            )
    
    async def _save_institutions(self, institutions: List[InstitutionData]) -> int:
        """Save institutions to database"""
        saved_count = 0
        
        for institution in institutions:
            try:
                insert_sql = """
                INSERT INTO institutions (
                    name, institution_type, country, province_state, city,
                    website_url, source_system, source_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (source_system, source_id) 
                DO UPDATE SET
                    name = EXCLUDED.name,
                    institution_type = EXCLUDED.institution_type,
                    country = EXCLUDED.country,
                    province_state = EXCLUDED.province_state,
                    city = EXCLUDED.city,
                    website_url = EXCLUDED.website_url,
                    updated_at = NOW(),
                    last_synced = NOW()
                """
                
                await self.db_connection.execute(
                    insert_sql,
                    institution.name, institution.institution_type, institution.country,
                    institution.province_state, institution.city, institution.website_url,
                    institution.source_system, institution.source_id
                )
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving institution {institution.name}: {e}")
        
        return saved_count
    
    async def _save_programs(self, programs: List[ProgramData]) -> int:
        """Save programs to database"""
        saved_count = 0
        
        for program in programs:
            try:
                # First get or create institution
                institution_query = """
                SELECT id FROM institutions 
                WHERE source_system = $1 AND source_id = $2
                """
                
                institution_row = await self.db_connection.fetchrow(
                    institution_query, program.source_system, program.source_id
                )
                
                if not institution_row:
                    # Create a minimal institution record
                    institution_insert = """
                    INSERT INTO institutions (
                        name, institution_type, source_system, source_id
                    ) VALUES ($1, $2, $3, $4)
                    RETURNING id
                    """
                    
                    institution_row = await self.db_connection.fetchrow(
                        institution_insert,
                        program.institution_name, program.institution_type,
                        program.source_system, f"{program.institution_name}_auto"
                    )
                
                institution_id = institution_row['id']
                
                # Insert program
                program_insert = """
                INSERT INTO programs (
                    title, institution_id, program_type, level, duration_months,
                    language, description, field_of_study, admission_requirements,
                    tuition_domestic, employment_rate, source_system, source_id, source_url
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                ON CONFLICT (source_system, source_id)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    program_type = EXCLUDED.program_type,
                    level = EXCLUDED.level,
                    duration_months = EXCLUDED.duration_months,
                    language = EXCLUDED.language,
                    description = EXCLUDED.description,
                    field_of_study = EXCLUDED.field_of_study,
                    admission_requirements = EXCLUDED.admission_requirements,
                    tuition_domestic = EXCLUDED.tuition_domestic,
                    employment_rate = EXCLUDED.employment_rate,
                    source_url = EXCLUDED.source_url,
                    updated_at = NOW(),
                    last_synced = NOW()
                """
                
                await self.db_connection.execute(
                    program_insert,
                    program.title, institution_id, program.program_type, program.level,
                    program.duration_months, program.language, program.description,
                    program.field_of_study, json.dumps(program.admission_requirements),
                    program.tuition_domestic, program.employment_rate,
                    program.source_system, program.source_id, program.source_url
                )
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving program {program.title}: {e}")
        
        return saved_count