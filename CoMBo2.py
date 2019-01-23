import numpy as np
from numpy.core.umath_tests import inner1d
from copy import deepcopy
import pandas as pd


class CoMBo2(object):
    def __init__(self, *args, **kwargs):
        if kwargs and args:
            raise ValueError(
                '''AdaBoostClassifier can only be called with keyword
                   arguments for the following keywords: base_estimator ,n_estimators,
                    learning_rate,algorithm,random_state''')
        allowed_keys = ['base_estimator', 'n_estimators', 'learning_rate', 'random_state']
        keywords_used = kwargs.keys()
        for keyword in keywords_used:
            if keyword not in allowed_keys:
                raise ValueError(keyword + ":  Wrong keyword used --- check spelling")

        n_estimators = 50
        learning_rate = 1
        random_state = None

        if kwargs and not args:
            if 'base_estimator' in kwargs:
                base_estimator = kwargs.pop('base_estimator')
            else:
                raise ValueError('''base_estimator can not be None''')
            if 'n_estimators' in kwargs: n_estimators = kwargs.pop('n_estimators')
            if 'learning_rate' in kwargs: learning_rate = kwargs.pop('learning_rate')
            if 'random_state' in kwargs: random_state = kwargs.pop('random_state')

        self.base_estimator_ = base_estimator
        self.n_estimators_ = n_estimators
        self.learning_rate_ = learning_rate
        self.random_state_ = random_state
        self.estimators_ = list()
        self.estimator_weights_ = np.zeros(self.n_estimators_)
        self.estimator_errors_ = np.ones(self.n_estimators_)


    def get_m(self, y):
        m = y.value_counts()
        return m


    def fit(self, X, y):
        self.n_samples = X.shape[0]
        # There is hidden trouble for classes, here the classes will be sorted.
        # So in boost we have to ensure that the predict results have the same classes sort
        self.classes_ = np.array(sorted(list(set(y))))
        self.n_classes_ = len(self.classes_)
        self.m = self.get_m(y)
        #print(self.m)
        # init score functions
        f = np.zeros([self.n_samples, self.n_classes_])
        self.score_functions = list()
        self.score_functions.append(f)

        self.cost_matrices = list()
        #print(self.m[1])

        d = [[1.0 / self.m[int(y[i])] if int(y[i]) != int(l) else -(self.n_classes_ - 1) / self.m[int(y[i])] for i in
              range(self.n_samples)] for l in self.classes_]


        d = np.asarray(d)
        temp_d = pd.DataFrame(d)
        temp_d = temp_d.transpose()
        d = temp_d.as_matrix()

        self.cost_matrices.append(d)

        self.deltas = list()
        self.alphas = list()
        self.y_preds = list()

        for t in range(0, self.n_estimators_):
            D_t = self.CoMBoost(X, y, t)

            # append error and weight
            self.cost_matrices.append(D_t)

        return self




    def newD_func(self, i, y, t):
        newD_sum = 0
        for j in range(self.n_classes_):
            if j != y[i]:
                newD_sum += np.exp(self.score_functions[t+1][i, j] - self.score_functions[t+1][i, int(y[i])])

        return newD_sum


    def CoMBoost(self, X, y, t):
        classifier = deepcopy(self.base_estimator_)
        if self.random_state_:
            classifier.set_params(random_state=1)

        classifier.fit(X, y)

        # compute error
        y_pred = classifier.predict(X)
        self.y_preds.append(y_pred)

        i = np.arange(self.n_samples)
        delta1 = np.sum(self.cost_matrices[t][i, y_pred.astype(int)])
        #print(delta1)
        #l = np.arange(self.n_classes_)

        # for every sample: for every class that isn't equal to the actual train_y class for sample i, here is the class
        # makes arrays of length 13, e.g. containing all classes that AREN'T this sample's/row's true class
        #l_s = [[l_val for l_val in l if l_val != y[l_i].astype(int)] for l_i in range(self.n_samples)]
        l_s = [[int(l_val) for l_val in self.classes_ if int(l_val) != y[l_i].astype(int)] for l_i in range(self.n_samples)]
        #print(l_s[0])
        # expand i so that there are 13 i's to go with the 13 l values that don't equal the actual training class
        i_expanded = [[i_val for l_val in range(self.n_classes_ - 1)] for i_val in i]
        #print(i_expanded[0])



        delta2 = np.sum(self.cost_matrices[t][i_expanded, l_s])
        #print(delta2)

        #delta2 = np.sum(self.cost_matrices[t][i_expanded, l_s])

        #for i in range(0, self.n_samples):
         #   delta1 += self.cost_matrices[t][i, int(y_pred[i])]
          #  for l in range(0, self.n_classes_):
           #     if l != int(y[i]):
            #        delta2 += self.cost_matrices[t][i, l]

        delta = - delta1 / delta2
        print(delta)
        self.deltas.append(delta)

        alpha = np.log((1 + delta) / (1 - delta)) / 2.0
        self.alphas.append(alpha)

        # for calculating score functions matrix f
        f_t = np.zeros([self.n_samples, self.n_classes_])
        for z in range(t):
            clf_same = [[1 if y_val == int(l_val) else 0 for y_val in self.y_preds[z]] for l_val in self.classes_]
            h = pd.DataFrame(clf_same)
            h = h.transpose()
            h_matrix = h.as_matrix()
            f_t += self.alphas[z] * h_matrix

        self.score_functions.append(f_t)

        newD = [[(np.exp(f_t[i, int(l)] - f_t[i, int(y[i])]) / self.m[int(y[i])]) if int(l) != y[i] else (
        - self.newD_func(i, y, t) / self.m[int(y[i])]) for i in range(self.n_samples)] for l in self.classes_]


        newD_temp = pd.DataFrame(newD)
        newD_temp = newD_temp.transpose()
        D_t = newD_temp.as_matrix()

        #f_t = np.zeros([self.n_samples, self.n_classes_])
        #d_t = np.zeros([self.n_samples, self.n_classes_])

        #for i in range(0, self.n_samples):
         #   for l in range(0, self.n_classes_):
          #      if l != int(y[i]):
           #         f_t[i, l], f_t[i, int(y[i])] = self.f(i, l, y[i], t)
            #
             #       d_t[i, l] = np.exp(f_t[i, l] - f_t[i, int(y[i])]) / self.m[int(y[i])]
              #  else:
               #     for j in range(0, self.n_classes_):
                #        if j != int(y[i]):
                 #         f_t[i, int(y[i])] = self.f(i, y[i], t, alpha)
                  #
                   #         d_t[i, l] = - np.exp(f_t[i, j] - f_t[i, int(y[i])]) / self.m[int(y[i])]


        #self.score_functions[t+1] = f_t
        self.estimators_.append(classifier)

        return D_t


    def predict(self, X):
        n_classes = self.n_classes_
        classes = self.classes_[:, np.newaxis]
        pred = None

        pred = sum((estimator.predict(X) == classes).T * alpha
                   for estimator, alpha in zip(self.estimators_,
                                               self.alphas))

        pred /= sum(self.alphas)

        return self.classes_.take(np.argmax(pred, axis=1), axis=0)