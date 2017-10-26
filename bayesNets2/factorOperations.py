# factorOperations.py
# -------------------
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


from bayesNet import Factor
import operator as op
import util

def joinFactorsByVariableWithCallTracking(callTrackingList=None):


    def joinFactorsByVariable(factors, joinVariable):
        """
        Input factors is a list of factors.
        Input joinVariable is the variable to join on.

        This function performs a check that the variable that is being joined on 
        appears as an unconditioned variable in only one of the input factors.

        Then, it calls your joinFactors on all of the factors in factors that 
        contain that variable.

        Returns a tuple of 
        (factors not joined, resulting factor from joinFactors)
        """

        if not (callTrackingList is None):
            callTrackingList.append(('join', joinVariable))

        currentFactorsToJoin =    [factor for factor in factors if joinVariable in factor.variablesSet()]
        currentFactorsNotToJoin = [factor for factor in factors if joinVariable not in factor.variablesSet()]

        # typecheck portion
        numVariableOnLeft = len([factor for factor in currentFactorsToJoin if joinVariable in factor.unconditionedVariables()])
        if numVariableOnLeft > 1:
            print "Factor failed joinFactorsByVariable typecheck: ", factor
            raise ValueError, ("The joinBy variable can only appear in one factor as an \nunconditioned variable. \n" +  
                               "joinVariable: " + str(joinVariable) + "\n" +
                               ", ".join(map(str, [factor.unconditionedVariables() for factor in currentFactorsToJoin])))
        
        joinedFactor = joinFactors(currentFactorsToJoin)
        return currentFactorsNotToJoin, joinedFactor

    return joinFactorsByVariable

joinFactorsByVariable = joinFactorsByVariableWithCallTracking()


def joinFactors(factors):
    """
    Question 3: Your join implementation 

    Input factors is a list of factors.  
    
    You should calculate the set of unconditioned variables and conditioned 
    variables for the join of those factors.

    Return a new factor that has those variables and whose probability entries 
    are product of the corresponding rows of the input factors.

    You may assume that the variableDomainsDict for all the input 
    factors are the same, since they come from the same BayesNet.

    joinFactors will only allow unconditionedVariables to appear in 
    one input factor (so their join is well defined).

    Hint: Factor methods that take an assignmentDict as input 
    (such as getProbability and setProbability) can handle 
    assignmentDicts that assign more variables than are in that factor.

    Useful functions:
    Factor.getAllPossibleAssignmentDicts
    Factor.getProbability
    Factor.setProbability
    Factor.unconditionedVariables
    Factor.conditionedVariables
    Factor.variableDomainsDict
    """

    # typecheck portion
    setsOfUnconditioned = [set(factor.unconditionedVariables()) for factor in factors]
    if len(factors) > 1:
        intersect = reduce(lambda x, y: x & y, setsOfUnconditioned)
        if len(intersect) > 0:
            print "Factor failed joinFactors typecheck: ", factor
            raise ValueError, ("unconditionedVariables can only appear in one factor. \n"
                    + "unconditionedVariables: " + str(intersect) + 
                    "\nappear in more than one input factor.\n" + 
                    "Input factors: \n" +
                    "\n".join(map(str, factors)))


    "*** YOUR CODE HERE ***"
    # Given two factors to be joined:
    # 1. Conditional factors stay conditional
    # 2. Factors that are conditional in one set but not the other are conditional
    # 3. Factors that are unconditional in both sets or unconditional in one and absent in the other stay unconditional   
    # Should work similar to XOR operation; think of it as a Venn diagram where the intersection is considered conditional
    vDD = factors[0].variableDomainsDict()
    result = factors[0]
    i = 1
    while i < len(factors):
        factor = factors[i]
        # Make the info from the previous factors into sets
        resultuncon = set(result.unconditionedVariables())
        resultcon = set(result.conditionedVariables())

        # Make the info from the current factor f into sets
        factoruncon = set(factor.unconditionedVariables())
        factorcon = set(factor.conditionedVariables())

        allresult = resultuncon.union(resultcon)
        allfactor = factoruncon.union(factorcon)

        check = allresult.intersection(allfactor)

        # All unconditional
        allu = resultuncon.union(factoruncon)
        # All conditional
        allc = (allresult.difference(allu)).union(allfactor.difference(allu))

        updated = Factor(list(allu), list(allc), vDD)   

        factora = factor.getAllPossibleAssignmentDicts()
        resulta = result.getAllPossibleAssignmentDicts()
        for a in factora:
            for b in resulta:
                for key in check:
                    # Make sure the assignments are equivalent in both sets of factors
                    if a[key] is not b[key]:
                        break
                else:
                    # Make a shallow copy of a and add all the values from b
                    cpy = a.copy()
                    for key in b:
                        cpy[key] = b[key]
                    updated.setProbability(cpy, factor.getProbability(a)*result.getProbability(b))

        result = updated

        i += 1
    return result

def eliminateWithCallTracking(callTrackingList=None):

    def eliminate(factor, eliminationVariable):
        """
        Question 4: Your eliminate implementation 

        Input factor is a single factor.
        Input eliminationVariable is the variable to eliminate from factor.
        eliminationVariable must be an unconditioned variable in factor.
        
        You should calculate the set of unconditioned variables and conditioned 
        variables for the factor obtained by eliminating the variable
        eliminationVariable.

        Return a new factor where all of the rows mentioning
        eliminationVariable are summed with rows that match
        assignments on the other variables.

        Useful functions:
        Factor.getAllPossibleAssignmentDicts
        Factor.getProbability
        Factor.setProbability
        Factor.unconditionedVariables
        Factor.conditionedVariables
        Factor.variableDomainsDict
        """
        # autograder tracking -- don't remove
        if not (callTrackingList is None):
            callTrackingList.append(('eliminate', eliminationVariable))

        # typecheck portion
        if eliminationVariable not in factor.unconditionedVariables():
            print "Factor failed eliminate typecheck: ", factor
            raise ValueError, ("Elimination variable is not an unconditioned variable " \
                            + "in this factor\n" + 
                            "eliminationVariable: " + str(eliminationVariable) + \
                            "\nunconditionedVariables:" + str(factor.unconditionedVariables()))
        
        if len(factor.unconditionedVariables()) == 1:
            print "Factor failed eliminate typecheck: ", factor
            raise ValueError, ("Factor has only one unconditioned variable, so you " \
                    + "can't eliminate \nthat variable.\n" + \
                    "eliminationVariable:" + str(eliminationVariable) + "\n" +\
                    "unconditionedVariables: " + str(factor.unconditionedVariables()))

        "*** YOUR CODE HERE ***"
        factoru = factor.unconditionedVariables()
        factorc = factor.conditionedVariables()
        vDD = factor.variableDomainsDict()
        e = eliminationVariable
        # Delete the elimination variable
        if e in factoru:
            factoru.remove(e)
        if e in factorc:
            factorc.remove(e)
        if e in vDD:
            del vDD[e]
        # Remake factor and prepare to change probabilities
        result = Factor(factoru, factorc, vDD)
        resulta = result.getAllPossibleAssignmentDicts()
        factora = factor.getAllPossibleAssignmentDicts()
        for a in resulta:
            p = 0
            for b in factora:
                # Make sure assignments match before updating
                if checkmatch(a, b):
                    p = p + factor.getProbability(b)
            result.setProbability(a, p)
        return result       

    return eliminate

eliminate = eliminateWithCallTracking()

def checkmatch(factor1, factor2):
    for key in factor1:
        if not (factor1[key] is factor2[key]):
            return False
    return True


def normalize(factor):
    """
    Question 5: Your normalize implementation 

    Input factor is a single factor.

    The set of conditioned variables for the normalized factor consists 
    of the input factor's conditioned variables as well as any of the 
    input factor's unconditioned variables with exactly one entry in their 
    domain.  Since there is only one entry in that variable's domain, we 
    can either assume it was assigned as evidence to have only one variable 
    in its domain, or it only had one entry in its domain to begin with.
    This blurs the distinction between evidence assignments and variables 
    with single value domains, but that is alright since we have to assign 
    variables that only have one value in their domain to that single value.

    Return a new factor where the sum of the all the probabilities in the table is 1.
    This should be a new factor, not a modification of this factor in place.

    If the sum of probabilities in the input factor is 0,
    you should return None.

    This is intended to be used at the end of a probabilistic inference query.
    Because of this, all variables that have more than one element in their 
    domain are assumed to be unconditioned.
    There are more general implementations of normalize, but we will only 
    implement this version.

    Useful functions:
    Factor.getAllPossibleAssignmentDicts
    Factor.getProbability
    Factor.setProbability
    Factor.unconditionedVariables
    Factor.conditionedVariables
    Factor.variableDomainsDict
    """

    # typecheck portion
    variableDomainsDict = factor.variableDomainsDict()
    for conditionedVariable in factor.conditionedVariables():
        if len(variableDomainsDict[conditionedVariable]) > 1:
            print "Factor failed normalize typecheck: ", factor
            raise ValueError, ("The factor to be normalized must have only one " + \
                            "assignment of the \n" + "conditional variables, " + \
                            "so that total probability will sum to 1\n" + 
                            str(factor))

    # Your normalize should return a new Factor.
    # normalize does not affect probability distributions (since probability distributions must already sum to 1).
    # For a general normalize operation, which variables are unconditioned in the returned Factor? 
    # Which variables are conditioned? Make sure to read the docstring of normalize for more instructions.
    # Remember that Factors store the variableDomainsDict of the original BayesNet, and not only the unconditioned and conditioned variables that they use. 
    # As a result, the returned Factor should have the same variableDomainsDict as the input Factor.
    "*** YOUR CODE HERE ***"
    factors = factor.variableDomainsDict()
    unconditioned = factor.unconditionedVariables()
    conditioned = factor.conditionedVariables()
    for key in factors:
        if len(factors[key]) == 1:
            if key in unconditioned:
                if key not in conditioned:
                    conditioned.add(key)
                unconditioned.remove(key)
    result = Factor(unconditioned, conditioned, factor.variableDomainsDict())
    resultPossibilities = result.getAllPossibleAssignmentDicts()
    normsum = 0
    for fact in resultPossibilities:
        normsum += factor.getProbability(fact)
    for fact in resultPossibilities:
        newProbability = factor.getProbability(fact)
        result.setProbability(fact, newProbability/normsum)
    return result
