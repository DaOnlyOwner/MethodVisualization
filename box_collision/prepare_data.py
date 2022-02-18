import os
from pathlib import Path

import yaml
import numpy as np
import pickle as pkl
import json as js
import itertools as it
from sklearn.manifold import MDS
import colorsys as cs
from shutil import copy2

try:
    from gather_words import BOX_COLLISION_DIRECTORY
except ImportError:
    # I get an import error, so I need to do that
    print("Warning: Cannot import BOX_COLLISION_DIRECTORY")
    BOX_COLLISION_DIRECTORY = Path(".")

SEED = 1202991

def load_data_all_clusters(input_dir = Path("../../testdata"), num_clusters=50):
    cluster_filenames = input_dir.glob("4clusters-*.yml")
    with open(input_dir / '2analysis_classes.txt', 'r') as freq_file:
        with open(input_dir / '3words_with_vectors.pkl','rb') as wwv_file:
            freq_dict = {}
            for line in freq_file:
                freq_key = line[0:line.find("{")].replace("(","").replace("'","").replace(",","").strip()
                freq_val = [x for x in line.replace(",","").split(" ") if x.isdigit()][0]
                freq_dict[freq_key]=int(freq_val)

            # Load the wwv
            wwv = pkl.load(wwv_file)
            clusters_list = []
            for path in cluster_filenames:
                with open (path, 'r') as clusters_file:
                    # Load the clusters
                    clusters = yaml.safe_load(clusters_file)
                    clusters_list.append(clusters)
                    # Load the frequencies
                    # wwv = dict()
                    # for name,v in wwv_:
                    #     wwv[name] = v
            return clusters_list, freq_dict,wwv
def load_data(input_dir, num_clusters):

    with open (input_dir / ('4clusters-' + str(num_clusters) + '.yml'), 'r') as clusters_file:
        with open(input_dir / '2analysis_classes.txt', 'r') as freq_file:
            with open(input_dir / '3words_with_vectors.pkl', 'rb') as wwv_file:
                # Load the clusters
                clusters = yaml.safe_load(clusters_file)

                # Load the frequencies
                freq_dict = {}
                for line in freq_file:
                    freq_key = line[0:line.find("{")].replace("(","").replace("'","").replace(",","").strip()
                    freq_val = [x for x in line.replace(",","").split(" ") if x.isdigit()][0]
                    freq_dict[freq_key]=int(freq_val)

                # Load the wwv
                wwv = pkl.load(wwv_file)
                # wwv = dict()
                # for name,v in wwv_:
                #     wwv[name] = v
                return clusters, freq_dict,wwv

# Filter out the words that are not in the cluster
def filter_words(clusters, freq, wwv):
    filtered_clusters = []
    for cluster in clusters:
        filtered_cluster = []
        for node in cluster:
            if node not in wwv:
                print(node, "was not present in words with vectors")
                continue
            final_freq = 1
            if node in freq:
                final_freq = freq[node]

            filtered_cluster.append((node,final_freq))
        if len(filtered_cluster) > 0:    
            filtered_clusters.append(filtered_cluster)
    return filtered_clusters


def map_pos_to_01_range(reduced):
    min_ = 10000000000000
    max_ = -1000000000000
    for elem in reduced:
        min_xyz = min(elem)
        max_xyz = max(elem)
        if(min_xyz < min_):
            min_ = min_xyz 
        if(max_xyz > max_):
            max_ = max_xyz
    if min_ < 0:
        reduced = map(lambda x: x+abs(min_),reduced)
        max_ = max_+abs(min_)
    elif min_ > 0:
        reduced = map(lambda x: x-abs(min_),reduced)
        max_ = max_-abs(min_)
    #print(list(reduced))
    #print(min_,max_)
    #input()
    return list(
            map(lambda x: tuple(x),
        map(lambda x: x / max_,reduced)))


def map_vecs_to_01_range(vecs):
    reduced = MDS(n_components=3,random_state=SEED).fit_transform(vecs)
    return map_pos_to_01_range(reduced)


def map_2dvectorlist_to_hsv(l):
    return list(map(lambda x: cs.hsv_to_rgb(x[0],x[1],0.5),map_pos_to_01_range(l)))


def calc_centroids(filtered_clusters, wwv):
    centroids = [] 
    for cluster in filtered_clusters:
        if len(cluster) == 0:
            print("WARNING: Cluster was empty")
            continue

        fst,_ = cluster[0]
        shp = np.shape(wwv[fst])
        centroid = np.zeros(shp)
        count = 0
        for node, freq in cluster:
            vec = wwv[node]
            centroid += vec
            count += 1
        centroid /= count 
        centroids.append(centroid)
    return centroids


def get_ctrd_name(i):
    return f"__centroid_{i}__"


def select_closest_node(cluster, p, wwv):
    min_name, min_dst = "", 1 << 63
    for name, _ in cluster:
        point = wwv[name]
        dst = np.linalg.norm(p-point)
        if min_dst > dst:
            min_dst = dst
            min_name = name
    return min_name


# FROM: https://codereview.stackexchange.com/questions/229282/performance-for-simple-code-that-converts-a-rgb-tuple-to-hex-string
def direct_format(tup):
    r, g, b = tup
    return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'


def prepare_nodes(filtered_clusters, wwv):
    centroids = calc_centroids(filtered_clusters, wwv)
    prep = []
    color = map_vecs_to_01_range(centroids)
    highest_freqs = []
    for i, cluster in enumerate(filtered_clusters):
        highest_freq = 0
        word_with_hf = ""
        for name, freq in cluster:
            d = {"name": name, "freq": freq, "is_centroid": False, "color": direct_format(color[i])}
            prep.append(d)
            if freq > highest_freq:
                highest_freq = freq
                word_with_hf = name
        highest_freqs.append(word_with_hf)

    for i, ctrd in enumerate(centroids):
        cw = select_closest_node(filtered_clusters[i], ctrd, wwv)
        prep.append({"name": get_ctrd_name(i), "highest_freq": highest_freqs[i], "freq": 1, "is_centroid": True, "closest_word" : cw, "color": direct_format(color[i])})

    return prep


def prepare_edges(filtered_clusters,wwv):
    centroids = calc_centroids(filtered_clusters,wwv)
    edges = []
    for i, cluster in enumerate(filtered_clusters):
        cluster_no_freq, freqs = zip(*cluster)
        ctrd = centroids[i]

        vecs = []
        for node in cluster_no_freq:
            vecs.append((node, wwv[node]))
        # Connect every node of the cluster to the repr
        for node, freq in cluster:
            if node == repr:
                continue
            dst = np.linalg.norm(wwv[node]-centroids[i])
            d = {"source": node, "target": get_ctrd_name(i), "dist": str(dst)}
            edges.append(d)
    
    for i in range(len(centroids)):
        for j in range(len(centroids)):
            if i == j:
                continue
            dst = np.linalg.norm(centroids[i]-centroids[j])
            d = {"source" : get_ctrd_name(i), "target":get_ctrd_name(j), "dist":str(dst*30)}
            edges.append(d)
    return edges

# Dont use that right now
def prepare_cluster_data_d3js_all_clusters(working_dir):
    clusters_list, freq, wwv_ = load_data_all_clusters(working_dir)
    wwv = dict()
    for word,vec in wwv_:
        wwv[word] = vec
    for clusters in clusters_list:
        f_clusters = filter_words(clusters,freq,wwv)
        nodes = prepare_nodes(f_clusters,wwv)
        edges = prepare_edges(f_clusters,wwv)
        data = {"amountClusters": len(clusters),"nodes":nodes, "edges":edges}
        jsfile = f"const data = {js.dumps(data)};"
        alt_dir = working_dir / 'graph_bounding_box' / ("visualization_"+str(len(clusters)))
        alt_dir.mkdir(parents=True,exist_ok=True)
        with open(alt_dir / 'prepared_data.js', "w") as f:
            f.write(jsfile)
        copy2(Path("d3.min.js"),alt_dir/"d3.min.js")
        copy2(Path("visualize.html"),alt_dir / "visualize.html")
        copy2(Path("d3js_License.txt"),alt_dir / "d3js_License.txt")

def prepare_cluster_data_d3js(working_dir, num_clusters=50):
    clusters, freq, wwv_ = load_data(working_dir, num_clusters)
    wwv = dict()
    for word,vec in wwv_:
        wwv[word] = vec
    f_clusters = filter_words(clusters, freq, wwv)
    nodes = prepare_nodes(f_clusters, wwv)
    edges = prepare_edges(f_clusters, wwv)
    data = {"amountClusters": len(clusters), "nodes": nodes, "edges": edges}
    jsfile = f"const data = {js.dumps(data)};"
    alt_dir = working_dir / 'graph_bounding_box'
    alt_dir.mkdir(parents=True,exist_ok=True)
    with open(alt_dir / 'prepared_data.js', "w") as f:
        f.write(jsfile)
    copy2(BOX_COLLISION_DIRECTORY/'d3.min.js', alt_dir/"d3.min.js")
    copy2(BOX_COLLISION_DIRECTORY/'visualize.html', alt_dir / "visualize.html")
    copy2(Path(BOX_COLLISION_DIRECTORY/'d3js_License.txt'), alt_dir / "d3js_License.txt")

#graph_bounding_box_directory = (working_dir / 'graph_bounding_box')
#graph_bounding_box_directory.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    prepare_cluster_data_d3js_all_clusters(Path("../../testdata"))
