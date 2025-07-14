"""
Pattern repository for managing and storing extraction patterns.
"""

import json
import yaml
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..data.models import Pattern
from .avianca_patterns import AviancaPatterns


class PatternRepository:
    """Manages storage and retrieval of extraction patterns."""
    
    def __init__(self, patterns_file: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.patterns_file = patterns_file
        self.patterns: Dict[str, Pattern] = {}
        
        # Initialize with built-in patterns
        self._load_builtin_patterns()
        
        # Load patterns from file if specified
        if patterns_file:
            self.load_patterns_from_file(patterns_file)
    
    def _load_builtin_patterns(self):
        """Load built-in patterns (Avianca, etc.)."""
        try:
            # Load Avianca patterns
            avianca = AviancaPatterns()
            for pattern_name in avianca.list_available_patterns():
                pattern_info = avianca.get_pattern_info(pattern_name)
                if pattern_info:
                    pattern = Pattern(
                        name=pattern_info["name"],
                        issuer=pattern_info["issuer"],
                        card_type=pattern_info["card_type"],
                        transaction_regex=pattern_info["transaction_regex"],
                        date_format=pattern_info["date_format"],
                        amount_format=pattern_info["amount_format"],
                        description_cleanup_rules=pattern_info["description_cleanup_rules"],
                        confidence_threshold=pattern_info["confidence_threshold"]
                    )
                    self.patterns[pattern_name] = pattern
            
            self.logger.info(f"Loaded {len(self.patterns)} built-in patterns")
            
        except Exception as e:
            self.logger.error(f"Error loading built-in patterns: {str(e)}")
    
    def load_patterns_from_file(self, file_path: str):
        """
        Load patterns from a YAML or JSON file.
        
        Args:
            file_path: Path to the patterns file
        """
        try:
            patterns_path = Path(file_path)
            if not patterns_path.exists():
                self.logger.warning(f"Patterns file not found: {file_path}")
                return
            
            with open(patterns_path, 'r', encoding='utf-8') as f:
                if patterns_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            if not isinstance(data, dict):
                self.logger.error("Patterns file must contain a dictionary")
                return
            
            patterns_data = data.get('patterns', data)
            loaded_count = 0
            
            for pattern_name, pattern_config in patterns_data.items():
                try:
                    pattern = Pattern(
                        name=pattern_config.get('name', pattern_name),
                        issuer=pattern_config['issuer'],
                        card_type=pattern_config.get('card_type', 'unknown'),
                        transaction_regex=pattern_config['transaction_regex'],
                        date_format=pattern_config.get('date_format', '%Y-%m-%d'),
                        amount_format=pattern_config.get('amount_format', '$X,XXX.XX'),
                        description_cleanup_rules=pattern_config.get('description_cleanup_rules', []),
                        confidence_threshold=pattern_config.get('confidence_threshold', 0.8)
                    )
                    
                    self.patterns[pattern_name] = pattern
                    loaded_count += 1
                    
                except KeyError as e:
                    self.logger.error(f"Missing required field in pattern {pattern_name}: {str(e)}")
                except Exception as e:
                    self.logger.error(f"Error loading pattern {pattern_name}: {str(e)}")
            
            self.logger.info(f"Loaded {loaded_count} patterns from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading patterns from file {file_path}: {str(e)}")
    
    def save_patterns_to_file(self, file_path: str):
        """
        Save current patterns to a YAML file.
        
        Args:
            file_path: Path where to save the patterns
        """
        try:
            patterns_data = {
                'patterns': {
                    name: pattern.to_dict() 
                    for name, pattern in self.patterns.items()
                }
            }
            
            patterns_path = Path(file_path)
            patterns_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(patterns_path, 'w', encoding='utf-8') as f:
                yaml.dump(patterns_data, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Saved {len(self.patterns)} patterns to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving patterns to file {file_path}: {str(e)}")
    
    def get_pattern(self, pattern_name: str) -> Optional[Pattern]:
        """
        Get a pattern by name.
        
        Args:
            pattern_name: Name of the pattern
            
        Returns:
            Pattern object or None if not found
        """
        return self.patterns.get(pattern_name)
    
    def add_pattern(self, pattern: Pattern) -> bool:
        """
        Add a new pattern to the repository.
        
        Args:
            pattern: Pattern object to add
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            if not pattern.name:
                self.logger.error("Pattern name cannot be empty")
                return False
            
            self.patterns[pattern.name] = pattern
            self.logger.info(f"Added pattern: {pattern.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding pattern {pattern.name}: {str(e)}")
            return False
    
    def remove_pattern(self, pattern_name: str) -> bool:
        """
        Remove a pattern from the repository.
        
        Args:
            pattern_name: Name of the pattern to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            if pattern_name in self.patterns:
                del self.patterns[pattern_name]
                self.logger.info(f"Removed pattern: {pattern_name}")
                return True
            else:
                self.logger.warning(f"Pattern not found: {pattern_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing pattern {pattern_name}: {str(e)}")
            return False
    
    def list_patterns(self) -> List[str]:
        """
        Get list of all available pattern names.
        
        Returns:
            List of pattern names
        """
        return list(self.patterns.keys())
    
    def list_patterns_by_issuer(self, issuer: str) -> List[str]:
        """
        Get list of patterns for a specific issuer.
        
        Args:
            issuer: Issuer name (e.g., 'avianca')
            
        Returns:
            List of pattern names for the issuer
        """
        return [
            name for name, pattern in self.patterns.items()
            if pattern.issuer.lower() == issuer.lower()
        ]
    
    def get_pattern_info(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a pattern.
        
        Args:
            pattern_name: Name of the pattern
            
        Returns:
            Pattern information dictionary or None if not found
        """
        pattern = self.get_pattern(pattern_name)
        return pattern.to_dict() if pattern else None
    
    def find_patterns_for_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Find patterns that might work for the given text.
        
        Args:
            text: PDF text content
            
        Returns:
            List of pattern suggestions with confidence scores
        """
        suggestions = []
        
        for pattern_name, pattern in self.patterns.items():
            try:
                # Test pattern against text
                import re
                regex = re.compile(pattern.transaction_regex, re.MULTILINE)
                matches = list(regex.finditer(text))
                
                if matches:
                    confidence = min(1.0, len(matches) / 10)  # Scale confidence
                    suggestions.append({
                        "pattern_name": pattern_name,
                        "issuer": pattern.issuer,
                        "match_count": len(matches),
                        "confidence": confidence,
                        "recommended": len(matches) >= 2 and confidence >= 0.3
                    })
                    
            except re.error:
                # Skip patterns with invalid regex
                continue
            except Exception as e:
                self.logger.debug(f"Error testing pattern {pattern_name}: {str(e)}")
                continue
        
        # Sort by match count and confidence
        suggestions.sort(key=lambda x: (x["match_count"], x["confidence"]), reverse=True)
        
        return suggestions
    
    def validate_pattern(self, pattern: Pattern) -> Dict[str, Any]:
        """
        Validate a pattern for correctness.
        
        Args:
            pattern: Pattern to validate
            
        Returns:
            Validation results dictionary
        """
        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check required fields
            if not pattern.name:
                validation["errors"].append("Pattern name is required")
            
            if not pattern.issuer:
                validation["errors"].append("Pattern issuer is required")
            
            if not pattern.transaction_regex:
                validation["errors"].append("Transaction regex is required")
            
            # Validate regex
            try:
                re.compile(pattern.transaction_regex)
            except re.error as e:
                validation["errors"].append(f"Invalid regex: {str(e)}")
            
            # Check confidence threshold
            if not (0.0 <= pattern.confidence_threshold <= 1.0):
                validation["errors"].append("Confidence threshold must be between 0.0 and 1.0")
            
            # Warnings for best practices
            if pattern.confidence_threshold < 0.5:
                validation["warnings"].append("Low confidence threshold may produce unreliable results")
            
            if len(pattern.description_cleanup_rules) == 0:
                validation["warnings"].append("No description cleanup rules defined")
            
            validation["valid"] = len(validation["errors"]) == 0
            
        except Exception as e:
            validation["errors"].append(f"Validation error: {str(e)}")
            validation["valid"] = False
        
        return validation
    
    def get_repository_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the pattern repository.
        
        Returns:
            Dictionary containing repository statistics
        """
        issuers = {}
        card_types = {}
        
        for pattern in self.patterns.values():
            # Count by issuer
            issuer = pattern.issuer.lower()
            issuers[issuer] = issuers.get(issuer, 0) + 1
            
            # Count by card type
            card_type = pattern.card_type.lower()
            card_types[card_type] = card_types.get(card_type, 0) + 1
        
        return {
            "total_patterns": len(self.patterns),
            "issuers": dict(issuers),
            "card_types": dict(card_types),
            "pattern_names": list(self.patterns.keys())
        }