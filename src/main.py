"""
Main module for the application.
"""

from fasthtml.common import *
from db.session import seed_db
from services.preset_service import get_all_presets, get_preset_by_id

seed_db()
app, rt = fast_app()


@rt("/")
def get():
    """
    Main page route.
    """
    presets = get_all_presets()

    return Div(
        H1("Luminasync"),
        P("Welcome to Luminasync, a light control application."),
        PresetList(presets),
        id="preset-list",
    )


def PresetList(presets):
    return Div(
        *map(PresetButton, presets),
        _class="preset-list",
    )


def PresetButton(preset):
    return Div(
        Button(
            preset["name"],
            hx_post=f'/apply-preset/{preset["id"]}',
            _class="preset-btn",
        ),
        P(f"Setting: {preset['value']}"),
        _class="preset-item",
    )


@rt("/apply-preset/<preset_id>", methods=["POST"])
def post(preset_id):
    """
    Route to apply a preset to a lamp.
    """
    preset = get_preset_by_id(preset_id)  # Fetch the preset by id
    if preset:
        # Apply the preset to the lamp, for example
        return f'Applied preset: {preset["name"]} with settings {preset["value"]}'
    return "Preset not found", 404


serve()
