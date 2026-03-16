import signal

from Kalah import KalahGame


GameActive = False


## function to handle ctrl-C and reasonable shutdown
def signal_handler(sig, frame):
    GameActive = False
    print('Game interrupted:: You pressed Ctrl+C!')




def main():
    print("% Main Started")
    GameActive = True

    #RR Listen for interrupt on 'Ctrl+C':
    signal.signal(signal.SIGINT, signal_handler)
    
    #RR Ask player to define game parameters
    myPits = input("Enter number of pits per player: ")
    myStones = input("Enter number of stones per pit: ")
    myPits = int(myPits)
    myStones = int(myStones)

    #RR Create a game board with given parameters:
    myGame = KalahGame(myPits, myStones)

    #RR Ask player to define who goes first
    myGame.askForFirstPlayer()


    while GameActive:

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