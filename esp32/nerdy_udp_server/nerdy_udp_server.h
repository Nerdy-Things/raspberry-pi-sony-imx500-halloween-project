/**
 * Start listening to the UDP messages on a port 
 * @param port - target port. 0-65000
 * To test use:
 * socat - UDP-DATAGRAM:255.255.255.255:REPLACE_WITH_YOR_PORT,broadcast 
*/
void nerdy_udp_server_start(int port);
