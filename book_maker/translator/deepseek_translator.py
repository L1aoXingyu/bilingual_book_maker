from itertools import cycle

from book_maker.translator.chatgptapi_translator import ChatGPTAPI


class DeepSeekTranslator(ChatGPTAPI):
    """
    OpenAI-compatible translator that targets the DeepSeek API.

    Defaults:
    - base_url: https://api.deepseek.com
    - models: deepseek-chat (non-thinking mode)
    """

    DEFAULT_API_BASE = "https://api.deepseek.com"
    DEFAULT_MODEL_LIST = ["deepseek-chat"]

    def __init__(
        self,
        key,
        language,
        api_base=None,
        prompt_template=None,
        prompt_sys_msg=None,
        temperature=1.0,
        context_flag=False,
        context_paragraph_limit=0,
        **kwargs,
    ):
        # DeepSeek follows the OpenAI schema; just point the OpenAI client to its base URL.
        api_base = api_base or self.DEFAULT_API_BASE
        super().__init__(
            key,
            language,
            api_base=api_base,
            prompt_template=prompt_template,
            prompt_sys_msg=prompt_sys_msg,
            temperature=temperature,
            context_flag=context_flag,
            context_paragraph_limit=context_paragraph_limit,
            **kwargs,
        )
        # Default to the chat model; can be overridden via set_model_list.
        self.model_list = cycle(self.DEFAULT_MODEL_LIST)

    def set_model_list(self, model_list):
        """Allow overriding DeepSeek model list while keeping a sensible default."""
        if not model_list:
            model_list = self.DEFAULT_MODEL_LIST
        super().set_model_list(model_list)
