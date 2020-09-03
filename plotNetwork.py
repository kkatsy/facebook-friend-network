import matplotlib.pyplot as plt
import community
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


# prune graph for central friends
central_friends = {}
removed = []
for k, v in friend_graph.items():
    # if mutual friends <= 2, remove from graph
    intersection_size = len(np.intersect1d(list(friend_graph.keys()), v))
    if intersection_size > 2:
        central_friends[k] = v
    else:
        removed.append(k)

print('Filtered out {} friends'.format(len(friend_graph.keys()) - len(central_friends.keys())))

# graph labeling choice
FULL_NAME = False
FIRST_NAME_W_INIT = False
FIRST_NAME = True
INITIALS = False

# create labels based on labeling choice
labels = {}
for pair in username_to_name:
    a_username = pair[0]
    a_name = pair[1]
    if a_username not in removed:
        if FULL_NAME:
            labels[a_username] = a_name
        elif FIRST_NAME_W_INIT:
            labels[a_username] = (a_name.split())[0] + " " + (a_name.split())[1][0]
        elif FIRST_NAME:
            labels[a_username] = a_name.split()[0]
        elif INITIALS:
            labels[a_username] = (a_name.split())[0][0] + (a_name.split())[1][0]
        else:
            labels[a_username] = a_username

# Extract edges from graph
edges = []
nodes = [CENTRAL_ID]
for k, v in central_friends.items():
    for item in v:
        if item in central_friends.keys() or item == CENTRAL_ID:
            edges.append((k, item))

# build networkx graph w edges
G = nx.Graph()
G.add_nodes_from([CENTRAL_ID])
G.add_nodes_from(central_friends.keys())
G.add_edges_from(edges)
print('Added {} edges'.format(len(edges)))

# create + graph friend graph
nx.set_node_attributes(G, labels, 'label')
pos = nx.spring_layout(G)
plt.rcParams['figure.figsize'] = [10, 10]

nx.draw_networkx(G, pos=pos, with_labels=True,
                 node_size=20, width=0.5, node_color='blue', edge_color='grey', labels=labels, font_size=9)
plt.show()
limits = plt.axis('off')

# apply louvain's community detection algo
partitioned = community.best_partition(G)                   # username, partition dict
values = [partitioned.get(node) for node in G.nodes()]      # partition num for v list

# create + graph community graph
fig = plt.figure()
fig.set_facecolor('white')
plt.rcParams['figure.figsize'] = [10, 10]

nx.draw_networkx(G, pos=pos,
                 cmap=plt.get_cmap('tab10'), node_color=values,
                 node_size=30, width=0.5, edge_color='grey', with_labels=True, labels=labels, font_size=9,
                 font_color='black')
plt.axis('off')
plt.show()