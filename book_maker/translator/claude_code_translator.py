import re
import json
import asyncio
from typing import Optional, List, Dict, Any
from rich import print

from .base_translator import Base

try:
    from claude_code_sdk import query, ClaudeCodeOptions, ClaudeSDKClient
    HAS_CLAUDE_CODE_SDK = True
except ImportError:
    HAS_CLAUDE_CODE_SDK = False


class ClaudeCodeTranslator(Base):
    """
    Claude Code SDK based translator with agentic capabilities.
    Falls back to regular Claude translator if SDK is not available.
    """
    
    def __init__(
        self,
        key,
        language,
        api_base=None,
        prompt_template=None,
        prompt_sys_msg=None,
        temperature=1.0,
        context_flag=False,
        context_paragraph_limit=5,
        agentic=False,
        agentic_options=None,
        **kwargs,
    ) -> None:
        # Claude Code SDK doesn't need API key, but we still need to accept it for compatibility
        super().__init__(key or "not-needed", language)
        
        self.language = language
        self.api_key = key  # May be None for Claude Code SDK
        self.api_base = api_base
        self.agentic = agentic
        self.agentic_options = agentic_options or {}
        
        # Check if agentic mode is requested but SDK is missing
        if self.agentic and not HAS_CLAUDE_CODE_SDK:
            raise ImportError(
                "Claude Code SDK is not installed. Please install it with:\n"
                "pip install bbook-maker[agentic] or pip install claude-code-sdk"
            )
        
        # If not agentic or SDK missing, fall back to regular Claude
        # Regular Claude DOES need an API key
        if not self.agentic or not HAS_CLAUDE_CODE_SDK:
            if not key:
                raise ValueError(
                    "API key is required for regular Claude mode. "
                    "Use --claude_key or set BBM_CLAUDE_API_KEY environment variable."
                )
            from .claude_translator import Claude
            self._fallback = Claude(
                key=key,
                language=language,
                api_base=api_base,
                prompt_template=prompt_template,
                prompt_sys_msg=prompt_sys_msg,
                temperature=temperature,
                context_flag=context_flag,
                context_paragraph_limit=context_paragraph_limit,
                **kwargs
            )
        else:
            self._fallback = None
        
        # Translation settings
        self.prompt_template = (
            prompt_template
            or "Translate the following text into {language}. Provide ONLY the translation without any additional text or explanation:\n\n{text}"
        )
        self.prompt_sys_msg = prompt_sys_msg or "You are a professional translator. Always provide only the translation without any additional commentary or explanations."
        self.temperature = temperature
        
        # Context management (compatible with existing translators)
        self.context_flag = context_flag
        self.context_list = []
        self.context_translated_list = []
        self.context_paragraph_limit = context_paragraph_limit
        
        # Default agentic options
        self.default_agentic_options = {
            "max_turns": 1,
            "allowed_tools": ["Read"],  # Safe default: only local file reading
            "permission_mode": "default",
        }
        
        # Merge user options with defaults
        self.sdk_options = {**self.default_agentic_options, **self.agentic_options}
        
        # Set model based on the chosen variant
        if 'model' not in self.sdk_options:
            self.sdk_options['model'] = 'glm-4.5'  # Default to GLM4.5 model

    def rotate_key(self):
        """Rotate API keys if multiple are provided"""
        pass

    def create_context_messages(self):
        """Create context from previous translations (compatible with existing pattern)"""
        if not self.context_flag or not self.context_list:
            return ""
        
        context = "Previous context:\n"
        for orig, trans in zip(self.context_list, self.context_translated_list):
            context += f"Original: {orig}\nTranslation: {trans}\n\n"
        return context

    def save_context(self, text, t_text):
        """Save translation pair to context"""
        if not self.context_flag:
            return
        
        self.context_list.append(text)
        self.context_translated_list.append(t_text)
        
        # Keep only recent paragraphs within limit
        if len(self.context_list) > self.context_paragraph_limit:
            self.context_list.pop(0)
            self.context_translated_list.pop(0)

    def _sync_wrapper(self, coro):
        """
        Safely run async code in sync context.
        Handles cases where event loop might already be running.
        """
        try:
            loop = asyncio.get_running_loop()
            # If we're in a running loop, we need a different approach
            # This is a simplified version - in production you might use anyio or nest_asyncio
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        except RuntimeError:
            # No running loop, we can use asyncio.run directly
            return asyncio.run(coro)

    async def _agentic_translate(self, text):
        """Perform translation using Claude Code SDK"""
        # Build the full prompt with context if available
        context = self.create_context_messages()
        full_prompt = ""
        
        if self.prompt_sys_msg:
            full_prompt = f"System: {self.prompt_sys_msg}\n\n"
        
        if context:
            full_prompt += f"{context}\n"
        
        full_prompt += self.prompt_template.format(
            text=text,
            language=self.language
        )
        
        # Create SDK options
        options = ClaudeCodeOptions(**self.sdk_options)
        
        # Configure environment variables for BigModel.cn if not already set
        import os
        if not os.getenv('ANTHROPIC_BASE_URL'):
            os.environ['ANTHROPIC_BASE_URL'] = 'https://open.bigmodel.cn/api/anthropic'
        if not os.getenv('ANTHROPIC_MODEL'):
            os.environ['ANTHROPIC_MODEL'] = 'glm-4.5'
        
        # Perform the translation
        response_text = ""
        async for message in query(prompt=full_prompt, options=options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_text += block.text
        
        return response_text.strip()

    def translate(self, text):
        """Main translation method"""
        print(text)
        self.rotate_key()
        
        # Use fallback if not in agentic mode
        if self._fallback:
            return self._fallback.translate(text)
        
        # Use agentic translation
        t_text = self._sync_wrapper(self._agentic_translate(text))
        
        if self.context_flag:
            self.save_context(text, t_text)
        
        print("[bold green]" + re.sub("\n{3,}", "\n\n", t_text) + "[/bold green]")
        return t_text

    def translate_list(self, text_list):
        """
        Batch translation method for EPUBs with --accumulated_num support.
        This is optional but improves performance for batch processing.
        """
        if self._fallback and hasattr(self._fallback, 'translate_list'):
            return self._fallback.translate_list(text_list)
        
        # Simple implementation: translate each item separately
        # A more sophisticated version could batch these in a single prompt
        translated_list = []
        for text in text_list:
            if text.strip():  # Skip empty strings
                translated_list.append(self.translate(text))
            else:
                translated_list.append("")
        
        return translated_list

    def set_claude_model(self, model_name):
        """Set specific Claude model"""
        if self._fallback and hasattr(self._fallback, 'set_claude_model'):
            self._fallback.set_claude_model(model_name)
        else:
            # Map model names to SDK models
            model_mapping = {
                "claude-code-sonnet": "claude-3-5-sonnet-20241022",
                "claude-code-opus": "claude-opus-4-20250514",
                "claude-code": "claude-3-5-sonnet-20241022",  # Default
                "glm-4.5": "glm-4.5",  # GLM4.5 model
                "glm": "glm-4.5",  # Short alias for GLM4.5
            }
            self.sdk_options['model'] = model_mapping.get(model_name, model_name)