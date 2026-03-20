import signal

from Kalah import KalahGame
from KalahaAI import KalahaAI

GameActive = False


## function to handle ctrl-C and reasonable shutdown
def signal_handler(sig, frame):
    GameActive = False
    print('Game interrupted:: You pressed Ctrl+C!')

def select_Difficulty():
    while True:
        difficulty = input("Select difficulty (easy, medium, hard): ").lower()
        if difficulty == 'easy':
            return 2
        elif difficulty == 'medium':
            return 4
        elif difficulty == 'hard':
            return 6
        else:
            print("Invalid input. Please enter 'easy', 'medium', or 'hard'.")



def main():
    print("% Main Started")
    GameActive = True

    #RR Listen for interrupt on 'Ctrl+C':
    signal.signal(signal.SIGINT, signal_handler)
    
    #RR Ask player to define game parameters
    myPits = int(input("Enter number of pits per player: "))
    myStones = int(input("Enter number of stones per pit: "))
    difficulty = select_Difficulty()
    #RR Create a game board with given parameters:
    myGame = KalahGame(myPits, myStones)

    #Create AI Player
    myGame.ai = KalahaAI(depth=difficulty)

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