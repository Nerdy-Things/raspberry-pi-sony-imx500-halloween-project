idf_component_register(
    SRCS "nerdy_wifi.c" "nerdy_wifi_config.c"
    REQUIRES esp_wifi nvs_flash
    INCLUDE_DIRS "."
)
