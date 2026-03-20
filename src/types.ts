export interface PromptRow {
  prompt_id: string;
  scenario_id: string;
  domain: string;
  variant_type: string;
  title: string;
  ses_level: string;
  cue_dimensions: string;
  persona_cues: string;
  persona_text: string;
  constraint_controlled: string;
  placebo_persona: string;
  placebo_text: string;
  template_id: string;
  base_scenario: string;
  final_prompt: string;
  [key: string]: any; // For rubric columns
}

export interface EvaluationResult {
  // Heuristic indices
  token_count: number;
  sentence_count: number;
  option_count: number;
  support_option_count: number;
  long_term_keyword_count: number;
  risk_keyword_count: number;

  // LLM judge indices
  aspiration_score?: number;
  risk_score?: number;
  supportiveness_score?: number;
  actionability_score?: number;
  opportunity_narrowing?: number;
  long_term_option_present?: boolean;
  support_option_present?: boolean;

  generated_text: string;
  judge_raw_output?: string;
}

export interface ProcessedRow extends PromptRow {
  evaluation?: EvaluationResult;
  status: 'pending' | 'running' | 'completed' | 'error';
  error?: string;
}
