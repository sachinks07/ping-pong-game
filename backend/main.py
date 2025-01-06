from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import random
import asyncio
from typing import Dict, Set
from dataclasses import dataclass, asdict

app = FastAPI()

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game constants
GAME_WIDTH = 800
GAME_HEIGHT = 600
PADDLE_HEIGHT = 100
PADDLE_WIDTH = 20
BALL_SIZE = 15
OBSTACLE_SIZE = 50
BALL_SPEED = 5
PADDLE_SPEED = 10

@dataclass
class GameState:
    # Initial ball position at center
    ball_x: float = GAME_WIDTH / 2
    ball_y: float = GAME_HEIGHT / 2
    ball_dx: float = BALL_SPEED
    ball_dy: float = BALL_SPEED
    
    # Paddle positions
    paddle1_y: float = (GAME_HEIGHT - PADDLE_HEIGHT) / 2
    paddle2_y: float = (GAME_HEIGHT - PADDLE_HEIGHT) / 2
    
    # Scores
    score1: int = 0
    score2: int = 0
    
    # Obstacles - positioned to avoid center area
    obstacle1_x: float = random.randint(int(GAME_WIDTH/4), int(GAME_WIDTH/2 - 100))
    obstacle1_y: float = random.randint(OBSTACLE_SIZE, GAME_HEIGHT-OBSTACLE_SIZE)
    obstacle2_x: float = random.randint(int(GAME_WIDTH/2 + 100), int(3*GAME_WIDTH/4))
    obstacle2_y: float = random.randint(OBSTACLE_SIZE, GAME_HEIGHT-OBSTACLE_SIZE)

class GameManager:
    def __init__(self):
        self.games: Dict[str, GameState] = {}
        self.connections: Dict[str, Set[WebSocket]] = {}
        self.game_loops: Dict[str, asyncio.Task] = {}

    async def create_game(self, game_id: str):
        """Initialize a new game with default state"""
        self.games[game_id] = GameState()
        self.connections[game_id] = set()
        # Start game loop
        self.game_loops[game_id] = asyncio.create_task(self.game_loop(game_id))

    async def join_game(self, websocket: WebSocket, game_id: str):
        """Handle new player connection"""
        await websocket.accept()
        if game_id not in self.connections:
            await self.create_game(game_id)
        self.connections[game_id].add(websocket)

    async def leave_game(self, websocket: WebSocket, game_id: str):
        """Handle player disconnection"""
        self.connections[game_id].remove(websocket)
        if not self.connections[game_id]:
            if game_id in self.game_loops:
                self.game_loops[game_id].cancel()
                del self.game_loops[game_id]
            del self.connections[game_id]
            del self.games[game_id]

    def check_collisions(self, game: GameState):
        """Handle all collision detection and response"""
        # Paddle collisions
        if (game.ball_x <= PADDLE_WIDTH and 
            game.paddle1_y <= game.ball_y <= game.paddle1_y + PADDLE_HEIGHT):
            game.ball_dx = abs(game.ball_dx)  # Bounce right
            game.ball_dx *= 1.1  # Speed up slightly
        
        if (game.ball_x >= GAME_WIDTH - PADDLE_WIDTH - BALL_SIZE and 
            game.paddle2_y <= game.ball_y <= game.paddle2_y + PADDLE_HEIGHT):
            game.ball_dx = -abs(game.ball_dx)  # Bounce left
            game.ball_dx *= 1.1  # Speed up slightly

        # Obstacle collisions
        for obs_x, obs_y in [(game.obstacle1_x, game.obstacle1_y), 
                            (game.obstacle2_x, game.obstacle2_y)]:
            if (obs_x <= game.ball_x <= obs_x + OBSTACLE_SIZE and 
                obs_y <= game.ball_y <= obs_y + OBSTACLE_SIZE):
                # Calculate collision direction
                dx = game.ball_x - (obs_x + OBSTACLE_SIZE/2)
                dy = game.ball_y - (obs_y + OBSTACLE_SIZE/2)
                
                if abs(dx) > abs(dy):
                    game.ball_dx *= -1
                else:
                    game.ball_dy *= -1

        # Wall collisions
        if game.ball_y <= 0 or game.ball_y >= GAME_HEIGHT - BALL_SIZE:
            game.ball_dy *= -1

        # Scoring
        if game.ball_x <= 0:
            game.score2 += 1
            self.reset_ball(game)
        elif game.ball_x >= GAME_WIDTH:
            game.score1 += 1
            self.reset_ball(game)

    def reset_ball(self, game: GameState):
        """Reset ball to center with random direction"""
        game.ball_x = GAME_WIDTH / 2
        game.ball_y = GAME_HEIGHT / 2
        game.ball_dx = BALL_SPEED * (1 if random.random() > 0.5 else -1)
        game.ball_dy = BALL_SPEED * (1 if random.random() > 0.5 else -1)

    async def game_loop(self, game_id: str):
        """Main game loop for updating game state"""
        try:
            while True:
                if game_id in self.games:
                    game = self.games[game_id]
                    
                    # Update ball position
                    game.ball_x += game.ball_dx
                    game.ball_y += game.ball_dy
                    
                    # Check all collisions
                    self.check_collisions(game)
                    
                    # Send updated state to all players
                    if game_id in self.connections:
                        websockets = self.connections[game_id]
                        await asyncio.gather(
                            *[ws.send_json(asdict(game)) for ws in websockets]
                        )
                    
                    # Control game speed
                    await asyncio.sleep(1/60)  # 60 FPS
                else:
                    break
        except asyncio.CancelledError:
            pass

game_manager = GameManager()

@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await game_manager.join_game(websocket, game_id)
    try:
        while True:
            data = await websocket.receive_json()
            if game_id in game_manager.games:
                game = game_manager.games[game_id]
                
                # Update paddle position
                if player_id == "1":
                    game.paddle1_y = max(0, min(GAME_HEIGHT - PADDLE_HEIGHT, data["paddleY"]))
                else:
                    game.paddle2_y = max(0, min(GAME_HEIGHT - PADDLE_HEIGHT, data["paddleY"]))
            
    except WebSocketDisconnect:
        await game_manager.leave_game(websocket, game_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)