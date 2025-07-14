"""
Pattern engine for managing transaction pattern recognition and learning.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from ..data.models import Pattern, Transaction
from ..patterns.pattern_matcher import PatternMatcher
from ..patterns.pattern_repository import PatternRepository
from ..patterns.avianca_patterns import AviancaPatterns


class PatternEngine:
    """Manages transaction pattern recognition and learning."""
    
    def __init__(self, patterns_file: Optional[str] = None):
        """
        Initialize the pattern engine.
        
        Args:
            patterns_file: Optional path to patterns configuration file
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.pattern_repository = PatternRepository(patterns_file)
        self.pattern_matcher = PatternMatcher()
        self.avianca_patterns = AviancaPatterns()
        
        self.logger.info("Pattern engine initialized")
    
    def detect_pattern(self, text: str) -> Optional[str]:
        """
        Detect which pattern applies to the text.
        
        Args:
            text: PDF text content
            
        Returns:
            Pattern name if detected, None otherwise
        """
        try:
            # First, try Avianca-specific detection
            avianca_pattern = self.avianca_patterns.detect_avianca_pattern(text)
            if avianca_pattern:
                self.logger.info(f"Detected Avianca pattern: {avianca_pattern}")
                return avianca_pattern
            
            # Then try all patterns in repository
            pattern_suggestions = self.pattern_repository.find_patterns_for_text(text)
            
            if pattern_suggestions:
                # Return the best match
                best_pattern = pattern_suggestions[0]
                if best_pattern["recommended"]:
                    self.logger.info(f"Detected pattern: {best_pattern['pattern_name']} (confidence: {best_pattern['confidence']:.2f})")
                    return best_pattern["pattern_name"]
            
            self.logger.warning("No suitable pattern detected for the text")
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting pattern: {str(e)}")
            return None
    
    def extract_transactions(self, text: str, pattern_name: Optional[str] = None) -> List[Transaction]:
        """
        Extract transactions using detected or specified pattern.
        
        Args:
            text: PDF text content
            pattern_name: Specific pattern to use, or None for auto-detection
            
        Returns:
            List of extracted transactions
        """
        try:
            # Auto-detect pattern if not specified
            if pattern_name is None:
                pattern_name = self.detect_pattern(text)
            
            if pattern_name is None:
                self.logger.warning("No pattern available for transaction extraction")
                return []
            
            # Use Avianca-specific extraction if it's an Avianca pattern
            if pattern_name in self.avianca_patterns.list_available_patterns():
                transactions = self.avianca_patterns.extract_transactions(text, pattern_name)
                self.logger.info(f"Extracted {len(transactions)} transactions using Avianca pattern {pattern_name}")
                return transactions
            
            # Use general pattern matching
            pattern = self.pattern_repository.get_pattern(pattern_name)
            if pattern is None:
                self.logger.error(f"Pattern not found: {pattern_name}")
                return []
            
            transactions = self.pattern_matcher.match_transactions(text, pattern)
            self.logger.info(f"Extracted {len(transactions)} transactions using pattern {pattern_name}")
            return transactions
            
        except Exception as e:
            self.logger.error(f"Error extracting transactions: {str(e)}")
            return []
    
    def learn_new_pattern(self, text: str, expected_transactions: List[Transaction], pattern_name: str) -> Optional[Pattern]:
        """
        Learn a new pattern from user-provided examples.
        
        Args:
            text: PDF text content
            expected_transactions: List of expected transactions
            pattern_name: Name for the new pattern
            
        Returns:
            New Pattern object if learning succeeded, None otherwise
        """
        try:
            self.logger.info(f"Learning new pattern: {pattern_name}")
            
            # Analyze text structure to find potential patterns
            potential_patterns = self.pattern_matcher.find_potential_patterns(text)
            
            if not potential_patterns:
                self.logger.warning("No potential patterns found in text")
                return None
            
            # Test each potential pattern against expected transactions
            best_pattern = None
            best_score = 0
            
            for suggestion in potential_patterns:
                # Create a temporary pattern
                temp_pattern = Pattern(
                    name=pattern_name,
                    issuer="learned",
                    card_type="unknown",
                    transaction_regex=suggestion["regex"],
                    date_format="%Y-%m-%d",  # Default format
                    amount_format="$X,XXX.XX",
                    confidence_threshold=suggestion["confidence"]
                )
                
                # Test the pattern
                extracted = self.pattern_matcher.match_transactions(text, temp_pattern)
                
                # Score based on how well it matches expected transactions
                score = self._score_pattern_match(extracted, expected_transactions)
                
                if score > best_score:
                    best_score = score
                    best_pattern = temp_pattern
            
            if best_pattern and best_score >= 0.7:  # Require 70% match
                # Add to repository
                self.pattern_repository.add_pattern(best_pattern)
                self.logger.info(f"Successfully learned pattern {pattern_name} with score {best_score:.2f}")
                return best_pattern
            else:
                self.logger.warning(f"Failed to learn pattern {pattern_name} - best score: {best_score:.2f}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error learning new pattern: {str(e)}")
            return None
    
    def _score_pattern_match(self, extracted: List[Transaction], expected: List[Transaction]) -> float:
        """
        Score how well extracted transactions match expected ones.
        
        Args:
            extracted: Extracted transactions
            expected: Expected transactions
            
        Returns:
            Score between 0.0 and 1.0
        """
        if not expected:
            return 0.0
        
        if not extracted:
            return 0.0
        
        # Simple scoring based on count and total amount
        count_score = min(1.0, len(extracted) / len(expected))
        
        expected_total = sum(t.amount for t in expected)
        extracted_total = sum(t.amount for t in extracted)
        
        if expected_total > 0:
            amount_score = 1.0 - abs(expected_total - extracted_total) / expected_total
            amount_score = max(0.0, amount_score)
        else:
            amount_score = 1.0 if extracted_total == 0 else 0.0
        
        # Weighted average
        return (count_score * 0.6) + (amount_score * 0.4)
    
    def validate_pattern_against_text(self, text: str, pattern_name: str) -> Dict[str, Any]:
        """
        Validate how well a pattern matches against text.
        
        Args:
            text: PDF text content
            pattern_name: Pattern to validate
            
        Returns:
            Validation results dictionary
        """
        try:
            # Use Avianca-specific validation if applicable
            if pattern_name in self.avianca_patterns.list_available_patterns():
                return self.avianca_patterns.validate_pattern_against_text(text, pattern_name)
            
            # Use general pattern validation
            pattern = self.pattern_repository.get_pattern(pattern_name)
            if pattern is None:
                return {"error": f"Pattern not found: {pattern_name}"}
            
            return self.pattern_matcher.test_pattern_against_text(text, pattern)
            
        except Exception as e:
            return {"error": str(e)}
    
    def list_available_patterns(self) -> List[str]:
        """
        Get list of all available patterns.
        
        Returns:
            List of pattern names
        """
        return self.pattern_repository.list_patterns()
    
    def get_pattern_info(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a pattern.
        
        Args:
            pattern_name: Name of the pattern
            
        Returns:
            Pattern information dictionary
        """
        # Check Avianca patterns first
        if pattern_name in self.avianca_patterns.list_available_patterns():
            return self.avianca_patterns.get_pattern_info(pattern_name)
        
        # Check repository patterns
        return self.pattern_repository.get_pattern_info(pattern_name)
    
    def add_custom_pattern(self, pattern: Pattern) -> bool:
        """
        Add a custom pattern to the repository.
        
        Args:
            pattern: Pattern object to add
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Validate pattern first
            validation = self.pattern_repository.validate_pattern(pattern)
            if not validation["valid"]:
                self.logger.error(f"Invalid pattern: {validation['errors']}")
                return False
            
            return self.pattern_repository.add_pattern(pattern)
            
        except Exception as e:
            self.logger.error(f"Error adding custom pattern: {str(e)}")
            return False
    
    def remove_pattern(self, pattern_name: str) -> bool:
        """
        Remove a pattern from the repository.
        
        Args:
            pattern_name: Name of the pattern to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        return self.pattern_repository.remove_pattern(pattern_name)
    
    def get_patterns_by_issuer(self, issuer: str) -> List[str]:
        """
        Get patterns for a specific issuer.
        
        Args:
            issuer: Issuer name
            
        Returns:
            List of pattern names for the issuer
        """
        return self.pattern_repository.list_patterns_by_issuer(issuer)
    
    def analyze_text_for_patterns(self, text: str) -> Dict[str, Any]:
        """
        Analyze text to suggest potential patterns and improvements.
        
        Args:
            text: PDF text content
            
        Returns:
            Analysis results dictionary
        """
        try:
            analysis = {
                "detected_patterns": [],
                "suggested_patterns": [],
                "text_characteristics": {},
                "recommendations": []
            }
            
            # Check existing patterns
            existing_patterns = self.pattern_repository.find_patterns_for_text(text)
            analysis["detected_patterns"] = existing_patterns
            
            # Find potential new patterns
            potential_patterns = self.pattern_matcher.find_potential_patterns(text)
            analysis["suggested_patterns"] = potential_patterns
            
            # Analyze text characteristics
            lines = text.split('\n')
            analysis["text_characteristics"] = {
                "total_lines": len(lines),
                "non_empty_lines": len([l for l in lines if l.strip()]),
                "avg_line_length": sum(len(l) for l in lines) / len(lines) if lines else 0,
                "has_currency_symbols": '$' in text or '€' in text or '£' in text,
                "has_dates": bool(re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)),
                "has_amounts": bool(re.search(r'\d+[.,]\d{2}', text))
            }
            
            # Generate recommendations
            if not existing_patterns:
                analysis["recommendations"].append("No existing patterns detected. Consider creating a custom pattern.")
            
            if potential_patterns:
                analysis["recommendations"].append(f"Found {len(potential_patterns)} potential patterns. Consider testing them.")
            
            if not analysis["text_characteristics"]["has_dates"]:
                analysis["recommendations"].append("No clear date patterns found. Check date format in PDF.")
            
            if not analysis["text_characteristics"]["has_amounts"]:
                analysis["recommendations"].append("No clear amount patterns found. Check amount format in PDF.")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing text for patterns: {str(e)}")
            return {"error": str(e)}
    
    def save_patterns(self, file_path: str) -> bool:
        """
        Save current patterns to file.
        
        Args:
            file_path: Path where to save patterns
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            self.pattern_repository.save_patterns_to_file(file_path)
            return True
        except Exception as e:
            self.logger.error(f"Error saving patterns: {str(e)}")
            return False
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the pattern engine.
        
        Returns:
            Dictionary containing engine statistics
        """
        try:
            repo_stats = self.pattern_repository.get_repository_stats()
            avianca_patterns = len(self.avianca_patterns.list_available_patterns())
            
            return {
                "repository_stats": repo_stats,
                "avianca_patterns": avianca_patterns,
                "total_patterns": repo_stats["total_patterns"] + avianca_patterns,
                "engine_status": "operational"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "engine_status": "error"
            }