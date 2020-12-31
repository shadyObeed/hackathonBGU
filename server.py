from socket import *
from struct import *
import time
import threading
import random

Bold = "\033[1m"
Red = "\033[31;1m"
Green = "\033[32;1m"
Yellow = "\033[33;1m"
Blue = "\033[34;1m"
end = "\033[0;1m"

GROUP_1 = []
GROUP_2 = []
TUP = [GROUP_1, GROUP_2]
Counter_TUP = [0, 0]
lock = threading.Lock()
lock2 = threading.Lock()
MV = []


def threaded(connection):  # run func for threading
    counter = 0
    ClientName = ''
    gotName = False
    endTime = time.time() + 10
    ClientName, gotName = getTeamName(ClientName, connection, endTime, gotName)
    n = random.randint(1, 2)
    if gotName:
        addTeamName(ClientName, n)
        message = f"{Green}you have 10 seconds start typing as fast as you cannnnnn{end}"
        try:
            connection.sendall(message.encode('utf-8'))
        except:
            print(f"{Red}connection from client lost{end}")
            try:
                connection.close()
                return
            except:
                return

    counter = getKeyboardInput(connection, counter)
    increaseCounter(counter, n)
    try:
        connection.sendall(GameOutput().encode())
        connection.close()
    except:
        try:
            connection.close()
        except:
            pass


def addTeamName(ClientName, n):
    lock.acquire()
    if n == 2:
        TUP[1].append(ClientName)
    else:
        TUP[0].append(ClientName)
    lock.release()


def increaseCounter(counter, n):
    lock.acquire()
    if (n == 1):
        Counter_TUP[0] = Counter_TUP[0] + counter
    else:
        Counter_TUP[1] = Counter_TUP[1] + counter
    lock.release()


def getKeyboardInput(connection, counter):
    endTime = time.time() + 10
    while time.time() < endTime:
        try:
            data = connection.recv(1)
            if data:
                counter = counter + 1
        except:
            pass
    return counter


def getTeamName(ClientName, connection, endTime, gotName):
    while time.time() < endTime and not gotName:
        try:
            data = connection.recv(1)
            if data.decode('utf-8') == '\n':
                gotName = True
            else:
                ClientName = ClientName + data.decode('utf-8')
        except:
            gotName = False
    return ClientName, gotName


def Main():
    # MV.append(0)

    ourPort = 2051
    # init the TCP connection
    sock = TCPInitConnection(ourPort)
    # init the UDP connection
    cs, message = UDPInitConnection(ourPort)
    try:
        sock.listen()
        while True:
            tmp_counter = 0  # thread counter
            threads = []

            # run for 10 sec and collecting players by adding them to the array of threads
            endTime = time.time() + 10
            while time.time() < endTime:
                try:
                    cs.sendto(message, ('255.255.255.255', 13117))  # broadcast
                except:
                    print(f"{Red}broadcasting failed{end}")
                time.sleep(1)
                sock.settimeout(0)  # non blocking con
                try:
                    # initializing threads
                    connection, addr = sock.accept()

                    # set the connection socket non blocking
                    connection.settimeout(0)

                    t = threading.Thread(target=threaded, args=(connection,))
                    threads.append(t)
                    tmp_counter = tmp_counter + 1
                except:
                    pass
            for x in threads:
                x.start()
            for x in threads:
                x.join()

            if tmp_counter > 0:
                print(GameOutput())
                # initializing vars
                Counter_TUP[0] = 0
                Counter_TUP[1] = 0
                TUP[1] = []
                TUP[0] = []
    except:
        pass
        # print(f"{Red}listen failed{end}")


def GameOutput():
    toPrint = f"{Green}GROUP1\n==\n{end}" + str(TUP[0]) + '\n' + f"{Green}GROUP2\n==\n{end}" + str(TUP[1]) + '\n'
    if (Counter_TUP[0] != 0 or Counter_TUP[1] != 0):
        # MAXTEAM =max(Counter_TUP[1],Counter_TUP[0])
        if Counter_TUP[0] > Counter_TUP[1]:
            toPrint = toPrint + f"{Blue}GROUP 1 WINSS WITH {end}" + str(Counter_TUP[0]) + f"{Blue} POINTS{end}" + '\n'
            for x in TUP[0]:
                toPrint = toPrint + x + '\n'
        elif Counter_TUP[0] < Counter_TUP[1]:
            toPrint = toPrint + f"{Blue}GROUP 2 WINS WITH {end}" + str(Counter_TUP[1]) + f"{Blue} POINTS{end}" + '\n'
            for x in TUP[1]:
                toPrint = toPrint + x + '\n'
        else:
            toPrint = toPrint + f"{Blue}its a DRAWWWWWW{end} " + '\n'
    # MV[0] = max(MV[0] ,Counter_TUP[0],Counter_TUP[1])
    # if MV[0] == MAXTEAM:
    #     toPrint = toPrint + 'The Winners has the best record ever!!!\n'
    return toPrint


def UDPInitConnection(ourPort):
    cs = socket(AF_INET, SOCK_DGRAM)
    cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    message = pack('!IBH', 0xfeedbeef, 0x2, ourPort)
    return cs, message


def TCPInitConnection(ourPort):
    # TCP
    host = gethostname()
    print(f"{Green}server started, listening on IP address{end}", host)
    sock = socket(AF_INET, SOCK_STREAM)
    server_address = (host, ourPort)
    try:
        sock.bind(server_address)
    except:
        print(f"{Red}error binding{end}")
    return sock


if __name__ == '__main__':
    Main()
