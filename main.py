import warnings
from tqdm import tqdm
import os
import networkx as nx
import pandas as pd

warnings.filterwarnings('ignore')

### "None"
def return_shortest_path_length(G, DG, directed, s, t):
        direct_edge_exists = DG.has_edge(s, t) if directed == '->' else G.has_edge(s, t)
                
        try:
            if direct_edge_exists:
                path_length = 1
            else:
                graph_to_use = DG if directed != '--' else G
                subgraph = graph_to_use.subgraph(node for node in graph_to_use if graph_to_use.nodes[node]['color'] != 'red' or node in [s, t])
                path_length = nx.shortest_path_length(subgraph, s, t)
        except nx.NetworkXNoPath:
             path_length = -1
        
        return path_length

### "Few"
def return_min_red_vertices_count(DG, directed, s, t, p_dict):
    if directed == "->":
        dp_min = {node: float('inf') for node in DG.nodes}
        dp_min[s] = 1 if DG.nodes[s]['color'] == 'red' else 0
        sorted_list = list(nx.topological_sort(DG))
        for current_node in sorted_list:
            if current_node in p_dict:
                dp_min[current_node] = 1 if DG.nodes[current_node]['color'] == 'red' else 0
                temp_count = float('inf')
                for j in p_dict[current_node]:
                    temp_count = min(temp_count, dp_min[current_node]+dp_min[j])
                dp_min[current_node] = temp_count
                
        count = dp_min[t] if dp_min[t] != float('inf') else -1 
        
    else:
        try:
            few_path = nx.shortest_path(DG, s, t, weight='weight')
            count = 0
            for i in few_path:
                if DG.nodes[i]['color'] == "red":
                    count += 1
        except nx.NetworkXNoPath:
            count = -1

    return count

### "Alternate"
def has_alternate_path(DG, G, directed, s, t):
    if directed == "->":
        alternate_path = nx.has_path(DG, s, t)
    else:
        alternate_path = nx.has_path(G, s, t)
    
    return alternate_path

### "Many"
def return_max_red_vertices_count(DG, directed, s, t, p_dict):
    if directed == "->":
        dp_max = {node: float('-inf') for node in DG.nodes}
        dp_max[s] = 1 if DG.nodes[s]['color'] == 'red' else 0
        sorted_list = list(nx.topological_sort(DG))
        for current_node in sorted_list:
            if current_node in p_dict:
                dp_max[current_node] = 1 if DG.nodes[current_node]['color'] == 'red' else 0
                temp_count = float('-inf')
                for j in p_dict[current_node]:
                    temp_count = max(temp_count, dp_max[current_node]+dp_max[j])
                dp_max[current_node] = temp_count
                
        count = dp_max[t] if dp_max[t] != float('-inf') else -1 
    else:
        count = "?!"

    return count

### "Some"
def has_some_path(G, DG, directed, s, t, p_dict, file, red_list):
    if directed == "->":
        some_path = (return_max_red_vertices_count(DG, directed, s, t, p_dict) > 0)
    elif file.startswith('wall-z'):
        some_path = "?!"
    else:
        if red_list:
            if s in red_list or t in red_list:
                some_path = nx.has_path(G, s, t)
            else:
                G.add_node('source_s', color='grey')
                G.add_node('sink_s', color='grey')
                G.add_edge(s, 'sink_s', capacity=1)
                G.add_edge(t, 'sink_s', capacity=1)
                for r in red_list:
                    if len(list(G.neighbors(r))) > 1:
                        G.add_edge('source_s', r, capacity=2)
                        break
                max_flow, _ = nx.maximum_flow(G, "source_s", "sink_s")
                if max_flow == 2:
                    some_path = True
                else:
                    some_path = False
        else:
            some_path = False
    
    return some_path


PATH = "./data/"

files_list = os.listdir(PATH)
df = pd.DataFrame(columns=['Instance name', 'n', 'm', 'A', 'F', 'M', 'N', 'S'])

for file in tqdm(files_list):
    if file.endswith('.txt'):
        full_path = os.path.join(PATH + file)
        if os.path.isfile(full_path):
            with open (full_path, 'r') as f:
                ### Alternate
                G_alternate = nx.Graph()
                DG_alternate = nx.DiGraph()

                ### Few
                DG_few = nx.DiGraph()

                ### Many
                DG_many = nx.DiGraph()

                ### None
                G_none = nx.Graph()
                DG_none = nx.DiGraph()

                ### Some
                DG_some = nx.DiGraph()
                red_list = []

                n, m, r = map(int, f.readline().strip().split())
                s, t = map(str, f.readline().strip().split())

                dp_dict = {}
                for i in range(n):
                    name = f.readline().strip().split(' ')
                    
                    if len(name) > 1:
                        color = "red"
                        red_list.append(name[0])
                    else:
                        color = "grey"
                    
                    for G, DG in [(G_alternate, DG_alternate), (G_none, DG_none)]:
                        G.add_node(name[0], color=color)
                        DG.add_node(name[0], color=color)
                        
                    for DG in [DG_few, DG_many, DG_some]:
                        DG.add_node(name[0], color=color)
                    
                p_dict = {}
                for j in range(m):
                    start, directed, end = f.readline().strip().split(' ')
                    
                    for prob, G, DG in [("Alternate", G_alternate, DG_alternate), ("None", G_none, DG_none)]:
                        if prob == "Alternate":
                            if directed == '->':
                                if DG.nodes[start]['color'] != DG.nodes[end]['color']:
                                    DG.add_edge(start, end)
                            else:
                                if G.nodes[start]['color'] != G.nodes[end]['color']:
                                    G.add_edge(start, end)
                        
                        if prob == "None":
                            if directed == '->':
                                DG.add_edge(start, end)
                            else:
                                G.add_edge(start, end)
                    
                    for prob, DG in [("Few", DG_few), ("Many", DG_many), ("Some", DG_some)]:
                        if prob == "Few":
                            if directed == '->':
                                if DG.nodes[end]['color'] == "red":
                                    DG.add_edge(start, end, weight=m)
                                else:
                                    DG.add_edge(start, end, weight=1)
                            else:
                                if DG.nodes[start]['color'] == "red":
                                    if DG.nodes[end]['color'] == "red":
                                        weight1, weight2 = m, m
                                    else:
                                        weight1, weight2 = 1, m
                                else:
                                    if DG.nodes[end]['color'] == "red":
                                        weight1, weight2 = m, 1
                                    else:
                                        weight1, weight2 = 1, 1

                                DG.add_edge(start, end, weight=weight1)
                                DG.add_edge(end, start, weight=weight2)

                        if prob == "Many":
                            if directed == "->":
                                DG.add_edge(start, end)
                                if end not in p_dict:
                                    p_dict[end] = []
                                p_dict[end].append(start)
                        
                        if prob == "Some":
                            if directed != "->":
                                DG.add_edge(start, end, capacity=1)
                                DG.add_edge(end, start, capacity=1)
                
                new_row = {'Instance name': file.replace('.txt', ''), 'n': n, 'm': m, 'A': has_alternate_path(DG_alternate, G_alternate, directed, s, t), 'F': return_min_red_vertices_count(DG_few, directed, s, t, p_dict), 'M': return_max_red_vertices_count(DG_many, directed, s, t, p_dict), 'N': return_shortest_path_length(G_none, DG_none, directed, s, t), 'S': has_some_path(DG_some, DG_many, directed, s, t, p_dict, file, red_list)}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

df.to_csv(r'results.txt', index=False, mode='a')