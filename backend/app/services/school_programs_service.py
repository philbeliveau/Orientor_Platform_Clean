"""
School Programs Service

This module provides business logic for school programs search and management.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
import hashlib
import json

# Make Redis optional
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.school_programs import ProgramSearchQuery, SearchResultsResponse, SaveProgramRequest
from app.models.user import User

logger = logging.getLogger(__name__)


class ProgramSearchService:
    """Service for program search operations"""
    
    def __init__(self, db: AsyncSession, cache, user: User):
        self.db = db
        self.cache = cache  # Can be None if Redis is not available
        self.user = user
        self.cache_ttl = 3600  # 1 hour
    
    async def search_programs(self, query: ProgramSearchQuery) -> SearchResultsResponse:
        """Search for programs based on query parameters"""
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(query)
            
            # Check cache first (if available)
            cached_result = None
            if self.cache:
                try:
                    cached_result = await self.cache.get(cache_key)
                    if cached_result:
                        logger.info(f"Cache hit for search query: {cache_key}")
                        result_data = json.loads(cached_result)
                        result_data['metadata']['cache_hit'] = True
                        return SearchResultsResponse(**result_data)
                except Exception as e:
                    logger.warning(f"Cache read failed: {e}")
                    # Continue without cache
            
            # Perform database search
            search_start = datetime.utcnow()
            
            # Build search filters
            filters = self._build_search_filters(query)
            
            # Execute search query using the database function
            search_results = await self._execute_search_query(query, filters)
            
            # Get facets for filtering
            facets = await self._get_search_facets(query, filters)
            
            # Calculate pagination
            total_results = len(search_results) if search_results else 0
            pagination = self._calculate_pagination(query.pagination, total_results)
            
            # Prepare response
            search_time = (datetime.utcnow() - search_start).total_seconds() * 1000
            
            response_data = {
                'results': search_results,
                'pagination': pagination,
                'facets': facets,
                'metadata': {
                    'search_time_ms': search_time,
                    'sources_queried': ['database'],
                    'cache_hit': False
                }
            }
            
            # Cache the results (if cache is available)
            if self.cache:
                try:
                    await self.cache.setex(
                        cache_key,
                        self.cache_ttl,
                        json.dumps(response_data, default=str)
                    )
                except Exception as e:
                    logger.warning(f"Cache write failed: {e}")
                    # Continue without cache
            
            return SearchResultsResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Error in program search: {e}")
            raise
    
    def _generate_cache_key(self, query: ProgramSearchQuery) -> str:
        """Generate cache key for search query"""
        query_str = json.dumps(query.dict(), sort_keys=True)
        return f"program_search:{hashlib.md5(query_str.encode()).hexdigest()}"
    
    def _build_search_filters(self, query: ProgramSearchQuery) -> Dict[str, Any]:
        """Build database filters from search query"""
        filters = {}
        
        if query.text:
            filters['search_text'] = query.text
        
        if query.program_types:
            filters['program_types'] = query.program_types
        
        if query.levels:
            filters['levels'] = query.levels
        
        if query.location:
            if query.location.get('country'):
                filters['countries'] = [query.location['country']]
            if query.location.get('province'):
                filters['provinces'] = [query.location['province']]
        
        if query.languages:
            filters['languages'] = query.languages
        
        if query.duration:
            if query.duration.get('max_months'):
                filters['max_duration'] = query.duration['max_months']
        
        return filters
    
    async def _execute_search_query(self, query: ProgramSearchQuery, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the actual search query against database"""
        try:
            # Use the database search function
            search_sql = """
            SELECT * FROM search_programs(
                $1::TEXT, $2::TEXT[], $3::TEXT[], $4::TEXT[], $5::TEXT[], 
                $6::TEXT[], $7::INTEGER, $8::DECIMAL, $9::INTEGER, $10::INTEGER
            )
            """
            
            # Prepare parameters
            search_text = filters.get('search_text', '')
            program_types = filters.get('program_types', [])
            levels = filters.get('levels', [])
            countries = filters.get('countries', [])
            provinces = filters.get('provinces', [])
            languages = filters.get('languages', [])
            max_duration = filters.get('max_duration')
            min_employment_rate = None
            
            limit = query.pagination.get('limit', 20)
            offset = (query.pagination.get('page', 1) - 1) * limit
            
            # Execute query
            connection = await self.db.connection()
            rows = await connection.fetch(
                search_sql,
                search_text, program_types, levels, countries, provinces,
                languages, max_duration, min_employment_rate, limit, offset
            )
            
            # Convert to response format
            results = []
            for row in rows:
                program_data = await self._format_program_response(dict(row))
                results.append(program_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Database search error: {e}")
            return []
    
    async def _format_program_response(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Format database row into program response"""
        return {
            'id': row['id'],
            'title': row['title'],
            'title_fr': None,
            'description': None,
            'description_fr': None,
            'institution': {
                'name': row['institution_name'],
                'city': row['city'],
                'province': row['province_state'],
                'type': 'cegep'
            },
            'program_details': {
                'type': row['program_type'],
                'level': row['level'],
                'duration_months': row['duration_months'],
                'language': ['en', 'fr']
            },
            'classification': {
                'field_of_study': 'Computer Science',
                'category': 'STEM'
            },
            'admission': {
                'requirements': [],
                'deadline': None
            },
            'academic_info': {
                'credits': None,
                'internship_required': False,
                'coop_available': False
            },
            'career_outcomes': {
                'employment_rate': row['employment_rate'],
                'job_titles': []
            },
            'costs': {
                'tuition_domestic': None,
                'currency': 'CAD'
            },
            'metadata': {
                'search_rank': row.get('search_rank', 1.0),
                'last_updated': datetime.utcnow().isoformat()
            }
        }
    
    async def _get_search_facets(self, query: ProgramSearchQuery, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get search facets for filtering UI"""
        return {
            'program_types': {
                'cegep': 150,
                'university': 200
            },
            'levels': {
                'diploma': 120,
                'bachelor': 180,
                'master': 50
            },
            'provinces': {
                'QC': 200,
                'ON': 150
            }
        }
    
    def _calculate_pagination(self, pagination_params: Dict[str, int], total_results: int) -> Dict[str, Any]:
        """Calculate pagination metadata"""
        page = pagination_params.get('page', 1)
        limit = pagination_params.get('limit', 20)
        total_pages = (total_results + limit - 1) // limit
        
        return {
            'page': page,
            'limit': limit,
            'total_pages': total_pages,
            'total_results': total_results,
            'has_next': page < total_pages,
            'has_previous': page > 1
        }


class UserInteractionService:
    """Service for user program interactions"""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    async def save_program(self, request: SaveProgramRequest) -> bool:
        """Save a program for the user"""
        try:
            insert_sql = """
            INSERT INTO user_saved_programs (
                user_id, program_id, personal_notes, priority_level, user_tags
            ) VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id, program_id) 
            DO UPDATE SET 
                personal_notes = EXCLUDED.personal_notes,
                priority_level = EXCLUDED.priority_level,
                user_tags = EXCLUDED.user_tags,
                updated_at = NOW()
            """
            
            connection = await self.db.connection()
            await connection.execute(
                insert_sql,
                self.user.id,
                request.program_id,
                request.notes,
                request.priority_level,
                request.tags
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving program: {e}")
            return False
    
    async def get_saved_programs(self) -> List[Dict[str, Any]]:
        """Get user's saved programs"""
        try:
            query_sql = """
            SELECT sp.*, p.title, p.program_type, p.level,
                   i.name as institution_name, i.city, i.province_state
            FROM user_saved_programs sp
            JOIN programs p ON sp.program_id = p.id
            JOIN institutions i ON p.institution_id = i.id
            WHERE sp.user_id = $1
            ORDER BY sp.saved_at DESC
            """
            
            connection = await self.db.connection()
            rows = await connection.fetch(query_sql, self.user.id)
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error fetching saved programs: {e}")
            return []