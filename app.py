import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium, folium_static
import numpy as np
from collections import defaultdict
import heapq

from pathlib import Path

path1 = Path(__file__).parent / "Shanghai.co"
path2 = Path(__file__).parent / "Shanghai.road-d"

with open(path1) as f:
    data = f.readlines()

loc = {}
for i, coords in enumerate(data[6:]):
    loc[i] = tuple(map(float, coords.strip().split()))

with open(path2) as f:
    data = f.readlines()

dist = defaultdict(dict)
for i, coords in enumerate(data[5:]):
    u, v, d = coords.strip().split()
    u = int(u)
    v = int(v)
    d = float(d)
    dist[u][v] = d

nodes = {node: loc[node] for node in dist}

locations = [(k, v) for k, v in nodes.items()]
np.random.shuffle(locations)

st.set_page_config(layout="wide")

c1, c2 = st.columns(2)

with c1:
    m = folium.Map(location=(31.231168, 121.462833), zoom_start=12)
    Draw(export=True).add_to(m)

    output = st_folium(
        m, width=700, height=500)

def find(src, dest):
    d = {}

    q = [(0, src, src)]
    heapq.heapify(q)
    while q:
        distance, cur, prev = heapq.heappop(q)
        if cur in d: continue

        d[cur] = prev

        if cur == dest:
            return d

        for k, v in dist[cur].items():
            heapq.heappush(q, (distance + v, k, cur))
    return False

if output['all_drawings'] and len(output['all_drawings']) == 2:
    data = output['all_drawings']
    p1 = data[0]['geometry']['coordinates'][::-1]
    p2 = data[1]['geometry']['coordinates'][::-1]

    points = np.array([loc[i] for i in range(len(loc))])
    src = np.argmin(np.sum((p1-points)**2, axis=1))
    dest = np.argmin(np.sum((p2-points)**2, axis=1))

    d = find(src, dest)
    if d:
        cur = dest
        road = [nodes[cur]]
        while cur != src:
            cur = d[cur]
            road.append(nodes[cur])

        # if 'markers' not in st.session_state:
        #     st.session_state["markers"] = [folium.Marker(p1), folium.Marker(p2)]
        #
        # fg = folium.FeatureGroup(name="Markers")
        # for marker in st.session_state["markers"]:
        #     fg.add_child(marker)

        with c2:

            m = folium.Map(location=(31.231168, 121.462833), zoom_start=12)

            folium.Marker(p1).add_to(m)
            folium.Marker(p2).add_to(m)

            folium.PolyLine(road, color='red', weight=5, opacity=1).add_to(m)

            folium_static(
                m,
                width=700, height=500)




