"""
This module is a simple interface for the OpenAI API.
It features methods to generate emotional responses and light presets using the API.
"""

import json
from textwrap import dedent
from typing import List, Literal, Union

from openai import OpenAI
from pydantic import BaseModel, Field

from prompts.analyze_weather_news import system_prompt as emotional_prompt
from prompts.create_presets import system_prompt as create_presets_prompt


class EmotionalResponses(BaseModel):
    emotional_responses: list[str]


class ColorSetting(BaseModel):
    type: Literal["color"] = "color"
    setting: str = Field(...)
    brightness: int = Field(...)


class TempSetting(BaseModel):
    type: Literal["temp"] = "temp"
    setting: int = Field(...)
    brightness: int = Field(...)


class Preset(BaseModel):
    name: str = Field(...)
    value: Union[TempSetting, List[ColorSetting]]

    def to_json(self):
        data = self.model_dump()
        if isinstance(data["value"], list):
            data["value"] = [item.model_dump() for item in self.value]
        else:
            data["value"] = self.value.model_dump()
        return json.dumps(data, ensure_ascii=False)


class LightPresetModel(BaseModel):
    presets: List[Preset] = Field(...)

    def to_json(self):
        return json.dumps(
            # pylint: disable=not-an-iterable
            [preset.model_dump() for preset in self.presets],
            ensure_ascii=False,
        )


class OpenAIInterfaceException(Exception):
    pass


class OpenAIInterflaceResponseValidationException(OpenAIInterfaceException):
    pass


class OpenAIInterface:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        # pylint: disable=too-many-function-args
        self.client = OpenAI(api_key=self.api_key)

    def get_emotional_responses(self, data: str) -> List[str]:
        """
        Generate emotional responses based on the input data.

        Args:
            data (str): The input data.

        Returns:
            List[str]: The generated emotional responses.
        """
        return self._get_message(
            emotional_prompt, data, EmotionalResponses
        ).emotional_responses

    def get_light_presets(self, data: str) -> LightPresetModel:
        """
        Generate light presets based on the input data.

        Args:
            data (str): The input data.

        Returns:
            List[Preset]: The generated light presets.
        """
        # Iterate a maximum of 3 times creating the output and validating it
        # For each iteration, the output is generated and validated
        # If the output is valid, return the presets
        # If the output is invalid after 3 iterations, catch the exception and raise a new one
        exception = None
        for _ in range(3):
            try:
                output: LightPresetModel = self._get_message(
                    create_presets_prompt, data, LightPresetModel
                )
                if self._validate_preset_output(output):
                    return output
            except OpenAIInterflaceResponseValidationException as e:
                exception = e
        raise OpenAIInterfaceException(
            f"Error generating light presets: {exception}"
        ) from exception

    def _get_message(
        self,
        system_message: str,
        user_message: str,
        response_format: type[BaseModel],
    ) -> str:
        """
        Generate a message using the OpenAI API.

        Args:
            system_message (str): The system message.
            user_message (str): The user message.

        Returns:
            str: The generated message.
        """
        try:
            completion = self.client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": dedent(system_message)},
                    {"role": "user", "content": user_message},
                ],
                response_format=response_format,
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            raise OpenAIInterfaceException(f"Error generating message: {e}") from e

    def _validate_preset_output(self, output: LightPresetModel) -> bool:
        """
        Validate the generated output using an additional GPT call.

        Args:
            output (LightPresetModel): The output to validate.

        Returns:
            bool: True if the output is valid, False otherwise.
        """
        schema = output.__class__.model_json_schema()
        schema_json = json.dumps(schema, indent=2)

        validation_prompt = f"""
        Please validate the following output against the provided JSON schema:

        OUTPUT:
        {output.model_dump_json(indent=2)}
        
        JSON SCHEMA:
        {schema_json}

        Ensure that:
        1. The output adheres to the specified schema.
          - When the type is "temp", the setting should be an integer value between 2700 and 6500.
          - When the type is "color", the setting should be a HEX value.
          - The brightness should be an integer value between 0 and 100.
        2. The content is appropriate and relevant.
        3. There are no logical inconsistencies or errors.

        Respond with 'VALID' if the output is correct, or 'INVALID' followed by a very brief explanation of only the errors.
        """
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data validation assistant.",
                    },
                    {"role": "user", "content": validation_prompt},
                ],
                temperature=0,
                max_tokens=500,
            )
            response = completion.choices[0].message.content.strip()
            if response.startswith("VALID"):
                return True
            raise OpenAIInterflaceResponseValidationException(
                f"Error validating output: {response}"
            )
        except Exception as e:
            raise OpenAIInterfaceException(f"Error validating output: {e}") from e
