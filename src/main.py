import valve.source
import valve.source.a2s
import valve.source.master_server
from threading import Event as threadingEvent
import time
import urllib.parse

class ServerChecker():
    last_unique = 0
    last_updatetime = 0

    def __init__(self, address :tuple):
        self.address = address

    def Check(self):
        try:
            with valve.source.a2s.ServerQuerier(self.address) as server:
                info = server.info()
                players = server.players()
        
        except valve.source.NoResponseError:
            print("Server {}:{} timed out!".format(*self.address))
            return 0
        
        server_name = info['server_name']
        player_count = info['player_count']
        max_players = info['max_players']
        address_str = f"{self.address[0]}:{self.address[1]}"

        # print(f"Address: {address_str} \nServer name: '{server_name}' \nPlayers: {player_count}/{max_players}")
        if(show_players_list):
            print(f"{'Player name'.ljust(32)} | {'Score'.ljust(5)} | Duration \n")
        unique = 0

        for player in sorted(players["players"], key=lambda p: p["score"], reverse=True):
            score = player['score']
            name = player['name'].ljust(32)
            
            duration = int(player['duration'])
           
            duration = duration % (24 * 3600)
            hour = duration // 3600
            duration %= 3600
            minutes = duration // 60
            duration %= 60
            seconds = duration

            timestr = f"{minutes}:{seconds}"
            if(show_players_list):
                print(f"{name} | {str(score).ljust(5)} | {timestr}")

            unique += (duration + score)

        unique_diff = abs(self.last_unique - unique)
        self.last_unique = unique

        if(unique_diff != 0):
            self.last_updatetime = time.time()

        return time.time() - self.last_updatetime 


def CheckServers():
    for server in servers:
        last_updatetime = server.Check()
        if(last_updatetime == 0.0):
            print(f"{server.address} -> A2S_INFO updated: {time.strftime('%H:%M:%S', time.gmtime())}")

def setInterval(func, time: int):
    e = threadingEvent()
    while not e.wait(time):
        func()

def parse_hostport(hp):
    # urlparse() and urlsplit() insists on absolute URLs starting with "//"
    result = urllib.parse.urlsplit('//' + hp)
    return result.hostname, result.port


servers: ServerChecker = []
def AddServers():
    with open('ip_list.txt', mode='r', encoding='utf-8') as f:
        for line in f:
            if(len(line)):
                address = parse_hostport(line)
                servers.append(ServerChecker(address))

show_players_list = False
def main():
    AddServers()
    CheckServers()
    setInterval(CheckServers, 1.0)

main()