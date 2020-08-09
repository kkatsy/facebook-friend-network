import copy
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pickle

# retrieve files created by getFB_data
GRAPH_FILENAME = 'friend_graph.pickle'
NAMES_FILENAME = 'name_to_id.pickle'

with open(GRAPH_FILENAME, 'rb') as f:
    friend_graph = pickle.load(f)

with open(NAMES_FILENAME, 'rb') as f:
    username_to_name = pickle.load(f)

# get your id/username: first entry in username_to_name list
CENTRAL_ID = username_to_name[0][0]

# friend graph info
print('Total # of friends: ', len(friend_graph) - 1)

print('Average # of mutual friends overall: ')
print('Highest # of mutual friends with friend: ')
print('Social network density: ')

print('Number of cliques: ')
print('Largest clique size: ')
print('Average clique size')
print("Number of independent cliques: ")