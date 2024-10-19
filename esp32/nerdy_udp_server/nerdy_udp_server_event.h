#ifndef NERDY_UDP_SERVER_EVENT_EVENT_H
#define NERDY_UDP_SERVER_EVENT_EVENT_H

#include "esp_event.h"

extern esp_event_base_t NERDY_UDP_SERVER_EVENT; 

enum {
    NERDY_UDP_SERVER_EVENT_ERROR,
    NERDY_UDP_SERVER_EVENT_MESSAGE
};

#endif
