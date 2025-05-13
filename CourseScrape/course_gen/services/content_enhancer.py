from course_gen.core.globals import (
    logger, re, List, os, traceback, Tuple, logging, lazy
)
    
class AIContentEnhancer:
    """Advanced AI content generation using GPT-2 with enhancements and improved error handling"""
    def __init__(self, model_name: str = "gpt2-large", cache_dir: str = "model_cache"):
        """Initialize AI Content Enhancer

        Args:
            model_name: Hugging Face model name (using smaller model for Colab)
            cache_dir: Directory to cache downloaded models
        """
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        # Flag to track if we should use rule-based generation
        self.use_rule_based = False

        # Load model with caching
        try:
            logger.info(f"Loading {model_name} model...")

            # Import here to allow graceful fallback if imports fail
            try:
                from transformers import GPT2TokenizerFast, GPT2LMHeadModel, GPT2Config
                self.tokenizer = GPT2TokenizerFast.from_pretrained(model_name, cache_dir=cache_dir)

                # Attempt to load model with optimizations
                try:
                    config = GPT2Config.from_pretrained(model_name, cache_dir=cache_dir)
                    self.model = GPT2LMHeadModel.from_pretrained(
                        model_name,
                        config=config,
                        cache_dir=cache_dir
                    )
                except:
                    self.model = GPT2LMHeadModel.from_pretrained(model_name, cache_dir=cache_dir)

                # Use GPU if available
                try:
                    self.device = lazy.torch.device("cuda" if lazy.torch.cuda.is_available() else "cpu")
                    if self.device.type == 'cuda':
                        logger.info("Using GPU acceleration")
                except (AttributeError, ImportError):
                    logger.warning("PyTorch not available or not properly imported via lazy loading")
                    self.device = None
                    self.use_rule_based = True

                if self.device is not None:
                    self.model.to(self.device)
                else:
                    logger.warning("Unable to move model to any device, using rule-based generation instead")
                    self.use_rule_based = True

                # Optimize for inference
                self.model.eval()

                # Add educational special tokens
                self.special_tokens = {
                    'explanation': '<|explanation|>',
                    'example': '<|example|>',
                    'exercise': '<|exercise|>',
                    'summary': '<|summary|>',
                    'beginner': '<|beginner|>',
                    'intermediate': '<|intermediate|>',
                    'advanced': '<|advanced|>'
                }

                # Add special tokens to tokenizer
                special_tokens_dict = {'additional_special_tokens': list(self.special_tokens.values())}
                num_added_toks = self.tokenizer.add_special_tokens(special_tokens_dict)
                self.model.resize_token_embeddings(len(self.tokenizer))

                logger.info(f"AI Content Enhancer initialized with {model_name} model")
                logger.info(f"Added {num_added_toks} special tokens to the tokenizer")

            except ImportError:
                logger.warning("Failed to import required libraries for AI model. Using rule-based generation.")
                self.model = None
                self.tokenizer = None
                self.use_rule_based = True

        except Exception as e:
            logger.error(f"Error initializing AI Content Enhancer: {str(e)}")
            # For simplicity in Colab, use rule-based generation if model fails
            self.model = None
            self.tokenizer = None
            self.use_rule_based = True
            logger.warning("Using simplified rule-based generation instead of GPT-2")

    def enhance_content(self,
                        prompt: str,
                        content_type: str,
                        max_length: int = 200,
                        temperature: float = 0.7,
                        top_p: float = 0.95,
                        repetition_penalty: float = 1.2) -> str:
        """Generate enhanced educational content using GPT-2 or rule-based fallback

        Args:
            prompt: Text prompt to generate from
            content_type: Type of content to generate (explanation, example, exercise, summary)
            max_length: Maximum length of generated text
            temperature: Sampling temperature (higher = more creative, lower = more deterministic)
            top_p: Nucleus sampling parameter
            repetition_penalty: Penalty for repeating tokens

        Returns:
            str: Generated content
        """
        # If model failed to load or we're using rule-based generation, use rule-based approach
        if self.use_rule_based or self.model is None:
            return self._rule_based_generation(prompt, content_type)

        try:
            # Validate content type and ensure it's a valid key
            if not isinstance(content_type, str) or content_type not in self.special_tokens:
                valid_types = ", ".join(self.special_tokens.keys())
                logger.warning(f"Invalid content type: {content_type}. Using 'explanation'. Valid types: {valid_types}")
                content_type = 'explanation'

            # Add special token to prompt
            prompt_with_token = f"{self.special_tokens[content_type]}{prompt}"

            # Ensure prompt isn't too long - truncate if needed to avoid sequence length errors
            tokens = self.tokenizer.encode(prompt_with_token)

            if len(tokens) > 900:
                logger.warning(f"Prompt too long ({len(tokens)} tokens), truncating intelligently...")
                head = tokens[:300]
                tail = tokens[-600:]
                tokens = head + tail
                prompt_with_token = self.tokenizer.decode(tokens)  # Optional: only if you use the string later

            # ALWAYS assign encoded_prompt
            encoded_prompt = lazy.torch.tensor([tokens]).to(self.device)
            input_len = encoded_prompt.size(1)

            # Prepare input for model
            try:
                encoded_prompt = self.tokenizer.encode(prompt_with_token, return_tensors="pt").to(self.device)
                input_len = encoded_prompt.size(1)

                # Check if encoded input is too long
                if input_len > 900:  # Another safety check
                    logger.warning(f"Encoded prompt too long ({input_len} tokens), using rule-based generation")
                    return self._rule_based_generation(prompt, content_type)

            except Exception as encoding_error:
                logger.error(f"Error encoding prompt: {str(encoding_error)}")
                return self._rule_based_generation(prompt, content_type)

            # Set generation parameters based on content type
            if content_type == 'explanation':
                temperature = min(temperature, 0.7)  # More factual
                repetition_penalty = 1.3  # Prevent repetition
            elif content_type == 'example':
                temperature = min(temperature, 0.6)  # More structured
                top_p = 0.92  # Slightly more focused
            elif content_type == 'exercise':
                temperature = min(temperature, 0.8)  # Allow some creativity

            # Memory optimization
            with lazy.torch.no_grad():
                try:
                    generation_max_length = min(input_len + max_length, 1024)

                    # Generate text with improved parameters
                    outputs = self.model.generate(
                        encoded_prompt,
                        max_length=generation_max_length,
                        do_sample=True,
                        top_k=50,
                        top_p=top_p,
                        temperature=temperature,
                        num_return_sequences=1,
                        pad_token_id=self.tokenizer.eos_token_id,
                        no_repeat_ngram_size=3,
                        repetition_penalty=repetition_penalty,
                    )

                    # Decode the generated text
                    generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

                    # Extract only the newly generated text
                    if prompt_with_token in generated_text:
                        generated_text = generated_text[generated_text.find(prompt_with_token) + len(prompt_with_token):]

                    # Process and format the generated text
                    formatted_text = self._post_process(generated_text, content_type)

                    return formatted_text

                except (IndexError, RuntimeError) as gen_error:
                    logger.error(f"Error during generation: {str(gen_error)}")
                    return self._rule_based_generation(prompt, content_type)

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}\n{traceback.format_exc()}")
            return self._rule_based_generation(prompt, content_type)

    def _rule_based_generation(self, prompt: str, content_type: str) -> str:
        """Fallback method for generating content without GPT-2"""
        # Extract important keywords from prompt
        words = re.findall(r'\b\w{4,}\b', prompt.lower())
        keywords = [word for word in words if word not in ['this', 'that', 'with', 'from', 'about', 'what', 'where', 'when', 'which']]
        keywords = keywords[:5] if keywords else ["this topic"]  # Just use top 5 keywords or default

        if content_type == 'explanation':
            return f"This section explains important concepts about {', '.join(keywords)}. Understanding these fundamentals is critical for mastering this topic. You'll learn how these concepts relate to each other and how they're applied in real-world scenarios."

        elif content_type == 'example':
            return f"Here's an example that demonstrates how {', '.join(keywords)} work together. This practical implementation shows the concepts in action and gives you a reference for your own projects."

        elif content_type == 'exercise':
            return f"Practice what you've learned about {', '.join(keywords)} with this exercise. Try to implement the solution on your own before checking the hints. This will reinforce your understanding of the key concepts."

        elif content_type == 'summary':
            return f"To summarize what we've covered about {', '.join(keywords)}: these concepts form the foundation of this topic. Review these points regularly and practice implementing them to build your expertise."

        else:
            return f"Content related to {', '.join(keywords)} would be presented here. Continue exploring these topics to deepen your understanding."

    def _post_process(self, text: str, content_type: str) -> str:
        """Clean and format generated text

        Args:
            text: Generated text to process
            content_type: Type of content (for specific formatting)

        Returns:
            str: Processed and formatted text
        """
        # Safety check - if text is None or empty, return a placeholder
        if not text:
            return self._rule_based_generation("content", content_type)

        # Remove special tokens if present
        for token in self.special_tokens.values() if hasattr(self, 'special_tokens') else []:
            text = text.replace(token, "")

        # Basic cleaning
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.strip()

        # Fix common punctuation issues
        replacements = [
            (r' ,', ','),
            (r' \.', '.'),
            (r' !', '!'),
            (r' \?', '?'),
            (r' ;', ';'),
            (r' :', ':'),
            (r'\( ', '('),
            (r' \)', ')'),
            (r" \'", "'"),
            (r' " ', '" '),
            (r' " ', '" ')
        ]

        for pattern, repl in replacements:
            text = re.sub(pattern, repl, text)

        # Content-specific processing
        if content_type == 'explanation':
            # Ensure text ends with a complete sentence
            text = self._ensure_complete_sentence(text)

            # Make sure we have paragraph breaks
            if len(text) > 200 and '\n\n' not in text:
                sentences = re.split(r'(?<=[.!?])\s+', text)
                if len(sentences) >= 3:
                    midpoint = len(sentences) // 2
                    sentences.insert(midpoint, '\n\n')
                    text = ' '.join(sentences)

        elif content_type == 'example':
            # For code examples, preserve code formatting
            text = text.replace('```', '')
            if '```' not in text and re.search(r'(for|if|def|class|import|function)\s+\w+', text):
                # This is likely code without code markers - preserve indentation
                text = text.replace('\n ', '\n')  # Fix extra spaces in indentation

        elif content_type == 'exercise':
            # Format exercise content with bullet points if not already using them
            if '-' not in text[:50] and '*' not in text[:50]:
                lines = text.split('\n')
                if len(lines) >= 3:
                    for i in range(1, len(lines)):
                        # Add bullet points to lines that look like list items
                        if lines[i].strip() and not lines[i].strip().startswith(('-', '*', '1.', '2.')):
                            lines[i] = '- ' + lines[i].strip()
                    text = '\n'.join(lines)

        return text

    def _ensure_complete_sentence(self, text: str) -> str:
        """Ensure text ends with a complete sentence"""
        # Safety check
        if not text:
            return text

        # Find the last sentence delimiter
        last_period = max(text.rfind('.'), text.rfind('!'), text.rfind('?'))

        if last_period == -1:
            # No sentence delimiter found
            return text + "."  # Add a period if none exists

        # Keep text up to the last complete sentence
        return text[:last_period + 1]

    def batch_enhance(self, prompts: List[Tuple[str, str]], batch_size: int = 4) -> List[str]:
        """Process multiple enhancements in batches for efficiency

        Args:
            prompts: List of (prompt, content_type) tuples
            batch_size: Number of prompts to process in each batch

        Returns:
            List[str]: Enhanced content for each prompt
        """
        results = []

        # Validate input to avoid unpacking errors
        if not prompts:
            logger.error("Empty prompts list provided to batch_enhance")
            return []

        # Check if each item in prompts is a tuple with exactly 2 elements
        valid_prompts = []
        for item in prompts:
            if isinstance(item, tuple) and len(item) == 2:
                valid_prompts.append(item)
            else:
                logger.error(f"Invalid prompt format: {item} - expected (prompt, content_type) tuple")
                # Add a placeholder for invalid items
                continue

        # If no valid prompts, return early
        if not valid_prompts:
            return results

        # Process valid prompts in batches
        for i in range(0, len(valid_prompts), batch_size):
            batch = valid_prompts[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(valid_prompts) + batch_size - 1) // batch_size}")

            batch_results = []
            for prompt_tuple in batch:
                try:
                    # Safe unpacking - we've already verified these are valid tuples
                    prompt, content_type = prompt_tuple
                    enhanced_text = self.enhance_content(prompt, content_type)
                    batch_results.append(enhanced_text)
                except Exception as e:
                    logger.error(f"Error in batch processing: {str(e)}")
                    # Add a placeholder on error
                    batch_results.append(self._rule_based_generation("error occurred", "explanation"))

            results.extend(batch_results)

        return results

    def unload_model(self):
        """Unload model from memory to free resources"""
        if hasattr(self, 'model') and self.model is not None:
            self.model = None
            if lazy.torch.cuda.is_available():
                lazy.torch.cuda.empty_cache()
            logger.info("Model unloaded from memory")