import copy

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
    ComputerIs0 = False

    SelectedMove = -1

    endGame = False

    InputValid = False

    # Initialize function - called every time an object is created
    def __init__(self, Pits, Stones):
        self.ai = None
        
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
        if self.ComputerIs0:
            ai_score = self.board[self.Player0End]
            human_score = self.board[self.Player1End]
        else:
            ai_score = self.board[self.Player1End]
            human_score = self.board[self.Player0End]

        if human_score > ai_score:
            print('\n Game finished. You Win!')
        elif human_score < ai_score:
            print('\n Game finished. You Lose!')
        else:
            print('\n Game finished. Draw!')

        print(f'\n Results: \n Your score: {human_score}   AI score: {ai_score}\n')

    def askForFirstPlayer(self):
        InputValid = False
        while not InputValid:
            firstPlayer = input("First move made by you? (y/n): ")
            InputValid = self.validatePlayer(firstPlayer)
        self.PlayerSets = [self.boardIndexing[self.Player0Start:self.Player0End+1], self.boardIndexing[self.Player1Start:self.Player1End+1]]

        if firstPlayer in ['y', 'Y', 'Yes']:
            self.CurrentPlayerIs0 = True
            #RR Redundant assignment as PlayerSets for True already assigned in initialization, but just in case and for readability
            #RR PlayerSets=[[CurrentPlayer's pits],[OppositePlayer's pits]]
        else: 
            self.ComputerIs0 = True
    
    def validatePlayer(self, InputVar):
        if InputVar not in ['y', 'Y', 'Yes', 'n', 'N', 'No']:
            print('Input invalid! Please try again!')
            return False
        else: 
            return True

    def askForMove(self):
        InputValid = False
        while not InputValid:
            if self.ComputerIs0 == self.CurrentPlayerIs0:
                SelectedMove = self.ai.chooseMove(self)
                print(f"\nComputer chooses pit {SelectedMove}")
                InputValid = self.validateMove(SelectedMove, self.PlayerSets[0][0], self.PlayerSets[0][-2])
                #print(f'in if InputValid {InputValid}')
            else:
                if self.CurrentPlayerIs0:
                    SelectedMove = input(f"\nPlayer - please select move (in range {self.Player0Start} - {self.Player0End-1} ): ")
                    InputValid = self.validateMove(SelectedMove, self.Player0Start, self.Player0End-1)
                else:
                    SelectedMove = input(f"\nPlayer - please select move (in range {self.Player1Start} - {self.Player1End-1} ): ")
                    InputValid = self.validateMove(SelectedMove, self.Player1Start, self.Player1End-1)

        
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

    def getLegalMoves(self):
        player_pits = self.PlayerSets[0][0:-1] #RR PlayerSets=[[CurrentPlayer's pits],[OppositePlayer's pits]] - return all pits of current player except the last one which is the goal
        return [pit for pit in player_pits if self.board[pit] > 0]

    def makeMove(self, theMove, print_board=True):
        pointer = theMove + 1
        StonesInPit = self.board[theMove]

        self.board[theMove] = 0

        for i in range(StonesInPit):
            if pointer == self.PlayerSets[1][-1]:
                pointer += 1
            if pointer == self.Player1End + 1:
                pointer = self.Player0Start

            self.board[pointer] += 1
            pointer += 1

        lastPointer = pointer - 1
        extra_turn = (lastPointer == self.PlayerSets[0][-1])

        if not extra_turn and self.board[lastPointer] == 1 and lastPointer in self.PlayerSets[0][0:-1] and self.board[2*self.Npits - lastPointer] != 0:
            self.board[self.PlayerSets[0][-1]] += self.board[2*self.Npits - lastPointer]
            self.board[2*self.Npits - lastPointer] = 0
            self.board[self.PlayerSets[0][-1]] += self.board[lastPointer]
            self.board[lastPointer] = 0

        current_side_empty = sum(self.board[self.PlayerSets[0][0]:self.PlayerSets[0][-1]]) == 0
        opposite_side_empty = sum(self.board[self.PlayerSets[1][0]:self.PlayerSets[1][-1]]) == 0

        if current_side_empty or opposite_side_empty:
            self.board[self.PlayerSets[0][-1]] += sum(self.board[self.PlayerSets[0][0]:self.PlayerSets[0][-1]])
            self.board[self.PlayerSets[1][-1]] += sum(self.board[self.PlayerSets[1][0]:self.PlayerSets[1][-1]])

            for i in self.PlayerSets[0][0:-1]:
                self.board[i] = 0
            for i in self.PlayerSets[1][0:-1]:
                self.board[i] = 0

            self.endGame = True

        if not extra_turn:
            self.CurrentPlayerIs0 = not self.CurrentPlayerIs0
            self.PlayerSets.reverse()

        if print_board:
            self.printBoard()

        return extra_turn        

    #used to replicate the board state for the AI to simulate moves without affecting the actual game state
    def clone(self):
        return copy.deepcopy(self)
    
    def gameResult(self):
        if self.ComputerIs0:
            computer_store = self.board[self.Player0End]
            human_store = self.board[self.Player1End]
        else:
            computer_store = self.board[self.Player1End]
            human_store = self.board[self.Player0End]

        if computer_store > human_store:
            return 1
        elif computer_store < human_store:
            return -1
        return 0
