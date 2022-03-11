import socket
import os
import sys
import dns.resolver
import re
import _thread
import shutil


def HELO(args, s, client_address, state):
    fileName = str(client_address[1]) + '.txt'
    if len(args) != 2:
        s.send(bytes("501 Syntax: HELO hostname \r\n", "utf-8"))
        return
    arList = list()
    # check if helo has been sent before
    if state['HELO'] == False:
        with open(fileName, 'w') as the_file:
            for arg in args:
                arList.append(arg.decode('UTF-8'))
            the_file.write(" ".join(arList) + "\r\n")
        state['HELO'] = True
        state['file'] = client_address[1]
        state['domain'] = args[1]
        s.send(bytes("250 " + str(client_address[1]) + " OK \r\n", "utf-8"))
    # if helo sent before reset all state and delete old file
    else:
        open(fileName, 'w').close()
        with open(fileName, 'a') as the_file:
            for arg in args:
                arList.append(arg.decode('UTF-8'))
            the_file.write(" ".join(arList) + "\r\n")
        state['HELO'] = False
        state['MAIL'] = False
        state['RCPT'] = False
        state['completedTransaction'] = False
        state['HELO'] = True
        s.send(bytes("250 " + str(client_address[1]) + " OK \r\n", "utf-8"))


# start the mail transaction after checking the sessions has be inititalized
def MAIL(args, s, client_address, state):
    fileName = str(state['file']) + '.txt'
    # first check that helo has been sent
    if state['HELO'] == False:
        s.send(bytes("503 5.5.1 Error: send HELO/EHLO first \r\n", "utf-8"))
    else:
        # make sure it's not a nested mail command
        if state['MAIL'] == False:
            # check if the arguments are provided
            if len(args) != 2:
                s.send(bytes("501 5.5.4 Syntax: MAIL FROM:<address> \r\n", "utf-8"))
                return
            checkSyntax = re.match("(^FROM:<[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+>$)", args[1], re.IGNORECASE)
            if (checkSyntax):
                arList = list()
                # check if this is the first mail transaction in this session
                if state['data'] == False:
                    with open(fileName, 'a') as the_file:
                        for arg in args:
                            arList.append(arg.decode('UTF-8'))
                        the_file.write(" ".join(arList) + "\r\n")
                    state['MAIL'] = True
                    s.send(bytes("250 2.1.0 Ok \r\n", "utf-8"))
                else:
                    state['file'] = state['file'] + 1
                    fileName = str(state['file']) + '.txt'
                    with open(fileName, 'a') as the_file:
                        for arg in args:
                            arList.append(arg.decode('UTF-8'))
                        the_file.write("helo " + state['domain'] + "\r\n")
                        the_file.write(" ".join(arList) + "\r\n")
                    state['MAIL'] = True
                    state['completedTransaction'] = False
                    s.send(bytes("250 2.1.0 Ok \r\n", "utf-8"))
            else:
                s.send(bytes("501 5.1.7 Bad sender address syntax \r\n", "utf-8"))
        else:
            s.send(bytes("503 5.5.1 Error: nested MAIL command \r\n", "utf-8"))


def RCPT(args, s, client_address, state):
    # check if a mail transaction has begon and helo is initiatied
    if state['MAIL'] == True and state['HELO'] == True:
        if len(args) != 2:
            s.send(bytes("501 5.5.4 Syntax: RCPT TO:<address> \r\n", "utf-8"))
            return
        # check the format of the email is valid
        checkSyntax = re.match("(^TO:<[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+>$)", args[1], re.IGNORECASE)
        if (checkSyntax):
            state['recipient'] = checkSyntax.group()
            fileName = str(state['file']) + '.txt'
            with open(fileName, 'a') as the_file:
                arList = list()
                for arg in args:
                    arList.append(arg.decode('UTF-8'))
                the_file.write(" ".join(arList) + "\r\n")
            state['RCPT'] = True
            s.send(bytes("250 2.1.5 Ok \r\n", "utf-8"))
        else:
            s.send(bytes("501 5.1.3 Bad recipient address syntax \r\n", "utf-8"))
    else:
        s.send(bytes("503 5.5.1 Error: need MAIL command \r\n", "utf-8"))


def DATA(args, s, client_address, state):
    fileName = str(state['file']) + '.txt'
    if state['MAIL'] == True and state['HELO'] == True and state['RCPT'] == True:
        s.send(bytes("354 End data with <CR><LF>.<CR><LF> \r\n", "utf-8"))
        data = recieveData(s, state)
        with open(fileName, 'a') as the_file:
            the_file.write("data \n")
            the_file.write(data)
            the_file.write("quit \n")
        state['MAIL'] = False
        state['RCPT'] = False
        s.send(bytes("250 queued " + str(state['file']) + "\r\n", "utf-8"))
        state['data'] = True
        state['completedTransaction'] = True
        _thread.start_new_thread(relayData, (state['file'], state))
    elif state['MAIL'] == True and state['RCPT'] == False:
        s.send(bytes("554 5.5.1 Error: no valid recipients \r\n", "utf-8"))
    else:
        s.send(bytes("503 5.5.1 Error: need RCPT command \r\n", "utf-8"))


def NOOP(args, s, client_address, state):
    s.send(bytes("250 Ok \n", "utf-8"))


def QUIT(args, s, client_address, state):
    state['loop'] = False
    s.send(bytes("221 2.0.0 Bye \r\n", "utf-8"))
    s.close()
    if state['completedTransaction'] == False:
        fileName = str(state['file']) + '.txt'
        os.remove(fileName)


# To avoid pishing and brute force discovery of emails this function is not implemented
def VRFY(args, s, client_address, state):
    if len(args) != 2:
        s.send(bytes("501 5.5.4 Syntax: VRFY address \n", "utf-8"))
        return
    checkSyntax = re.match("TO:<\w+@\w+\.\w+>", args[1], re.IGNORECASE)
    if (checkSyntax):
        s.send(bytes("252  Cannot VRFY user \n", "utf-8"))
    else:
        s.send(bytes("450 4.1.2 Recipient address rejected: Domain not found \n", "utf-8"))


def RSET(args, s, client_address, state):
    fileName = str(state['file'] + '.txt')
    with open(fileName) as f:
        first_line = f.readline()
    open(fileName, 'w').close()
    with open(fileName, 'a') as the_file:
        the_file.write(first_line)
    state['MAIL'] = False
    state['RCPT'] = False
    s.send(bytes("250 OK \r\n", "utf-8"))


def findMXServer(email):
    domain = re.search("@[\w.]+", email)
    domain = domain.group()
    domain = domain[1:]
    try:
        mailExchangeServers = dns.resolver.query(domain, 'MX')
    except:
        print("no domain found \n")
        return
    lowestPref = ""
    pref = mailExchangeServers[0].preference
    for rdata in mailExchangeServers:
        if rdata.preference <= pref:
            lowestPref = rdata.exchange.__str__()
    lowestPref = lowestPref[:-1]
    return lowestPref


def relayData(client_address, state):
    filename = str(client_address) + '.txt'
    # The remote host
    HOST = findMXServer(state['recipient'])
    # if we got results for the host mx server
    if HOST:
        PORT = 25  # email port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        data = s.recv(1024)
        print('Received', repr(data))
        with open(filename) as fp:
            for line in fp:
                print('sent', repr(line))
                s.sendall(line)
                if line == ".\r\n":
                    data = s.recv(1024)
                    print('Received', repr(data))
                    answer = data.split(" ")
                    # check if the relaying successed, if it didn't write the session to the errors folder
                    if answer[0] != "250":
                        filePath = os.path.realpath(filename)
                        folderPath = os.path.join('errors', os.path.basename(filePath))
                        shutil.copy(filename, folderPath)
        os.remove(filename)
    else:
        print("Host not found \n")
        # write the session to the errors folder
        filePath = os.path.realpath(filename)
        folderPath = os.path.join('errors', os.path.basename(filePath))
        shutil.copy(filename, folderPath)


# end the loop of handling a client and delete the commands file
def closeAndClean(s, state):
    state['loop'] = False
    s.close()
    if state['completedTransaction'] == False:
        fileName = str(state['file']) + '.txt'
        os.remove(fileName)


# keep on recieving data until you find a dot on a new line
def recieveData(s, state):
    bufferSize = 4096
    buffer = s.recv(bufferSize)
    # remove timeout if commands are recieved
    buffering = True
    while buffering:
        if "\r\n.\r\n" in buffer:
            return buffer
        else:
            more = s.recv(4096)
            if not more:
                buffering = False
            else:
                buffer += more
    return buffer


dispatch = {
    b'helo': HELO,
    b'mail': MAIL,
    b'rcpt': RCPT,
    b'data': DATA,
    b'quit': QUIT,
    b'vrfy': VRFY,
    b'rest': RSET,
    b'noop': NOOP
}


# processes all the commands recieved from the SMTP client
def process_network_command(command, args, s, client_address, state):
    command = command.lower()
    try:
        dispatch[command](args, s, client_address, state)
    except KeyError:
        s.send(bytes("502 5.5.2 Error: command not recognized \r\n", "utf-8"))


def linesplit(s, state):
    try:
        s.settimeout(300)
        buffer = s.recv(4096)
        print(buffer)
        s.settimeout(None)
        buffering = True
        while buffering:
            print(buffer)
            if buffer == "\r\n":
                s.send(bytes("500 5.5.2 Error: Syntax error \n", "utf-8"))
            if bytes("\n", "utf-8") in buffer:
                (line, buffer) = buffer.split(bytes("\n", "utf-8"), 1)
                return line
            else:
                more = s.recv(4096)
                if not more:
                    buffering = False
                else:
                    buffer += more
    except socket.timeout:
        closeAndClean(s, state)


# take care of the sessions of one client with all of it's transactions
# each call to this function is handled in a seperate section
def handleClient(s, client_address):
    state = {
        'HELO': False,
        'MAIL': False,
        'RCPT': False,
        'loop': True,
        'data': False,
        'recipient': "",
        'file': 0,
        'domain': "",
        'completedTransaction': False
    }
    try:
        s.send(bytes("220 SMTP Service ready 1.0 \r\n", "utf-8"))
        print(sys.stderr, 'connection from', client_address)
        while state['loop']:
            lines = linesplit(s, state)
            try:
                args = lines.split()
            except AttributeError:
                print(args)
            if len(args) > 0:
                process_network_command(args[0], args, s, client_address, state)
    finally:
        s.close()


def main():
    print(sys.argv)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevent address is already in use error
    server_address = (sys.argv[1], 1024)
    sock.bind(server_address)
    sock.listen(0)

    while True:
        print('waiting for a connection')
        connection, client_address = sock.accept()
        if connection:
            _thread.start_new_thread(handleClient, (connection, client_address))


if __name__ == "__main__":
    main()
