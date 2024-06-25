import pygame
BLACK = 0
WHITE = 1
SQSIZE = 80

# Holds information about a game piece
class Checker:
    def __init__(self, color, x, y, graph):
        self.color = color
        self.graph = graph
        self.king = False
        self.sprite = "red.png" if color == WHITE else "black.png"
        self.image = pygame.image.load(self.sprite)
        self.image.set_colorkey(self.image.get_at((0,0)))
        self.updateLocation(x, y)
    
    def updateLocation(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x -40, self.y - 40, SQSIZE, SQSIZE)
    
    def kinged(self, sprite, graph):
        self.king = True
        self.sprite = sprite
        self.image = pygame.image.load(self.sprite)
        self.image.set_colorkey(self.image.get_at((0,0)))
        self.graph = graph


# Handles all the game logic and holds the pieces
class Game:
    def __init__(self):
        self.gameOver = False
        self.createPositions()
        self.createWhiteGraph()
        self.createBlackGraph()
        self.createKingGraph()
        self.createPieces()
        self.selected = None
        self.possibleMoves = []
        self.highlightRects = []
        self.forcedMoves = []
        self.turn = BLACK
        self.canJump = False
        self.lastMoved = None
        self.getValidMoves()

# Creates a dictionary containing the coordinates for each playable space
# Key: the space number in accordance with standard checkers numbering
# Value: the coordinates (x, y) the point to the center of each playable space
    def createPositions(self):
        positions = {}
        for i in range(8):
            for j in range(4):
                x = j * 160 + 40 if i % 2 == 1 else j * 160 + 120
                y = i * 80 + 40
                positions[i*4 + j + 1] = (x, y)
        
        self.positions = positions

# Creates the connections between points for the white (red) pieces using a dictionary
# Key: the starting square
# Value: the spaces that a piece can move to from the key
    def createWhiteGraph(self):
        graph = {}
        for k, _ in self.positions.items():
            edges = []
            if k <= 28:
                edges.append(k + 4)
            if k <= 28 and k % 4 != 0 and k % 8 <= 4:
                edges.append(k + 5)
            if k <= 28 and k % 4 != 1 and k % 8 in (0, 6, 7):
                edges.append(k + 3)
            graph[k] = edges
        
        self.whiteGraph = graph

# Same as the white graph, but for the black pieces (basically just inverts the white graph)
    def createBlackGraph(self):
        connections = [[] for _ in range(32)]
        for vert, edges in self.whiteGraph.items():
            for e in edges:
                connections[e-1].append(vert)

        graph = {}
        for i in range(32):
            graph[i+1] = connections[i]

        self.blackGraph = graph

    def createKingGraph(self):
        connections = [[] for _ in range(32)]
        for vert, edges in self.whiteGraph.items():
            for e in edges:
                connections[e-1].append(vert)
        
        for vert, edges in self.blackGraph.items():
            for e in edges:
                connections[e-1].append(vert)
        
        graph = {}
        for i in range(32):
            graph[i+1] = connections[i]
        
        self.kingGraph = graph
# Creates a dictionary containing the pieces
# Key: the space on the board
# Value: the piece that exists there (otherwise: None)
    def createPieces(self):
        pieces = {}
        # The red pieces
        for i in range(1, 13):
            pieces[i] = Checker(WHITE, self.positions[i][0], self.positions[i][1], self.whiteGraph)
        # Empty spaces in the middle
        for i in range(13, 21):
            pieces[i] = None
        # The black pieces
        for i in range(21, 33):
            pieces[i] = Checker(BLACK, self.positions[i][0], self.positions[i][1], self.blackGraph)

        self.pieces = pieces

# draw pieces and available moves of the selected piece
    def draw(self, screen:pygame.display):
        for _, p in self.pieces.items():
            if type(p) is Checker:
                screen.blit(p.image, p.rect)
        
        if self.selected:
            self.drawMoves(screen)

# Logic for a click on screen
    def clicked(self, pos):
        updated = False

        if self.gameOver:
            return

        # Check if a piece was clicked
        for position, piece in self.pieces.items():
            if type(piece) is Checker:
                if piece.rect.collidepoint(pos) and piece.color == self.turn:
                    self.selected = position
                    self.findMoves()
                    updated = True
                    break
    
        # If a piece was not clicked, check if it is a move
        if not updated:
            for i in range(len(self.highlightRects)):
                if self.highlightRects[i].collidepoint(pos):
                    try:
                        location = self.possibleMoves[i]
                        difference = abs(self.selected - location)
                        self.movePiece(location)
                        self.selected = location
                        additionalJumps = self.checkJump(self.pieces[location], location)
                        if len(additionalJumps) > 0 and difference >= 7:
                            self.forcedMoves = additionalJumps
                        else:
                            self.turn = BLACK if self.turn == WHITE else WHITE
                            self.getValidMoves()
                        break
                    except KeyError:
                        print('key error line 157')
                        pass

            self.selected = None

    def findMoves(self):
        self.possibleMoves = []
        self.highlightRects = []
        piece = self.pieces[self.selected]
        if type(piece) is Checker:
            if len(self.forcedMoves) == 0:
                for v in piece.graph[self.selected]:
                    if self.pieces[v] == None:
                        self.addToMoves(v)
            else:
                moves = self.checkJump(piece, self.selected)
                for move in moves:
                    self.addToMoves(move)

    def checkJump(self, piece, position):
        moves = []
        if type(piece) is Checker:
            if piece.color == self.turn:
                for adj in piece.graph[position]:
                    if type(self.pieces[adj]) is Checker:
                        if self.pieces[adj].color != piece.color:
                            for jump in piece.graph[adj]:
                                # Using the numbered squares reference, a valid jump moves 7 or 9 squares
                                if (abs(self.selected - jump) == 7 or abs(self.selected - jump) == 9) and self.pieces[jump] == None:
                                    moves.append(jump)
        return moves
    
    def movePiece(self, moveTo):
        self.pieces[moveTo] = self.pieces[self.selected]
        self.pieces[moveTo].updateLocation(*self.positions[moveTo])
        self.pieces[self.selected] = None

        if self.pieces[moveTo].color == WHITE and moveTo >= 29:
            self.pieces[moveTo].kinged("redKing.png", self.kingGraph)
        
        elif self.pieces[moveTo].color == BLACK and moveTo <= 4:
            self.pieces[moveTo].kinged("blackKing.png", self.kingGraph)

        # Check for capture and where
        difference = abs(self.selected - moveTo)

        # Jumps move 7 or 9 spaces
        if difference == 7 or difference == 9:
            # White piece
            if moveTo > self.selected:
                # Find a line in the graph that goes from starting point to end point
                for i in self.whiteGraph[self.selected]:
                    for j in self.whiteGraph[i]:
                        if j == moveTo:
                            # End point found, remove the midpoint
                            self.pieces[i] = None
            # Black piece, same as above
            elif moveTo < self.selected:
                for i in self.blackGraph[self.selected]:
                    for j in self.blackGraph[i]:
                        if j == moveTo:
                            self.pieces[i] = None

        self.highlightRects = []
        self.possibleMoves = []

# Draw the possible moves for the selected piece
    def drawMoves(self, screen):
        for position in self.possibleMoves:
            cords = self.positions[position]
            x = cords[0] - 40
            y = cords[1] - 40
            pygame.draw.circle(screen, "green", cords, 5)
    
    def addToMoves(self, position):
        self.possibleMoves.append(position)
        x, y = self.positions[position]
        self.highlightRects.append(pygame.Rect(x - 40, y - 40, SQSIZE, SQSIZE))

    def getValidMoves(self):
        moves = []
        for k, piece in self.pieces.items():
            if type(piece) is Checker:
                if piece.color == self.turn:
                    self.selected = k
                for move in self.checkJump(piece, k):
                    moves.append(move)
        
        self.forcedMoves = moves
    
    def checkWinner(self, screen):
        whiteLeft = False
        blackLeft = False
        for _, piece in self.pieces.items():
            if type(piece) is Checker:
                if piece.color == WHITE:
                    whiteLeft = True
                if piece.color == BLACK:
                    blackLeft = True
        
        if not whiteLeft:
            self.winnerScreen(screen, "BLACK")
        elif not blackLeft:
            self.winnerScreen(screen, "WHITE")
    
    def winnerScreen(self, screen, winner):
        self.gameOver = True
        winnerScreen = pygame.Surface((640, 640), pygame.SRCALPHA)
        winnerScreen.fill(pygame.Color(0,255,0,75))
        screen.blit(winnerScreen, (0,0))
        font = pygame.font.Font(None, 30)
        winnerIs = "WINNER IS"
        text = font.render(winnerIs, True, "black")
        text_rect = text.get_rect(center=(320, 280))
        screen.blit(text, text_rect)
        text = font.render(winner, True, "black")
        text_rect = text.get_rect(center=(320, 320))
        screen.blit(text, text_rect)