import signal

from Kalah import KalahGame
from KalahaAI import KalahaAI

GameActive = False


## function to handle ctrl-C and reasonable shutdown
def signal_handler(sig, frame):
    GameActive = False
    print('Game interrupted:: You pressed Ctrl+C!')

def select_Depth():
    while True:
        difficulty = input("Select depth (2, 4, 6): ")
        if difficulty == '2':
            return 2
        elif difficulty == '4':
            return 4
        elif difficulty == '6':
            return 6
        else:
            print("Invalid input. Please enter '2', '4', or '6'.")
    
def select_Evaluation():
    while True:
        evaluation = input("Select evaluation function (Simple, Medium, Advanced): ").lower()
        if evaluation == 'simple':
            return KalahaAI.evaluate_Simple
        elif evaluation == 'medium':
            return KalahaAI.evaluate_Medium
        elif evaluation == 'advanced':
            return KalahaAI.evaluate_Adv
        else:
            print("Invalid input. Please enter 'simple', 'medium', or 'advanced'.")

def select_Pruning():
    while True:
        pruning = input("Select pruning method (None, Alpha-Beta): ").lower()
        if pruning == 'none':
            return KalahaAI.minimax
        elif pruning == 'alpha-beta':
            return KalahaAI.minimax_ab
        else:
            print("Invalid input. Please enter 'none' or 'alpha-beta'.")

def main():
    print("% Main Started")
    GameActive = True

    #RR Listen for interrupt on 'Ctrl+C':
    signal.signal(signal.SIGINT, signal_handler)
    
    #RR Ask player to define game parameters
    myPits = int(input("Enter number of pits per player: "))
    myStones = int(input("Enter number of stones per pit: "))
    depth = select_Depth()
    pruning = select_Pruning()
    evaluation = select_Evaluation()
    #RR Create a game board with given parameters:
    myGame = KalahGame(myPits, myStones)

    #Create AI Player
    myGame.ai = KalahaAI(depth, pruning, evaluation)

    #RR Ask player to define who goes first
    myGame.askForFirstPlayer()

    if myGame.ComputerIs0:
        myGame.askForMove()
        myGame.makeMove(myGame.SelectedMove)  

    while GameActive and not myGame.endGame:

        ##RR Ask Player 0 to make a move
        myGame.askForMove()
        
        ##RR Make the move
        myGame.makeMove(myGame.SelectedMove)

        if myGame.endGame == True:
            break

    myGame.printResults()
    GameActive = False


    print("% Main Terminated")


if __name__ == "__main__":

    main()