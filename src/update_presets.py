import json
import os

from dotenv import load_dotenv

from db.models import Lamp, Preset
from db.session import get_session
from interfaces.newsdata_interface import NewsDataInterface
from interfaces.openai_interface import OpenAIInterface
from interfaces.weather_api_interface import WeatherAPIInterface
from services.preset_service import create_preset, delete_preset


def update_presets():
    """
    Updates the presets based on weather, local and global news.

    This function can be called both programmatically and via command-line.
    It fetches weather, local news, and global news, and uses OpenAI to
    generate new lighting presets, which are then saved in the database.
    """
    load_dotenv()

    try:
        session = get_session()

        # Step 1: Clear non-persistent presets
        presets = session.query(Preset).all()
        for preset in presets:
            preset_dict = preset.to_dict()
            if not preset_dict["protected"]:
                delete_preset(preset_dict["id"])
        print("Non-persistent presets deleted successfully.")

        # Step 2: Fetch weather data
        weather_interface = WeatherAPIInterface(59.1031, 18.0446)
        weather = weather_interface.fetch_weather_data()
        print("Weather data fetched successfully.")

        # Step 3: Fetch local and global news
        newsdata_interface = NewsDataInterface(os.getenv("NEWSDATA_API_KEY"))
        newsdata_global = newsdata_interface.fetch_news_data()
        newsdata_local = newsdata_interface.fetch_news_data(
            country="se", query="Stockholm"
        )
        print("News data fetched successfully.")

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
        print("Presets fetched successfully.")

        # Step 7: Save presets to the database
        for preset in presets.presets:
            preset_json = json.loads(
                preset.to_json()
            )  # Convert JSON string back to dict
            saved_preset = create_preset(preset_json["name"], preset_json["value"])
            print(f"Preset saved: {json.dumps(saved_preset)}")

        print("Presets updated successfully.")
        session.close()

        return True
    # pylint: disable=broad-except
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    update_presets()
