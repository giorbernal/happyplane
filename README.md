# Happy-Plane
In this project we are going to try to implement an AI (Reinforcement Learning) Algorithm to allocate passengers in an airplane.

## Problem set up
The problem is as follows, we have a **definition file** like this:
```
4 4
1w 2 3
4 5 6
7 8 9w
10 11 12 13 14
15 16
```

when each row represents next:
1) Dimensions of the plane (to be accurate, a *side* of the plane), 4 rows with 4 sites each row.
2) Group 1 of 3 passengers, number one require to be next to the window. (left site of a row)
3) Group 2 of 3 passengers.
4) Group 3 of 3 pasengers. number 9 require to be next to the wondow.
5) Group 4 of 5 passengers.
6) Group 5 of 2 passengers.

We need to find an algorithm to satisfy this two requirements:
- Each Group wants to be at the same row. 
- Passengers that require a window should be next to a window.

We will try to fullfil this requirements by using a reinforcement learning algorithm

## Files Description
### Cases
- *planes/\**: folder that contains the diferent use cases. plane1.txt is the base case.

### Main Code
- *src/main/PlaneEnvironmet.py*: Contains the environment definition OpenAI style.
- *src/main/QLearningAlgorithm.py*: Contains the implementation of Q-Learning algorithm with Linear Regressor aproximation for Q Values.
- *src/main/PlaneEnv.ipynb*: Jupyter test of the rewards history to check the performance of the each algorithm (only Q-Learning so far). Click [here](https://github.com/giorbernal/happyplane/blob/master/src/main/PlaneEnv.ipynb) to get there.

### Test
- *src/test/PlainEnvTest.py*: This is the unit test file to check environment definition.

## Conclusions
So far, we have tested only **Q-Learning** algorithm and with it we have not reach an optimal solution. The reason seems to come from two ideas:
- There are a certain asymetry in actions. At environment, we have described X+1 actions. being X, the number of rows. Each 'x' action set a passenger at next free site in the row x. And the '+1' actions, rotate the passengers of the group to leave preference to the 'window requirer' one.
- Related to the previous point. The reward system is complex. As a first case,  we have tried to avoid give rewards in intermediate states. But this way, the algorithm did not reach an optimal allocation. So, we tested some intermidiate rewards. We did not succed improving the two requirements at the same time, when one was improved the other was worse.

It would be a good idea to try **Monte Carlo** Method. In this case could be a better choice as number of steps to complete an episode es really low. Maybe Q-Learning is not the best choice just for this case.

