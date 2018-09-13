import argparse
import socket
import sys
import os
import queue
from threading import Thread

BYTE = 4096

# use queue to storage the send or receive data
senddata = queue.Queue()
recvdata = queue.Queue()

# try to parse the command arguments


def argParse():
    parser = argparse.ArgumentParser(
        description="ncat python version", prog="ncat")
    subParser = parser.add_subparsers(
        help="sub-command help", dest="subparser_name")

    clientParser = subParser.add_parser("client", help="make nc as client")
    clientParser.add_argument("address", help="connect address")
    clientParser.add_argument("port", help="connect port", type=int)
    clientParser.add_argument(
        "-u", "--udp", help="use udp instead of default tcp", action='store_true')

    serverParser = subParser.add_parser("server", help="make nc as server")
    serverParser.add_argument("address", help="bind local ip address")
    serverParser.add_argument("port", help="bind port", type=int)
    serverParser.add_argument(
        "-u", "--udp", help="use udp instead of default tcp", action='store_true')

    return parser.parse_args()

# receive data from socket, then put them into queue:recvdata


def recv_data(sock):
    if sock.type == socket.SOCK_STREAM:
        while True:
            data = sock.recv(BYTE)
            if not data:
                os._exit(0)
            else:
                recvdata.put(data.decode().rstrip('\n'))
    if sock.type == socket.SOCK_DGRAM:
        while True:
            data = sock.recv(BYTE)
            if not data:
                os._exit(0)
            else:
                recvdata.put(data.decode().rstrip('\n'))

# get data from queue:senddata, then send them to the socket


def send_data(sock, address=("0,0,0,0", 1080)):
    if sock.type == socket.SOCK_STREAM:
        while True:
            try:
                sock.send(senddata.get().encode())
            except Exception:
                os._exit(0)
    if sock.type == socket.SOCK_DGRAM:
        while True:
            if address == "":
                raise Exception("argument addr can not be None")
            sock.sendto(senddata.get().encode(), address)

# get input data,then put them into queue:senddata


def get_input():
    while True:
        try:
            data = sys.stdin.readline()
        except Exception:
            os._exit(0)
        senddata.put(data)

# get data from queue:recvdata, then print them


def get_print():
    while True:
        data = recvdata.get()
        print(data)

# try to use 4 thread assigning the tasks


def run_thread(sock, address):
    if sock.type == socket.SOCK_STREAM:
        Thread(target=send_data, args=(sock,)).start()
    if sock.type == socket.SOCK_DGRAM:
        Thread(target=send_data, args=(sock, address,)).start()
    Thread(target=recv_data, args=(sock,)).start()
    Thread(target=get_input).start()
    Thread(target=get_print).start()


def main():
    args = argParse()
    subcommand = args.subparser_name
    address = (args.address, args.port)
    if args.udp:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if subcommand == "client":
        if not args.udp:
            sock.connect(address)
        run_thread(sock, address)
    elif subcommand == "server":
        sock.bind(address)
        if args.udp:
            data, addr = sock.recvfrom(BYTE)
            print(data.decode().rstrip('\n'))
            run_thread(sock, addr)
        else:
            sock.listen()
            print("tcp server listen on ", address)

            conn, addr = sock.accept()
            print("accepted connection from ", addr)
            run_thread(conn, addr)


if __name__ == "__main__":
    main()
