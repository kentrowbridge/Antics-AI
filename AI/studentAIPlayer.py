  # -*- coding: latin-1 -*-
import random
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *
from random import randint

##
#StudentAIPlayer
#Authors: Kenny Trowbridge, Sean Pierson
#
#Sources:
#Code from AIPlayer.py in the AI folder of antics was used
#Code from http://stackoverflow.com/questions/26815096/ was used to generate
#random numbers
#
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
#
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "KennyAndSeanHW1")
    
    ##
    #getPlacement
    #Description: The getPlacement method corresponds to the 
    #action taken on setup phase 1 and setup phase 2 of the game. 
    #In setup phase 1, the AI player will be passed a copy of the 
    #state as currentState which contains the board, accessed via 
    #currentState.board. The player will then return a list of 10 tuple 
    #coordinates (from their side of the board) that represent Locations 
    #to place the anthill and 9 grass pieces. In setup phase 2, the player 
    #will again be passed the state and needs to return a list of 2 tuple
    #coordinates (on their opponent’s side of the board) which represent
    #Locations to place the food sources. This is all that is necessary to 
    #complete the setup phases.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is 
    #       requesting a placement from the player.(GameState)
    #
    #Return: If setup phase 1: list of ten 2-tuples of ints -> [(x1,y1), (x2,y2),…,(x10,y10)]
    #       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
    ##
    def getPlacement(self, currentState):
        if currentState.phase == SETUP_PHASE_1:
            return [(5,0), (5,1), (4,0), (6,0), (4,3), (4,2), (3,0), (5,2), (6,2), (6,1), (7,0)]

        #this else if is what sets up the food. it only lets us place 2 pieces
        #of food
        elif currentState.phase == SETUP_PHASE_2:
            x = 0
            y = 6
            result = []
            listToCheck = [4,5,3,6,2,7,1,8,0,9]

            for y in [6,7]:

                for num in listToCheck:
                    if(getConstrAt(currentState, (num, y)) == None):
                        result.append((num, y))
                        if(len(result)== 2):
                            return result

        else:
            return None

    ##
    #  HELPER METHODS
    ##

    def getNextStep(self, currentState, src, dst, movement):
        #find the next step in the fastest path to the destination
        moveList = [src] #length is movement + 1
        tracker = src

        #horizontal movement first, then vertical
        for n in range(0, movement, 1):
            print listReachableAdjacent(currentState, tracker, movement)
            print tracker
            if (tracker[0] < dst[0]):#Move right
                if((tracker[0] + 1, tracker[1]) in listReachableAdjacent(currentState, tracker, movement)):
                    moveList.append((tracker[0] + 1, tracker[1]))
                    #adjust tracker for next iteration
                    tracker = (tracker[0] + 1, tracker[1])
            elif (tracker[0] > dst[0]):#move left
                if((tracker[0] - 1, tracker[1]) in listReachableAdjacent(currentState, tracker, movement)):
                    moveList.append((tracker[0] - 1, tracker[1]))
                    #adjust tracker for next iteration
                    tracker = (tracker[0] - 1, tracker[1])
            elif (tracker[1] > dst[1]):#move down
                if((tracker[0], tracker[1] - 1) in listReachableAdjacent(currentState, tracker, movement)):
                    moveList.append((tracker[0], tracker[1] - 1))
                    #adjust tracker for next iteration
                    tracker = (tracker[0], tracker[1] - 1)
            elif (tracker[1] < dst[1]):#move up
                if((tracker[0], tracker[1] + 1) in listReachableAdjacent(currentState, tracker, movement)):
                    moveList.append((tracker[0], tracker[1] + 1))
                    #adjust tracker for next iteration
                    tracker = (tracker[0], tracker[1] + 1)

        return moveList


    ##
    #Function:  nearestFood
    #
    #Parameters:current state, coords of ant
    #
    #
    #
    #
    ##
    # def nearestFood(self, currentState, antCoord):
    #     foodLocList = getConstrList(currentState, playerId, FOOD)
    #     shorest = stepsToReach(currentState, antCoord, foodLocList[0].coords)
    #     for x in range(1, 4, 1):
    #         if(shortest > stepsToReach(currentState, antCoord, foodLocList[x].coords)):
    #             shorest = stepsToReach(currentState, antCoord, foodLocList[x].coords)
    #             tester = x
    #     return foodLocList[tester].coords
    ##
    #getMove
    #
    #Description: The getMove method corresponds to the play phase of the game 
    #and requests from the player a Move object. All types are symbolic 
    #constants which can be referred to in Constants.py. The move object has a 
    #field for type (moveType) as well as field for relevant coordinate 
    #information (coordList). If for instance the player wishes to move an ant, 
    #they simply return a Move object where the type field is the MOVE_ANT constant 
    #and the coordList contains a listing of valid locations starting with an Ant 
    #and containing only unoccupied spaces thereafter. A build is similar to a move 
    #except the type is set as BUILD, a buildType is given, and a single coordinate 
    #is in the list representing the build location. For an end turn, no coordinates 
    #are necessary, just set the type as END and return.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is 
    #       requesting a move from the player.(GameState)   
    #
    #Return: Move(moveType [int], coordList [list of 2-tuples of ints], buildType [int]
    #
    def getMove(self, currentState):
        mergedList = getAntList(currentState, PLAYER_TWO, [(WORKER)])
        foodLocList = getConstrList(currentState, None, [(FOOD)])
        homes = getConstrList(currentState, PLAYER_TWO, [(ANTHILL), (TUNNEL)])

        #For each ant we own
        for ant in mergedList:
            #Ant's current coordinates
            antCoords = ant.coords
            print "AntCoords:"
            print antCoords
            if(ant.hasMoved == False):
                if(ant.type == WORKER ):
                    #Movement paths of a worker ant
                    paths = listAllMovementPaths(currentState, antCoords, 2)
                    if(ant.carrying == False):
                        #Retrieve food
                        for f in foodLocList:
                            #find the closest food
                            for m in range(0, len(paths),1):
                                if(f.coords in paths[m]):
                                    return Move(MOVE_ANT, paths[m], None)
                            #food not accessible, move towards food
                            moveList = self.getNextStep(currentState, antCoords, f.coords, 2)
                            return Move(MOVE_ANT, moveList, None)

                    if(ant.carrying == True):
                        #Return home if carrying food
                        for h in homes:
                            #find the closest nest, Tunnel or Hill
                            for m in range(0, len(paths),1):
                                if(h.coords in paths[m]):
                                    return Move(MOVE_ANT, paths[m], None)
                                #food not accessible, move towards food
                            moveList = self.getNextStep(currentState, antCoords, h.coords, 2)
                            return Move(MOVE_ANT, moveList, None)

        return Move(END, None, None)

    ##
    #getAttack
    #Description: The getAttack method is called on the player whenever an ant completes 
    #a move and has a valid attack. It is assumed that an attack will always be made 
    #because there is no strategic advantage from withholding an attack. The AIPlayer 
    #is passed a copy of the state which again contains the board and also a clone of 
    #the attacking ant. The player is also passed a list of coordinate tuples which 
    #represent valid locations for attack. Hint: a random AI can simply return one of 
    #these coordinates for a valid attack. 
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is requesting 
    #       a move from the player. (GameState)
    #   attackingAnt - A clone of the ant currently making the attack. (Ant)
    #   enemyLocation - A list of coordinate locations for valid attacks (i.e. 
    #       enemies within range) ([list of 2-tuples of ints])
    #
    #Return: A coordinate that matches one of the entries of enemyLocations. ((int,int))
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]
        
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
        #method templaste, not implemented
        pass
