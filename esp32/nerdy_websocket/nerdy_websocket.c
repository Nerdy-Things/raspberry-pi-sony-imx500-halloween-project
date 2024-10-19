#include "esp_websocket_client.h"
#include "nerdy_websocket_event.h"
#include "esp_log.h"

static const char *TAG_WS = "WebSocket";


void nerdy_websocket_event_handler(void* handler_args, esp_event_base_t base, int32_t event_id, void* event_data) 
{
    ESP_LOGI(TAG_WS, "Received websocket event: %s %" PRId32 " ", base, event_id);
    switch (event_id) {
        case WEBSOCKET_EVENT_CLOSED:
        case WEBSOCKET_EVENT_ERROR:
        case WEBSOCKET_EVENT_DISCONNECTED:
            ESP_LOGI(TAG_WS, "Disonnected or error");
            // gpio_set_level(RELAY_PIN, 0);
            break;
        case WEBSOCKET_EVENT_CONNECTED:
            ESP_LOGI(TAG_WS, "Connected");
            // gpio_set_level(RELAY_PIN, 0);
            break;
        case WEBSOCKET_EVENT_DATA:
            esp_websocket_event_data_t* data = (esp_websocket_event_data_t*)event_data;
            char *message = (char *)malloc(data->data_len + 1);
            if (message == NULL) {
                free(message);
                return;
            }
            memcpy(message, data->data_ptr, data->data_len);
            message[data->data_len] = '\0';
            ESP_LOGI(TAG_WS, "Received message %s len: %d", message, data->data_len);

            ESP_ERROR_CHECK(esp_event_post(
                NERDY_WEBSOCKET_EVENT, 
                NERDY_WEBSOCKET_EVENT_MESSAGE, 
                message, strlen(message), 
                portMAX_DELAY)
            );

            free(message);
            break;
        default: 
            // gpio_set_level(RELAY_PIN, 0);
            break;
    }
}

void nerdy_websocket_listen(char* host, int port) {
    ESP_LOGI(TAG_WS, "WebSockets Connect %s:%d", host, port);
    const esp_websocket_client_config_t ws_cfg = {
        .host = host,
        .port = port,
        .reconnect_timeout_ms = 10000,
        .network_timeout_ms = 10000,
    };

    esp_websocket_client_handle_t client = esp_websocket_client_init(&ws_cfg);
    esp_websocket_register_events(client, WEBSOCKET_EVENT_ANY, &nerdy_websocket_event_handler, (void*)client);
    esp_websocket_client_start(client);
}