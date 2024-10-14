import json
import logging
import os

from dotenv import load_dotenv

from db.models import Lamp, Preset
from db.session import get_session
from interfaces.newsdata_interface import NewsDataInterface
from interfaces.openai_interface import OpenAIInterface
from interfaces.weather_api_interface import WeatherAPIInterface
from services.preset_service import create_preset, delete_preset

logger = logging.getLogger("LuminaSync")


def update_presets():
    """
    Updates the presets based on weather, local and global news.

    This function can be called both programmatically and via command-line.
    It fetches weather, local news, and global news, and uses OpenAI to
    generate new lighting presets, which are then saved in the database.
    """
    load_dotenv()

    session = get_session()
    try:
        # Step 1: Clear non-persistent presets

        # Step 2: Fetch weather data
        weather_interface = WeatherAPIInterface(59.1031, 18.0446)
        weather = weather_interface.fetch_weather_data()
        logger.info("Weather data fetched successfully.")

        # Step 3: Fetch local and global news
        newsdata_interface = NewsDataInterface(os.getenv("NEWSDATA_API_KEY"))
        newsdata_global = newsdata_interface.fetch_news_data()
        newsdata_local = newsdata_interface.fetch_news_data(
            country="se", query="Stockholm"
        )
        logger.info("News data fetched successfully.")

        # Step 4: Prepare data and get emotional responses from OpenAI
        data = {
            "weather": weather,
            "local_news": newsdata_local,
            "global_news": newsdata_global,
        }
        openai_interface = OpenAIInterface(os.getenv("OPENAI_API_KEY"))
        emotional_responses = openai_interface.get_emotional_responses(json.dumps(data))

        # Step 5: Create input for the OpenAI preset prompt
        preset_input = {
            "lamp_count": len(session.query(Lamp).all()),
            "descriptions": emotional_responses,
        }

        # Step 6: Fetch presets from OpenAI
        presets = openai_interface.get_light_presets(json.dumps(preset_input))
        logger.info("Presets fetched successfully.")

        old_presets = session.query(Preset).all()
        for old_preset in old_presets:
            preset_dict = old_preset.to_dict()
            if not preset_dict["protected"]:
                delete_preset(preset_dict["id"])
        logger.info("Non-persistent presets deleted successfully.")

        # Step 7: Save presets to the database
        logger.debug(f"Presets: {presets.model_dump_json()}")

        for preset in presets.presets:
            preset_data = preset.model_dump()

            # Determine which value field is populated based on the type
            if preset_data["type"] == "color":
                value = preset_data.get("value_color")
            elif preset_data["type"] == "temp":
                value = preset_data.get("value_temp")
            else:
                logger.error(f"Unknown preset type: {preset_data['type']}")
                continue  # Skip unknown types

            # Save to the database
            saved_preset = create_preset(preset_data["name"], value)
            logger.info(f"Preset saved: {json.dumps(saved_preset)}")

        logger.info("Presets updated successfully.")
        session.close()

        return True
    except Exception as e:
        session.rollback()
        logger.error(f"An error occurred: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    update_presets()
