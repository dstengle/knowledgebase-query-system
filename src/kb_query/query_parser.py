"""Parse natural language queries into structured form"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from .interfaces import IQueryParser, QueryPattern, ParsedQuery
from .exceptions import QueryParseError

logger = logging.getLogger(__name__)

class NaturalLanguageQueryParser(IQueryParser):
    """Parse natural language queries using patterns"""
    
    def __init__(self):
        self.temporal_patterns = {
            'today': lambda: datetime.now().date(),
            'yesterday': lambda: (datetime.now() - timedelta(days=1)).date(),
            'tomorrow': lambda: (datetime.now() + timedelta(days=1)).date(),
            'this week': lambda: self._get_week_range(0),
            'last week': lambda: self._get_week_range(-1),
            'this month': lambda: self._get_month_range(0),
            'last month': lambda: self._get_month_range(-1)
        }
    
    def parse(self, query: str, patterns: List[QueryPattern]) -> ParsedQuery:
        """Parse natural language query using available patterns"""
        query = query.strip().lower()
        
        # Find matching pattern
        matched_pattern, extracted = self._match_pattern(query, patterns)
        
        if not matched_pattern:
            # Try to find similar patterns for suggestions
            suggestions = self._find_similar_patterns(query, patterns)
            raise QueryParseError(
                f"Could not parse query: '{query}'",
                suggestions=suggestions
            )
        
        # Extract components
        entity_type = self._extract_entity_type(matched_pattern)
        filters = self._extract_filters(matched_pattern, extracted)
        temporal = self._extract_temporal_constraints(query)
        
        return ParsedQuery(
            entity_type=entity_type,
            filters=filters,
            temporal_constraints=temporal,
            limit=self._extract_limit(query),
            order_by=self._extract_ordering(query)
        )
    
    def suggest_queries(self, partial: str, patterns: List[QueryPattern]) -> List[str]:
        """Suggest query completions"""
        partial = partial.strip().lower()
        suggestions = []
        
        for pattern in patterns:
            for example in pattern.examples:
                if example.startswith(partial):
                    suggestions.append(example)
        
        # Sort by relevance (length, then alphabetically)
        suggestions.sort(key=lambda x: (len(x), x))
        return suggestions[:10]  # Return top 10
    
    def _match_pattern(self, query: str, patterns: List[QueryPattern]) -> Tuple[Optional[QueryPattern], Dict]:
        """Find pattern that matches the query"""
        for pattern in patterns:
            # Convert pattern to regex
            regex_pattern = self._pattern_to_regex(pattern.pattern)
            match = re.match(regex_pattern, query)
            
            if match:
                return pattern, match.groupdict()
        
        return None, {}
    
    def _pattern_to_regex(self, pattern: str) -> str:
        """Convert pattern template to regex"""
        # Escape special regex characters except {}
        pattern = re.escape(pattern)
        pattern = pattern.replace(r'\{', '{').replace(r'\}', '}')
        
        # Replace {value} with capturing group
        pattern = pattern.replace('{value}', r'(?P<value>[\w\s]+)')
        
        # Make pattern more flexible
        pattern = pattern.replace(' ', r'\s+')
        
        return f'^{pattern}$'
    
    def _extract_entity_type(self, pattern: QueryPattern) -> str:
        """Extract entity type from pattern"""
        # Get local name from class URI
        class_uri = pattern.required_class
        if '#' in class_uri:
            return class_uri.split('#')[-1]
        else:
            return class_uri.split('/')[-1]
    
    def _extract_filters(self, pattern: QueryPattern, extracted: Dict) -> Dict[str, str]:
        """Extract filter values"""
        filters = {}
        
        if pattern.required_property and 'value' in extracted:
            prop_name = pattern.required_property.split('#')[-1]
            filters[prop_name] = extracted['value'].strip()
        
        return filters
    
    def _extract_temporal_constraints(self, query: str) -> Optional[Dict[str, str]]:
        """Extract temporal constraints from query"""
        for temporal_key, date_func in self.temporal_patterns.items():
            if temporal_key in query:
                date_range = date_func()
                if isinstance(date_range, tuple):
                    return {
                        'start': date_range[0].isoformat(),
                        'end': date_range[1].isoformat()
                    }
                else:
                    return {'date': date_range.isoformat()}
        
        # Check for explicit dates
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        date_match = re.search(date_pattern, query)
        if date_match:
            return {'date': date_match.group()}
        
        return None
    
    def _extract_limit(self, query: str) -> Optional[int]:
        """Extract limit from query"""
        limit_patterns = [
            (r'top (\d+)', 1),
            (r'first (\d+)', 1),
            (r'last (\d+)', 1),
            (r'(\d+) results?', 1)
        ]
        
        for pattern, group in limit_patterns:
            match = re.search(pattern, query)
            if match:
                return int(match.group(group))
        
        return None
    
    def _extract_ordering(self, query: str) -> Optional[Tuple[str, str]]:
        """Extract ordering from query"""
        if 'latest' in query or 'most recent' in query:
            return ('created', 'DESC')
        elif 'oldest' in query:
            return ('created', 'ASC')
        elif 'alphabetical' in query:
            return ('title', 'ASC')
        
        return None
    
    def _find_similar_patterns(self, query: str, patterns: List[QueryPattern]) -> List[str]:
        """Find patterns similar to the query"""
        suggestions = []
        query_words = set(query.split())
        
        for pattern in patterns:
            for example in pattern.examples:
                example_words = set(example.split())
                # Calculate word overlap
                overlap = len(query_words & example_words)
                if overlap > 0:
                    suggestions.append((overlap, example))
        
        # Sort by overlap and return top suggestions
        suggestions.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in suggestions[:5]]
    
    def _get_week_range(self, week_offset: int) -> Tuple[datetime, datetime]:
        """Get date range for a week"""
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_target_week = start_of_week + timedelta(weeks=week_offset)
        end_of_target_week = start_of_target_week + timedelta(days=6)
        return (start_of_target_week, end_of_target_week)
    
    def _get_month_range(self, month_offset: int) -> Tuple[datetime, datetime]:
        """Get date range for a month"""
        today = datetime.now().date()
        if month_offset == 0:
            start = today.replace(day=1)
        else:
            # Handle month boundaries
            month = today.month + month_offset
            year = today.year
            if month < 1:
                month = 12
                year -= 1
            elif month > 12:
                month = 1
                year += 1
            start = today.replace(year=year, month=month, day=1)
        
        # Get last day of month
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
        
        return (start, end)
