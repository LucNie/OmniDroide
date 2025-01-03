const WebSocket = require('ws');
const { exec } = require('child_process');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const PORT = 6666;

// Create a WebSocket server
const wss = new WebSocket.Server({ port: PORT }, () => {
  console.log(`WebSocket server started on ws://0.0.0.0:${PORT}`);
});

// Listen for client connections
wss.on('connection', (ws) => {
  console.log('Client connected');

  // Listen for incoming messages from the client
  ws.on('message', (message) => {
    console.log('Received:', message);

    // Handle commands (e.g., simulate key presses, retrieve video feed)
    if (message === 'get_video') {
      sendVideoFeed(ws);
    } else {
      // Simulate keypresses using `adb` or custom command
      exec(`input keyevent ${message}`, (error) => {
        if (error) {
          console.error('Error sending key event:', error);
        } else {
          console.log(`Key event ${message} sent successfully`);
        }
      });
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

// Function to send video feed to the client
function sendVideoFeed(ws) {
  const screenCaptureProcess = spawn('screenrecord', ['--output-format=h264', path.join(__dirname, 'screen.h264')]);

  screenCaptureProcess.stdout.on('data', (data) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(data);
    }
  });

  screenCaptureProcess.on('close', () => {
    console.log('Screen recording process ended');
  });
}
