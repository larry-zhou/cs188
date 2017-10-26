# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        iterations = self.iterations
        states = self.mdp.getStates()
        for i in range(iterations):
          # for some reason, not making a copy created weird problems
          values = self.values.copy()
          for state in states:
            # set value to an infinitely small number
            value = float("-inf")
            # if the state is terminal, then it has a value of 0
            if self.mdp.isTerminal(state):
              value = 0
            # find the qValues and return the max qValue
            for action in self.mdp.getPossibleActions(state):
              qValue = self.computeQValueFromValues(state,action)
              # set value equal to the max of value and qValue
              value = max(value, qValue)
            # put it inside the dictionary
            values[state] = value
            #save the values back into self
          self.values = values

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        discount = self.discount
        tnp = self.mdp.getTransitionStatesAndProbs(state, action)
        qValue = 0
        # tnpPair is in the format (nextState, probability)
        for tnpPair in tnp:
          # extracting some info
          st = tnpPair[0]
          prob = tnpPair[1]
          reward = self.mdp.getReward(state, action, state)
          value = self.getValue(st)
          # formula from lecture
          qValue += prob * (reward + discount * value)
        return qValue


    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        # using qValue to find the best action
        qValue = float("-inf")
        bestAction = None
        possibleActions = self.mdp.getPossibleActions(state)
        for action in possibleActions:
          value = self.computeQValueFromValues(state, action)
          if value > qValue:
            bestAction, qValue = action, value
        return bestAction

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        iterations = self.iterations
        states = self.mdp.getStates()
        numStates = len(states)
        value = float("-inf")
        for i in range(iterations):
          # for some reason, not making a copy created weird problems
          values = self.values.copy()

          state = states[i%numStates]
          # set value to an infinitely small number
          value = float("-inf")
          # if the state is terminal, then it has a value of 0
          if self.mdp.isTerminal(state):
            value = 0
          # find the qValues and return the max qValue
          for action in self.mdp.getPossibleActions(state):
            qValue = self.computeQValueFromValues(state,action)
            # set value equal to the max of value and qValue
            value = max(value, qValue)
          # put it inside the dictionary
          values[state] = value
            #save the values back into self
          self.values = values

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        theta = self.theta
        maxQ = None
        states = self.mdp.getStates()
        iterations = self.iterations
        dictionary = {}
        # When you compute predecessors of a state, make sure to store them in a set, not a list, to avoid duplicates.
        for state in states:
          dictionary[state] = set() 
        pQ = util.PriorityQueue()
        for state in states:
          if not self.mdp.isTerminal(state):
            for action in self.mdp.getPossibleActions(state):
              tnp = self.mdp.getTransitionStatesAndProbs(state, action)
              for tnpPair in tnp:
                # extracting some info
                st = tnpPair[0]
                prob = tnpPair[1]
                dictionary[st].add(state)
              qValue = self.getQValue(state, action)
              maxQ = max(maxQ, qValue)
            diff = abs(self.getValue(state) - maxQ)
            maxQ = None
            pQ.push(state, -diff)
        # following the second part of what is online
        for i in range(iterations):
          maxQ = None
          if pQ.isEmpty():
            return
          state = pQ.pop()
          for action in self.mdp.getPossibleActions(state):
            qValue = self.getQValue(state, action)
            maxQ = max(maxQ, qValue)
          self.values[state] = maxQ
          for predecessor in dictionary[state]:
            maxQ = None
            # third time doing this, might want to make a helper function
            for action in self.mdp.getPossibleActions(predecessor):
              qValue = self.getQValue(predecessor, action)
              maxQ = max(maxQ, qValue)
            diff = abs(self.values[predecessor] - maxQ)
            if diff > theta:
              pQ.update(predecessor, -diff)