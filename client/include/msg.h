#ifndef _MSG_H_
#define _MSG_H_

#include <libconfig.h>
#include "../../utils/include/dir_utils.h"

typedef struct node_t {
    char *val;
    struct node_t *next;
} node_t;

void add_first(struct node_t **head, char *val);
int remove_first(node_t **head);
int count(node_t *head);

char *read_msg_file(char *email_path);

#endif