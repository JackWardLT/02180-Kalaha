class KalahGame:
    """
    Example starting layout ( 7 pits per player, 3 stones in each)
    Player 2: [14] [13] [12] [11] [10]  [9]  [8]        # Field indexing
                3    3    3    3    3    3   3
      [15] 0                                    0 [7]   
                3    3    3    3    3    3   3
    Player 1:  [0]  [1]  [2]  [3]  [4]  [5]  [6]
         
    """
    

    board = list() # list of Nr of stones in each pit
    boardIndexing = list() # list of pit indexing [0] to e.g.[13]
    PlayerSets = list() # PlayerSets=[[CurrentPlayer's pits],[OppositePlayer's pits]]
    

    Npits = 0
    Nstones = 0

    Player0Start = 0
    Player0End = 0
    Player1Start = 0
    Player1End = 0

    CurrentPlayerIs0 = True

    SelectedMove = -1

    endGame = False

    InputValid = False


    # Print function - displays current state of the board
    def printBoard(self):
        #Arrange state of the stones and score in readable format
        #Player0
        Player0List = '                  ' + (str(self.board[self.Player0Start]))
        Player0IndexList = '        Player0:'
        
        # create a formatted string with Player0 stone distribution
        for i in range(self.Player0Start+1,self.Player0End):
            if len(str(self.board[i]))<2:
                Player0List = Player0List + ' '
            Player0List = Player0List + '  -  '  + str(self.board[i])
            
        # create a formatted string with Player0 pit indexing
        for i in range(self.Player0Start,self.Player0End):
            Player0IndexList = Player0IndexList + ' ['  + str(self.boardIndexing[i]) + ']  '
            if len(str(self.boardIndexing[i]))<2:
                Player0IndexList = Player0IndexList + ' '

        #Player1
        Player1List =  '                  ' + (str(self.board[self.Player1End-1]))
        Player1IndexList = '        Player1:'

        # create a formatted string with Player1 stone distribution
        for i in reversed(range(self.Player1Start,self.Player1End-1)):
            if len(str(self.board[i]))<2:
                Player1List = Player1List + ' '
            Player1List = Player1List + '  -  '  + str(self.board[i])
        
        # create a formatted string with Player0 pit indexing
        for i in reversed(range(self.Player1Start,self.Player1End)):
            Player1IndexList = Player1IndexList + ' ['   + str(self.boardIndexing[i]) + ']  '
            if len(str(self.boardIndexing[i]))<2:
                Player1IndexList = Player1IndexList + ' '


        # create a formatted string with stone distribution in stores
        #Store fields Player1 - Player0
        StoreList =   '        [' + str(self.boardIndexing[self.Player1End]) + '] ' + str(self.board[self.Player1End])
        for i in range(self.Npits):
            StoreList = StoreList+ '       '
        StoreList = StoreList + '   ' + str(self.board[(self.Player0End)]) + ' [' + str(self.boardIndexing[self.Player0End]) + '] ' 
        
        print()
        #Player1
        print(Player1IndexList)
        print (Player1List)

        #Stores
        print (StoreList)
        
        #Player0
        print(Player0List)
        print(Player0IndexList)
    
    def printResults(self):
        if self.board[self.Player0End]> self.board[self.Player1End]:
            print('\n Game finished. You Win!')
            print(f'\n Results: \n Your score: {self.board[self.Player0End]}   AI score: {self.board[self.Player1End]}\n\n')
        elif self.board[self.Player0End]< self.board[self.Player1End]:
            print('\n Game finished. You Lose!')
            print(f'\n Results: \n Your score: {self.board[self.Player0End]}   AI score: {self.board[self.Player1End]}\n\n')
        else:
            print('\n Game finished. Draw!')
            print(f'\n Results: \n Your score: {self.board[self.Player0End]}   AI score: {self.board[self.Player1End]}\n\n')


    def askForFirstPlayer(self):
        InputValid = False
        while not InputValid:
            firstPlayer = input("First move made by you? (y/n): ")
            InputValid = self.validatePlayer(firstPlayer)

        if firstPlayer in ['y', 'Y', 'Yes']:
            self.CurrentPlayerIs0 = True
            #RR Redundant assignment as PlayerSets for True already assigned in initialization, but just in case and for readability
            #RR PlayerSets=[[CurrentPlayer's pits],[OppositePlayer's pits]]
            self.PlayerSets = [self.boardIndexing[self.Player0Start:self.Player0End+1], self.boardIndexing[self.Player1Start:self.Player1End+1]]
        else: 
            self.CurrentPlayerIs0 = False
            #RR If Player1 goes first reverse sets so that PlayerSets[0] always belongs to current player
            self.PlayerSets.reverse()  #RR PlayerSets=[[CurrentPlayer's pits],[OppositePlayer's pits]]
    
    def validatePlayer(self, InputVar):
        if InputVar not in ['y', 'Y', 'Yes', 'n', 'N', 'No']:
            print('Input invalid! Please try again!')
            return False
        else: 
            return True


    def askForMove(self):
        InputValid = False
        while not InputValid:
            if self.CurrentPlayerIs0:
                SelectedMove = input(f"\nPlayer0 - please select move (in range {self.Player0Start} - {self.Player0End-1} ): ")
                InputValid = self.validateMove(SelectedMove, self.Player0Start, self.Player0End-1)
                #print(f'in if InputValid {InputValid}')
            else:
                SelectedMove = input(f"\nPlayer1 - please select move (in range {self.Player1Start} - {self.Player1End-1} ): ")
                InputValid = self.validateMove(SelectedMove, self.Player1Start, self.Player1End-1)
                #print(f'in else InputValid {InputValid}')
        if InputValid == True:
            self.SelectedMove = int(SelectedMove)
        #print(f'selectedMove {self.SelectedMove}')
    
    def validateMove(self, InputVar, LowMargin, HighMargin):
        try: 
            MyInput = int(InputVar)
        except: 
            print('Type of input invalid! Please try again!')
            return False

        if MyInput < LowMargin or MyInput > HighMargin:
            print('Input invalid! Please try again!')
            return False
        
        if self.board[MyInput] == 0:
            print('Input invalid! Selected pit is empty! Please try again!')
            return False
        else:
            return True


    
    def makeMove(self, theMove):
        pointer = theMove+1       
        StonesInPit = self.board[theMove]

        # Empty selected pit
        self.board[theMove] = 0

        #RR based on how many stones in the selected pit, distribute the stones:
        for i in range(StonesInPit):
            # skip opponent's goal (if the stone distribution passes through opponents goal, do not add a stone to it )
            ## RR self.PlayerSets[1][-1] corresponds to last element in opponent's list of pits
            if pointer == self.PlayerSets[1][-1]:  #RR PlayerSets=[[CurrentPlayer's pits],[OppositePlayer's pits]]
                pointer += 1
            # if the move has made a full circle, reset pointer to 0
            if pointer == self.Player1End+1:
                pointer = self.Player0Start

            #RR distribute stones among the pits
            self.board[pointer] += 1
            pointer += 1
        
        #RR Find index of the last pit a stone was placed into
        lastPointer = pointer-1
        #print (f'lastPointer {lastPointer}')

        # if last stone IN Player's goal, make one more move:
        if lastPointer == self.PlayerSets[0][-1]: #RR PlayerSets=[[CurrentPlayer's pits],[OppositePlayer's pits]] 
            self.CurrentPlayerIs0 = self.CurrentPlayerIs0 # redundant move, but the if condition works as condition for next elif

        #if only 1 stone in the last pit, and last pit in current player's set and and opposite pit not empty -->
        #take opponents stones from opposite pit and the stone from last pit
        elif self.board[lastPointer] == 1 and lastPointer in self.PlayerSets[0] and self.board[2*self.Npits - lastPointer] !=0:         
            '''
            #for testing and visualization:
            scoreBeforeAdding = self.board[self.PlayerSets[0][-1]]
            #thislocation = self.Npits + (self.Npits - lastPointer) = 2*self.Npits - lastPointer # opposite pit's index for Player0
            #thislocation = self.Npits - (lastPointer - self.Npits) = 2*self.Npits - lastPointer # opposite pit's index for Player1
            # both equations equal:
            thislocation = 2*self.Npits - lastPointer # opposite pit's index 
            addFromOpponent = self.board[thislocation]
            addOwnLastStone = self.board[lastPointer]
            toThisGoal = self.PlayerSets[0][-1]
            print(f'scoreBeforeAdding {scoreBeforeAdding}')
            print(f'addFromOpponent {addFromOpponent}')
            print(f'addOwnLastStone {addOwnLastStone}')
            print(f'toThisGoal {toThisGoal}')
            '''
            # add opponent's stones to player's goal
            #Index self.PlayerSets[0][-1] corresponds to the last element of the first list in PlayerSets = Current player' s goal
            self.board[self.PlayerSets[0][-1]] += self.board[2*self.Npits - lastPointer]
            self.board[2*self.Npits - lastPointer] = 0
            # add current player's last stone to current player's goal
            self.board[self.PlayerSets[0][-1]] += self.board[lastPointer]
            self.board[lastPointer] = 0

        # if the current player has no more moves to make, end game!
        if sum(self.board[self.PlayerSets[0][0]:self.PlayerSets[0][-1]])==0:
            '''
            #for testing and visualization
            #opponent's remaining stones in play:
            sumsum = sum(self.board[self.PlayerSets[1][0]:self.PlayerSets[1][-1]])
            scorebefore = self.board[self.PlayerSets[1][-1]] 
            print(f'sumsum {sumsum}')
            print(f'scorebefore {scorebefore}')
            '''

            #add opponent's remaining stones in play to opponent's store
            self.board[self.PlayerSets[1][-1]] += sum(self.board[self.PlayerSets[1][0]:self.PlayerSets[1][-1]])
            
            #empty all opponent's pits:
            for i in  self.PlayerSets[1][0:-1]: #self.PlayerSets[1]:
                self.board[i] = 0

            self.endGame = True
        
        # if last move NOT IN Current Player's goal:
        if lastPointer != self.PlayerSets[0][-1]: #RR PlayerSets=[[CurrentPlayer's pits],[OppositePlayer's pits]] 
            #switch player
            self.CurrentPlayerIs0 = not self.CurrentPlayerIs0 # move to next player
            #switch Player sets so that PlayerSets[0] always corresponds to current player
            self.PlayerSets.reverse() # PlayerSets=[[CurrentPlayer's pits],[OppositePlayer's pits]]
        
        self.printBoard()
        



    # Initialize function - called every time an object is created
    def __init__(self, Pits, Stones):
        self.Npits = Pits
        self.Nstones = Stones

        # Indexing - defines which list elements belong to which player
        self.Player0Start = 0
        self.Player0End = self.Npits 
        self.Player1Start = self.Npits + 1
        self.Player1End = self.Npits * 2 + 1

        # initialize list of stone values in pits:
        self.board = [0] * (2*Pits+2) 

        # initialize list of pit indexing
        self.boardIndexing = [0] * (2*Pits+2) 
        for i in  range(len(self.boardIndexing)):
            self.boardIndexing[i] = i
        #self.boardIndexing = list(enumerate(self.board))

        #Player0 stones
        for x in range(self.Player0End): #Pits
            self.board[x] = Stones
        
        #Player1 stones
        for x in range(self.Player1Start,self.Player1End): #(Pits+1,Pits*2+1)
            self.board[x] = Stones
            #self.board[x] = x

        #Delete - for testing;
        #self.board[2*Pits+1] = 3
        
        # Fields in each player's control = set of 2 sets(of pit indexing):
        # PlayerSets=[[CurrentPlayer's pits],[OppositePlayer's pits]]
        if self.CurrentPlayerIs0:
            self.PlayerSets = [self.boardIndexing[self.Player0Start:self.Player0End+1], self.boardIndexing[self.Player1Start:self.Player1End+1]]
        else: #Redundant condition as CurrentPlayerIs0 always true in initialization, but just in case and for readability
            self.PlayerSets = [self.boardIndexing[self.Player1Start:self.Player1End+1], self.boardIndexing[self.Player0Start:self.Player0End+1]]
        
        self.printBoard()

        

