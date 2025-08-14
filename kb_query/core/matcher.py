"""Pattern Matcher for matching user input to query patterns."""

import re
from typing import List, Dict, Optional
from difflib import SequenceMatcher

from ..core.entities import Pattern, Grammar, MatchResult
from ..exceptions import QueryParseError


class PatternMatcher:
    """Matches natural language input to query patterns."""
    
    def __init__(self, similarity_threshold: float = 0.7):
        """Initialize pattern matcher with similarity threshold."""
        self.similarity_threshold = similarity_threshold
    
    def find_matches(self, input_text: str, grammar: Grammar) -> List[MatchResult]:
        """Find matching patterns for user input."""
        # Don't normalize the original text - we need to preserve case for entities
        matches = []
        
        for pattern in grammar.patterns:
            match_result = self._match_pattern(input_text, pattern)
            if match_result and match_result.confidence >= self.similarity_threshold:
                matches.append(match_result)
        
        # Sort by confidence, highest first
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches
    
    def extract_entities(self, input_text: str, pattern: Pattern) -> Dict[str, str]:
        """Extract entity values from input text based on pattern template."""
        # Try exact extraction first
        regex_pattern = self._template_to_regex(pattern.template)
        match = re.match(regex_pattern, input_text, re.IGNORECASE)
        
        if match:
            return self._extract_entities_from_match(match, pattern)
        
        # Fallback to positional extraction
        return self._extract_entities_positional(input_text, pattern)
    
    def suggest_corrections(self, input_text: str, grammar: Grammar) -> List[str]:
        """Generate query suggestions for failed matches."""
        suggestions = []
        input_tokens = self._tokenize(input_text.lower())
        
        # Find patterns with similar keywords or words
        for pattern in grammar.patterns:
            # Check keyword similarity
            if pattern.keywords:
                similarity = self._calculate_keyword_similarity(input_tokens, pattern.keywords)
                if similarity > 0.3:
                    suggestions.extend(pattern.examples[:2])
            
            # Also check if any input tokens match pattern words
            pattern_words = self._tokenize(pattern.template.lower())
            word_match = any(token in pattern_words for token in input_tokens)
            if word_match:
                suggestions.extend(pattern.examples[:1])
        
        # Remove duplicates and return top suggestions
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)
        
        return unique_suggestions[:5]
    
    def _match_pattern(self, input_text: str, pattern: Pattern) -> Optional[MatchResult]:
        """Match input against a single pattern."""
        # Try exact match first (fastest path)
        exact_match = self._try_exact_match(input_text, pattern)
        if exact_match:
            return exact_match
        
        # Try fuzzy match
        fuzzy_match = self._try_fuzzy_match(input_text, pattern)
        if fuzzy_match:
            return fuzzy_match
        
        return None
    
    def _try_exact_match(self, input_text: str, pattern: Pattern) -> Optional[MatchResult]:
        """Try exact pattern matching using regex."""
        regex_pattern = self._template_to_regex(pattern.template)
        
        match = re.match(regex_pattern, input_text, re.IGNORECASE)
        if match:
            entities = self._extract_entities_from_match(match, pattern)
            return MatchResult(
                pattern=pattern,
                confidence=1.0,
                entities=entities,
                match_type="exact"
            )
        
        return None
    
    def _try_fuzzy_match(self, input_text: str, pattern: Pattern) -> Optional[MatchResult]:
        """Try fuzzy pattern matching using token similarity."""
        # Tokenize input and pattern
        input_tokens = self._tokenize(input_text)
        pattern_tokens = self._tokenize_template(pattern.template)
        
        # Calculate similarity
        similarity = self._calculate_token_similarity(input_tokens, pattern_tokens)
        
        if similarity >= self.similarity_threshold:
            entities = self._extract_entities_fuzzy(input_text, pattern)
            return MatchResult(
                pattern=pattern,
                confidence=similarity,
                entities=entities,
                match_type="fuzzy"
            )
        
        return None
    
    def _template_to_regex(self, template: str) -> str:
        """Convert pattern template to regex."""
        # Escape special regex characters except for our placeholders
        regex = re.escape(template)
        
        # Replace escaped placeholders with capture groups
        # \{person\} becomes (.+?)
        regex = re.sub(r'\\{([^}]+)\\}', r'(.+?)', regex)
        
        # Allow optional 's for possessives
        regex = regex.replace("\\'s", "'?s?")
        
        return f"^{regex}$"
    
    def _extract_entities_from_match(self, match: re.Match, pattern: Pattern) -> Dict[str, str]:
        """Extract entities from regex match."""
        entities = {}
        
        # Find all placeholders in template
        placeholders = re.findall(r'{([^}]+)}', pattern.template)
        
        # Map captured groups to placeholders (preserve original case)
        for i, placeholder in enumerate(placeholders):
            if i < len(match.groups()):
                # Don't lowercase the entity value - preserve original case
                entities[placeholder] = match.group(i + 1).strip()
        
        return entities
    
    def _extract_entities_positional(self, input_text: str, pattern: Pattern) -> Dict[str, str]:
        """Extract entities based on position in template."""
        entities = {}
        
        # Split template and input into parts
        template_parts = re.split(r'({[^}]+})', pattern.template)
        
        # Build regex pattern for positional matching
        regex_parts = []
        placeholders = []
        
        for part in template_parts:
            if part.startswith('{') and part.endswith('}'):
                # This is a placeholder
                placeholder = part[1:-1]
                placeholders.append(placeholder)
                regex_parts.append('(.+?)')
            elif part:
                # Regular text
                regex_parts.append(re.escape(part))
        
        if not placeholders:
            return entities
        
        # Try to match with the constructed regex
        regex_pattern = ''.join(regex_parts)
        match = re.search(regex_pattern, input_text, re.IGNORECASE)
        
        if match:
            for i, placeholder in enumerate(placeholders):
                if i < len(match.groups()):
                    entities[placeholder] = match.group(i + 1).strip()
        
        return entities
    
    def _extract_entities_fuzzy(self, input_text: str, pattern: Pattern) -> Dict[str, str]:
        """Extract entities using fuzzy matching."""
        # First try positional extraction
        entities = self._extract_entities_positional(input_text, pattern)
        
        # If positional fails, try a more flexible approach for fuzzy matching
        if not entities:
            entities = self._extract_entities_fuzzy_flexible(input_text, pattern)
        
        return entities
    
    def _extract_entities_fuzzy_flexible(self, input_text: str, pattern: Pattern) -> Dict[str, str]:
        """Extract entities using flexible fuzzy matching."""
        entities = {}
        
        # Tokenize input and pattern
        input_tokens = self._tokenize(input_text)
        pattern_tokens = self._tokenize_template(pattern.template)
        
        # Find placeholders and their positions
        placeholders = []
        placeholder_positions = []
        
        for i, token in enumerate(pattern_tokens):
            if token['type'] == 'placeholder':
                placeholders.append(token['name'])
                placeholder_positions.append(i)
        
        if not placeholders:
            return entities
        
        # For simple patterns like "meetings with {person}", extract the entity
        # by finding the position after the known pattern words
        pattern_words = [t['text'] for t in pattern_tokens if t['type'] == 'word']
        
        if len(placeholders) == 1 and len(pattern_words) >= 1:
            # Find the best matching word in the pattern
            best_match_idx = -1
            best_similarity = 0
            
            for i, pattern_word in enumerate(pattern_words):
                for j, input_token in enumerate(input_tokens):
                    similarity = SequenceMatcher(None, input_token, pattern_word).ratio()
                    if similarity > best_similarity and similarity > 0.6:
                        best_similarity = similarity
                        best_match_idx = j
            
            # If we found a match, extract entity after it
            if best_match_idx != -1 and best_match_idx < len(input_tokens) - 1:
                # Extract remaining tokens as the entity
                entity_tokens = input_tokens[best_match_idx + 1:]
                if entity_tokens:
                    # Reconstruct original case from input text
                    entity_value = self._reconstruct_entity_from_tokens(input_text, entity_tokens)
                    entities[placeholders[0]] = entity_value
        
        return entities
    
    def _reconstruct_entity_from_tokens(self, original_text: str, tokens: List[str]) -> str:
        """Reconstruct entity value preserving original case."""
        # Find the position of the first token in the original text
        first_token = tokens[0]
        original_lower = original_text.lower()
        token_pos = original_lower.find(first_token.lower())
        
        if token_pos != -1:
            # Find the end of the last token
            remaining_text = original_text[token_pos:]
            words = remaining_text.split()
            if len(words) >= len(tokens):
                return ' '.join(words[:len(tokens)])
        
        # Fallback: return tokens as-is
        return ' '.join(tokens)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Split on whitespace and punctuation, but keep apostrophes
        tokens = re.findall(r"\w+(?:'\w+)?", text.lower())
        return tokens
    
    def _tokenize_template(self, template: str) -> List[Dict]:
        """Tokenize template preserving placeholders."""
        tokens = []
        # Split template into parts, preserving placeholders
        parts = re.split(r'({[^}]+})', template)
        
        for part in parts:
            if part.strip():
                if part.startswith('{') and part.endswith('}'):
                    # Placeholder
                    tokens.append({
                        'type': 'placeholder',
                        'name': part[1:-1],
                        'text': part
                    })
                else:
                    # Regular words
                    words = self._tokenize(part)
                    for word in words:
                        tokens.append({
                            'type': 'word',
                            'text': word
                        })
        
        return tokens
    
    def _calculate_token_similarity(self, input_tokens: List[str], 
                                   pattern_tokens: List[Dict]) -> float:
        """Calculate similarity between tokenized input and pattern."""
        # Extract just the word tokens for comparison
        pattern_words = [t['text'] for t in pattern_tokens if t['type'] == 'word']
        
        if not pattern_words:
            return 0.0
        
        # For fuzzy matching, check if the pattern structure matches even with typos
        # Use both sequence matching and individual word similarity
        
        # 1. Sequence similarity
        seq_matcher = SequenceMatcher(None, input_tokens[:len(pattern_words)], pattern_words)
        seq_similarity = seq_matcher.ratio()
        
        # 2. Individual word similarity (handles typos better)
        word_similarities = []
        for i, pattern_word in enumerate(pattern_words):
            if i < len(input_tokens):
                word_matcher = SequenceMatcher(None, input_tokens[i], pattern_word)
                word_similarities.append(word_matcher.ratio())
            else:
                word_similarities.append(0.0)
        
        # Average of word similarities
        avg_word_similarity = sum(word_similarities) / len(word_similarities) if word_similarities else 0
        
        # Combine both scores (weighted average)
        return 0.4 * seq_similarity + 0.6 * avg_word_similarity
    
    def _calculate_keyword_similarity(self, input_tokens: List[str], 
                                     keywords: List[str]) -> float:
        """Calculate similarity based on keyword overlap."""
        if not keywords:
            return 0.0
        
        # Count matching keywords
        matches = sum(1 for keyword in keywords if keyword in input_tokens)
        return matches / len(keywords)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching."""
        # Basic normalization: lowercase and strip whitespace
        return text.lower().strip()