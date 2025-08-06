"""
ComplexityAnalyzer for intelligent routing decisions
Analyzes prompt complexity to determine optimal provider selection
"""

import hashlib
import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models.complexity import (
    ComplexityScore,
    ComplexityLevel,
    ComplexityFactor,
    ComplexityThresholds,
    ComplexityAnalysisConfig,
    ComplexityAnalysisResult
)
from ..models.requests import AIRequest


class ComplexityAnalyzer:
    """
    Analyzes prompt complexity to determine optimal provider selection.
    Supports multiple analysis factors and configurable thresholds.
    """
    
    def __init__(self, config: Optional[ComplexityAnalysisConfig] = None):
        """Initialize the complexity analyzer with configuration."""
        self.config = config or self._get_default_config()
        self._analysis_cache: Dict[str, ComplexityAnalysisResult] = {}
        
        # Technical terms for detection
        self._technical_terms = self._load_technical_terms()
        
    def _get_default_config(self) -> ComplexityAnalysisConfig:
        """Get default configuration for complexity analysis."""
        from ..models.complexity import ComplexityThresholds
        
        thresholds = ComplexityThresholds()
        
        factor_weights = {
            ComplexityFactor.LENGTH: 0.2,
            ComplexityFactor.TECHNICAL_TERMS: 0.15,
            ComplexityFactor.MULTI_STEP: 0.2,
            ComplexityFactor.CREATIVE: 0.1,
            ComplexityFactor.ANALYTICAL: 0.15,
            ComplexityFactor.CODE_GENERATION: 0.1,
            ComplexityFactor.REASONING: 0.1,
        }
        
        return ComplexityAnalysisConfig(
            thresholds=thresholds,
            factor_weights=factor_weights
        )
    
    def _load_technical_terms(self) -> List[str]:
        """Load technical terms for complexity detection."""
        # This would typically load from a file or database
        # For now, using a basic set of technical terms
        return [
            "algorithm", "api", "authentication", "backend", "database", "encryption",
            "framework", "frontend", "http", "json", "microservices", "oauth",
            "protocol", "query", "schema", "sdk", "sql", "ssl", "tls", "webhook",
            "docker", "kubernetes", "aws", "azure", "gcp", "rest", "graphql",
            "websocket", "redis", "postgresql", "mongodb", "elasticsearch",
            "machine learning", "ai", "neural network", "tensorflow", "pytorch",
            "deployment", "ci/cd", "git", "version control", "testing", "unit test",
            "integration test", "load balancing", "scaling", "monitoring", "logging"
        ]
    
    def analyse(self, prompt: str) -> ComplexityScore:
        """
        Analyze the complexity of a given prompt.
        
        Args:
            prompt: The input prompt to analyze
            
        Returns:
            ComplexityScore with detailed analysis
        """
        start_time = time.time()
        
        # Basic text analysis
        word_count = len(prompt.split())
        character_count = len(prompt)
        sentence_count = len(re.split(r'[.!?]+', prompt))
        
        # Technical term detection
        technical_term_count = self._count_technical_terms(prompt)
        
        # Code block detection
        code_blocks = len(re.findall(r'```[\s\S]*?```', prompt))
        
        # URL detection
        urls = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', prompt))
        
        # Factor analysis
        factors = self._analyze_factors(prompt, word_count, technical_term_count, code_blocks)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(factors)
        level = self._determine_complexity_level(overall_score)
        
        # Estimate tokens and cost
        estimated_tokens = self._estimate_tokens(prompt)
        estimated_cost = self._estimate_cost(estimated_tokens)
        
        # Determine recommended provider
        recommended_provider = self._recommend_provider(level, estimated_cost)
        
        analysis_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return ComplexityScore(
            overall_score=overall_score,
            level=level,
            factors=factors,
            factor_weights=self.config.factor_weights,
            word_count=word_count,
            character_count=character_count,
            sentence_count=sentence_count,
            technical_term_count=technical_term_count,
            code_blocks=code_blocks,
            urls=urls,
            estimated_tokens=estimated_tokens,
            estimated_cost_usd=estimated_cost,
            recommended_provider=recommended_provider,
            analysis_time_ms=analysis_time,
            confidence=0.85  # Base confidence level
        )
    
    def _count_technical_terms(self, prompt: str) -> int:
        """Count technical terms in the prompt."""
        prompt_lower = prompt.lower()
        count = 0
        
        for term in self._technical_terms:
            if term.lower() in prompt_lower:
                count += 1
                
        return count
    
    def _analyze_factors(self, prompt: str, word_count: int, technical_terms: int, code_blocks: int) -> Dict[ComplexityFactor, float]:
        """Analyze individual complexity factors."""
        factors = {}
        
        # Length factor (0-1 based on word count)
        max_words = 1000  # Threshold for maximum complexity
        factors[ComplexityFactor.LENGTH] = min(word_count / max_words, 1.0)
        
        # Technical terms factor
        max_technical_terms = 10
        factors[ComplexityFactor.TECHNICAL_TERMS] = min(technical_terms / max_technical_terms, 1.0)
        
        # Multi-step factor (detect multi-step instructions)
        step_indicators = ['step', 'first', 'second', 'then', 'next', 'finally', '1.', '2.', '3.']
        step_count = sum(1 for indicator in step_indicators if indicator.lower() in prompt.lower())
        factors[ComplexityFactor.MULTI_STEP] = min(step_count / 5, 1.0)
        
        # Creative factor (detect creative writing indicators)
        creative_indicators = ['creative', 'story', 'imagine', 'write a', 'compose', 'narrative']
        creative_count = sum(1 for indicator in creative_indicators if indicator.lower() in prompt.lower())
        factors[ComplexityFactor.CREATIVE] = min(creative_count / 3, 1.0)
        
        # Analytical factor (detect analysis indicators)
        analytical_indicators = ['analyze', 'compare', 'evaluate', 'assess', 'examine', 'investigate']
        analytical_count = sum(1 for indicator in analytical_indicators if indicator.lower() in prompt.lower())
        factors[ComplexityFactor.ANALYTICAL] = min(analytical_count / 3, 1.0)
        
        # Code generation factor
        code_indicators = ['code', 'function', 'class', 'program', 'script', 'algorithm']
        code_count = sum(1 for indicator in code_indicators if indicator.lower() in prompt.lower())
        factors[ComplexityFactor.CODE_GENERATION] = min((code_count + code_blocks) / 5, 1.0)
        
        # Reasoning factor (detect reasoning indicators)
        reasoning_indicators = ['why', 'how', 'explain', 'reason', 'logic', 'because']
        reasoning_count = sum(1 for indicator in reasoning_indicators if indicator.lower() in prompt.lower())
        factors[ComplexityFactor.REASONING] = min(reasoning_count / 4, 1.0)
        
        return factors
    
    def _calculate_overall_score(self, factors: Dict[ComplexityFactor, float]) -> float:
        """Calculate overall complexity score using weighted factors."""
        total_score = 0.0
        total_weight = 0.0
        
        for factor, weight in self.config.factor_weights.items():
            if factor in factors:
                total_score += factors[factor] * weight
                total_weight += weight
        
        if total_weight > 0:
            return total_score / total_weight
        return 0.0
    
    def _determine_complexity_level(self, score: float) -> ComplexityLevel:
        """Determine complexity level based on score."""
        if score <= self.config.thresholds.simple_threshold:
            return ComplexityLevel.SIMPLE
        elif score <= self.config.thresholds.moderate_threshold:
            return ComplexityLevel.MODERATE
        elif score <= self.config.thresholds.complex_threshold:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.VERY_COMPLEX
    
    def _estimate_tokens(self, prompt: str) -> int:
        """Estimate token count for the prompt."""
        # Simple estimation: ~4 characters per token
        return len(prompt) // 4
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on token count."""
        # Rough estimation: $0.002 per 1k tokens
        return (tokens / 1000) * 0.002
    
    def _recommend_provider(self, level: ComplexityLevel, estimated_cost: float) -> Optional[str]:
        """Recommend provider based on complexity and cost."""
        if level == ComplexityLevel.SIMPLE:
            return "groq"  # Fast and cheap for simple requests
        elif level == ComplexityLevel.MODERATE:
            return "openai"  # Balanced for moderate complexity
        elif level == ComplexityLevel.COMPLEX:
            return "anthropic"  # Better reasoning for complex tasks
        else:  # VERY_COMPLEX
            return "anthropic"  # Best for very complex reasoning
    
    def analyze_request(self, request: AIRequest) -> ComplexityAnalysisResult:
        """
        Analyze an AI request for complexity.
        
        Args:
            request: The AI request to analyze
            
        Returns:
            Complete complexity analysis result
        """
        # Generate cache key
        prompt_hash = hashlib.md5(request.prompt.encode()).hexdigest()
        
        # Check cache if enabled
        if self.config.cache_analysis_results and prompt_hash in self._analysis_cache:
            cached_result = self._analysis_cache[prompt_hash]
            cached_result.cache_hit = True
            return cached_result
        
        # Perform analysis
        score = self.analyse(request.prompt)
        
        # Create analysis result
        result = ComplexityAnalysisResult(
            score=score,
            prompt_hash=prompt_hash,
            prompt_preview=request.prompt[:100] + "..." if len(request.prompt) > 100 else request.prompt,
            analysis_id=f"analysis_{int(time.time())}",
            analysis_timestamp=datetime.now().isoformat(),
            analysis_version="1.0.0",
            total_analysis_time_ms=score.analysis_time_ms,
            cache_hit=False,
            recommended_providers=[score.recommended_provider] if score.recommended_provider else [],
            cost_optimization_suggestions=self._generate_optimization_suggestions(score),
            metadata={
                "request_id": request.request_id,
                "user_id": request.user_id,
                "priority": request.priority.value
            }
        )
        
        # Cache result if enabled
        if self.config.cache_analysis_results:
            self._analysis_cache[prompt_hash] = result
        
        return result
    
    def _generate_optimization_suggestions(self, score: ComplexityScore) -> List[str]:
        """Generate cost optimization suggestions based on complexity."""
        suggestions = []
        
        if score.overall_score > 0.8:
            suggestions.append("Consider breaking down complex requests into smaller parts")
        
        if score.factors.get(ComplexityFactor.LENGTH, 0) > 0.7:
            suggestions.append("Prompt is quite long - consider summarizing or focusing on key points")
        
        if score.factors.get(ComplexityFactor.TECHNICAL_TERMS, 0) > 0.6:
            suggestions.append("High technical content - consider using specialized models")
        
        if score.estimated_cost_usd > 0.1:
            suggestions.append("High estimated cost - consider using more efficient models")
        
        return suggestions
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._analysis_cache),
            "cache_hit_rate": 0.0,  # Would need to track hits/misses
            "max_cache_size": 1000,  # Configurable
        }
    
    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        self._analysis_cache.clear()