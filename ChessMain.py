import sys
sys.path.append('E:\pythonProject\project\Chess\Chess')  # Adjust the path as necessary
from Chess import ChessEngine, smartMoveFinder
import pygame as p
from multiprocessing import Process, Queue

WIDTH, HEIGHT = 512, 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

'''
INIT a global dictionary of images. This will be called exactly once in the main
'''

def loadImages():
    pieces = ["wR", "wN", "wB", "wQ", "wK", "bR", "bN", "bB", "bQ", "bK", "wp", "bp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # when a move is made

    loadImages()
    running = True

    sqSELECTED = ()  # no of sq selected, keep track of the last click of the user
    playerClicks = []  # keep track of player clicks (two tuples: [(6, 4)])
    gameOver = False
    playerOne= True #for white piece
    playerTwo = False #for black piece
    AIThinking=False
    moveFinderProcess=None
    moveUndone=False

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sqSELECTED == (row, col):  # if user clicks the same sq twice
                        sqSELECTED = ()  # unselect
                        playerClicks = []  # reset
                    else:
                        sqSELECTED = (row, col)
                        playerClicks.append(sqSELECTED)  # append for both 1st & 2nd click

                    if len(playerClicks) == 2 and humanTurn:  # after the second click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSELECTED = ()  # reset user clicks
                                playerClicks = []  # if not, then player len would not be 2 again
                        if not moveMade:
                            playerClicks = [sqSELECTED]
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z is pressed
                    gs.undoMove()
                    sqSELECTED=()
                    playerClicks=[]
                    moveMade = True
                    animate = False
                    gameOver=False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking=False
                    moveUndone=True

                if e.key == p.K_r: #reset
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSELECTED = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone=True

        #ai move finder logic
        if not gameOver and not humanTurn and not moveUndone :
            if not AIThinking:
                AIThinking=True
                print("thinking.....")
                returnQueue = Queue()
                moveFinderProcess=Process(target=smartMoveFinder.findBestMove, args=(gs,validMoves, returnQueue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():  # Corrected method
                print("done...")
                AIThinking = False
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = smartMoveFinder.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                moveUndone=False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)  # Fix the reference to the last move
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSELECTED)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'B L A C K  W I N S  B Y  C H E C K M A T E')
            else:
                drawText(screen, 'W H I T E  W I N S  B Y  C H E C K M A T E')
        elif gs.staleMate:
            gameOver= True
            drawText(screen, 'D R A W  B Y  S T A L E M A T E')
        clock.tick(MAX_FPS)
        p.display.flip()

# THIS WILL HIGHLIGHT THE SQUARE SELECTED
def highlightSquare(screen, gs, validMoves, sqSELECTED):
    if sqSELECTED != ():
        r, c = sqSELECTED
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight the selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('black'))

            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSELECTED):
    drawBoard(screen)  # draw squares on the board
    highlightSquare(screen, gs, validMoves, sqSELECTED)
    drawPieces(screen, gs.board)  # draw pieces on the board

def drawBoard(screen):
    global colors
    colors = [p.Color("#ADD8E6"), p.Color("#0095B6")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock):
    global colors  # Assuming colors is defined elsewhere

    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 2  # Lower value for faster animation

    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):
        r = move.startRow + dR * frame / frameCount
        c = move.startCol + dC * frame / frameCount

        drawBoard(screen)
        drawPieces(screen, board)

        # Erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # Draw captured piece onto rectangle if there's a captured piece
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # Draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        p.display.flip()
        clock.tick(120)  # Higher value for faster updates



def drawText(screen, text):
    font = p.font.SysFont("Roboto Mono", 32, True, False)
    textObject = font.render(text, True, p.Color('White'))

    # Create a background box
    textBackground = p.Surface((textObject.get_width() + 20, textObject.get_height() + 20))
    textBackground.fill(p.Color('Grey'))

    # Calculate position for the text and the background
    textRect = textBackground.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    textPos = textObject.get_rect(center=textRect.center)

    # Draw the background and then the text
    screen.blit(textBackground, textRect.topleft)
    screen.blit(textObject, textPos.topleft)


if __name__ == "__main__":
    main()
