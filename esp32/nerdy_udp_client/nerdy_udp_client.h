/**
 * Sends a message via UDP 
 * @param id - target IP address. Could be a 1-1 (192.168.1.2), could be a broadcast 192.168.1.255
 * @param port - target port. 0-65000
 * @param message - message to be sent. Any format. Could be plain text, could be JSON string "{\"text\":\"awesome message\"}"
*/
void nerdy_udp_client_send_message(char * ip, int port, char * message);
