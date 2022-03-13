#include "../include/msg.h"

char *read_msg_file(char *email_path) {
    FILE *fp;
    long file_size;
    char *buffer;

    fp = fopen(email_path, "r");
    if (fp == NULL) {
        printf("%s\n", strerror(errno));
//        exit(0);
        return NULL;
    }

    fseek(fp, 0L, SEEK_END);
    file_size = ftell(fp);
    rewind(fp);

    /* allocate memory for entire content */
    buffer = calloc(1, file_size + 1);
    if (!buffer) {
        fclose(fp), fputs("memory alloc fails", stderr), exit(1);
    }

    /* copy the file into the buffer */
    fread(buffer, file_size, 1, fp);

    fclose(fp);
    return buffer;
}

void add_first(struct node_t **head, char *val) {
    struct node_t *new_node = (struct node_t *)malloc(sizeof(struct node_t));
    new_node->val = malloc(strlen(val));
    strcpy(new_node->val, val);
    new_node->next = *head;
    *head = new_node;
}

int remove_first(node_t ** head) {
    node_t *next_node = NULL;
    if (*head == NULL) {
        return -1;
    }

    next_node = (*head)->next;
    free((*head)->val);
    free(*head);
    *head = next_node;
    return 1;
}

int count(node_t *head) {
    int i = -1;
    while (head != NULL) {
        head = head->next;
        i++;
    }
    return i;
}