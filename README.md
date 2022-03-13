# SMTP client

#### Developed an SMTP client using the select call and workflows. Logging in a separate process. All messages are sent for one MX per session. Implemented unit tests as well as a test server

##### Server*
```
  cd server/
  python3 server.py
```
Runs on `localhost:1024`

##### Client**

```
  cd client/
  make
  ./smtp_client ./client.cfg /home/ivachernov/smtp-client/client/logs/
```

##### Unit-tests
```
  cd client/tests/unit_tests
  make
  ./smtp_client_test
```

1. *Expand virtualenv for debug
2. **You need to install the CUnit library, libconf, autogen, maybe something else. Don't forget to change client.conf and paths for ftok