Maxwell Carmichael

Professor Alberto Quattrini Li
###### CS76 - PA5: Propositional Logic

### Introduction
In this programming assignment, I created a propositional logic satisfiability solver, which takes information on a .cnf file and returns a boolean assignment of all variables which satisfies all clauses on the .cnf file.

### Description
A lot of the code was provided, specifically the code for handling and converting Sudoku puzzles to conjunctive normal form and displaying .sol files. I created the SAT class, which takes a .cnf file and generates a boolean assignment (solution) using either the walksat or the gsat algorithms.


##### Generating KB
The first step in my process was converting the .cnf file into a knowledge base (KB), as well as generating any other information I would need. I decided I would represent KB as a list of lists - the inner lists being clauses, and the elements of the inner lists being variables as **integers**, negative if negated. Because I deal with negative/positive versions of integers as my variables, I cannot have the integer 0 be a variable (else there is no way to negate it). Thus I count variables starting with 1.

Example: (A OR B) AND (~B OR C) could be represented as [[1,2],[-2,3]].

Thus, it follows that I loop through each line (clause) of the .cnf file and then loop through each variable of the line. If I see a variable I have never seen before, I assign it to the lowest positive integer I have not assigned yet using a dictionary. I then add the variables (negative if negated) to the clause, and add the clause to the KB.

For reasons I will explain under GSAT, I also created a map from each variable (in positive integer form) to the indices of clauses in the KB which contain it or its negation.

I return the KB, along with (1) a map from variable (as integer) to variable (as found in .cnf) and (2) a map from variable (as integer) to indices of clauses which contain the variable.

##### GSAT
I implemented GSAT according to the psuedocode in the assignment description. My initial "random assignment" was just a list of all False values with length as the number of variables. I check for a valid solution with ``doesSatisfyKB``, which uses the ``doesSatisfyClause`` helper method. To tell if an assignment satisfies a clause, you can look at each variable in the clauses and find whether it's True by indexing into the assignment, the index being the integer variable minus 1.

I then iterate as many times as my preset constant ``ITERATION_LIMIT`` allows, stopping only if ``doesSatisfyKB`` returns ``True``. With a probability determined by my preset constant h, I flip a random element of the assignment, and reiterate. Otherwise, I pick the variables which, when flipped, would satisfy the most clauses. If multiple elements, when flipped, would satisfy the most clauses, then I flip one of them randomly in the actual assignment, then reiterate. If I iterate more times than allowed, I return ``False``.

The way that I tell which variables would satisfy the most clauses is by utilizing the ``genHighestScorersGSAT`` method. In my initial approach (which can still be enabled by setting ``scoreByNet `` to False), I loop over each variable and count the number of clauses satisfied by the assignment with the variable flipped. The variables with the highest number of clauses satisfied get returned in a set. In this case we loop over the entire KB.

There is a potentially more efficient way to get this score, using the map from variable to indices of clauses which contain the variable. If the assignment with the variable flipped satisfies *n* clauses which contain the variable, and if the assignment without the variable flipped satisfies *m* clauses which contain the variable, then the net number of clauses that would be flipped *because of* the flip is *n* - *m*. To do this calculation, we have to loop over the subset of clauses which contain the variable twice (once for without the flip, once with the flip). If the clauses which contain the variable make up less than half of the KB, it is more efficient to use this method. For sudoku, it can increase performance roughly fourfold.

##### WalkSAT
To implement WalkSAT, I took GSAT and modified it according to the pseudocode in the textbook. The first modification (which can be disabled/"unmodified") is the selection of the random variable (with probability h). Instead of selecting a random variable from the set of all variables, select a random variable from a random unsatisfied clause. A benefit of this is that it increases the likelihood of selecting a variable that, when flipped, gets us closer to a solution. A drawback may be that it decreases our ability to escape from local minima, where our algorithm repeatedly tells us to flip from the same set of variables (this is why there is an element of randomness in the first place).

The second change is how we select the variables which, when flipped, would satisfy the most clauses; I use ``genHighestScorersWalkSAT``. Rather than iterate through **all** the variables, I instead select a random unsatisfied clause and iterate through just the variables found in the clause, and return the highest scorers from those.

### Analysis
##### WalkSAT Puzzle Solutions
Below is the solution produced by the WalkSAT algorithm on the three puzzles, seeded at 1. I used an h value of 0.35 (discussed why later). My algorithm was successful in all cases.

**puzzle1:**
```
Found solution after 8027 iterations and 13.476 seconds.

5 8 1 | 3 7 6 | 4 9 2
6 3 4 | 2 9 5 | 7 1 8
9 7 2 | 1 8 4 | 5 6 3
---------------------
8 1 5 | 4 6 9 | 3 2 7
4 6 3 | 8 2 7 | 9 5 1
7 2 9 | 5 3 1 | 6 8 4
---------------------
1 5 8 | 9 4 3 | 2 7 6
3 9 7 | 6 1 2 | 8 4 5
2 4 6 | 7 5 8 | 1 3 9
```

**puzzle2:**
```
Found solution after 35787 iterations and 52.091 seconds.
1 3 4 | 9 8 6 | 5 2 7
5 8 6 | 1 2 7 | 3 4 9
2 9 7 | 4 5 3 | 6 1 8
---------------------
8 1 2 | 7 6 5 | 4 9 3
3 6 5 | 8 9 4 | 2 7 1
7 4 9 | 3 1 2 | 8 5 6
---------------------
9 5 1 | 6 4 8 | 7 3 2
4 7 8 | 2 3 9 | 1 6 5
6 2 3 | 5 7 1 | 9 8 4
```

**puzzle_bonus:**
```
Found solution after 13157 iterations and 17.742 seconds.
5 3 4 | 6 7 8 | 9 1 2
6 7 2 | 1 9 5 | 3 4 8
1 9 8 | 3 4 2 | 5 6 7
---------------------
8 5 9 | 7 6 1 | 4 2 3
4 2 6 | 8 5 3 | 7 9 1
7 1 3 | 9 2 4 | 8 5 6
---------------------
9 6 1 | 5 3 7 | 2 8 4
2 8 7 | 4 1 9 | 6 3 5
3 4 5 | 2 8 6 | 1 7 9
```

##### GSAT vs. WalkSAT
GSAT was able to complete one_cell.cnf, all_cells.cnf, and rows.cnf, but nothing past that, as I stopped the algorithms after three minutes. WalkSAT, on the other hand, always found a solution (at h=0.35) for all puzzles within 100,000 iterations.

##### Seeds
| Puzzle\Seed | 1     | 2     | 3     | 4     | 5     | 6     |
|-------------|-------|-------|-------|-------|-------|-------|
| puzzle1     | 13.07 | 9.99  | 3.25  | 22.17 | 26.09 | 24.94 |
| puzzle2     | 64.37 | 17.12 | 43.09 | 49.36 | 38.42 | 98.72 |

**Table 1.** The time (in seconds) it takes for the algorithm to find a solution for different puzzles and different seeds.

Here, I analyze the time it takes for the algorithm to find a solution for puzzle1 and puzzle2 for different initial seeds. Clearly, the seed used matters greatly for the runtime, indicating the importance of the randomness. The importance is likely due to the chance that we end up at a solution versus a non-solution local minimum, as well as the chance we make it out of the local minimum quickly.

##### Optional Parameters (WalkSATPureRandom, scoreByNet)
I've talked about both these parameters abstractly before, but here I just want to state that throughout testing I found setting WalkSATPureRandom to be false (when we choose a random variable to flip with probability h, if WalkSATPureRandom is false then we flip a random variable from a random unsatisfied clause) to be faster in all cases. As well, I found setting scoreByNet to be faster in all cases (understandably, as you iterate through much less clauses when scoring), but I made it a parameter because in some puzzles perhaps most variables appear in most clauses, so the algorithm would be faster if you just iterate through the entire KB once for each variable when scoring.

##### Different h values
I am not going to formally report results here. They are hard to measure because of how runtime depends on seeding, thus runtimes based on changes of h could be uncorrelated with the change of h. It would take too long for the scope of this programming assignment to formally measure the optimal h, so I am just going to go by intuition: 0.3 sometimes was not enough to escape local minima within 100,000 iterations, while 0.4 worked but seemed to take too long to reduce the number of unsatisfied clauses. 0.35 seemed to have the best of both worlds (I'm sure there is a more optimal h value, but most importantly my tests never failed at this value), so I chose to do all testing at 0.35.
