CC = gcc
CFLAGS = -Wall -Werror -std=gnu99 -ggdb3
LDFLAGS= -lresolv  -lrt -lcunit

CMD_DIR = cmd
OBJ_DIR = build
LIB = -lconfig -lresolv -lcunit
TARGET = smtp_client_test

CMD = smtp_client_test.c ../../../cmd/smtp_client.c ../../../cmd/msg.c ../../../cmd/mx_utils.c ../../../cmd/log.c ../../../../common/src/string_utils.c
OBJECTS = $(patsubst %.o,$(OBJ_DIR)/%.o, $(CMD:.c=.o))

all: tests

tests: $(OBJECTS)
	$(CC) $(LDFLAGS) -o $(TARGET) $(OBJECTS) $(LIB)

$(OBJECTS): $(OBJ_DIR)/%.o : $(CMD_DIR)/%.c
	mkdir -p $(OBJ_DIR)
	$(CC) -c -o $@ $< $(CFLAGS) -I $(INC) $(LIB)

clean:
	rm -f $(OBJECTS) $(TARGET)

.PHONY: tests clean
