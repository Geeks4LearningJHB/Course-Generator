from course_gen.core.globals import (logger, os, re, lazy)

class KnowledgeEnhancer:
    def __init__(self, model_name="Qwen/Qwen3-0.6B", cache_dir = "scraper_model_cache", use_bfloat16=True):
        """
        Initializes the QwenParser with tokenizer and model loaded from Hugging Face.
        
        Args:
            model_name (str): Hugging Face model ID.
            use_bfloat16 (bool): Whether to use bfloat16 or fallback to float16.
        """
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        try:
            
            logger.info(f"Loading {model_name} model...")

            self.tokenizer = lazy.AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                trust_remote_code=True
            )
            self.model = lazy.AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                device_map="auto",
                torch_dtype=lazy.torch.bfloat16 if use_bfloat16 else lazy.torch.float16,
                trust_remote_code=True
            )
            
            logger.info(f"AI Content Enhancer initialized with {model_name} model")
        except Exception as e:
            logger.error(f"Error initializing AI Knowledge Enhancer: {str(e)}")

    def format_prompt(self, chunk, task="educational_content", enable_thinking=True):
        if task == "educational_content":
            content = (
                "You are an AI assistant tasked with restructuring raw educational material into well-organized, structured components for course generation.\n\n"
                "From the following text, extract and format the following components, using markdown-style headings:\n"
                "- **Definition**: Clearly define important terms.\n"
                "- **Key Concept**: Highlight and briefly explain the key ideas.\n"
                "- **Explanation**: Expand on the concepts to make them easy to understand.\n"
                "- **Example**: Give practical examples (use triple backticks ``` for code if applicable).\n\n"
                "Label each section clearly using headings such as '### Definition'.\n"
                "Only return educational content used for learning. Be concise. Do not repeat the input.\n\n"
                f"Text:\n{chunk}\n"
            )
        elif task == "classification":
            content = (
                "Is the following text educational in nature?"
                "Only return 'True' if it is clearly intended for learning or teaching purposes. Otherwise, return 'False'.\n\nText:\n" + chunk
            )
        elif task == "topics":
            content = (
                "Extract 3 key topics from the following educational text."
                "Each topic should be a one-word summary of a major theme (e.g., 'recursion', 'loops', 'variables'). Return them as a comma-separated list.\n\nText:\n" + chunk
            )
        elif task == "difficulty":
            content = (
                "Extract 3 key topics from the following educational text."
                "Each topic should be a one-word summary of a major theme (e.g., 'recursion', 'loops', 'variables')."
                "Return them as a comma-separated list.\n\nText:\n" + chunk

            )
        else:
            raise ValueError(f"Unknown task type: {task}")

        messages = [{"role": "user", "content": content}]
        return self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=enable_thinking
        )

    def parse_with_model(self, dom_chunks, task, thinking_mode=True):
        """
        Parses text chunks using the Qwen3 model to extract educational content.

        Args:
            dom_chunks (list): List of text chunks to process.
            task (str): Which prompt to use.
            thinking_mode (bool): Enable Qwen’s thinking mode.

        Returns:
            str: Parsed results joined by double newlines.
        """
        parsed_results = []

        for i, chunk in enumerate(dom_chunks, start=1):
            formatted_prompt = self.format_prompt(chunk, task, thinking_mode)
            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.model.device)

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=500,
                do_sample=True,
                temperature=0.6 if thinking_mode else 0.7,
                top_p=0.95 if thinking_mode else 0.8,
                pad_token_id=self.tokenizer.eos_token_id
            )

            output_ids = outputs[0][len(inputs.input_ids[0]):]
            decoded = self.tokenizer.decode(output_ids, skip_special_tokens=True)

            if thinking_mode:
                # Remove all content between <think> tags including the tags themselves
                decoded = re.sub(r'<think>.*?</think>', '', decoded, flags=re.DOTALL).strip()
                # Also handle cases where closing tag might be missing
                decoded = re.sub(r'<think>.*', '', decoded, flags=re.DOTALL).strip()

            parsed_results.append(decoded)
            print(f"Parsed chunk {i}/{len(dom_chunks)}")

        return "\n\n".join(parsed_results)