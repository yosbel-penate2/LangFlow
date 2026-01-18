from pydantic.v1 import SecretStr
from typing_extensions import override

from lfx.base.models.model import LCModelComponent
from lfx.field_typing import LanguageModel
from lfx.field_typing.range_spec import RangeSpec
from lfx.inputs.inputs import (
    IntInput,
    DictInput,
    DropdownInput,
    SecretStrInput,
    SliderInput,
    BoolInput,

)

GIGACHAT_MODELS = [
    "GigaChat",
    "GigaChat-Pro",
    "GigaChat-Max",
]

class GigaChatModelComponent(LCModelComponent):
    display_name = "GigaChat"
    description = "Generate text using GigaChat LLMs."
    icon = "MessageSquare"

    inputs = [
        *LCModelComponent.get_base_inputs(),
        DropdownInput(
            name="model_name",
            display_name="Model Name",
            options=GIGACHAT_MODELS,
            value="GigaChat",
            refresh_button=False,
        ),
        SecretStrInput(
            name="credentials",
            display_name="GigaChat Credentials",
            info="Authorization key from GigaChat API",
            required=True,
        ),
        SliderInput(
            name="temperature",
            display_name="Temperature",
            value=0.7,
            range_spec=RangeSpec(min=0, max=2, step=0.01),
            advanced=True,
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            value=1024,
            range_spec=RangeSpec(min=0, max=32768),
            advanced=True,
        ),
        DictInput(
            name="model_kwargs",
            display_name="Model Kwargs",
            advanced=True,
        ),
        BoolInput(
            name="verify_ssl_certs",
            display_name="Verify SSL Certificates",
            value=False,
            advanced=True,
        )
    ]

    def build_model(self) -> LanguageModel:
        try:
            from langchain_gigachat.chat_models import GigaChat
        except ImportError as e:
            msg = (
                "langchain-gigachat not installed. "
                "Install with `pip install langchain-gigachat`"
            )
            raise ImportError(msg) from e

        credentials = (
            SecretStr(self.credentials).get_secret_value()
            if self.credentials
            else None
        )

        return GigaChat(
            credentials=credentials,
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens or None,
            verify_ssl_certs=self.verify_ssl_certs,
            **(self.model_kwargs or {}),
        )

    @override
    def _get_exception_message(self, e: Exception):
        return str(e)
