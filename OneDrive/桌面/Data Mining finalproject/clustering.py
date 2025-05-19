import numpy as np
def unknown_detector(model, x, theta=0.9):
    probability = model.predict_proba(x)
    unknown = np.where(probability.max(axis=1) < theta)[0]
    known   = np.where(probability.max(axis=1) >= theta)[0]
    return known, unknown

def kmeans(x, k=2, max_iter=100, restarts=10, tolerance=1e-4, seed=40):
    rng = np.random.default_rng(seed)
    best_labels = None 
    best_sse = np.inf
    n_samples = x.shape[0]
    for _ in range(restarts):
        # randomly pick
        init_idx = rng.choice(n_samples, size=k, replace=False)
        centroids = x[init_idx]
        for _ in range(max_iter):
            distances = np.linalg.norm(x[:, None, :] - centroids[None, :, :], axis=2)
            cluster_labels = distances.argmin(axis=1) # assign to the nearestt
            new_centroids = np.zeros_like(centroids)
            for i in range(k):
                members = cluster_labels == i  # The one assigned to clustering i
                if members.any():
                    new_centroids[i] = x[members].mean(axis=0) # The avg of the clustering i(as new centroid)
                else: # no one in this clustering (with very low prob just to ensure that)
                    rand_idx = rng.integers(n_samples)
                    new_centroids[i] = x[rand_idx]
            
            centroid_shift = np.linalg.norm(new_centroids - centroids)
            centroids = new_centroids
            if(centroid_shift < tolerance):
                break # considerd as unchanged iteration

        sse = ((x - centroids[cluster_labels]) ** 2).sum()
        if sse < best_sse: # better clustering way
            best_sse = sse
            best_labels = cluster_labels.copy()
    return best_labels


# dbscan issue:無法分出群
'''
def dbscan(x, eps=1.5, min_samples=5):
    n_samples = x.shape[0]
    labels = -np.ones(n_samples, dtype=int)   # noise by default
    cluster = 0                       

    # compute distance and store it (for acceleration)
    difference = x[:, None, :] - x[None, :, :]      # (n, n, d)
    distances = np.linalg.norm(difference, axis=2)  # (n, n)

    for i in range(n_samples):
        if labels[i] != -1:
            continue

        neighbor = distances[i] <= eps
        neighbor_idxs = np.where(neighbor)[0]

        if neighbor_idxs.size < min_samples:
            labels[i] = -1 # noise
            continue
        labels[i] = cluster
        seeds = list(neighbor_idxs) # all neighboor

        # chain expansion
        while seeds:
            seed_idx = seeds.pop()
            if labels[seed_idx] == -1:
                labels[seed_idx] = cluster
            elif labels[seed_idx] != -1: # already be clustered
                continue
            labels[seed_idx] = cluster

            # other core point
            seed_neighbors = np.where(distances[seed_idx] <= eps)[0]
            if seed_neighbors.size >= min_samples:
                seeds.extend(seed_neighbors.tolist())

        cluster += 1
    return labels
'''

        




            