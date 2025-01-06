# Multiplayer Ping Pong Game

A real-time multiplayer ping pong game with dynamic obstacles built using Python (FastAPI) for the backend and React for the frontend. Players can compete across different browser tabs using WebSocket communication.

<img width="1791" alt="Screenshot 2025-01-06 at 2 50 26 PM" src="https://github.com/user-attachments/assets/5e0a45c6-151b-4ea2-8be0-cc3cd7d1823a" />

## Features

- Real-time multiplayer gameplay
- Dynamic obstacles that affect ball trajectory
- Score tracking system
- Paddle control using arrow keys
- Cross-browser tab gameplay
- Automatic game state synchronization
- Visual feedback for game events

## Prerequisites

Before you begin, ensure you have installed:
- Python 3.8 or higher
- Node.js 16.0 or higher
- npm (Node Package Manager)

## Project Structure

```
ping-pong-game/
├── backend/
│   ├── main.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── PongGame.jsx
    │   ├── App.jsx
    │   └── main.jsx
    ├── index.html
    └── package.json
```

## Installation & Setup

### Backend Setup

1. Create and activate a virtual environment:
```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install fastapi uvicorn websockets
```

3. Start the server:
```bash
python main.py
```
The backend server will start on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```
The frontend will be available at `http://localhost:5173`

## How to Play

1. Open `http://localhost:5173` in your browser for Player 1
2. Share the generated game URL (shown in console) with Player 2
3. Use the arrow keys (↑ and ↓) to move your paddle
4. Try to get the ball past your opponent's paddle while avoiding or using the obstacles
5. First player to reach the target score wins!

## Game Controls

- ↑ (Up Arrow): Move paddle up
- ↓ (Down Arrow): Move paddle down

## Game Rules

1. Each player controls a paddle on their side of the screen
2. The ball bounces off paddles, walls, and obstacles
3. Score points by getting the ball past your opponent's paddle
4. Ball speed increases slightly with each paddle hit
5. Obstacles can be used strategically to change ball direction

## Technical Details

### Backend
- Built with FastAPI for WebSocket support
- Real-time game state management
- Collision detection system
- Player session handling

### Frontend
- React-based user interface
- Canvas for game rendering
- WebSocket for real-time communication
- Responsive design

## Troubleshooting

1. WebSocket Connection Issues:
   - Ensure the backend server is running
   - Check if the correct ports are being used
   - Verify no firewall is blocking WebSocket connections

2. Game Performance:
   - Close other browser tabs to improve performance
   - Ensure stable internet connection for both players

3. Common Errors:
   - "WebSocket connection failed": Check if backend server is running
   - "Game not responding": Refresh the page and reconnect

## Development

To modify the game:

1. Game Constants (backend/main.py):
   - Adjust BALL_SPEED for different difficulty levels
   - Modify PADDLE_HEIGHT and PADDLE_WIDTH
   - Change OBSTACLE_SIZE for different challenge levels

2. Visual Customization (frontend/src/components/PongGame.jsx):
   - Modify colors in the render function
   - Adjust canvas dimensions
   - Change paddle and ball sizes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with FastAPI and React
- Inspired by classic Pong game mechanics
- Enhanced with modern multiplayer capabilities


