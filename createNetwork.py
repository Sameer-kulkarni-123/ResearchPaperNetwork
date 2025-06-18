import json
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network

def build_knowledge_graph(triplets):
    G = nx.DiGraph()  # Directed graph

    for subj, obj, rel in triplets:
        G.add_node(subj)
        G.add_node(obj)
        G.add_edge(subj, obj, label=rel)

    return G

def draw_graph(G, figsize=(12, 8)):
    pos = nx.spring_layout(G, k=0.8)
    # pos = nx.kamada_kawai_layout(G)  # more spread out
    # pos = nx.spring_layout(G, k=20, iterations=100)



    plt.figure(figsize=figsize)
    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=3000, font_size=10, font_weight='bold', arrows=True)
    
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    
    plt.title("Knowledge Graph")
    plt.axis('off')
    plt.show()


def interactive_graph(triplets, output_file="graph.html"):
  net = Network(notebook=False, directed=True)
  net.force_atlas_2based()

  for subj, obj, rel in triplets:
      net.add_node(subj, label=subj)
      net.add_node(obj, label=obj)
      net.add_edge(subj, obj, label=rel)

  # net.save_graph(output_file)
  html = net.generate_html()
  with open(output_file, "w", encoding="utf-8") as f:
      f.write(html)


def runNetworkx():
  triplets_file = open("outputs/imp_sor_list.json", "r")
  triplets = json.load(triplets_file)
  G = build_knowledge_graph(triplets)
  draw_graph(G)


def runPyvis(triplets):
  # triplets_file = open("outputs/imp_sor_list.json", "r")
  # triplets = json.load(triplets_file)
  interactive_graph(triplets)

# def runPyvis():
#   triplets_file = open("outputs/imp_sor_list.json", "r")
#   triplets = json.load(triplets_file)
#   interactive_graph(triplets)

# def showGraph():

# runNetworkx() #uncomment to visualize using networkx
# runPyvis() #creates a html file, "graph.html" open the html file in a web browser to visualize

"""
  There are two ways to visualize
  1) networkx
  2)pyvis
"""