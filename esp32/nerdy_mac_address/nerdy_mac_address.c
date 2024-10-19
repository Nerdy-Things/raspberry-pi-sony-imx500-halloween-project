
#include <stdlib.h>
#include <string.h>
#include "esp_log.h"
#include "esp_mac.h"

#define TAG "MAC"

char * nerdy_get_mac_address(void)
{
    uint8_t base_mac_addr[6] = {0};
    esp_err_t ret = ESP_OK;
    char * mac_address;
    //Get base MAC address from EFUSE BLK0(default option)
    ret = esp_read_mac(base_mac_addr, ESP_MAC_EFUSE_FACTORY);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to get base MAC address from EFUSE BLK0. (%s)", esp_err_to_name(ret));
        ESP_LOGE(TAG, "Aborting");
        abort();
    } else {
        ESP_LOGI(TAG, "Base MAC Address read from EFUSE BLK0");
    }

    //Set the base MAC address using the retrieved MAC address
    ESP_LOGI(TAG, "Using \"0x%x, 0x%x, 0x%x, 0x%x, 0x%x, 0x%x\" as base MAC address",
             base_mac_addr[0], base_mac_addr[1], base_mac_addr[2], base_mac_addr[3], base_mac_addr[4], base_mac_addr[5]);
    esp_iface_mac_addr_set(base_mac_addr, ESP_MAC_BASE);

    char *string;
    asprintf(&string, "0x%x:0x%x:0x%x:0x%x:0x%x:0x%x", base_mac_addr[0], base_mac_addr[1], base_mac_addr[2], base_mac_addr[3], base_mac_addr[4], base_mac_addr[5]);
    return string;             
}
