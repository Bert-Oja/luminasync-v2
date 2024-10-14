# main.py
"""Main module for the application."""

# Standard library imports
import json
import logging
import os
from functools import cache
from typing import Any

# Third-party imports
from fasthtml.common import (
    A,
    Body,
    Button,
    Div,
    FastHTML,
    Head,
    Html,
    I,
    Img,
    JSONResponse,
    Li,
    Link,
    Meta,
    Nav,
    Request,
    Script,
    Span,
    Title,
    Ul,
    serve,
)
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

# Local application imports
from db.models import Lamp, Preset
from db.session import get_session, seed_db
from logging_config import setup_logging
from services.preset_service import apply_preset, turn_off_bulbs
from update_presets import update_presets

# Set up logging
setup_logging()
logger = logging.getLogger("LuminaSync")

# Seed the database
seed_db()

# Set up the FastHTML app with some basic configuration
# All CSS is defined by MaterializeCSS
materialize_fonts_link = Link(
    href="https://fonts.googleapis.com/icon?family=Material+Icons", rel="stylesheet"
)
materialize_css_link = Link(
    href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css",
    rel="stylesheet",
)
materialize_js = Script(
    src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"
)

custom_css = Link(href="public/css/main.css", rel="stylesheet")
custom_js = Script(src="public/js/main.js")
favicon = Link(href="public/favicon.ico", rel="icon")
manifest = Link(href="manifest.webmanifest", rel="manifest")


@cache
def get_html_headers():
    return (
        Title("LuminaSync"),
        materialize_fonts_link,
        materialize_css_link,
        materialize_js,
        custom_css,
        custom_js,
        favicon,
        manifest,
        Meta(charset="UTF-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
    )


app = FastHTML(default_hdrs=False)
rt = app.route
# Mount the static files directory using Starlette
app.mount("/public", StaticFiles(directory="public"), name="public")


def wrap_content_in_html(content: Any) -> Any:
    """Wrap the content in an HTML document."""
    return Html(Head(*get_html_headers()), Body(content))


@cache
def header_content():
    return Div(
        Nav(
            Div(
                A(
                    Img(
                        src="public/logo192.png",
                        alt="Logo",
                        style="height: auto; max-height: 100%; padding: 0; vertical-align: middle;",
                    ),
                    Span(
                        "LuminaSync",
                        style="vertical-align: middle; padding-left: 10px;",
                    ),
                    href="#",
                    cls="brand-logo left",
                    style="display: flex; align-items: center; height: 100%;",
                ),
                Ul(
                    Li(
                        A(
                            I("power_settings_new", cls="material-icons"),
                            href="#",
                            id="nav-turn-off",
                        ),
                    ),
                    Li(
                        A(
                            I("refresh", cls="material-icons"),
                            href="#",
                            id="nav-update-presets",
                        ),
                    ),
                    id="side-nav",
                    cls="right",
                ),
                cls="nav-wrapper",
            )
        ),
    )


@rt("/service-worker.js")
async def serve_service_worker():
    return FileResponse("public/service-worker.js", media_type="application/javascript")


@rt("/manifest.webmanifest")
async def serve_manifest():
    return FileResponse(
        "public/manifest.webmanifest", media_type="application/manifest+json"
    )


# Define the main route
@rt("/")
async def get():
    try:
        session = get_session()
        presets = session.query(Preset).all()
        logger.debug(f"Presets: {presets}")
        lamps = session.query(Lamp).all()
        session.close()

        preset_buttons = [
            Div(
                Button(
                    preset.name,
                    cls="waves-effect waves-dark btn-large preset-button",
                    id=f"preset-{preset.id}",
                    value=str(preset.id),
                ),
                cls="col s12 center-align",
            )
            for preset in presets
        ]

        lamp_icons = [
            I(
                "lightbulb",
                cls="medium material-icons lamp-icon",
                # If the lamp.state is "Off", the color should be set to black with an opacity of 0
                style=f"color: {lamp.hex if lamp.state == 'On' else 'rgba(0, 0, 0, 0)'}; opacity: {lamp.brightness if lamp.state == 'On' else 0};",
                id=f"lamp-{lamp.id}",
            )
            for lamp in lamps
        ]

        return wrap_content_in_html(
            (
                # Loader Div
                Div(
                    Div(
                        Div(
                            Div(Div(cls="circle"), cls="circle-clipper left"),
                            Div(Div(cls="circle"), cls="gap-patch"),
                            Div(Div(cls="circle"), cls="circle-clipper right"),
                            cls="spinner-layer spinner-blue-only",
                        ),
                        cls="preloader-wrapper big active",
                    ),
                    id="loader",
                    cls="loader-container",
                ),
                header_content(),
                Div(
                    Div(
                        *[
                            Div(
                                lamp_icon,
                                cls=f"col s{12 // len(lamp_icons)} center-align",
                            )
                            for lamp_icon in lamp_icons
                        ],
                        cls="row",
                        style="margin-top: 20px;",
                    ),
                    Div(
                        *preset_buttons,
                        cls="button-container",
                    ),
                    cls="container",
                ),
            )
        )
    except Exception:
        logger.exception("An unexpected error occurred in the root route.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


@rt("/apply", methods=["post"])
async def apply(request: Request):
    try:
        session = get_session()
        data = await request.json()
        logger.debug(f"Received JSON data: {data}")

        preset_id = data.get("preset_id")
        preset = session.query(Preset).filter_by(id=preset_id).first()
        lamps = session.query(Lamp).all()
        session.close()

        if preset is None:
            logger.warning(f"Preset with ID {preset_id} not found.")
            return JSONResponse(
                {
                    "success": False,
                    "message": "Preset not found.",
                },
                status_code=HTTP_404_NOT_FOUND,
            )

        # Fetch the preset value, parse it into a dict or list of dicts
        try:
            lamp_settings = apply_preset(preset.value, lamps)

            return JSONResponse(
                {
                    "success": True,
                    "message": "Preset applied successfully.",
                    "lamp_data": lamp_settings,
                },
                status_code=HTTP_200_OK,
            )
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding preset value: {e}")
            return JSONResponse(
                {
                    "success": False,
                    "message": "Error decoding preset value.",
                },
                status_code=HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("An error occurred while applying the preset.")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while applying the preset.",
            )
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON received: {e}")
        return JSONResponse(
            {
                "success": False,
                "message": "Invalid JSON received.",
            },
            status_code=HTTP_400_BAD_REQUEST,
        )
    except Exception:
        logger.exception("An unexpected error occurred in the apply route.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


@rt("/turn-off", methods=["post"])
async def turn_off():
    try:
        turn_off_bulbs()
        return JSONResponse(
            {
                "success": True,
                "message": "All bulbs turned off successfully.",
            },
            status_code=HTTP_200_OK,
        )
    except Exception:
        logger.exception("An error occurred while turning off the bulbs.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while turning off the bulbs.",
        )


@rt("/update-presets", methods=["post"])
async def update():
    try:
        update_presets()
        return JSONResponse(
            {
                "success": True,
                "message": "Presets updated successfully.",
            },
            status_code=HTTP_200_OK,
        )
    except Exception:
        logger.exception("An error occurred while updating presets.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating presets.",
        )


if __name__ == "__main__":
    SHOULD_RELOAD = True if "DEBUG" in os.environ else False
    serve(port=5173, reload=SHOULD_RELOAD)
