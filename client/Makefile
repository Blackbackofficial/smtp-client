CC = gcc
CFLAGS = -Wall -Werror -std=gnu99 -ggdb3
LDFLAGS=-lresolv  -lrt

INC = -I include -I ../common/include
CMD_DIR = cmd
OBJ_DIR = build
LIB = -lconfig -lresolv
TARGET = smtp_client

CMD = client.c scheduler.c domain_proc.c mx_utils.c smtp_client.c msg.c log.c client-fsm.c ../../common/cmd/string_utils.c ../../common/cmd/dir_utils.c
OBJECTS = $(patsubst %.o,$(OBJ_DIR)/%.o, $(CMD:.c=.o))

all: client

client: $(OBJECTS)
	$(CC) $(LDFLAGS) -o $(TARGET) $(OBJECTS) $(LIB)

$(OBJECTS): $(OBJ_DIR)/%.o : $(CMD_DIR)/%.c
	mkdir -p $(OBJ_DIR)
	$(CC) -lrt -c -o $@ $< $(CFLAGS) -I $(INC) $(LIB)

clean:
	rm -f $(OBJECTS) $(TARGET)

.PHONY: client clean
