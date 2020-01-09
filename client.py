import socket
import sys
import ast

try:
    SERVER_IP = sys.argv[1]
except IndexError:
    print('Missing Server IP argument!\nGet the server IP and run "python3 client.py <SERVER_IP>"', file=sys.stderr)
    sys.exit()

class Victim():

    def __init__(self):
        self.name = 'v'
        self.is_dead = False

    def dead(self):
        self.is_dead = True

class Detective():

    def __init__(self):
        self.name = 'd'
        self.players_list = []
        self.suspected = None

    def suspect(self, player):
        self.suspected = player

    def get_suspected(self):
        return ('suspect:'+self.suspected)

    def accuse(self):
        return ('accuse:' + self.suspected)

class Assassin():

    def __init__(self):
        self.name = 'a'
        self.players_list = []
        self.threatened = None

    def threaten(self, player):
        self.threatened = player

    def get_threatened(self):
        return ('threatened:' + self.threatened)

    def blink(self):
        return('blink:'+self.threatened)

def createPlayer(role):
    if role == 'victim':
        return Victim()
    elif role == 'detective':
        return  Detective()
    else:
        return Assassin()

action_counter = 0
response_counter = 0
players_list = []
role = ''

messages = [ 'Hello I am a client' ]
server_address = (SERVER_IP, 10000)
my_host = socket.gethostbyname(socket.gethostname())
print("My host:", my_host)
# Create a TCP/IP socket
socks = [ socket.socket(socket.AF_INET, socket.SOCK_STREAM) ]

# Connect the socket to the port where the server is listening
# print('connecting to %s port %s' % server_address, file=sys.stderr)
for s in socks:
    s.connect(server_address)

while True:

    '''for s in socks:
        if role == '':
            data = s.recv(4000)
            role = data.decode('utf-8')'''

    # Send messages on both sockets
    for s in socks:

        if action_counter == 0:
            message = 'role'
            action_counter += 1
        elif action_counter ==1:
            message = 'get_players_list'
            action_counter +=1
        elif action_counter ==2:
            if role == 'assassin':

                question = int(input('You are an assassin. \n [0] to threaten player \n [1] to blink\n'))
                if question == 0:
                    answer = input('Qual jogador deseja ameaçacar? '+ str(players_list))
                    player.threaten(answer)
                    message = player.get_threatened()
                else:
                    if player.threatened != None:
                        message = player.blink()
                        player.threatened = None
                    else:
                        answer = input('Nao há jogador ameaçado. Qual deseja ameaçacar? ' + str(players_list))
                        player.threaten(answer)
                        message = player.get_threatened()

            elif role == 'detective':

                question = int(input('You are a detective. \n [0] to suspect player \n [1] to accuse\n'))
                if question == 0:
                    answer = input('Which player do you suspect? ' + str(players_list))
                    player.suspect(answer)
                    message = player.get_suspected()
                else:
                    if player.suspected != None:
                        message = player.accuse()
                        player.suspected = None
                    else:
                        answer = input('You do not suspect anyone. Who do you want to suspect? ' + str(players_list))
                        player.suspect(answer)
                        message = player.get_suspected()


            else:
                message = input()
        else:
            message = input()
        # print('{0}: sending "{1}"'.format(s.getsockname(), message), file=sys.stderr)
        s.send(str.encode(message))

    # Read responses on both sockets
    for s in socks:
        data = s.recv(4000).decode('utf-8')
        if response_counter == 0:
            role = data
            player = createPlayer(role)
            print('player_name: {0}'.format(player.name))
            response_counter +=1
        elif response_counter ==1:
            players_list = ast.literal_eval(data)
            players_list.remove(my_host)
            print('player_list: {0}'.format(players_list))
            response_counter += 1

        if data == 'won':
            print('You won the game')
            sys.exit()

        # print('{0}: received "{1}"'.format(s.getsockname(), data), file=sys.stderr)
        if not data:
            print('closing socket', s.getsockname(), file=sys.stderr)
            s.close()

    print('player_role: {0}'.format(role))