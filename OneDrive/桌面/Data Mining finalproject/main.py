from __future__ import annotations
import argparse 
from collections import Counter
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from dataset import GeneDataset
from classification import classifier_controller
from clustering import unknown_detector, kmeans


def  vote_and_map(cluster_labels, true_labels): 
    mapping = {}
    for cluster_id in np.unique(cluster_labels): 
        # map to the majority true label based on the cluster
        members = cluster_labels == cluster_id
        majority = Counter(true_labels[members]).most_common(1)[0][0]
        mapping[cluster_id] = majority
    return mapping

def run(classify_name, x_train, y_train, x_test, y_test, *, theta, k, seed):
    classify = classifier_controller(classify_name)
    classify.fit(x_train, y_train)

    # split known/unkown
    known_idx, unknown_idx = unknown_detector(classify, x_test, theta)
    y_pred = np.empty_like(y_test, dtype=object)

    if known_idx.size:
        y_pred[known_idx] = classify.predict(x_test[known_idx])
    cluster_counter = 0
    if unknown_idx.size:
        x_unknown = x_test[unknown_idx]
        cluster_labels = kmeans(x_unknown, k=k,seed=seed)
        cluster_counter = k
        mapping = vote_and_map(cluster_labels, y_test[unknown_idx])
        y_pred[unknown_idx] = np.array([mapping[c] for c in cluster_labels], dtype=object)

    # eval
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    result = {
        "clf": classify_name,
        "acc": acc,
        "prec": prec,
        "rec": rec,
        "f1": f1,
        "known": int(known_idx.size),
        "unk": int(unknown_idx.size),
        "clusters": cluster_counter,
        "cm": cm,}
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--theta", type=float, default=0.9, help="unknown threshold")
    parser.add_argument("--k", type=int, default=2, help="k for K‑Means")
    parser.add_argument("--seed", type=int, default=40)
    parser.add_argument("--show_cm", action="store_true", help="print confusion matrices")
    args = parser.parse_args()

    ds = GeneDataset()
    x_train, y_train = ds.get_train()
    x_test, y_test = ds.get_test()
    classifiers = ["svm", "logreg", "rf"]
    results = []
    for classify_name in classifiers:
        result = run(classify_name,x_train,y_train,x_test,y_test,theta=args.theta,k=args.k,seed=args.seed)
        results.append(result)
    
    svm_res = next(r for r in results if r["clf"] == "svm")
    labels = np.unique(y_test)
    df = pd.DataFrame(svm_res["cm"], index=labels, columns=labels)
    df["Total"] = df.sum(axis=1)         
    df.to_csv("baseline_svm_confusion.csv", index_label="True/Pred")

    print("\nbaseline result:")
    header="#  Classifier  Clu.  Acc.   Prec.  Rec.   F1   Known  Unknown"
    print(header)
    print("-"*len(header))
    for i, r in enumerate(results, 1):
        print(
            f"{i:<3}{r['clf']:^11}{r['clusters']:^6}"
            f"{r['acc']:.3f} {r['prec']:.3f} {r['rec']:.3f} {r['f1']:.3f} "
            f"{r['known']:^7}{r['unk']:^9}"
        )
    # chosen parameter
    print(f"Params  θ={args.theta}  k={args.k}  seed={args.seed}\n")
    if args.show_cm:
        for i, r in enumerate(results, 1):
            print(f"\n=== Confusion Matrix {i} ({r['clf']}) ===")
            print(r['cm'])

if __name__ == '__main__':
    main()


