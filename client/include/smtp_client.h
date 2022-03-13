#ifndef _SMTP_CLIENT_H_
#define _SMTP_CLIENT_H_

#include <sys/time.h>
#include "../include/log.h"
#include "../include/msg.h"

#define MAX_BUF_LEN 1024
#define INITIAL_SIZE 10

char client_host_name[MAX_BUF_LEN];

int connect_to_mail_server(int socket_fd, struct sockaddr_in mail_server, char *email_domain);
int send_msg_to_server(struct mail_domain_dscrptr *cur_mail_domain);

int send_helo(int socket_fd, char *request_buf);
int send_mail_from(int socket_fd, char *msg, char *request_buf);
int send_rcpt_to(int socket_fd, char *msg, char *request_buf);
int send_data_msg(int socket_fd, char *request_buf);
int send_msg_body(int socket_fd, char *request_buf);
int send_quit(int socket_fd, char *request_buf);
int send_data(char *data, int socket_fd);

char *read_data_from_server(int socket_fd);
te_client_fsm_event check_server_code(char *response);

#endif