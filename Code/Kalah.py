class KalahGame:
    """
    Example starting layout ( 7 cups per player, 3 stones in each)
    Player 2: [14] [13] [12] [11] [10]  [9]  [8]        # Field indexing
                3    3    3    3    3    3   3
      [15] 0                                    0 [7]   
                3    3    3    3    3    3   3
    Player 1:  [0]  [1]  [2]  [3]  [4]  [5]  [6]
         
    """
    

    board = list() # list of Nr of stones in each cup
    boardIndexing = list() # list of cup indexing [0] to e.g.[13]
    PlayerSets = list() # PlayerSets=[[CurrentPlayer's cups],[OppositePlayer's cups]]
    

    Ncups = 0
    Nstones = 0

    Player0Start = 0
    Player0End = 0
    Player1Start = 0
    Player1End = 0

    CurrentPlayerIs0 = True

    SelectedMove = 0

    endGame = False


    # Print function - displays current state of the board
    def printBoard(self):
        #Arrange state of the stones and score in readable format
        #Player0
        Player0List = '                  ' + (str(self.board[self.Player0Start]))
        Player0IndexList = '        Player0:'
        
        for i in range(self.Player0Start+1,self.Player0End):
            if len(str(self.board[i]))<2:
                Player0List = Player0List + ' '
            Player0List = Player0List + '  -  '  + str(self.board[i])
            
        
        for i in range(self.Player0Start,self.Player0End):
            Player0IndexList = Player0IndexList + ' ['  + str(self.boardIndexing[i]) + ']  '
            if len(str(self.boardIndexing[i]))<2:
                Player0IndexList = Player0IndexList + ' '

        #Player1
        Player1List =  '                  ' + (str(self.board[self.Player1End-1]))
        Player1IndexList = '        Player1:'

        for i in reversed(range(self.Player1Start,self.Player1End-1)):
            if len(str(self.board[i]))<2:
                Player1List = Player1List + ' '
            Player1List = Player1List + '  -  '  + str(self.board[i])
        
        for i in reversed(range(self.Player1Start,self.Player1End)):
            Player1IndexList = Player1IndexList + ' ['   + str(self.boardIndexing[i]) + ']  '
            if len(str(self.boardIndexing[i]))<2:
                Player1IndexList = Player1IndexList + ' '


        #goal fields Player1 - Player0
        goalList =   '        [' + str(self.boardIndexing[self.Player1End]) + '] ' + str(self.board[self.Player1End])
        for i in range(self.Ncups):
            goalList = goalList+ '       '
        goalList = goalList + '   ' + str(self.board[(self.Player0End)]) + ' [' + str(self.boardIndexing[self.Player0End]) + '] ' 
        
        print()
        #Player1
        print(Player1IndexList)
        print (Player1List)

        #Goals
        print (goalList)
        
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
        firstPlayer = input("First move made by you? (y/n): ")
        assert (firstPlayer in ['y', 'n', 'Y', 'N']),  print('Invalid input, please start over!')

        if firstPlayer in ['y', 'Y', 'Yes']:
            self.CurrentPlayerIs0 = True
            #RR Redundant assignment as PlayerSets for True already assigned in initialization, but just in case and for readability
            #RR PlayerSets=[[CurrentPlayer's cups],[OppositePlayer's cups]]
            self.PlayerSets = [self.boardIndexing[self.Player0Start:self.Player0End+1], self.boardIndexing[self.Player1Start:self.Player1End+1]]
        else: 
            self.CurrentPlayerIs0 = False
            #RR If Player1 goes first reverse sets so that PlayerSets[0] always belongs to current player
            self.PlayerSets.reverse()  #RR PlayerSets=[[CurrentPlayer's cups],[OppositePlayer's cups]]

    def askForMove(self):
        if self.CurrentPlayerIs0:
            SelectedMove = input(f"\nPlayer0 - please select move (in range {self.Player0Start} - {self.Player0End-1} ): ")
        else:
            SelectedMove = input(f"\nPlayer1 - please select move (in range {self.Player1Start} - {self.Player1End-1} ): ")
        self.SelectedMove = int(SelectedMove)
    
    def makeMove(self, theMove):
        pointer = theMove+1       
        StonesInCup = self.board[theMove]

        # Empty selected cup
        self.board[theMove] = 0

        #RR based on how many stones in the selected cup, distribute the stones:
        for i in range(StonesInCup):
            # skip opponent's goal (if the stone distribution passes through opponents goal, do not add a stone to it )
            ## RR self.PlayerSets[1][-1] corresponds to last element in opponent's list of cups
            if pointer == self.PlayerSets[1][-1]:  #RR PlayerSets=[[CurrentPlayer's cups],[OppositePlayer's cups]]
                pointer += 1
            # if the move has made a full circle, reset pointer to 0
            if pointer == self.Player1End+1:
                pointer = self.Player0Start

            #RR distribute stones among the cups
            self.board[pointer] += 1
            pointer += 1
        
        lastPointer = pointer-1
        #print (f'lastPointer {lastPointer}')

    
        if lastPointer == self.PlayerSets[0][-1]: # if last move IN Player's goal, make one more move
            self.CurrentPlayerIs0 = self.CurrentPlayerIs0 # redundant move, but the if condition works as condition for next elif
        #if only 1 stone in the last cup, and last cup in current player's set and and opposite cup not empty, 
        #take opponents stones from opposite cup and the stone from last cup
        elif self.board[lastPointer] == 1 and lastPointer in self.PlayerSets[0] and self.board[2*self.Ncups - lastPointer] !=0:         
            '''
            #for testing and visualization:
            goalbeforeadding = self.board[self.PlayerSets[0][-1]]
            #thislocation = self.Ncups + (self.Ncups - lastPointer) = 2*self.Ncups - lastPointer
            #thislocation = self.Ncups - (lastPointer - self.Ncups) = 2*self.Ncups - lastPointer
            thislocation = 2*self.Ncups - lastPointer
            addfromopponent = self.board[thislocation]
            addownlaststone = self.board[lastPointer]
            tothisgoal = self.PlayerSets[0][-1]
            print(f'goalbeforeadding {goalbeforeadding}')
            print(f'addfromopponent {addfromopponent}')
            print(f'addownlaststone {addownlaststone}')
            print(f'tothisgoal {tothisgoal}')
            '''
            # add opponent's stones to player's goal
            #Index self.PlayerSets[0][-1] corresponds to the last element of the first list in PlayerSets = Current player' s goal
            self.board[self.PlayerSets[0][-1]] += self.board[2*self.Ncups - lastPointer]
            self.board[2*self.Ncups - lastPointer] = 0
            # add current player's lest stone to current player's goal
            self.board[self.PlayerSets[0][-1]] += self.board[lastPointer]
            self.board[lastPointer] = 0

        if lastPointer != self.PlayerSets[0][-1]: # if last move NOT IN Current Player's goal 
            self.CurrentPlayerIs0 = not self.CurrentPlayerIs0 # move to next player
            #switch Player sets so that PlayerSets[0] always corresponds to current player
            self.PlayerSets.reverse() # PlayerSets=[[CurrentPlayer's cups],[OppositePlayer's cups]]
        # if the current player has no more moves to make, end game!
        if sum(self.board[self.PlayerSets[0][0]:self.PlayerSets[0][-1]])==0:
            self.endGame = True
        
        self.printBoard()
        



    # Initialize function - called every time an object is created
    def __init__(self, Cups, Stones):
        self.Ncups = Cups
        self.Nstones = Stones

        # Indexing - defines which list elements belong to which player
        self.Player0Start = 0
        self.Player0End = self.Ncups 
        self.Player1Start = self.Ncups + 1
        self.Player1End = self.Ncups * 2 + 1

        self.board = [0] * (2*Cups+2) 
        self.boardIndexing = [0] * (2*Cups+2) 
        for i in  range(len(self.boardIndexing)):
            self.boardIndexing[i] = i
        #self.boardIndexing = list(enumerate(self.board))

        #Player0 stones
        for x in range(self.Player0End): #Cups
            self.board[x] = Stones
        
        #Player1 stones
        for x in range(self.Player1Start,self.Player1End): #(Cups+1,Cups*2+1)
            self.board[x] = Stones
            #self.board[x] = x

        
        # Player sets of fields
        # PlayerSets=[[CurrentPlayer's cups],[OppositePlayer's cups]]
        if self.CurrentPlayerIs0:
            self.PlayerSets = [self.boardIndexing[self.Player0Start:self.Player0End+1], self.boardIndexing[self.Player1Start:self.Player1End+1]]
        else: #Redundant condition as CurrentPlayerIs0 always true in initialization, but just in case and for readability
            self.PlayerSets = [self.boardIndexing[self.Player1Start:self.Player1End+1], self.boardIndexing[self.Player0Start:self.Player0End+1]]
        
        
        self.printBoard()

        

