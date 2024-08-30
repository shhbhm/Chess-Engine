import random

# Piece values
pieceScore = {
    "k": 0, "q": 9, "r": 5, "b": 3, "n": 3, "p": 1,  # black pieces
    "K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1   # white pieces
}

# Positional scores for each piece

whitePawnScores =[[8, 8, 8, 8, 8, 8, 8, 8],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [5, 6, 6, 7, 7, 6, 6, 5],
                    [2, 3, 3, 5, 5, 3, 3, 2],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [0,0,0,0,0,0,0,0] ]

blackPawnScores =[[0, 0, 0, 0,0,0,0,0],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                    [2, 3, 3, 5, 5, 3, 3, 2],
                    [5, 6, 6, 7, 7, 6, 6, 5],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                  [8, 8, 8, 8, 8, 8, 8, 8]]

knightScore = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

bishopScore = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3,4,3,3,4,3, 2],
    [1, 2,3,4,4,3,2, 1],
    [1, 2,3,4,4,3,2, 1],
    [2, 3,4,3,3,4,3, 2],
    [3, 4,3,2,2,3,4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]

rookScore = [
    [4,3,4,4,4,4,3,4],
    [4,4,4,4,4,4,4,4],
    [1,1,2,3,3,2,1,1],
    [1,2,3,4,4,3,2,1],
    [1,2,3,4,4,3,2,1],
    [1,1,2,2,2,2,1,1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4,3,4,4,4,4,3,4]
]

queenScore = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3,3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1,2,3,3,3,2,2,1],
    [1,1,2,3,3,1,1,1],
    [1,2,2,3,3,1,1,1],
    [1, 1, 1, 3, 1, 1, 1, 1]
]


# Assigning the scores to each piece
piecePositionScores = {
    "P": whitePawnScores,  # Use whitePawnScores here
    "N": knightScore,
    "B": bishopScore,
    "R": rookScore,
    "Q": queenScore,
    "K": knightScore
}


# Constants
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

# To store the best move found
nextMove = None

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

def findBestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove)

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        gs.undoMove()
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return maxScore

def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE  # Black wins
        else:
            return CHECKMATE  # White wins
    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piecePositionScore = 0
                if square[1] != "K":
                    if square[1] == "p":
                        # Check the color of the pawn to use the appropriate score
                        if square[0] == 'w':
                            piecePositionScore = whitePawnScores[row][col]
                        else:
                            piecePositionScore = blackPawnScores[row][col]
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][col]

                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore * .1
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore * .1
    return score

