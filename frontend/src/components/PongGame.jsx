import React, { useEffect, useRef, useState } from 'react';

const PongGame = () => {
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const [gameState, setGameState] = useState(null);
  const [playerId, setPlayerId] = useState(null);
  const [gameId, setGameId] = useState(null);
  const [error, setError] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);

  // Game constants
  const GAME_WIDTH = 800;
  const GAME_HEIGHT = 600;
  const PADDLE_HEIGHT = 100;
  const PADDLE_WIDTH = 20;
  const BALL_SIZE = 15;
  const OBSTACLE_SIZE = 50;

  // Initialize game and player IDs
  useEffect(() => {
    const gid = new URLSearchParams(window.location.search).get('game') || 
                Math.random().toString(36).substring(7);
    setGameId(gid);
    
    const pid = window.location.hash ? "2" : "1";
    setPlayerId(pid);
    
    if (pid === "1") {
      const shareUrl = `${window.location.origin}${window.location.pathname}?game=${gid}#2`;
      console.log('Share this URL with player 2:', shareUrl);
    }
  }, []);

  const connectWebSocket = () => {
    if (!gameId || !playerId || isConnecting) return;

    setIsConnecting(true);
    setError(null);

    const ws = new WebSocket(`ws://localhost:8000/ws/${gameId}/${playerId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('Connected to game server');
      setIsConnecting(false);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const newState = JSON.parse(event.data);
        setGameState(newState);
      } catch (e) {
        console.error('Error parsing game state:', e);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error. Please make sure the game server is running.');
      setIsConnecting(false);
    };

    ws.onclose = () => {
      setError('Connection lost. Click to reconnect.');
      setIsConnecting(false);
    };
  };

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [gameId, playerId]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !gameState) return;

    const ctx = canvas.getContext('2d');
    
    ctx.clearRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

    ctx.strokeStyle = '#333';
    ctx.setLineDash([10, 10]);
    ctx.beginPath();
    ctx.moveTo(GAME_WIDTH / 2, 0);
    ctx.lineTo(GAME_WIDTH / 2, GAME_HEIGHT);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = '#fff';
    ctx.fillRect(0, gameState.paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT);
    ctx.fillRect(GAME_WIDTH - PADDLE_WIDTH, gameState.paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT);

    ctx.shadowColor = '#fff';
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.arc(gameState.ball_x, gameState.ball_y, BALL_SIZE / 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    ctx.fillStyle = '#ff4444';
    ctx.fillRect(gameState.obstacle1_x, gameState.obstacle1_y, OBSTACLE_SIZE, OBSTACLE_SIZE);
    ctx.fillRect(gameState.obstacle2_x, gameState.obstacle2_y, OBSTACLE_SIZE, OBSTACLE_SIZE);

    ctx.fillStyle = '#fff';
    ctx.font = 'bold 48px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(gameState.score1, GAME_WIDTH / 4, 60);
    ctx.fillText(gameState.score2, 3 * GAME_WIDTH / 4, 60);
  }, [gameState]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN || !gameState) return;

      let newPaddleY;
      if (playerId === "1") {
        newPaddleY = gameState.paddle1_y;
      } else {
        newPaddleY = gameState.paddle2_y;
      }

      if (e.key === "ArrowUp") {
        newPaddleY = Math.max(0, newPaddleY - 20);
      } else if (e.key === "ArrowDown") {
        newPaddleY = Math.min(GAME_HEIGHT - PADDLE_HEIGHT, newPaddleY + 20);
      } else {
        return;
      }

      wsRef.current.send(JSON.stringify({ paddleY: newPaddleY }));
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [gameState, playerId]);

  return (
    <div className="flex flex-col items-center p-8 min-h-screen bg-gray-900">
      <h1 className="text-3xl font-bold mb-6 text-white">Multiplayer Ping Pong</h1>
      
      {error && (
        <div 
          className="bg-red-500 text-white px-4 py-2 rounded mb-4 cursor-pointer"
          onClick={() => !isConnecting && connectWebSocket()}
        >
          {error}
          {!isConnecting && " (Click to retry)"}
        </div>
      )}
      
      {isConnecting && (
        <div className="text-blue-400 mb-4">
          Connecting to game server...
        </div>
      )}
      
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
        <canvas
          ref={canvasRef}
          width={GAME_WIDTH}
          height={GAME_HEIGHT}
          className="border border-gray-700 rounded"
        />
      </div>
      
      <div className="text-center mt-6 text-white">
        <p className="text-xl">You are Player {playerId}</p>
        <p className="text-gray-400">Game ID: {gameId}</p>
        <p className="mt-4 text-sm">
          Use ↑ and ↓ arrow keys to move your paddle
        </p>
      </div>
    </div>
  );
};

export default PongGame;