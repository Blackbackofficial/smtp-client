#ifndef _MAP_H_
#define _MAP_H_

#include <resolv.h>
#include <sys/msg.h>
#include "client-fsm.h"

#define MAX_BUF_LEN 1024

// Describes one mail domain
// Network information, socket and number of letters
struct mail_domain_dscrptr {
    char *domain;
    struct sockaddr_in domain_mail_server;
    int socket_fd;
    int mails_count;
    struct node_t *mails_list;
    te_client_fsm_state state;
    char *buffer;  // Buffer for storing the read message

    int retry_time;
    int total_send_time;

    int last_attempt_time;
    int can_be_send;

    char request_buf[MAX_BUF_LEN];   // Buffer for sending data
};

struct mail_process_dscrptr {
    pid_t pid;         // child process pid
    int msg_queue_id;  // id of the message queue from which the process receives information about messages
    int domains_count; // number of domains handled by the process
    int mails_count;   // number of emails processed by the process
    char *domains[60]; // names of processed domains
};

// Describes single domain mails, that have to be sent
struct domain_mails {
    char *domain;
    char *mails_paths[100];
    int mails_count;
};

typedef struct queue_msg {
    long mtype;
    char mtext[500];
} queue_msg;

#endif