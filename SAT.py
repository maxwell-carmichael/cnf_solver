# Maxwell Carmichael - 10/25/2020.
# cs76
import random
import math
import time

class SAT:
    def __init__(self, filename, print = True, WalkSATPureRandom = False, scoreByNet = True):
        self.PRINT_FLAG = print
        self.WALKSAT_FLAG = WalkSATPureRandom
        self.SCORE_FLAG = scoreByNet  # what you need to know: should be True if each variable occurs in less than half the clauses on average.

        self.H = 0.35  # probability of NOT choosing randomly in walksat and gsat
        self.ITERATION_LIMIT = 100000 # maximum num of iterations of walksat and gsat

        KB = self.genKB(filename)
        self.intToVariable = KB[0]  # variable as int -> variable as found in .cnf
        self.intToClauses = KB[1]  # variable as int -> indices of KB
        self.KB = KB[2]  # 2d list, inner list are clauses with variables as ints


        self.assignment = self.genAssignment()
        # index + 1 of list revers to the variable as integer


        # Returns the knowledge base in a 2d list, with variables as integers.
        # Also returns a map from variables as integers to variables as they
        # are stated in the file.
    def genKB(self, filename):
        f = open(filename, "r")

        KB = []  # knowledgebase as a 2d list
        variableToInt = {}  # map to be reversed & returned
        intToClauses = {}  # map from variable to integer to list of clauses which we find it in

        i = 1  # variable as integer index
        c = 0  # index of currently handled clause

        # transform lines of .cnf file to clauses (lists), where "commas" are ORs
        for line in f:
            clause = []

            for variable in line.split():
                # handle Falses
                if variable[0] == '-':
                    trueVar = variable[1:]
                    # if variable is not in the map, assign it
                    if trueVar not in variableToInt:
                        intToClauses[i] = [c]

                        variableToInt[trueVar] = i
                        i += 1  # increment i to handle next new variable
                    else:
                        intToClauses[variableToInt[trueVar]].append(c)


                    clause.append(-1 * variableToInt[trueVar])

                # handle Trues
                else:
                    # if variable is not in the map, assign it
                    if variable not in variableToInt:
                        variableToInt[variable] = i
                        intToClauses[i] = [c]
                        i += 1  # increment i to handle next new variable
                    else:
                        intToClauses[variableToInt[variable]].append(c)

                    clause.append(variableToInt[variable])

            KB.append(clause)
            c += 1

        f.close()

        # reverse the map
        intToVariable = {int : var for var, int in variableToInt.items()}
        return (intToVariable, intToClauses, KB)

        # doesn't matter, but could potentially modify
    def genAssignment(self):
        l = len(self.intToVariable)
        return [False] * l

    def gsat(self):
        assignment = self.genAssignment()  # start with any assignment

        i = 1
        t = time.time()

        while i <= self.ITERATION_LIMIT:
            # if our assignment satisfied the knowledge base, we've finished.
            if self.doesSatisfyKB(assignment):
                self.assignment = assignment

                if self.PRINT_FLAG:
                    print("Found solution after " + str(i) + " iterations and " + str(time.time() - t) + " seconds.")
                    print("Used an h value of " + str(self.H))
                    print("NetScore: " + str(self.SCORE_FLAG))

                return True

            # flip a random index
            if random.random() < self.H:
                self.flip(assignment)
            # flip one of the random highest scorers
            else:
                highestScorers = self.genHighestScorersGSAT(assignment)
                self.flip(assignment, random.choice(tuple(highestScorers)))

            i += 1

        if self.PRINT_FLAG:
            print("Found NO solution after " + str(i) + " iterations and " + str(time.time() - t) + " seconds.")
            print("Used an h value of " + str(self.H))
            print("NetScore: " + str(self.SCORE_FLAG))
        return False


    def walksat(self):
        assignment = self.genAssignment()  # start with any assignment

        i = 1
        t = time.time()

        while i <= self.ITERATION_LIMIT:
            i += 1

            if self.doesSatisfyKB(assignment):
                self.assignment = assignment

                if self.PRINT_FLAG:
                    print("Found solution after " + str(i) + " iterations and " + str(time.time() - t) + " seconds.")
                    print("Used an h value of " + str(self.H))
                    print("NetScore: " + str(self.SCORE_FLAG))
                    print("WalkSATPureRandom: " + str(self.WALKSAT_FLAG))

                return True

            if random.random() < self.H:
                # flip a random index out of all indices
                if self.WALKSAT_FLAG:
                    self.flip(assignment)
                # flip a random index out of unsatisfied clauses
                else:
                    unsatisfiedClauses = self.getUnsatisfiedClauses(assignment)
                    choice = random.choice(unsatisfiedClauses)

                    indices = set()
                    for variable in choice:
                        indices.add(abs(variable) - 1)

                    self.flip(assignment, random.choice(tuple(indices)))

            # flip one of the random highest scorers
            else:
                highestScorers = self.genHighestScorersWalkSAT(assignment)
                j = random.choice(tuple(highestScorers))
                self.flip(assignment, j)

        if self.PRINT_FLAG:
            print("Found NO solution after " + str(i) + " iterations and " + str(time.time() - t) + " seconds.")
            print("Used an h value of " + str(self.H))
            print("NetScore: " + str(self.SCORE_FLAG))
            print("WalkSATPureRandom: " + str(self.WALKSAT_FLAG))
        return False

        # checks if an assignment satisfies KB
    def doesSatisfyKB(self, assignment):
        for clause in self.KB:
            if not self.doesSatisfyClause(assignment, clause):
                return False

        return True

        # checks if an assignment satisfies clause
    def doesSatisfyClause(self, assignment, clause):
        for var in clause:
            if var < 0:
                # if var is False, clause is satisfied
                if not assignment[abs(var) - 1]:
                    return True
            if var > 0:
                # if var is True, clause is satisfied
                if assignment[var - 1]:
                    return True

        return False

        # flips the assignment at a given index. random if no index.
    def flip(self, assignment, index = None):
        if index is None:
            index = int(random.random() * len(assignment))

        assignment[index] = not assignment[index]

        # returns a list of clauses which are unsatisfied
    def getUnsatisfiedClauses(self, assignment):
        unsatisfiedClauses = []

        for clause in self.KB:
            if not self.doesSatisfyClause(assignment, clause):
                unsatisfiedClauses.append(clause)

        return unsatisfiedClauses

        # get score after flipping at index i
    def findScore(self, assignment, i):
        score = 0

        if self.SCORE_FLAG:
            # score will become magnitude of number of clauses which contain var i+1
            # satisfied by current assignment
            for clause in self.intToClauses[i + 1]:
                if self.doesSatisfyClause(assignment, self.KB[clause]):
                    score -= 1

            # flip to test
            self.flip(assignment, i)

            # add to score number of clauses containing var i+1 which are satisfied after the flip
            for clause in self.intToClauses[i + 1]:
                if self.doesSatisfyClause(assignment, self.KB[clause]):
                    score += 1

            self.flip(assignment, i)

            # Now, the score is the NET number of clauses which BECOME "True" after the flip.
            return score

        else:
            self.flip(assignment, i)

            for clause in self.KB:
                if self.doesSatisfyClause(assignment, clause):
                    score += 1

            self.flip(assignment, i)

            # Now, the score is the TOTAL number of clauses which ARE "True" after the flip.
            return score

        # returns a set of which variables, when flipped, would satisfy most clauses
    def genHighestScorersGSAT(self, assignment):
        currHighest = -math.inf
        highestScorers = set()

        # go over all indices and find which ones satisfy the most clauses
        for i in range(0, len(assignment), 1):
            score = self.findScore(assignment, i)

            # if we beat the score, update everything
            if score > currHighest:
                currHighest = score
                highestScorers = { i }

            # if we tied the score, add the assignment index
            elif score == currHighest:
                highestScorers.add(i)

        return highestScorers

        # returns a set of a specific subset of variables which, when flipped, would satisfy most clauses
    def genHighestScorersWalkSAT(self, assignment):
        unsatisfiedClauses = self.getUnsatisfiedClauses(assignment)

        choice = random.choice(unsatisfiedClauses)
        # SUPER useful print statement for testing!
        # print("Unsatisfied: " + str(len(unsatisfiedClauses)))

        indices = set()
        for variable in choice:
            indices.add(abs(variable) - 1)

        # rest of this is similar to GSAT, except you go over only the selected indices
        currHighest = -math.inf
        highestScorers = set()

        for i in indices:
            score = self.findScore(assignment, i)

            # if we beat the score, update everything
            if score > currHighest:
                currHighest = score
                highestScorers = { i }

            # if we tied the score, add the assignment index
            elif score == currHighest:
                highestScorers.add(i)

        return highestScorers

    def write_solution(self, filename):
        f = open(filename, "w")

        for i in range(len(self.assignment)):
            variable = self.intToVariable[i + 1]

            if self.assignment[i]:
                f.write(str(variable) + "\n")
            else:
                f.write("-" + str(variable) + "\n")

        f.close()

if __name__ == "__main__":
    s = SAT("all_cells.cnf")
    print(s.intToVariable)
    print(s.KB)
    print(s.assignment)
    ones_assigned = [True, False, False, False, False, False, False, False, False]*81
    print(s.doesSatisfyKB(ones_assigned))
    firsttrue = [True]
    firsttrue.extend([False]*728)
    print(s.genHighestScorersGSAT(firsttrue))
    # s.gsat()
    # print(s.assignment)
