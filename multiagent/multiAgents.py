# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions, Actions
import random, util
import itertools

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        # What we're aiming to do: greedily consume dots, maintaining a radius around pacman. If a move would bring pacman's radius into contact with a ghost, discourage that move.
        # To make this more efficient, we could add a clause about eating a ghost whenever able
        "*** YOUR CODE HERE ***"
        if successorGameState.isWin():
          return float('inf')
        if successorGameState.isLose():
          return float('-inf')
        score = successorGameState.getScore()        
        # If the action puts pacman within a radius 5 of a ghost, discourage it
        # 0 case should be covered by checking isLose(), but just in case...
        discourage = {0: -99999999,
                      1: -10000,
                      2: -50,
                      3: -25,
                      4: -12,
                      5: -6}
        ghosts = successorGameState.getGhostPositions()              
        ghostDist = []
        ghostFactor = 0
        for g in ghosts:
          ghostDist.append(util.manhattanDistance(newPos, g))
        for gd in ghostDist:
          if gd in discourage:
            ghostFactor = ghostFactor + discourage[gd]
        # If the action puts pacman within a radius 5 of a food pellet, encourage it (diminishing returns)
        encourage = {0: 100,
                    1: 50,
                    2: 25,
                    3: 12,
                    4: 6,
                    5: 3}
        closestFood = float('inf')
        foodFactor = 0
        for i in range(newFood.width):
          for j in range(newFood.height):
            if newFood[i][j]:
              closestFood = min(closestFood, util.manhattanDistance(newPos, (i, j)))
        if closestFood in encourage:
          foodFactor = foodFactor + encourage[closestFood]
        else:
          # 3 => 930.5
          # 6 => 1201.5
          # 10 => 1201.1
          # 12 => 1155.0
          # 25 => 1040.2
          # Need some sort of foodFactor regardless of whether or not the proximity radius triggers, or an infinite loop can occur because the action is chosen randomly
          foodFactor = 6/closestFood
        score = score + ghostFactor + foodFactor
        # If the action itself would result in eating a food, strongly encourage it; without this, pacman sometimes doesn't eat an adjacent dot because the code above only checks state after the action is taken
        if currentGameState.getFood()[newPos[0]][newPos[1]]:
          score = score + 100
        return score

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game

          gameState.isWin():
            Returns whether or not the game state is a winning state

          gameState.isLose():
            Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"  
        def value(state, depth, agentNum): # value, maxvalue, and minvalue from lecture slides
          if agentNum == 0:
            return maxValue(state, depth, agentNum)
          else:
            return minValue(state, depth, agentNum)
        def maxValue(state, depth, agentNum):
          if state.isWin() or state.isLose() or depth == 0: 
            return self.evaluationFunction(state)
          v = float("-inf")
          legalMoves = state.getLegalActions(0) # pacman always 0
          for moves in legalMoves:
            sucState = state.generateSuccessor(0, moves)
            v = max(v, value(sucState, depth, 1)) #only need to add 1 because pacman is the maximizer
          return v
        def minValue(state, depth, agentNum):
          if state.isWin() or state.isLose(): #dont have to check for depth 0 because logic will never allow it here
            return self.evaluationFunction(state)
          v = float("inf")
          legalMoves = state.getLegalActions(agentNum)
          for moves in legalMoves:
            sucState = state.generateSuccessor(agentNum, moves)           
            if agentNum == numAgents - 1:
              v = min(v, value(sucState, depth - 1, 0))
            else:
              v = min(v, value(sucState, depth, agentNum + 1)) 
          return v
        numAgents = gameState.getNumAgents()
        legalActions = gameState.getLegalActions()
        minimaxMove = None
        score = float("-inf")
        for moves in legalActions:
            nextState = gameState.generateSuccessor(0, moves)
            oldscore = score #hold score
            score = max(score, value(nextState, self.depth, 1))
            if score > oldscore:
                minimaxMove = moves
        return minimaxMove
class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        def value(state, depth, agentNum, alpha, beta): # value, maxvalue, and minvalue from lecture slides
          if agentNum == 0:
            return maxValue(state, depth, agentNum, alpha, beta)
          else:
            return minValue(state, depth, agentNum, alpha, beta)
        def maxValue(state, depth, agentNum, alpha, beta):
          if state.isWin() or state.isLose() or depth == 0: 
            return self.evaluationFunction(state)
          v = float("-inf")
          legalMoves = state.getLegalActions(0) # pacman always 0
          for moves in legalMoves:
            sucState = state.generateSuccessor(0, moves)
            v = max(v, value(sucState, depth, 1, alpha, beta)) #only need to add 1 because pacman is the maximizer
            if v > beta:
              return v
            alpha = max(alpha, v)
          return v
        def minValue(state, depth, agentNum, alpha, beta):
          if state.isWin() or state.isLose(): #dont have to check for depth 0 because logic will never allow it here
            return self.evaluationFunction(state)
          v = float("inf")
          legalMoves = state.getLegalActions(agentNum)
          for moves in legalMoves:
            sucState = state.generateSuccessor(agentNum, moves)           
            if agentNum == numAgents - 1:
              v = min(v, value(sucState, depth - 1, 0, alpha, beta))
              if v < alpha:
                return v
              beta = min(beta, v)
            else:
              v = min(v, value(sucState, depth, agentNum + 1, alpha, beta)) 
              if v < alpha:
                return v
              beta = min(beta, v)
          return v
        numAgents = gameState.getNumAgents()
        legalActions = gameState.getLegalActions()
        alphabetaMove = None
        score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")
        for moves in legalActions:
            nextState = gameState.generateSuccessor(0, moves)
            oldscore = score #hold score
            score = max(score, value(nextState, self.depth, 1, alpha, beta))
            if score > oldscore:
                alphabetaMove = moves
            alpha = max(alpha, score)
        return alphabetaMove

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        def value(state, depth, agentNum): # value, maxvalue, and minvalue from lecture slides
          if agentNum == 0:
            return maxValue(state, depth, agentNum)
          else:
            return expectiValue(state, depth, agentNum)
        def maxValue(state, depth, agentNum):
          if state.isWin() or state.isLose() or depth == 0: 
            return self.evaluationFunction(state)
          v = float("-inf")
          legalMoves = state.getLegalActions(0) # pacman always 0
          for moves in legalMoves:
            sucState = state.generateSuccessor(0, moves)
            v = max(v, value(sucState, depth, 1)) #only need to add 1 because pacman is the maximizer
          return v
        def expectiValue(state, depth, agentNum):
          if state.isWin() or state.isLose(): #dont have to check for depth 0 because logic will never allow it here
            return self.evaluationFunction(state)
          v = 0
          legalMoves = state.getLegalActions(agentNum)
          probability = (1.0 / len(legalMoves))
          for moves in legalMoves:
            sucState = state.generateSuccessor(agentNum, moves)           
            if agentNum == numAgents - 1:
              v += value(sucState, depth - 1, 0)
            else:
              v += value(sucState, depth, agentNum + 1)
          return v * probability
        numAgents = gameState.getNumAgents()
        legalActions = gameState.getLegalActions()
        minimaxMove = None
        score = float("-inf")
        for moves in legalActions:
            nextState = gameState.generateSuccessor(0, moves)
            oldscore = score #hold score
            score = max(score, value(nextState, self.depth, 1))
            if score > oldscore:
                minimaxMove = moves
        return minimaxMove

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: Aggressively eats dots, with a bonus towards actions that would put pacman closer to a capsule.
      Next step would be to hunt ghosts, work in progress.
    """
    "*** YOUR CODE HERE ***"
    # Useful information you can extract from a GameState (pacman.py)   
    newPos = currentGameState.getPacmanPosition()
    newFood = currentGameState.getFood()
    newGhostStates = currentGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

    # Check basic Win/Lose conditions 
    if currentGameState.isWin():
      return float('inf')
    if currentGameState.isLose():
      return float('-inf')
    score = currentGameState.getScore()

    # Ghost Factor using flat cost
    # Work in progress: move towards ghosts and eat them if the scared timers permit it
    ghosts =currentGameState.getGhostPositions()   
    ghostDist = []
    for g in ghosts:
      ghostDist.append(util.manhattanDistance(newPos, g))
    dead = 0
    if dead in ghostDist:
      return float('-inf')
    else:
      ghostFactor = -100 * len(ghosts)    

    # Food Factor using reciprocal value of distance
    closestFood = float('inf')
    for i in range(newFood.width):
      for j in range(newFood.height):
        if newFood[i][j]:
          closestFood = min(closestFood, util.manhattanDistance(newPos, (i, j)))
    # Apparently returns Directions.STOP? occasionally when 10 is an integer instead of a float, causing "Illegal Action: None"
    foodFactor = 10.0/closestFood

    # Capsule Factor using reciprocal value of distance
    # Take into account all capsules, using only the closest capsule results in a lower score
    capsules = currentGameState.getCapsules()
    # closestCapsule = 999
    capsuleFactor = 0
    for c in capsules:
      capsuleDist = util.manhattanDistance(newPos, c)
      # Either double the distance, or there's a closer capsule that can be visited
      capsuleFactor = capsuleFactor + max(capsuleFactor, 10/capsuleDist)

    # Summation of factors for score calculation
    score = score + ghostFactor + foodFactor + capsuleFactor
    return score


# Abbreviation
better = betterEvaluationFunction

