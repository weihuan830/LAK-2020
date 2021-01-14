import numpy as np
from numpy import dot
from numpy.linalg import norm
from sklearn.svm import SVC
from sklearn.model_selection import KFold
from sklearn.neural_network import MLPClassifier
from sklearn import tree
from sklearn import linear_model
import matplotlib.pyplot as plt
import json
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import AdaBoostClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn import ensemble
from sklearn import datasets

class model:
    nsp = 2
    def data_KF(self):
        # [6760.8, 155, 0.1181274431010222, 0.10719225449515905, 0.12903225806451613, 17, 123.1450542670388, 114.62330297616656, 1.5342155458838798, 152.5757201526707, 154.147007179132, 1.428656635799412, 0.14203053982352407, 0.08456832103549808, -0.01063006893889186, 0.12458022979547259, 0.08293802443596311, 0.26190061534262693, 0.12458022979547259, 0.08293802443596311, 0.26190061534262693, 24.93103448275862, 11.97931267829687, -0.7523606742143267, 57233.102, 0.3132780082987552, 1447, 100, 1, '23173', '2350x67dbe3cf12d34feb', '2019-05-30 15:44:04']
        data = []
        with open("data.json", "r") as f:
            data = json.loads(f.readline())
        arrX = []
        arrY = []
        for item in data:
            arrX.append(item[0:len(item)-5])
            if item[len(item)-5]==100:
                arrY.append(0)
            # elif item[len(item)-5]>=80:
            #     arrY.append(2)
            else:
                arrY.append(1)
        X = np.array( arrX )
        y = np.array( arrY )
        kf = KFold(n_splits=self.nsp, random_state=10, shuffle=False)
        kf.get_n_splits(X)
        return kf,X,y

    def model_svm(self):
        kf,X,y = self.data_KF()
        avg = 0
        for train_index, test_index in kf.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            clf = SVC(C=2.0, kernel='rbf', degree=3, gamma='auto', coef0=0.0, shrinking=True, probability=False, tol=1e-4, cache_size=200, class_weight=None, verbose=False, max_iter=-1, decision_function_shape='ovo',random_state=None)
            clf = linear_model.SGDClassifier(max_iter=1000, tol=1e-3)
            clf.fit(X_train, y_train)
            result = clf.predict(X_test)
            count0 = 0
            for index in range(len(result)):
                if result[index] == y_test[index]:
                    count0 += 1
            avg += count0/len(result)
        return avg/self.nsp
    
    def model_SGD(self):
        kf,X,y = self.data_KF()
        avg = 0
        for train_index, test_index in kf.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            clf = linear_model.SGDClassifier(max_iter=1000, tol=1e-3)
            clf.fit(X_train, y_train)
            result = clf.predict(X_test)
            count0 = 0
            for index in range(len(result)):
                if result[index] == y_test[index]:
                    count0 += 1
            avg += count0/len(result)
        return avg/self.nsp

    def model_Rcov(self):
        kf,X,y = self.data_KF()
        avg = 0
        for train_index, test_index in kf.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(150, 120), random_state=1)
            clf.fit(X_train, y_train)
            result = clf.predict(X_test)
            count0 = 0
            for index in range(len(result)):
                if result[index] == y_test[index]:
                    count0 += 1
            avg += count0/len(result)
        print( avg/self.nsp )

    def plot_results(self, predicted_data, true_data):
        fig = plt.figure(facecolor='white')
        ax = fig.add_subplot(111)
        ax.plot(true_data, label='True Data')
        for index in range(0,len(predicted_data)):
            plt.plot(predicted_data[index], label=('Prediction'+str(index)))
        plt.legend()
        plt.show()

    def model_KNN(self):
        kf,X,y = self.data_KF()
        avg = 0
        for train_index, test_index in kf.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            clf = KNeighborsClassifier(n_neighbors=500)
            clf.fit(X_train, y_train)
            result = clf.predict(X_test)
            count0 = 0
            for index in range(len(result)):
                if result[index] == y_test[index]:
                    count0 += 1
            avg += count0/len(result)
            # print(result)
        return avg/self.nsp

    def model_LOF(self):
        kf,X,y = self.data_KF()
        avg = 0
        for train_index, test_index in kf.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            clf = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
            clf.fit(X_train, y_train)
            result = clf.fit_predict(X_test)
            count0 = 0
            for index in range(len(result)):
                if result[index] == y_test[index]:
                    count0 += 1
            avg += count0/len(result)
            # print(result)
        return avg/self.nsp

    def model_adaBoost(self):
        kf,X,y = self.data_KF()
        avg = 0
        for train_index, test_index in kf.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            clf = AdaBoostClassifier(n_estimators=4, random_state=10)
            clf.fit(X_train, y_train)
            result = clf.predict(X_test)
            count0 = 0
            for index in range(len(result)):
                if result[index] == y_test[index]:
                    count0 += 1
            avg += count0/len(result)
            # print(result)
        return avg/self.nsp
    
    def model_GPC(self):
        kf,X,y = self.data_KF()
        avg = 0
        for train_index, test_index in kf.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            kernel = 1.0 * RBF(1.0)
            gpc = GaussianProcessClassifier(kernel=kernel, random_state=0).fit(X, y)
            result = gpc.predict_proba(X_test)
            count0 = 0
            for index in range(len(result)):
                if result[index] == y_test[index]:
                    count0 += 1
            avg += count0/len(result)
            # print(result)
        return avg/self.nsp

obj = model()
st = ""
for i in range(2, 7):
    obj.nsp = i
    # obj.modeGBDT()
    # st = st + str(round(obj.model_svm(),3)) + ", "
    # obj.model_Rcov()
    # obj.model_KNN()
    # st += str(round(obj.model_LOF(), 3)) + ", "
    # st += str(round(obj.model_SGD(), 3)) + ", "
    st += str(round(obj.model_adaBoost(), 3)) + ", "
print(st)
