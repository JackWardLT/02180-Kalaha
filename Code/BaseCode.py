import signal

from Kalah import KalahGame


GameActive = True


## function to handle ctrl-C and reasonable shutdown
def signal_handler(sig, frame):
    GameActive = False
    print('Game interrupted:: You pressed Ctrl+C!')




def main():
    print("% Main Started")

    #RR Listen for interrupt on 'Ctrl+C':
    signal.signal(signal.SIGINT, signal_handler)
    
    #RR Ask player to define game parameters
    mycups = input("Enter number of cups per player: ")
    mystones = input("Enter number of stones per cup: ")
    mycups = int(mycups)
    mystones = int(mystones)

    #RR Create a game board with given parameters:
    myGame = KalahGame(mycups, mystones)

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
    #print(GameActive)

    

    print("% Main Terminated")


if __name__ == "__main__":

    main()