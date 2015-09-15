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
    #coordinates (on their opponent�s side of the board) which represent
    #Locations to place the food sources. This is all that is necessary to
    #complete the setup phases.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a placement from the player.(GameState)
    #
    #Return: If setup phase 1: list of ten 2-tuples of ints -> [(x1,y1), (x2,y2),�,(x10,y10)]
    #       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
    ##
    def getPlacement(self, currentState):
        if currentState.phase == SETUP_PHASE_1:
            return [(4,1), (4,0), (9,3), (8,2), (7,3), (6,2), (5,3), (0,3), (3,3), (2,2), (1,3)]

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
        legalMoves = listAllLegalMoves(currentState)
        hill = getConstrList(currentState, self.playerId, [(ANTHILL)])[0].coords
        for move in legalMoves:
            if(move.moveType == MOVE_ANT):
                ant = getAntAt(currentState, move.coordList[0])
                antType = ant.type
                antCoords = ant.coords
                endPoint = None
                if(antType == QUEEN):
                    if(len(move.coordList) > 1 and antCoords == hill):
                        return move
                    continue

                elif(antType == WORKER or antType == DRONE):
                    foodList = getConstrList(currentState, None, [(FOOD)])
                    tunnel = getConstrList(currentState, self.playerId, [(TUNNEL)])[0].coords
                    steps = 100
                    if(ant.carrying == False and antType == WORKER):
                        for f in foodList:
                            temp = stepsToReach(currentState, antCoords, f.coords)
                            if(temp < steps):
                                steps = temp
                                endPoint = f.coords
                    if(ant.carrying == True and antType == WORKER):
                        endPoint = tunnel
                    if(antType == DRONE):
                        enemyQueen = getAntList(currentState, self.playerId - 1, [(QUEEN)])[0].coords
                        endPoint = enemyQueen


                    possiblePaths = listAllMovementPaths(currentState, antCoords, 2)
                    minSteps = 100
                    finalPath = None
                    for path in possiblePaths:
                        pathEndCoord = path[-1]
                        stepsToEnd = stepsToReach(currentState, pathEndCoord, endPoint)
                        if(stepsToEnd < minSteps):
                            minSteps = stepsToEnd
                            finalPath = path
                    if(move.coordList == finalPath):
                        return move

            elif(move.moveType == BUILD):
                drones = getAntList(currentState, self.playerId, [(DRONE)])
                if(move.buildType == DRONE):
                    if(len(drones) < 2):
                        return move
                if(move.buildType == WORKER):
                    workers = getAntList(currentState, self.playerId, [(WORKER)])
                    if(len(workers) < 1):
                        return move
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
        for e in enemyLocations:
            trucktion = getConstrAt(currentState, e)
            if(trucktion == None):
                return e
            elif(trucktion.type == ANTHILL or trucktion.type == QUEEN):
                return e
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
