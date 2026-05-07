"""
Interface for local LLMs using Hugging Face transformers
"""
import torch
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class LocalLLMInterface:
    """Interface for loading and using local LLMs from Hugging Face"""
    
    def __init__(self, model_name: str, config: Optional[Dict] = None):
        """
        Initialize LLM interface
        
        Args:
            model_name: Hugging Face model name or path
            config: Configuration dictionary with model settings
        """
        self.model_name = model_name
        self.config = config or {}
        self.model = None
        self.tokenizer = None
        self.device = None
        self.pipeline = None
        
        self._import_dependencies()
        self._load_model()
    
    def _import_dependencies(self):
        """Import required libraries"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            self.AutoTokenizer = AutoTokenizer
            self.AutoModelForCausalLM = AutoModelForCausalLM
            self.torch = torch
        except ImportError:
            raise ImportError(
                "transformers or torch not installed. "
                "Install: pip install transformers torch accelerate"
            )
    
    def _load_model(self):
        """Load model and tokenizer"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            
            device = self.config.get('device', 'cuda' if torch.cuda.is_available() else 'cpu')
            dtype_str = self.config.get('dtype', 'float16')
            
            # Map dtype string to torch dtype
            dtype_map = {
                'float16': torch.float16,
                'float32': torch.float32,
                'bfloat16': torch.bfloat16,
            }
            dtype = dtype_map.get(dtype_str, torch.float16)
            
            # Load tokenizer
            self.tokenizer = self.AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Set padding token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with quantization if using float16 on CUDA
            model_kwargs = {
                'trust_remote_code': True,
                'device_map': 'auto' if device == 'cuda' else device,
            }
            
            if device == 'cuda' and dtype == torch.float16:
                model_kwargs['torch_dtype'] = torch.float16
            
            self.model = self.AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            self.device = device
            self.model.eval()
            
            logger.info(f"Model loaded successfully on {device}")
            logger.info(f"Model dtype: {dtype}")
            
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {str(e)}")
            raise
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Generate text from prompt
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p probability threshold
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        try:
            max_tokens = max_tokens or self.config.get('max_tokens', 512)
            temperature = temperature or self.config.get('temperature', 0.7)
            top_p = top_p or self.config.get('top_p', 0.9)
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=2048
            ).to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask'],
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    **kwargs
                )
            
            # Decode
            generated_text = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            # Remove prompt from output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
        
        except Exception as e:
            logger.error(f"Error during generation: {str(e)}")
            raise
    
    def generate_batch(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[str]:
        """
        Generate text for multiple prompts
        
        Args:
            prompts: List of input prompts
            **kwargs: Generation parameters
            
        Returns:
            List of generated texts
        """
        results = []
        for prompt in prompts:
            try:
                result = self.generate(prompt, **kwargs)
                results.append(result)
            except Exception as e:
                logger.warning(f"Error generating for prompt: {str(e)}")
                results.append("")
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded model"""
        if self.model is None:
            return {}
        
        return {
            'model_name': self.model_name,
            'device': str(self.device),
            'dtype': str(self.model.dtype),
            'num_parameters': sum(p.numel() for p in self.model.parameters()),
            'vocab_size': self.tokenizer.vocab_size,
        }
    
    def unload(self):
        """Unload model to free memory"""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Model unloaded")


class ModelRecommendations:
    """Recommendations for different hardware configurations"""
    
    RECOMMENDATIONS = {
        'colab_t4': {
            'model': 'Qwen/Qwen2-7B',
            'dtype': 'float16',
            'batch_size': 4,
            'description': 'Qwen 7B - Best reasoning capability on T4 GPU',
            'alternatives': [
                'meta-llama/Llama-2-7b-hf',
                'mistralai/Mistral-7B-v0.1',
            ]
        },
        'colab_3b': {
            'model': 'Qwen/Qwen2-1.5B',
            'dtype': 'float16',
            'batch_size': 8,
            'description': 'Qwen 1.5B - Fast for limited VRAM',
            'alternatives': [
                'TinyLlama/TinyLlama-1.1B-Chat-v1.0',
            ]
        },
        'rtx3090': {
            'model': 'Qwen/Qwen2-32B',
            'dtype': 'float16',
            'batch_size': 8,
            'description': 'Qwen 32B - Best reasoning with high VRAM',
            'alternatives': [
                'meta-llama/Llama-2-13b-hf',
                'Qwen/Qwen2-14B',
            ]
        },
        'cpu_only': {
            'model': 'TinyLlama/TinyLlama-1.1B-Chat-v1.0',
            'dtype': 'float32',
            'batch_size': 1,
            'description': 'CPU-only model (slow but works)',
        }
    }
    
    @classmethod
    def get_recommendation(cls, hardware: str) -> Dict[str, Any]:
        """
        Get model recommendation for hardware
        
        Args:
            hardware: Hardware configuration (colab_t4, colab_3b, rtx3090, cpu_only)
            
        Returns:
            Recommendation dictionary
        """
        return cls.RECOMMENDATIONS.get(
            hardware,
            cls.RECOMMENDATIONS['colab_t4']
        )
    
    @classmethod
    def print_recommendations(cls):
        """Print all recommendations"""
        print("\n" + "="*70)
        print("LLM MODEL RECOMMENDATIONS FOR DATASET GENERATION")
        print("="*70 + "\n")
        
        for hw, rec in cls.RECOMMENDATIONS.items():
            print(f"Hardware: {hw.upper()}")
            print(f"  Recommended Model: {rec['model']}")
            print(f"  Data Type: {rec['dtype']}")
            print(f"  Batch Size: {rec['batch_size']}")
            print(f"  Description: {rec['description']}")
            if 'alternatives' in rec:
                print(f"  Alternatives: {', '.join(rec['alternatives'])}")
            print()
