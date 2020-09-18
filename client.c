#include <stdint.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdlib.h>

#define SERVER_PORT 1337

struct Packet {
    uint8_t header[4];
    uint64_t test_run;
    uint8_t signal;
};

int main(uint32_t argc, uint8_t* argv[]) {
    uint8_t* server_host;
    uint16_t server_port;

    if (argc < 2) {
        printf("Usage: %s program_to_fuzz program_args\n", argv[0]);
        return 0;
    }

    if (!(server_host = getenv("SERVER_HOST"))) {
        puts("Error: Specify SERVER_HOST environment variable.");
    }

    if (!(server_port = atoi(getenv("SERVER_PORT")))) {
        server_port = SERVER_PORT;
    }


    struct sockaddr_in serv_addr;
    uint32_t sock;

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr(argv[2]);
    serv_addr.sin_port = htons(server_port);

    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(struct sockaddr)) == -1) {
        perror("Connect failed");
        exit(1);
    }
}
