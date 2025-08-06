"""
PromptOptimizer for token reduction with ≥50% target
Optimizes prompts to reduce token usage while maintaining quality
"""

import re
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ..models.requests import AIRequest


class PromptOptimizer:
    """
    Optimizes prompts to reduce token usage while maintaining quality.
    Targets ≥50% token reduction through various optimization techniques.
    """
    
    def __init__(self):
        """Initialize prompt optimizer."""
        self.optimization_techniques = {
            "remove_redundancy": self._remove_redundancy,
            "simplify_language": self._simplify_language,
            "remove_unnecessary_context": self._remove_unnecessary_context,
            "optimize_formatting": self._optimize_formatting,
            "compress_instructions": self._compress_instructions
        }
        
        # Common redundant phrases
        self.redundant_phrases = [
            "please", "kindly", "if you could", "would you mind",
            "I would like you to", "I want you to", "can you",
            "I need you to", "I would appreciate if", "it would be great if"
        ]
        
        # Unnecessary context markers
        self.context_markers = [
            "as you know", "as mentioned", "as stated", "as discussed",
            "previously", "earlier", "before", "in the past"
        ]
    
    def optimise(self, prompt: str) -> str:
        """
        Optimize a prompt to reduce token usage.
        
        Args:
            prompt: The original prompt
            
        Returns:
            Optimized prompt with reduced tokens
        """
        original_tokens = self._estimate_tokens(prompt)
        optimized_prompt = prompt
        
        # Apply optimization techniques
        for technique_name, technique_func in self.optimization_techniques.items():
            optimized_prompt = technique_func(optimized_prompt)
        
        # Ensure we don't over-optimize (maintain quality)
        optimized_prompt = self._ensure_quality(optimized_prompt, prompt)
        
        optimized_tokens = self._estimate_tokens(optimized_prompt)
        reduction_percentage = (original_tokens - optimized_tokens) / original_tokens * 100
        
        return optimized_prompt
    
    def _remove_redundancy(self, prompt: str) -> str:
        """Remove redundant phrases and words."""
        optimized = prompt
        
        # Remove redundant phrases
        for phrase in self.redundant_phrases:
            pattern = r'\b' + re.escape(phrase) + r'\b'
            optimized = re.sub(pattern, '', optimized, flags=re.IGNORECASE)
        
        # Remove excessive punctuation
        optimized = re.sub(r'[!]{2,}', '!', optimized)
        optimized = re.sub(r'[?]{2,}', '?', optimized)
        optimized = re.sub(r'[.]{2,}', '.', optimized)
        
        # Remove extra whitespace
        optimized = re.sub(r'\s+', ' ', optimized)
        optimized = optimized.strip()
        
        return optimized
    
    def _simplify_language(self, prompt: str) -> str:
        """Simplify language while maintaining meaning."""
        # Replace complex phrases with simpler ones
        replacements = {
            r'\bconsequently\b': 'so',
            r'\bnevertheless\b': 'but',
            r'\bnonetheless\b': 'but',
            r'\bmoreover\b': 'also',
            r'\bfurthermore\b': 'also',
            r'\badditionally\b': 'also',
            r'\bhowever\b': 'but',
            r'\bnevertheless\b': 'but',
            r'\bthus\b': 'so',
            r'\btherefore\b': 'so',
            r'\bhence\b': 'so',
            r'\baccordingly\b': 'so',
            r'\bconsequently\b': 'so',
            r'\bultimately\b': 'finally',
            r'\bessentially\b': 'basically',
            r'\bfundamentally\b': 'basically',
            r'\bprimarily\b': 'mainly',
            r'\binitially\b': 'first',
            r'\bsubsequently\b': 'then',
            r'\bpreviously\b': 'before'
        }
        
        optimized = prompt
        for pattern, replacement in replacements.items():
            optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
        
        return optimized
    
    def _remove_unnecessary_context(self, prompt: str) -> str:
        """Remove unnecessary context and background information."""
        optimized = prompt
        
        # Remove context markers
        for marker in self.context_markers:
            pattern = r'\b' + re.escape(marker) + r'[,\s]*'
            optimized = re.sub(pattern, '', optimized, flags=re.IGNORECASE)
        
        # Remove excessive explanations
        optimized = re.sub(r'\([^)]*\)', '', optimized)  # Remove parentheses content
        optimized = re.sub(r'\[[^\]]*\]', '', optimized)  # Remove bracket content
        
        # Clean up extra spaces
        optimized = re.sub(r'\s+', ' ', optimized)
        optimized = optimized.strip()
        
        return optimized
    
    def _optimize_formatting(self, prompt: str) -> str:
        """Optimize formatting and structure."""
        optimized = prompt
        
        # Remove excessive line breaks
        optimized = re.sub(r'\n{3,}', '\n\n', optimized)
        
        # Remove excessive spaces around punctuation
        optimized = re.sub(r'\s+([,.!?])', r'\1', optimized)
        
        # Normalize quotes
        optimized = optimized.replace('"', '"').replace('"', '"')
        optimized = optimized.replace(''', "'").replace(''', "'")
        
        return optimized
    
    def _compress_instructions(self, prompt: str) -> str:
        """Compress multiple instructions into concise format."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', prompt)
        compressed_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Compress instruction patterns
            if re.search(r'\b(please|kindly|can you|would you)\b', sentence, re.IGNORECASE):
                # Remove polite markers
                sentence = re.sub(r'\b(please|kindly|can you|would you)\b', '', sentence, flags=re.IGNORECASE)
                sentence = sentence.strip()
            
            # Compress multiple actions
            if ' and ' in sentence.lower():
                parts = sentence.split(' and ')
                if len(parts) > 2:
                    # Keep only the main action
                    sentence = parts[0]
            
            compressed_sentences.append(sentence)
        
        return '. '.join(compressed_sentences) + '.'
    
    def _ensure_quality(self, optimized: str, original: str) -> str:
        """Ensure optimization doesn't compromise quality."""
        # If optimization is too aggressive, revert some changes
        original_tokens = self._estimate_tokens(original)
        optimized_tokens = self._estimate_tokens(optimized)
        
        # If reduction is more than 70%, we might be over-optimizing
        reduction = (original_tokens - optimized_tokens) / original_tokens
        if reduction > 0.7:
            # Revert some optimizations
            return self._partial_optimize(original)
        
        return optimized
    
    def _partial_optimize(self, prompt: str) -> str:
        """Apply only conservative optimizations."""
        optimized = prompt
        
        # Only apply safe optimizations
        optimized = self._remove_redundancy(optimized)
        optimized = self._optimize_formatting(optimized)
        
        return optimized
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def get_optimization_stats(self, original: str, optimized: str) -> Dict[str, Any]:
        """Get optimization statistics."""
        original_tokens = self._estimate_tokens(original)
        optimized_tokens = self._estimate_tokens(optimized)
        reduction = (original_tokens - optimized_tokens) / original_tokens * 100
        
        return {
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "tokens_saved": original_tokens - optimized_tokens,
            "reduction_percentage": reduction,
            "target_achieved": reduction >= 50.0,
            "original_length": len(original),
            "optimized_length": len(optimized),
            "length_reduction": len(original) - len(optimized)
        }
    
    def optimize_request(self, request: AIRequest) -> Tuple[str, Dict[str, Any]]:
        """
        Optimize an AI request prompt.
        
        Args:
            request: The AI request to optimize
            
        Returns:
            Tuple of (optimized_prompt, optimization_stats)
        """
        original_prompt = request.prompt
        optimized_prompt = self.optimise(original_prompt)
        
        stats = self.get_optimization_stats(original_prompt, optimized_prompt)
        
        return optimized_prompt, stats