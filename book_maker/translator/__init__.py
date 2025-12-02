from book_maker.translator.caiyun_translator import Caiyun
from book_maker.translator.chatgptapi_translator import ChatGPTAPI
from book_maker.translator.deepl_translator import DeepL
from book_maker.translator.deepl_free_translator import DeepLFree
from book_maker.translator.google_translator import Google
from book_maker.translator.claude_translator import Claude
from book_maker.translator.deepseek_translator import DeepSeekTranslator
from book_maker.translator.gemini_translator import Gemini
from book_maker.translator.groq_translator import GroqClient
from book_maker.translator.tencent_transmart_translator import TencentTranSmart
from book_maker.translator.custom_api_translator import CustomAPI
from book_maker.translator.xai_translator import XAIClient
from book_maker.translator.qwen_translator import QwenTranslator
from book_maker.translator.claude_code_translator import ClaudeCodeTranslator

MODEL_DICT = {
    "openai": ChatGPTAPI,
    "chatgptapi": ChatGPTAPI,
    "gpt4": ChatGPTAPI,
    "gpt4omini": ChatGPTAPI,
    "gpt4o": ChatGPTAPI,
    "o1preview": ChatGPTAPI,
    "o1": ChatGPTAPI,
    "o1mini": ChatGPTAPI,
    "o3mini": ChatGPTAPI,
    "google": Google,
    "caiyun": Caiyun,
    "deepl": DeepL,
    "deeplfree": DeepLFree,
    "claude": Claude,
    "claude-3-5-sonnet-latest": Claude,
    "claude-3-5-sonnet-20241022": Claude,
    "claude-3-5-sonnet-20240620": Claude,
    "claude-3-5-haiku-latest": Claude,
    "claude-3-5-haiku-20241022": Claude,
    "gemini": Gemini,
    "geminipro": Gemini,
    "groq": GroqClient,
    "tencentransmart": TencentTranSmart,
    "customapi": CustomAPI,
    "xai": XAIClient,
    "qwen": QwenTranslator,
    "qwen-mt-turbo": QwenTranslator,
    "qwen-mt-plus": QwenTranslator,
    "claude-code": ClaudeCodeTranslator,
    "claude-code-sonnet": ClaudeCodeTranslator,
    "claude-code-opus": ClaudeCodeTranslator,
    "glm-4.5": ClaudeCodeTranslator,
    "glm": ClaudeCodeTranslator,
    "deepseek": DeepSeekTranslator,
    "deepseek-chat": DeepSeekTranslator,
    "deepseek-reasoner": DeepSeekTranslator,
    # add more here
}
