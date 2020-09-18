CC=gcc
CFLAGS=

client: client.c
	     $(CC) client.c -o client $(CFLAGS)
