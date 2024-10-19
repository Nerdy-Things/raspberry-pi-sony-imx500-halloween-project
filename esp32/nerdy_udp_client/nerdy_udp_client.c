#include <string.h>
#include <sys/param.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"

#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include <lwip/netdb.h>

static const char *TAG = "UDP";

/**
 * Sends a message via UDP 
 * @param ip - target IP address. Could be a 1-1 (192.168.1.2), could be a broadcast 192.168.1.255
 * @param port - target port. 0-65000
 * @param message - message to be sent. Any format. Could be plain text, could be JSON string "{\"text\":\"awesome message\"}"
*/
void nerdy_udp_client_send_message(char * ip, int port, char * message)
{
    // Set up parameters
    char rx_buffer[128];

    char host_ip[strlen(ip)];
    strcpy(host_ip, ip);

    int addr_family = 0;
    int ip_protocol = 0;

    struct sockaddr_in dest_addr;
    dest_addr.sin_addr.s_addr = inet_addr(ip);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(port);
    addr_family = AF_INET;
    ip_protocol = IPPROTO_IP;

    int sock = socket(addr_family, SOCK_DGRAM, ip_protocol);
    if (sock < 0) {
        ESP_LOGE(TAG, "Unable to create socket: errno %d", errno);
        return;
    }

    // Set timeout
    struct timeval timeout;
    timeout.tv_sec = 10;
    timeout.tv_usec = 0;
    setsockopt (sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof timeout);

    ESP_LOGI(TAG, "Socket created, sending to %s:%d", ip, port);

    // Send message
    int err = sendto(sock, message, strlen(message), 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (err < 0) {
        ESP_LOGE(TAG, "Error occurred during sending: errno %d", errno);
    } else {
        ESP_LOGI(TAG, "Message sent: %s", message);
    }

    // Close socket
    if (sock != -1) {
        shutdown(sock, 0);
        close(sock);
    }
}
