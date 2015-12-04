import pickle, traceback
import random
import sys
sys.path.append("..")
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import *
from Move import Move
from GameState import *
from AIPlayerUtils import *
from Location import *
from Inventory import *

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##

DISCOUNT_FACTOR = 0.8
INPUT_FILE = 'TrowbridgePinto-StateUtils.txt'

class AIPlayer(Player):
    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):        
        global closestFood
        closestFood = None
        loadedValues = self.load()

        self.stateUtilities = loadedValues[0]
        self.gamesPlayed = loadedValues[1]
        self.learningRate = 2/(1 + 0.999**(-self.gamesPlayed))

        print "game # loaded: " + `self.gamesPlayed`
        super(AIPlayer,self).__init__(inputPlayerId, "Tiny DANTser")
    
    ##
    #consolidateState()
    #
    #Description: this method consolidates a normal antics state into a 
    #   smaller version so that our learning algorithm can traverse the
    #   the utilities in a timely manner.
    #
    #Parameters:
    #   state - the state to consolidate
    ##
    def consolidateState(self, state):
        enemyInv = state.inventories[not self.playerId] 
        playerInv = state.inventories[self.playerId]       

        enemyQ = enemyInv.getQueen()
        playerAnt = getAntList(state, self.playerId, (WORKER,))
        if playerAnt != []:
            playerAntCoords = playerAnt[0].coords
        else:
            playerAntCoords = (0,0)

        if enemyQ is None:
            enemyQHealth = 0
            enemyQCoords = (0,0)
        else:
            enemyQHealth = enemyQ.health
            enemyQCoords = enemyQ.coords

        newState = State(enemyQHealth, enemyQCoords, playerAntCoords, \
            (playerInv.foodCount == FOOD_GOAL), (enemyInv.foodCount == FOOD_GOAL), \
            (playerInv.getQueen().health == 0))

        return newState

    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]
    
    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        moves = listAllLegalMoves(currentState)

        glieValue = random.randint(0,1)

        #GLIE learning decisions
        if(glieValue < self.learningRate):
            return moves[random.randint(0,len(moves) - 1)]
        else:
            bestRating = None
            bestMove = None

            # look for the best possible move
            for m in moves:
                if(m == None):
                    continue
                stateProjection = self.getStateProjection(currentState, m)
                stateProjection = self.consolidateState(stateProjection)

                #apply TD function
                rating = self.tdFunction(self.consolidateState(currentState), stateProjection)
            
                if bestRating == None or rating >=  bestRating:
                    bestMove = m
                    bestRating = rating

            # print self.printStateUtilities()
            return bestMove

    ##
    #tdFunction()
    #
    #Description:
    #   Apply the temporal difference learning function
    #   to update the utility of the current state
    #
    #Parameters:
    #   currentState - state to update the utility for
    #   projectedState - used to grab utility for next state
    #
    #Returns:
    #   The utility for the next state, used in getmove to select
    #   the move with the best utility
    #
    ##
    def tdFunction(self, currentState, projectedState):
        # look for current state in lookup table
        currStateUtil = self.findState(currentState)
        if currStateUtil == None:
            #create tuple for state utilities list
            newEntry = [currentState, 0.0]
            self.stateUtilities.append(newEntry)
            currStateUtil = newEntry

        # look for projected state in lookup table
        projStateUtil = self.findState(projectedState)
        if projStateUtil == None:
            #create dictionary entry for pojected state
            newEntry = [projectedState, 0.0]
            self.stateUtilities.append(newEntry)
            projStateUtil = newEntry


        print "alpha: " + `self.learningRate`
        newUtil = currStateUtil[1] + self.learningRate*(self.reward(currentState) + (DISCOUNT_FACTOR * projStateUtil[1]) - currStateUtil[1])
        currStateUtil[1] = newUtil

        #return the utility for move selection
        return projStateUtil[1]

    ##
    #findState()
    #
    #Description:
    #   Search the state utilities hash for a given state utility pair
    #
    #Parameters:
    #   state - state to find
    #
    #Returns:
    #   The state-utility pair of the given state
    ##
    def findState(self, state):
        for x in self.stateUtilities:
            if state == x[0]:
                return x
        return None

    ##
    #getStateProjection()
    #
    #Description:
    #   Predict what a given state will look like after a move is applied to it
    #
    #Parameters:
    #   currentState - the current state of the game
    #   move - the move to simulate
    #
    #Returns:
    #   A copy of the state after the move has been applied
    ##
    def getStateProjection(self, currentState, move):
        state = currentState.fastclone()
        currPlayer = state.whoseTurn
        playerInv = state.inventories[currPlayer]
        enemyInv = state.inventories[(not currPlayer)]

        #update Ant/Constr list after placement/removal
        if(move.moveType == BUILD):
            # #add the built ant to the ant list
            antType = move.buildType
            antHill = playerInv.getAnthill().coords

            newAnt = Ant(antHill, antType, currPlayer)
            playerInv.ants.append(newAnt)

            #calculate build cost
            buildCost = 1
            if(newAnt.type == SOLDIER or newAnt.type == R_SOLDIER):
                buildCost = 2 #soldiers cost 2 food

            #subtract cost from food
            playerInv.foodCount -= buildCost

        elif (move.moveType == MOVE_ANT):
            # #update coordinates of ant
            newPosition = move.coordList[-1]
            ant = getAntAt(state, move.coordList[0])

            ant.coords = newPosition
            ant.hasMoved = True

            #project an attack, if there is one
            #list nearby ants
            listToCheck = listAdjacent(ant.coords)

            antsInRange = []
            for a in listToCheck:
                nearbyAnt = getAntAt(state, a)
                if(nearbyAnt != None):
                    if(nearbyAnt.player == (not currPlayer)):
                        antsInRange.append(a)

            if(len(antsInRange) > 0):#check for empty list
                attackedAntCoords = self.getAttack(state, ant, antsInRange)

                #update health of attacked ant
                attackedAnt = getAntAt(state, attackedAntCoords)
                attackedAnt.health -= 1

                #remove dead ant from board
                if(attackedAnt.health == 0):
                    enemyInv.ants.remove(attackedAnt)

        elif (move.moveType == END):
            antHillCoords = playerInv.getAnthill().coords
            antOnHill = getAntAt(state, antHillCoords)
            antOnTunnel = getAntAt(state, playerInv.getTunnels()[0].coords)

            #handle food drop off
            if(antOnHill != None and antOnHill.carrying):
                playerInv.foodCount += 1
                antOnHill.carrying = False
            if(antOnTunnel != None and antOnTunnel.carrying):
                playerInv.foodCount += 1
                antOnTunnel.carrying = False

            #update if ant is on Food
            foodLocs = getConstrList(state, None, [(FOOD)])
            #list of current players ants that are on food
            antsOnFood = []
            for f in foodLocs:
                tempAnt = getAntAt(state, f.coords)
                if(tempAnt != None and tempAnt.player == currPlayer):
                    antsOnFood.append(tempAnt)

            for a in antsOnFood:
                a.carrying = True

        
        return state.fastclone()

    ##
    #reward()
    #
    #Description:
    #   Reward function for the remporal difference learning agent
    #
    #Parameters:
    #   state - state to evaluate
    #
    #Returns:
    #   A rating for the given state
    ##
    def reward(self, state):
        #check win conditions
        if state.enemyQHealth == 0 :
            return 1.0
        if state.foodVictory:
            return 1.0

        #check lose conditions
        if state.foodLoss:
            return -1.0
        if state.playerQDead:
            return -1.0

        #beat it with a stick
        return -0.01

    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #Description: The last method, registerWin, is called when the game ends and simply 
    #indicates to the AI whether it has won or lost the game. This is to help with 
    #learning algorithms to develop more successful strategies.
    #
    #Parameters:
    #   hasWon - True if the player has won the game, False if the player lost. (Boolean)
    #
    def registerWin(self, hasWon):  
        # adjust the learning rate based on games played
        self.gamesPlayed += 1
        self.learningRate = 2/(1 + 0.999**(-self.gamesPlayed))    

        self.save()

    ##
    #load()
    #
    #Description:
    #   Loads the saved values of the state utility pairs that were
    #   saved to the input file from a previous instance of the agent
    #
    ##
    def load(self):
        try:
            fl = open('../' + INPUT_FILE, 'rb')
            #write games played for learning rate
            toLoad = pickle.load(fl)
            # stateUtils = toLoad[0]
            # games = toLoad[1]

            fl.close()
        except IOError:
            print "IO Error"
            traceback.print_exc(file=sys.stdout)
            return ([], 0)
        return toLoad

    ##
    #save()
    #
    #Description:
    #   Saves the values of the state utility pairs as well as the number 
    #   of games played by this agent.
    #
    ##
    def save(self):
        #open file for writing
        fl = open(INPUT_FILE, 'wb')
        toSave = (self.stateUtilities, self.gamesPlayed)
        pickle.dump(toSave, fl)

        print "states seen: " + `len(toSave[0])`
        print "games played: " + `toSave[1]`
        
        fl.close()


    def printStateUtilities(self):
        print "====State Utilities===="
        print len(self.stateUtilities)        
        for x in self.stateUtilities:
            print "    EnemyQHealth " + `x[0].enemyQHealth`
            print "    EnemyQPos " + `x[0].enemyQPos`
            print "    PlayerWorkers "
            for w in x[0]['playerWorkers']:
                print w.coords
            print "    FoodVictory " + `x[0].foodVictory`
            print "    FoodLoss " + `x[0].foodLoss`
            print "    PlayerQDead " + `x[0].playerQDead`
            print "++++"+ `x[1]` + "++++"

class State:
    
    def __init__(self, enemyQHealth, enemyQPos, playerWorker, foodVictory, foodLoss, playerQDead):
        self.enemyQHealth = enemyQHealth
        self.enemyQPos = enemyQPos
        self.playerWorker = playerWorker
        self.foodVictory = foodVictory
        self.foodLoss = foodLoss
        self.playerQDead = playerQDead

    def __eq__(self, state):

        if self.enemyQHealth != state.enemyQHealth or \
            self.enemyQPos != state.enemyQPos or \
            self.playerWorker != state.playerWorker or \
            self.foodVictory != state.foodVictory or \
            self.foodLoss != state.foodLoss or \
            self.playerQDead != state.playerQDead:
            return False

        return True  
