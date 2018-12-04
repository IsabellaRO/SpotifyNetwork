from queue import Queue
 
from unidecode import unidecode
import networkx as nx
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
 
 
SEED_UID_1 = '6XpaIBNiVzIetEPCWDvAFP' # Whitney Houston
SEED_UID_2 = '4NJhFmfw43RLBLjQvxDuRS' # Wolfgang Amadeus Mozart
 
GRAPH_NAME = 'spotify'
 
 
class SpotifyWrapper:
    def __init__(self):
        credentials = SpotifyClientCredentials(
            client_id='d9a2223d179b4d9b845953cdc3b1f49b',
            client_secret='0b2e5ce4a3d345b6a31793c13141b3aa',
        )
 
        self.spotify = Spotify(client_credentials_manager=credentials)
 
 
    def filter(self, artist):
        return {key: artist[key] for key in ('name', 'popularity')}
 
 
    def artist(self, n):
        artist = self.spotify.artist(n)
 
        return self.filter(artist)
 
 
    def related_artists(self, n):
        related = self.spotify.artist_related_artists(n)
 
        for artist in related['artists']:
            yield artist['id'], self.filter(artist)
 
 
def add_node(g, n, artist):
    g.add_node(n)
 
    for key in artist:
        g.nodes[n][key] = artist[key]
 
 
def main():
    q = Queue()
    g = nx.DiGraph()
    w = SpotifyWrapper()
 
    q.put(SEED_UID_1)
    add_node(g, SEED_UID_1, w.artist(SEED_UID_1))
 
    q.put(SEED_UID_2)
    add_node(g, SEED_UID_2, w.artist(SEED_UID_2))
 
    while not q.empty():
        print(g.number_of_nodes(), g.number_of_edges())
 
        n = q.get()
 
        for m, artist in w.related_artists(n):
            if not g.has_node(m):
                q.put(m)
                add_node(g, m, artist)
 
            if not g.has_edge(n, m):
                g.add_edge(n, m)
 
        n = SEED_UID_1
        m = SEED_UID_2
 
        if nx.has_path(g, n, m) and nx.has_path(g, m, n):
            print('connected')
            break
 
    nodes = list(g.nodes)
 
    with open(GRAPH_NAME + '.gml', 'w') as file:
        file.write('graph [\n')
        file.write('  directed 1\n')
 
        for i, n in enumerate(nodes):
            name = unidecode(g.nodes[n]['name']).replace('"', "'")
            popularity = g.nodes[n]['popularity']
 
            file.write('  node [\n')
            file.write('    id {}\n'.format(i))
            file.write('    label "{}"\n'.format(name))
            file.write('    popularity {}\n'.format(popularity))
            file.write('  ]\n')
 
        for n, m in g.edges:
            file.write('  edge [\n')
            file.write('    source {}\n'.format(nodes.index(n)))
            file.write('    target {}\n'.format(nodes.index(m)))
            file.write('  ]\n')
 
        file.write(']\n')
 
 
if __name__ == '__main__':
    main()
