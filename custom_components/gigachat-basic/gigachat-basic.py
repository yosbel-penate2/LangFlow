# from lfx.field_typing import Data
from lfx.custom.custom_component.component import Component
from lfx.io import MessageTextInput, Output
from lfx.schema.data import Data


class CustomComponent(Component):
    display_name = "Custom Component"
    description = "Use as a template to create your own component."
    documentation: str = "https://docs.langflow.org/components-custom-components"
    icon = "code"
    name = "CustomComponent"
    

    inputs = [
        MessageTextInput(
            name="input_value",
            display_name="Input Value",
            info="This is a custom component Input",
            value="Hello, World!",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(
                display_name="Output",
                name="output",
                method="build_output"
            ),
    ]

    def build_output(self) -> Data:
        from langchain_gigachat.chat_models import GigaChat
        from langchain_gigachat.chat_models import GigaChat

        giga = GigaChat(
            # Для авторизации запросов используйте ключ, полученный в проекте GigaChat API
            credentials="api-key",
            verify_ssl_certs=False,
        )
        result = giga.invoke(self.input_value)
        data = Data(value=result.content)
        self.status = data
        return data
