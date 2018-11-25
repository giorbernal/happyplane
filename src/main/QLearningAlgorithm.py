import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.pipeline import FeatureUnion
from sklearn.preprocessing import StandardScaler
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import SGDRegressor
from PlaneEnvironment import PlaneEnv

class FeatureTransformer:
    def __init__(self, env, n_components=500):
        observation_examples = self.__getObservations__(env, 1000)
        scaler = StandardScaler()
        scaler.fit(observation_examples)

        # Used to converte a state to a featurizes represenation.
        # We use RBF kernels with different variances to cover different parts of the space
        featurizer = FeatureUnion([
                ("rbf1", RBFSampler(gamma=5.0, n_components=n_components)),
                ("rbf2", RBFSampler(gamma=2.0, n_components=n_components)),
                ("rbf3", RBFSampler(gamma=1.0, n_components=n_components)),
                ("rbf4", RBFSampler(gamma=0.5, n_components=n_components))
                ])
        example_features = featurizer.fit_transform(scaler.transform(observation_examples))

        self.dimensions = example_features.shape[1]
        self.scaler = scaler
        self.featurizer = featurizer

    def transform(self, observations):
        # print "observations:", observations
        scaled = self.scaler.transform(observations)
        # assert(len(scaled.shape) == 2)
        return self.featurizer.transform(scaled)
    
    def __getObservations__(self, env, iters):
        data=[]
        for i in range(iters):
            env.reset()
            done = False
            while (done == False):
                action = env.action_space_sample()
                (x, reward, done, info) = env.step(action)
                data.append(x)
        return np.array(data)

# Holds one SGDRegressor for each action
class Model:
    def __init__(self, env, feature_transformer, learning_rate):
        self.env = env
        self.models = []
        self.feature_transformer = feature_transformer
        for i in range(env.action_space_n()):
            model = SGDRegressor(learning_rate=learning_rate, max_iter=1000, tol=1e-3)
            model.partial_fit(feature_transformer.transform( [env.reset()] ), [0])
            self.models.append(model)

    def predict(self, s):
        X = self.feature_transformer.transform([s])
        result = np.stack([m.predict(X) for m in self.models]).T
        assert(len(result.shape) == 2)
        return result

    def update(self, s, a, G):
        X = self.feature_transformer.transform([s])
        assert(len(X.shape) == 2)
        self.models[a].partial_fit(X, [G])

    def sample_action(self, s, eps):
        # eps = 0
        # Technically, we don't need to do epsilon-greedy
        # because SGDRegressor predicts 0 for all states
        # until they are updated. This works as the
        # "Optimistic Initial Values" method, since all
        # the rewards for Mountain Car are -1.
        if np.random.random() < eps:
              return self.env.action_space_sample()
        else:
              return np.argmax(self.predict(s))

class QLearning:
	def __init__(self, filePath):
		self.filePath=filePath

    # returns a list of states_and_rewards, and the total reward
	def __play_one__(self,model, env, eps, gamma):
		observation = env.reset()
		done = False
		totalreward = 0
		iters = 0
		ia1=0
		ia2=0
		ia3=0
		while not done and iters < 10000:
		    action = model.sample_action(observation, eps)
		    prev_observation = observation
		    (observation, reward, done, info) = env.step(action)
		    if ( (info['ia1']==True) | (info['ia2']==True) | (info['ia3']==True) ):
		        if (info['ia1']==True):
		            ia1 += 1
		        if (info['ia2']==True):
		            ia2 += 1
		        if (info['ia3']==True):
		            ia3 += 1
		        iters += 1
		        continue

		    # update the model
		    next = model.predict(observation)
		    # assert(next.shape == (1, env.action_space.n))
		    G = reward + gamma*np.max(next[0])
		    model.update(prev_observation, action, G)

		    totalreward += reward
		    iters += 1

		if (done == False):
		    print("WARN: More iterations required")

		return (totalreward, iters, ia1, ia2, ia3)

	def launch(self,show_plots=True, gamma=0.99, epsType='t2', slot=100, N=1000):
		env = PlaneEnv(self.filePath)
		ft = FeatureTransformer(env)
		model = Model(env, ft, "constant")

		totalrewards = np.empty(N)
		iterss = np.empty(N)
		ia1s = np.empty(N)
		ia2s = np.empty(N)
		ia3s = np.empty(N)
		for n in range(N):
		    if (epsType=='t1'):
		        eps = 1.0/(0.1*n+1)
		    if (epsType=='t2'):
		        eps = 0.1*(0.97**n)
		    if (epsType=='t3'):
		        eps = 1.0/np.sqrt(n+1)
		    if n == slot:
		        print("eps:", eps)
		    (totalreward, iters, ia1, ia2, ia3) = self.__play_one__(model, env, eps, gamma)
		    totalrewards[n] = totalreward
		    iterss[n] = iters
		    ia1s[n] = ia1
		    ia2s[n] = ia2
		    ia3s[n] = ia3

		    if (n + 1) % slot == 0:
		        print("episode:", n, "total reward:", totalreward, ",iters:",iters, ",ia1:",ia1, "ia2:", ia2, ",ia3:", ia3)
		        env.plane.drawPlane()
		    print("avg reward for last ", slot, " episodes:", totalrewards[max(n-slot,0):n].mean())
		    #print("total steps:", -totalrewards.sum())

		env.plane.drawPlane()
		return (totalrewards,ia3s)

