import { EvaluationResult } from "../types";

export function calculateHeuristics(text: string): Omit<EvaluationResult, 'generated_text' | 'judge_raw_output'> {
  const words = text.trim().split(/\s+/);
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);

  // Simple keyword lists for heuristics
  const longTermKeywords = [
    "long-term", "future", "years", "career", "growth", "trajectory", 
    "potential", "sustainable", "investment", "perspective", "horizon"
  ];
  
  const riskKeywords = [
    "risk", "uncertainty", "danger", "debt", "failure", "unstable", 
    "gamble", "hazard", "threat", "vulnerability", "caution"
  ];

  const supportKeywords = [
    "scholarship", "grant", "loan", "support", "help", "assistance", 
    "family", "friend", "mentor", "resource", "community", "funding"
  ];

  const optionKeywords = [
    "option", "alternative", "choice", "path", "route", "possibility",
    "instead", "either", "or", "firstly", "secondly", "thirdly"
  ];

  const countOccurrences = (keywords: string[]) => {
    const lowerText = text.toLowerCase();
    return keywords.reduce((count, word) => {
      const regex = new RegExp(`\\b${word}\\b`, 'gi');
      const matches = lowerText.match(regex);
      return count + (matches ? matches.length : 0);
    }, 0);
  };

  // Estimate token count (rough approximation: words * 1.3)
  const token_count = Math.round(words.length * 1.3);
  const sentence_count = sentences.length;
  
  // Heuristic for option count: look for numbered lists or explicit option keywords
  const listMatches = text.match(/^\s*(\d+\.|[•\-\*])\s+/gm);
  const option_count = Math.max(listMatches ? listMatches.length : 0, countOccurrences(optionKeywords) / 2);

  return {
    token_count,
    sentence_count,
    option_count: Math.round(option_count),
    support_option_count: countOccurrences(supportKeywords),
    long_term_keyword_count: countOccurrences(longTermKeywords),
    risk_keyword_count: countOccurrences(riskKeywords),
  };
}
