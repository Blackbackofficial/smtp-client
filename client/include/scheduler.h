#ifndef _SCHEDULER_H_
#define _SCHEDULER_H_

#include "domain_proc.h"

#define MAX_MAIL_DOMAIN_NUM 50
#define RETRY_DIR_READ_TIME 25

int run_client(int proc_num, int total_send_time, int retry_time);
int master_process_worker_start(int proc_num, struct mail_process_dscrptr *mail_procs);
int child_process_worker_start(int proc_idx, int total_send_time, int retry_time);
int get_mail_proc_idx(char *domain_name, int domains_count, struct mail_process_dscrptr *mail_procs, int proc_num);

void wait_for(unsigned int secs);
void shutdown_master_properly(int proc_num, struct mail_process_dscrptr *mail_procs);
void shutdown_child_properly(int signal, int maxfd);

#endif