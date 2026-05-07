"""
Dataset generation with AI-driven question generation and reasoning-based conversations.
Text is treated as the answer, and questions are generated for it.
Every output includes reasoning (chain-of-thought).
"""
import json
import re
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import yaml

logger = logging.getLogger(__name__)


class ReasoningConversationGenerator:
    """Generate reasoning-based conversations by turning text into Q&A"""
    
    def __init__(self, llm_interface, prompts_file: str = "prompts.yaml", config: Optional[Dict] = None):
        """
        Initialize conversation generator
        
        Args:
            llm_interface: LocalLLMInterface instance for generation
            prompts_file: Path to prompts.yaml file
            config: Configuration dictionary
        """
        self.llm = llm_interface
        self.config = config or {}
        self.prompts = self._load_prompts(prompts_file)
        
        # Ensure all outputs have reasoning
        self.force_reasoning = True
        self.cot_marker = self.prompts.get('cot_markers', {}).get('reasoning_start', 'Let me think through this step by step:')
    
    def _load_prompts(self, prompts_file: str) -> Dict:
        """Load prompts from YAML file"""
        try:
            with open(prompts_file, 'r') as f:
                prompts = yaml.safe_load(f)
            logger.info(f"Loaded prompts from {prompts_file}")
            return prompts
        except FileNotFoundError:
            logger.warning(f"Prompts file not found: {prompts_file}. Using defaults.")
            return self._get_default_prompts()
        except Exception as e:
            logger.error(f"Error loading prompts: {str(e)}. Using defaults.")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict:
        """Fallback default prompts"""
        return {
            'system_instructions': {
                'reasoning_educator': 'You are an expert educator. Show clear reasoning for every response.',
            },
            'cot_markers': {
                'reasoning_start': 'Let me think through this step by step:',
            }
        }
    
    def generate_questions_for_text(self, text: str, num_questions: int = 3) -> List[Dict]:
        """
        Generate questions about the provided text.
        Text is treated as the answer content.
        
        Args:
            text: The source text to generate questions about
            num_questions: Number of questions to generate (3-5)
            
        Returns:
            List of question dicts: [{'question': '...', 'difficulty': 'easy|medium|hard', 'type': '...'}]
        """
        try:
            prompt_template = self.prompts.get('question_generation', {}).get('prompt_qa', '')
            prompt = prompt_template.format(text=text[:1000])  # Reduced to 1000 chars to save memory
            
            logger.info(f"[Q-Gen] Generating {num_questions} questions from text (len={len(text)})...")
            response = self.llm.generate(prompt, max_tokens=1000)
            
            # Parse JSON response
            questions = self._parse_json_response(response)
            
            if isinstance(questions, list) and len(questions) > 0:
                logger.info(f"[Q-Gen] ✓ Generated {len(questions)} questions")
                return questions[:num_questions]  # Return requested number
            else:
                logger.warning(f"[Q-Gen] Failed to parse questions, generating default ({num_questions})")
                return self._generate_default_questions(text, num_questions)
        
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return self._generate_default_questions(text, num_questions)
    
    def _generate_default_questions(self, text: str, num_questions: int) -> List[Dict]:
        """Generate basic default questions from text"""
        default_questions = [
            {'question': 'What is the main idea in this text?', 'difficulty': 'easy', 'type': 'literal'},
            {'question': 'How would you explain this concept to someone unfamiliar with it?', 'difficulty': 'medium', 'type': 'inferential'},
            {'question': 'What are the key implications or applications of this information?', 'difficulty': 'hard', 'type': 'analytical'},
            {'question': 'What are the most important points to remember?', 'difficulty': 'easy', 'type': 'literal'},
            {'question': 'How does this relate to broader concepts?', 'difficulty': 'hard', 'type': 'analytical'},
        ]
        return default_questions[:num_questions]
    
    def generate_answer_with_reasoning(self, question: str, text: str) -> str:
        """
        Generate answer with chain-of-thought reasoning.
        
        Args:
            question: The question to answer
            text: The source text to base the answer on
            
        Returns:
            Answer with reasoning included
        """
        try:
            prompt_template = self.prompts.get('answer_generation', {}).get('prompt_with_reasoning', '')
            prompt = prompt_template.format(question=question, text=text[:1000])  # Reduced to 1000 chars
            
            logger.info(f"[A-Gen] Answering: {question[:60]}...")
            response = self.llm.generate(prompt, max_tokens=1500)
            
            # Ensure reasoning is present
            if self._has_reasoning_markers(response):
                return response
            else:
                # Add reasoning if missing
                return self.cot_marker + "\n" + response
        
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return f"{self.cot_marker}\nUnable to generate answer at this time."
    
    def _has_reasoning_markers(self, text: str) -> bool:
        """Check if text contains reasoning markers"""
        markers = self.prompts.get('keywords', {}).get('reasoning_required', [])
        # Check for common reasoning patterns
        reasoning_patterns = ['step', 'think', 'reason', 'because', 'therefore', 'let me', 'first', 'then', 'finally']
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in reasoning_patterns)
    
    def generate_multi_turn_conversation(
        self,
        text: str,
        num_turns: int = 3,
        document_id: str = "doc1"
    ) -> Dict:
        """
        Generate a multi-turn conversation from a single text/page.
        All Q&A pairs from this page form one conversation.
        Every response includes reasoning.
        
        Args:
            text: Source text (page/chunk)
            num_turns: Number of Q&A pairs/turns
            document_id: Document identifier
            
        Returns:
            Multi-turn conversation dict
        """
        try:
            logger.debug(f"Generating {num_turns}-turn conversation from text...")
            
            # Step 1: Generate questions for this text
            questions = self.generate_questions_for_text(text, num_questions=num_turns)
            
            # Step 2: Build conversation
            system_prompt = self.prompts.get('system_instructions', {}).get('reasoning_educator', 
                                            'You are an expert educator showing clear reasoning.')
            
            conversation = {
                'type': 'multi_turn',
                'document_id': document_id,
                'source_text_preview': text[:200],
                'system': system_prompt,
                'conversations': [],
                'has_reasoning': True,  # Always true
                'format_decided': 'multi_turn_qa',
                'num_turns': len(questions),
                'created_at': datetime.now().isoformat(),
            }
            
            # Step 3: Add Q&A pairs
            for i, q_dict in enumerate(questions):
                question = q_dict.get('question', '')
                if not question:
                    continue
                
                # Add user question
                conversation['conversations'].append({
                    'role': 'user',
                    'content': question,
                })
                
                # Generate answer with reasoning
                answer = self.generate_answer_with_reasoning(question, text)
                
                conversation['conversations'].append({
                    'role': 'assistant',
                    'content': answer,
                    'has_reasoning': True,
                    'question_difficulty': q_dict.get('difficulty', 'medium'),
                    'question_type': q_dict.get('type', 'general'),
                })
            
            logger.debug(f"Generated {len(questions)}-turn conversation with reasoning")
            return conversation
        
        except Exception as e:
            logger.error(f"Error generating multi-turn conversation: {str(e)}")
            return self._create_fallback_conversation(text)
    
    def generate_problem_solving_conversation(
        self,
        text: str,
        problem_type: str = "general",
        document_id: str = "doc1"
    ) -> Dict:
        """
        Generate problem-solving conversation where text contains a problem.
        
        Args:
            text: Problem text/content
            problem_type: Type of problem (math, physics, chemistry, biology, general)
            document_id: Document identifier
            
        Returns:
            Problem-solving conversation
        """
        try:
            logger.debug(f"Generating {problem_type} problem-solving conversation...")
            
            # Generate solving approach
            prompt_template = self.prompts.get('answer_generation', {}).get('prompt_problem_solving', '')
            prompt = prompt_template.format(text=text[:2000])
            
            solution = self.llm.generate(prompt, max_tokens=2000)
            
            # Ensure reasoning included
            if not self._has_reasoning_markers(solution):
                solution = f"{self.cot_marker}\n{solution}"
            
            system_prompt = f'You are an expert {problem_type} tutor. Solve problems with step-by-step reasoning.'
            
            conversation = {
                'type': 'problem_solving',
                'document_id': document_id,
                'problem_type': problem_type,
                'system': system_prompt,
                'conversations': [
                    {
                        'role': 'user',
                        'content': text,
                    },
                    {
                        'role': 'assistant',
                        'content': solution,
                        'has_reasoning': True,
                    }
                ],
                'has_reasoning': True,  # Always true
                'format_decided': 'problem_solving',
                'created_at': datetime.now().isoformat(),
            }
            
            logger.debug("Generated problem-solving conversation")
            return conversation
        
        except Exception as e:
            logger.error(f"Error generating problem-solving conversation: {str(e)}")
            return self._create_fallback_conversation(text)
    
    def generate_analysis_conversation(
        self,
        text: str,
        document_id: str = "doc1"
    ) -> Dict:
        """
        Generate analytical conversation about the text.
        
        Args:
            text: Text to analyze
            document_id: Document identifier
            
        Returns:
            Analysis conversation
        """
        try:
            logger.debug("Generating analytical conversation...")
            
            # Generate analysis questions
            analysis_questions = [
                "What are the key arguments or points made in this text?",
                "What are the underlying assumptions or premises?",
                "What evidence or examples support the main ideas?",
                "What are potential criticisms or alternative perspectives?",
                "What are the implications of this information?",
            ]
            
            system_prompt = 'You are a critical analyst. Provide deep analysis with clear reasoning.'
            
            conversation = {
                'type': 'analysis',
                'document_id': document_id,
                'system': system_prompt,
                'conversations': [],
                'has_reasoning': True,
                'format_decided': 'analytical',
                'created_at': datetime.now().isoformat(),
            }
            
            # Add analysis Q&A
            selected_questions = random.sample(analysis_questions, min(2, len(analysis_questions)))
            
            for question in selected_questions:
                conversation['conversations'].append({
                    'role': 'user',
                    'content': question,
                })
                
                answer = self.generate_answer_with_reasoning(question, text)
                
                conversation['conversations'].append({
                    'role': 'assistant',
                    'content': answer,
                    'has_reasoning': True,
                })
            
            logger.debug("Generated analytical conversation")
            return conversation
        
        except Exception as e:
            logger.error(f"Error generating analysis conversation: {str(e)}")
            return self._create_fallback_conversation(text)
    
    def _parse_json_response(self, response: str) -> Optional[List[Dict]]:
        """
        Parse JSON response from LLM.
        Handles various formatting issues.
        """
        try:
            # Clean response - remove markdown code blocks
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse JSON
            parsed = json.loads(cleaned)
            return parsed if isinstance(parsed, list) else [parsed]
        
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON response: {response[:100]}")
            return None
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return None
    
    def _create_fallback_conversation(self, text: str) -> Dict:
        """Create fallback conversation when generation fails"""
        return {
            'type': 'multi_turn',
            'system': 'You are a helpful educator.',
            'conversations': [
                {
                    'role': 'user',
                    'content': 'What is the main idea in this text?',
                },
                {
                    'role': 'assistant',
                    'content': f'{self.cot_marker}\nBased on the provided text, here are the key ideas...',
                    'has_reasoning': True,
                }
            ],
            'has_reasoning': True,
            'format_decided': 'fallback',
            'created_at': datetime.now().isoformat(),
        }


class DatasetGenerator:
    """Generate complete dataset in JSONL format with reasoning-based conversations"""
    
    def __init__(
        self,
        llm_interface,
        output_file: str = "generated_dataset.jsonl",
        prompts_file: str = "prompts.yaml",
        config: Optional[Dict] = None
    ):
        """
        Initialize dataset generator
        
        Args:
            llm_interface: LocalLLMInterface instance
            output_file: Output JSONL file path
            prompts_file: Path to prompts YAML file
            config: Configuration dictionary
        """
        self.llm = llm_interface
        self.output_file = output_file
        self.config = config or {}
        self.conv_generator = ReasoningConversationGenerator(llm_interface, prompts_file, config)
        self.dataset_count = 0
        
        # Initialize or append to existing file
        self._check_existing_dataset()
    
    def _check_existing_dataset(self):
        """Check if dataset file exists and get count"""
        try:
            with open(self.output_file, 'r') as f:
                self.dataset_count = sum(1 for _ in f)
            logger.info(f"Found existing dataset with {self.dataset_count} entries")
        except FileNotFoundError:
            self.dataset_count = 0
            logger.info("Creating new dataset file")
    
    def add_document(
        self,
        document_id: str,
        text: str,
        source: str = "unknown",
        num_conversations: int = 5,
        preprocessor=None
    ) -> int:
        """
        Process document and add reasoning-based conversations to dataset.
        
        Each chunk/page becomes one multi-turn conversation with all its Q&A pairs.
        
        Args:
            document_id: Unique document identifier
            text: Document text
            source: Source of document (file path, URL, etc.)
            num_conversations: Approximate number of conversations to generate
            preprocessor: TextPreprocessor instance for smart chunking
            
        Returns:
            Number of conversations added
        """
        try:
            added = 0
            
            logger.info(f"Processing document {document_id} for reasoning-based generation...")
            
            # Use smart chunking if available
            if preprocessor and hasattr(preprocessor, 'smart_chunk_text'):
                try:
                    chunks = preprocessor.smart_chunk_text(text)
                    logger.debug(f"Split document into {len(chunks)} chunks")
                except Exception as e:
                    logger.warning(f"Chunking failed, using whole text: {str(e)}")
                    chunks = [{'content': text, 'problems': []}]
            else:
                chunks = [{'content': text, 'problems': []}]
            
            # Process each chunk/page as a single multi-turn conversation
            for chunk_idx, chunk_data in enumerate(chunks):
                chunk_text = chunk_data.get('content', '')
                problem_info = chunk_data.get('problems', [])
                
                if not chunk_text or len(chunk_text.strip()) < 50:
                    logger.debug(f"[Chunk {chunk_idx+1}/{len(chunks)}] Skipping: too short")
                    continue
                
                logger.info(f"[Chunk {chunk_idx+1}/{len(chunks)}] Processing chunk ({len(chunk_text)} chars)...")
                
                # Determine number of turns for this chunk
                turns_per_chunk = max(1, num_conversations // len(chunks)) if len(chunks) > 0 else num_conversations
                
                # Decide format based on content
                if problem_info and random.random() > 0.3:
                    # Problem-solving format
                    problem = random.choice(problem_info)
                    logger.info(f"[Chunk {chunk_idx+1}] Detected problem-solving content")
                    conversation = self.conv_generator.generate_problem_solving_conversation(
                        text=chunk_text,
                        problem_type=problem.get('type', 'general'),
                        document_id=document_id
                    )
                else:
                    # Multi-turn Q&A format
                    logger.info(f"[Chunk {chunk_idx+1}] Generating {turns_per_chunk}-turn Q&A conversation...")
                    conversation = self.conv_generator.generate_multi_turn_conversation(
                        text=chunk_text,
                        num_turns=turns_per_chunk,
                        document_id=document_id
                    )
                
                # Add metadata
                entry = {
                    'dataset_id': self.dataset_count + added,
                    'document_id': document_id,
                    'chunk_index': chunk_idx,
                    'total_chunks': len(chunks),
                    'source': source,
                    **conversation
                }
                
                # Write to JSONL
                self._write_entry(entry)
                added += 1
                logger.info(f"[Chunk {chunk_idx+1}/{len(chunks)}] ✓ Added conversation {added}/{num_conversations}")
            
            self.dataset_count += added
            logger.info(f"Added {added} reasoning-based conversations from document {document_id}")
            return added
        
        except Exception as e:
            logger.error(f"Error adding document {document_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0


    def _write_entry(self, entry: Dict):
        """Write single entry to JSONL file"""
        try:
            with open(self.output_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing entry to JSONL: {str(e)}")
    
    def get_dataset_stats(self) -> Dict:
        """Get statistics about generated dataset"""
        try:
            stats = {
                'total_entries': self.dataset_count,
                'output_file': self.output_file,
                'file_size_mb': 0,
                'reasoning_entries': 0,
                'multi_turn_entries': 0,
                'problem_solving_entries': 0,
            }
            
            # Analyze dataset
            try:
                from pathlib import Path
                file_path = Path(self.output_file)
                if file_path.exists():
                    stats['file_size_mb'] = file_path.stat().st_size / (1024 * 1024)
                    
                    # Count entry types
                    with open(self.output_file, 'r') as f:
                        for line in f:
                            try:
                                entry = json.loads(line)
                                if entry.get('has_reasoning'):
                                    stats['reasoning_entries'] += 1
                                if entry.get('type') == 'multi_turn':
                                    stats['multi_turn_entries'] += 1
                                elif entry.get('type') == 'problem_solving':
                                    stats['problem_solving_entries'] += 1
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.warning(f"Error analyzing dataset: {str(e)}")
            
            return stats
        
        except Exception as e:
            logger.error(f"Error getting dataset stats: {str(e)}")
            return {}


# Backward-compatible alias for existing imports and call sites.
ConversationGenerator = ReasoningConversationGenerator
