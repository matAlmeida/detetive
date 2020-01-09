import select
import socket
import sys
import queue
import random

try:
    SERVER_IP = sys.argv[1]
except IndexError:
    print('Missing Server IP argument!\nGet yout IP and run "python3 server.py <YOUR_IP>"', file=sys.stderr)
    sys.exit()

action_counter = 0
response_counter = 0

THREATENED = ''
SUSPECTED = ''


with open('list.txt', 'r') as f:
    clients_list = f.read().split()

random.shuffle(clients_list)

roles_list = []

for i in range(len(clients_list)):
    if i == 0:
        roles_list.append('assassin')
    elif i == 1:
        roles_list.append('detective')
    else:
        roles_list.append('victim')

roles_dict = dict(zip(clients_list, roles_list))

print(roles_dict)

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Allows the server to keep listening to other sockets
server.setblocking(0)

# Bind the socket to the port
server_address = (SERVER_IP, 10000)
print('Server on HOST: {0} | PORT: {1}'.format(SERVER_IP, 10000), file=sys.stderr)
server.bind(server_address)

# Listen for incoming connections
server.listen(5)

# Sockets from which we expect to read
inputs = [ server ]

# Sockets to which we expect to write
outputs = [ ]

# Outgoing message queues (socket:Queue)
message_queues = {}

while inputs:

    # Wait for at least one of the sockets to be ready for processing
    # print('\n waiting for the next event', file=sys.stderr)
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    # Handle inputs
    for s in readable:

        if s is server:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            print('New connection from', client_address, file=sys.stderr)
            connection.setblocking(0)
            inputs.append(connection)

            # Give the connection a queue for data we want to send
            message_queues[connection] = queue.Queue()

        else:
            data = s.recv(4000).decode('utf-8')
            if data:
                # A readable client socket has data
                print('received "{0}" from {1}'.format(data, s.getpeername()), file=sys.stderr)

                if ':' in data:
                    data,target = data.split(':')
                if data == 'role':
                    print(client_address[0])
                    message_queues[s].put(roles_dict.get(client_address[0]))
                    # message_queues[s].put('detective')
                elif data =='get_players_list':
                    message_queues[s].put(clients_list)

                elif data == 'threatened':
                    THREATENED = target
                    message_queues[s].put('ok')

                elif data == 'suspected':
                    SUSPECTED = target

                elif data == 'blink':
                    if roles_dict.get(target) == 'detective':
                        print('Assassin tried to kill the Detective. Detective won the game.')
                        sys.exit()
                    else:
                        if roles_dict.get(SUSPECTED) == 'assassin':
                            print('Assassin suspected by the Detective. Detective won the game.')
                            sys.exit()
                        else:
                            clients_list.remove(THREATENED)
                            if len(clients_list) <= 3:
                                print('Not enough player. Assassin won the game.')
                                message_queues[s].put('won')
                                sys.exit()
                            else:
                                message_queues[s].put(THREATENED)

                elif data == 'accuse':
                    if roles_dict.get(SUSPECTED) == 'assassin':
                        print('Assassin accused by the Detective. Detective won the game.')
                        sys.exit()
                    else:
                        print('Victim accused by the  Detective. Assassin won the game.')
                        sys.exit()

                else:
                    message_queues[s].put(data)
                # Add output channel for response
                if s not in outputs:
                    outputs.append(s)

                else:
                    # Interpret empty result as closed connection
                    print('closing %s', client_address, 'after reading no data', file=sys.stderr)
                    # Stop listening for input on the connection
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()

                    # Remove message queue
                    del message_queues[s]

    # Handle outputs
    for s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
        except queue.Empty:
            # No messages waiting so stop checking for writability.
            print('output queue for', s.getpeername(), 'is empty', file=sys.stderr)
            outputs.remove(s)
        else:
            print('sending "{0}" to {1}'.format(next_msg, s.getpeername()), file=sys.stderr)
            if next_msg == THREATENED:
                for i in inputs:
                    s.send(str(next_msg).encode())
            s.send(str(next_msg).encode())

    # Handle "exceptional conditions"
    for s in exceptional:
        print('handling exceptional condition for', s.getpeername(), file=sys.stderr)
        # Stop listening for input on the connection
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()

        # Remove message queue
        del message_queues[s]

    '''for i in inputs[1:]:
        i.sendall(str(input('O que enviar? ')).encode())
        print(i)'''