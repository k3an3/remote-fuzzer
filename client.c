#include <stdint.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define SERVER_PORT 1337

#pragma pack(1)
struct Packet {
    uint8_t header[4];
    uint64_t test_run;
    uint8_t signal;
};
#pragma pack(0)

uint32_t run_program(uint8_t* args[]) {
    pid_t child;
    uint32_t status;

    if (!(child = fork()) > 0) {
        execv(args[0], (char* const*)args+1);
        exit(EXIT_SUCCESS);
    } else if (child == -1) {
        perror("Couldn't fork");
        exit(EXIT_FAILURE);
    }
    waitpid(child, &status, 0);
    return status;
}

uint32_t main(uint32_t argc, uint8_t* argv[]) {
    struct Packet packet;
    uint16_t server_port;
    char *server_host, *env_port, *env_run;

    if (argc < 2) {
        printf("Usage: %s program_to_fuzz program_args\n", argv[0]);
        return 0;
    }

    if (!(server_host = getenv("SERVER_HOST"))) {
        puts("Error: Specify SERVER_HOST environment variable.");
        return 1;
    }

    if ((env_port = getenv("SERVER_PORT")) != NULL) {
        server_port = atoi(env_port);
    } else {
        server_port = SERVER_PORT;
    }

    if ((env_run = getenv("TEST_RUN")) != NULL) {
        packet.test_run = atoll(env_run);
    } else {
        puts("Didn't find TEST_RUN environment variable, or it wasn't a valid integer.");
        return 1;
    }

    packet.signal = run_program(argv+1);
    memcpy(packet.header, "FUZZ", 4);

    struct sockaddr_in serv_addr = {};
    uint32_t sock;

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr(server_host);
    serv_addr.sin_port = htons(server_port);

    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(struct sockaddr)) == -1) {
        perror("Connect failed");
        return 1;
    }

    if (!send(sock, &packet, sizeof(struct Packet), 0)) {
        perror("Send failed");
        return 1;
    }

    shutdown(sock, SHUT_RDWR);
    close(sock);
}
