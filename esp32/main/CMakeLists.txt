idf_component_register(
    SRCS "app_main.c"
    REQUIRES nvs_flash esp_event driver nerdy_wifi nerdy_mac_address nerdy_udp_server
    INCLUDE_DIRS "."
)
