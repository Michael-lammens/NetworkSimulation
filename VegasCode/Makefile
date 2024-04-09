.PHONY: all clean

CC = gcc
CFLAGS = -g
CPPFLAGS = -std=gnu99 -Wall -pedantic -Wextra

Targets = emulate client server

all: ${Targets}


#Emulate
emulate: emulate.o liblist.a
	${CC} ${CFLAGS} -o emulate emulate.o -L./ -llist -lm

emulate.o: emulator.c protocol.h
	${CC} ${CFLAGS} ${CPPFLAGS} -I. -c emulator.c -o emulate.o

client: client.o liblist.a
	${CC} ${CFLAGS} -o client client.o -L./ -llist -lm
client.o: client.c
	${CC} ${CFLAGS} ${CPPFLAGS} -I. -c client.c -o client.o
server: server.o
	${CC} ${CFLAGS} -o server server.o -lm
server.o: server.c protocol.h
	${CC} ${CFLAGS} ${CPPFLAGS} -I. -c server.c -o server.o


# list
liblist.a: list_adders.o list_removers.o list_movers.o
	ar -r -c -s liblist.a list_adders.o list_removers.o list_movers.o

list_adders.o: list_adders.c list.h
	${CC} ${CFLAGS} ${CPPFLAGS} -I. -c list_adders.c -o list_adders.o

list_removers.o: list_removers.c list.h
	${CC} ${CFLAGS} ${CPPFLAGS} -I. -c list_removers.c -o list_removers.o

list_movers.o: list_movers.c list.h
	${CC} ${CPPFLAGS} ${CFLAGS} -I. -c list_movers.c -o list_movers.o

clean:
	rm -f emulate server client *.o *.a

