import fs from 'fs';
import path from 'path';
import axios from 'axios';
import { parse } from 'csv-parse/sync';
import { createObjectCsvWriter } from 'csv-writer';
import dotenv from 'dotenv';

dotenv.config();

// --- CONFIGURATION ---
const INPUT_FILE = 'prompts.csv';
const OUTPUT_FILE = 'results.csv';

// Models to iterate through (Example using Hugging Face Inference API)
// You can also point these to local Ollama/LM Studio endpoints (http://localhost:11434/v1/chat/completions)
const MODELS = [
  { id: 'meta-llama/Llama-2-7b-chat-hf', name: 'Llama-2' },
  { id: 'mistralai/Mistral-7B-Instruct-v0.2', name: 'Mistral' },
  { id: 'tiiuae/falcon-7b-instruct', name: 'Falcon' }
];

const HF_API_KEY = process.env.HF_API_KEY || '';

// --- PREPROCESSING & HEURISTICS ---

function preprocessText(text: string) {
  // 1. Clean special characters (keep basic punctuation)
  const cleaned = text.replace(/[^\w\s.,!?;:"'-]/g, '');
  
  // 2. Tokenize (simple whitespace split for research proxy)
  const tokens = cleaned.toLowerCase().split(/\s+/).filter(t => t.length > 0);
  
  // 3. Segment into sentences
  const sentences = cleaned.split(/[.!?]+/).filter(s => s.trim().length > 0);
  
  return { cleaned, tokens, sentences };
}

function calculateHeuristics(text: string) {
  const { tokens, sentences } = preprocessText(text);
  
  const longTermKeywords = ['long-term', 'future', 'investment', 'career', 'growth', 'sustainability', 'prospects'];
  const riskKeywords = ['risk', 'uncertainty', 'debt', 'failure', 'loan', 'interest', 'instability', 'trade-off'];
  const supportKeywords = ['scholarship', 'grant', 'loan', 'financial aid', 'family support', 'safety net', 'assistance'];

  // Count occurrences
  const longTermCount = tokens.filter(t => longTermKeywords.includes(t)).length;
  const riskCount = tokens.filter(t => riskKeywords.includes(t)).length;
  const supportCount = tokens.filter(t => supportKeywords.includes(t)).length;

  // Detect options (numbered lists or bullet points)
  const optionMatches = text.match(/^\s*(\d+\.|\*|-)\s+/gm);
  const optionCount = optionMatches ? optionMatches.length : 0;

  return {
    token_count: tokens.length,
    sentence_count: sentences.length,
    option_count: optionCount,
    support_option_count: supportCount,
    long_term_keyword_count: longTermCount,
    risk_keyword_count: riskCount
  };
}

// --- LLM CALLING ---

async function callLLM(modelId: string, prompt: string): Promise<string> {
  try {
    // Defaulting to Hugging Face Inference API
    const response = await axios.post(
      `https://api-inference.huggingface.co/models/${modelId}`,
      { inputs: prompt, parameters: { max_new_tokens: 500, return_full_text: false } },
      { headers: { Authorization: `Bearer ${HF_API_KEY}` } }
    );
    
    // HF returns an array, sometimes with different structures depending on the model
    if (Array.isArray(response.data)) {
      return response.data[0].generated_text || response.data[0].summary_text || '';
    }
    return '';
  } catch (error: any) {
    console.error(`Error calling ${modelId}:`, error.message);
    return `ERROR: ${error.message}`;
  }
}

// --- MAIN PIPELINE ---

async function runPipeline() {
  console.log('🚀 Starting LLM Bias Research Pipeline...');

  if (!fs.existsSync(INPUT_FILE)) {
    console.error(`❌ Input file ${INPUT_FILE} not found.`);
    return;
  }

  const fileContent = fs.readFileSync(INPUT_FILE, 'utf-8');
  const records = parse(fileContent, { columns: true, skip_empty_lines: true });

  const csvWriter = createObjectCsvWriter({
    path: OUTPUT_FILE,
    header: [
      { id: 'prompt_id', title: 'PROMPT_ID' },
      { id: 'model_name', title: 'MODEL_NAME' },
      { id: 'original_prompt', title: 'ORIGINAL_PROMPT' },
      { id: 'generated_text', title: 'GENERATED_TEXT' },
      { id: 'token_count', title: 'TOKEN_COUNT' },
      { id: 'sentence_count', title: 'SENTENCE_COUNT' },
      { id: 'option_count', title: 'OPTION_COUNT' },
      { id: 'support_option_count', title: 'SUPPORT_OPTION_COUNT' },
      { id: 'long_term_keyword_count', title: 'LONG_TERM_KEYWORD_COUNT' },
      { id: 'risk_keyword_count', title: 'RISK_KEYWORD_COUNT' }
    ]
  });

  const allResults = [];

  for (const record of records) {
    const promptId = record.prompt_id || record.id || 'unknown';
    const promptText = record.final_prompt || record.prompt || '';

    console.log(`\n📝 Processing Prompt: ${promptId}`);

    for (const model of MODELS) {
      console.log(`   🤖 Querying ${model.name}...`);
      
      const generatedText = await callLLM(model.id, promptText);
      const heuristics = calculateHeuristics(generatedText);

      allResults.push({
        prompt_id: promptId,
        model_name: model.name,
        original_prompt: promptText,
        generated_text: generatedText.replace(/\n/g, ' '), // Flatten for CSV
        ...heuristics
      });

      // Avoid hitting rate limits (1s delay)
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  await csvWriter.writeRecords(allResults);
  console.log(`\n✅ Pipeline complete! Results saved to ${OUTPUT_FILE}`);
}

runPipeline().catch(console.error);
