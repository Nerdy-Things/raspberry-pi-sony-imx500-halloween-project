idf_component_register(
    SRCS "nerdy_websocket.c" "nerdy_websocket_event.c"
    REQUIRES esp_websocket_client esp_event
    INCLUDE_DIRS "."
)
