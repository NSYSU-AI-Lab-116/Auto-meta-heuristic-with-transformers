import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.decomposition import PCA
import os
class GeneDataset:
    def __init__(self, dir="data", var_threshold=0.0):
        self.dir=dir
        self.var_threshold=var_threshold
        self.loading()
        self.processing()
    
    def loading(self):
        df_temp = pd.read_csv(os.path.join(self.dir, "train_data.csv"),header=0)
        self.x_train = df_temp.drop("id", axis=1).to_numpy(dtype=np.float32)
        df_temp = pd.read_csv(os.path.join(self.dir, "train_label.csv"),header=0,usecols=["Class"])
        self.y_train = df_temp["Class"].to_numpy()
        df_temp = pd.read_csv(os.path.join(self.dir, "test_data.csv"),header=0)
        self.x_test = df_temp.drop("id", axis=1).to_numpy(dtype=np.float32)
        df_temp = pd.read_csv(os.path.join(self.dir, "test_label.csv"),header=0,usecols=["Class"])
        self.y_test = df_temp["Class"].to_numpy()
    def processing(self):
        if(self.var_threshold is not None):
            Vt = VarianceThreshold(self.var_threshold)
            self.x_train = Vt.fit_transform(self.x_train)
            self.x_test  = Vt.transform(self.x_test)

        Std = StandardScaler
        self.x_train = Std().fit_transform(self.x_train)
        self.x_test = Std().fit_transform(self.x_test)
    
        pca = PCA(n_components=100, random_state=0).fit(self.x_train)
        self.x_train = pca.transform(self.x_train)
        self.x_test  = pca.transform(self.x_test)
        #print(self.x_test.shape)
    def get_train(self):
        return self.x_train, self.y_train
    def get_test(self):
        return self.x_test, self.y_test

if __name__ == "__main__":
    ds = GeneDataset(var_threshold=0.0) # None -> 20531 & 0.0 -> 20242
    print()
    print("train:", ds.get_train()[0].shape, ds.get_train()[1].shape)
    #print("train:", ds.get_train()[0], ds.get_train()[1])
    print("test :", ds.get_test()[0].shape, ds.get_test()[1].shape)
    #print("test :", ds.get_test()[0], ds.get_test()[1])
