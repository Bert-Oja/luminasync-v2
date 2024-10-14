"""
This module is a simple interface for the OpenAI API.
It features methods to generate emotional responses and light presets using the API.
"""

import json
from textwrap import dedent
from typing import List, Literal, Optional

from openai import OpenAI
from pydantic import BaseModel, Field

from logging_config import get_logger
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
    type: Literal["color", "temp"] = Field(..., description="Type of the preset")
    name: str = Field(..., description="Name of the preset")
    # Optional fields for color and temp presets
    value_color: Optional[List[ColorSetting]] = Field(
        None, description="List of color settings"
    )
    value_temp: Optional[TempSetting] = Field(None, description="Temperature setting")


class LightPresetModel(BaseModel):
    presets: List[Preset]


class ValidationModel(BaseModel):
    validation: Literal["VALID", "INVALID"] = Field(...)
    explanation: str = Field(...)


class OpenAIInterfaceException(Exception):
    pass


class OpenAIInterflaceResponseValidationException(OpenAIInterfaceException):
    pass


class OpenAIInterface:
    def __init__(self, api_key: str) -> None:
        self.logger = get_logger(self.__class__)
        self.api_key = api_key
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
                    self.logger.info("Light presets generated successfully.")
                    self.logger.debug(output)
                    return output
            except OpenAIInterfaceException as e:
                self.logger.error(e)
                exception = e
        raise OpenAIInterfaceException(
            f"Error generating light presets: {exception}"
        ) from exception

    def _get_message(
        self,
        system_message: str,
        user_message: str,
        response_format: type[BaseModel],
        model: str = "gpt-4o",
    ) -> BaseModel:
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
                model=model,
                messages=[
                    {"role": "system", "content": dedent(system_message)},
                    {"role": "user", "content": dedent(user_message)},
                ],
                response_format=response_format,
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            self.logger.error(f"Error generating message: {e}")
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
        You are a data validation assistant.
        Your task is to validate the output of a light preset generation model.

        You will be given the output of the model that you validate against a JSON schema specified below.

        JSON SCHEMA:
        {schema_json}

        Follow these steps carefully before providing a final answer:
        1. Internally review the output in detail and validate whether it fully adheres to the specified schema:
        - When the type is "temp", the setting should be an integer value between 2700 and 6500.
        - When the type is "color", the setting should be a HEX value.
        - The brightness should be an integer value between 0 and 100.
        2. Make sure there are no contradictions or logical errors in the output. Each evaluation should result in a clear, consistent conclusion.
        3. Consider all validation rules before formulating an answer to ensure there are no conflicting assessments.
        4. Double-check the conclusions and explanations for consistency and accuracy before providing a response.
        5. Only respond once you are certain of the final assessment.

        Your output should either be 'VALID' or 'INVALID' followed by a clear, concise explanation of the issues. 
        Ensure that your explanation is logically sound and free from contradictions. If the output is correct, do not list any errors.
        """

        try:
            response: ValidationModel = self._get_message(
                validation_prompt,
                output.model_dump_json(indent=2),
                ValidationModel,
                model="gpt-4o-mini",
            )
            if response.validation == "VALID":
                return True
            raise OpenAIInterflaceResponseValidationException(response)
        except (Exception, OpenAIInterflaceResponseValidationException) as e:
            raise OpenAIInterfaceException(f"Error validating output: {e}") from e
