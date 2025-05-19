# 看不同種病的統計資料
import pandas as pd
def main():
    train = pd.read_csv("data/train_label.csv")["Class"].value_counts().sort_index()
    test  = pd.read_csv("data/test_label.csv")["Class"].value_counts().sort_index()
    print("== Train ==")
    for d, n in train.items():
        print(f"{d}: {n}")

    print("\n\n== Test ==")
    for d, n in test.items():
        print(f"{d}: {n}")
        
if __name__ == "__main__":
    main()
