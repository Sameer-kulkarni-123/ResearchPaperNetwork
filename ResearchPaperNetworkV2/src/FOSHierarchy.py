import json
import time
import requests
import numpy as np
from collections import defaultdict
from tqdm import tqdm

INPUT_JSON = "batch_0.json"
HIERARCHY_JSON = "fos_hierarchy.json"
SIM_MATRIX_FILE = "fos_similarity_matrix_batch0.npy"

# --------------------------
# Step 1: Extract all unique FOS
# --------------------------
with open(INPUT_JSON, "r", encoding="utf8") as f:
    papers = json.load(f)

fos_set = set()
for paper in papers:
    fos_tags = paper.get("fos", [])
    for tag in fos_tags:
        fos_set.add(tag.strip())

fos_list = sorted(list(fos_set))  # Keep consistent ordering
print(f"🧠 Found {len(fos_list)} unique FOS tags.")

# --------------------------
# Step 2: Use OpenAlex API to get FOS parents (1-level up)
# --------------------------
base_url = "https://api.openalex.org/concepts?filter=display_name.search:"
fos_hierarchy = defaultdict(list)

print("🔍 Querying OpenAlex for FOS parent relationships...")
for fos in tqdm(fos_list):
    try:
        time.sleep(1.0)  # be polite
        response = requests.get(base_url + requests.utils.quote(fos))
        data = response.json()
        if "results" in data and data["results"]:
            top_result = data["results"][0]
            ancestors = top_result.get("ancestors", [])
            for anc in ancestors:
                fos_hierarchy[fos].append(anc["display_name"])
    except Exception as e:
        print(f"Failed for {fos}: {e}")

# Save hierarchy
with open(HIERARCHY_JSON, "w", encoding="utf8") as f:
    json.dump(fos_hierarchy, f, indent=2)
print(f"Saved hierarchy to {HIERARCHY_JSON}")

# --------------------------
# Step 3: Create FOS similarity matrix
# --------------------------
fos_index = {fos: idx for idx, fos in enumerate(fos_list)}
N = len(papers)
fos_matrix = np.zeros((N, N))

def compute_fos_similarity(fos_a, fos_b):
    set_a = set(fos_a)
    set_b = set(fos_b)
    shared = set_a & set_b
    if not shared:
        return 0.0
    return len(shared) / (len(set_a | set_b))  # Jaccard similarity

for i in tqdm(range(N), desc="Building FOS similarity matrix"):
    fos_i = papers[i].get("fos", [])
    for j in range(N):
        if i == j:
            continue
        fos_j = papers[j].get("fos", [])
        fos_matrix[i][j] = compute_fos_similarity(fos_i, fos_j)

# Save similarity matrix
np.save(SIM_MATRIX_FILE, fos_matrix)
print(f"Saved FOS similarity matrix: {SIM_MATRIX_FILE}")
