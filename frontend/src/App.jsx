import React, { useState, useEffect, useRef } from 'react';
import { Mic, Square, Activity, StopCircle, RefreshCw } from 'lucide-react';
import './index.css';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [logs, setLogs] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isStopped, setIsStopped] = useState(false);
  
  const wsRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const pollIntervalRef = useRef(null);

  const initSession = () => {
    // Generate a new session ID when the app loads or restarts
    const newSessionId = "cimet_live_" + Math.floor(Math.random() * 10000);
    setSessionId(newSessionId);
    setLogs([]);
    setIsStopped(false);
    
    // Connect WebSocket
    const ws = new WebSocket(`ws://localhost:8000/ws/voice/${newSessionId}`);
    
    ws.onopen = () => setIsConnected(true);
    
    ws.onmessage = async (event) => {
      // We receive binary audio data from the AI
      const audioBlob = new Blob([event.data], { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
      fetchLogs(newSessionId);
    };
    
    ws.onclose = () => setIsConnected(false);
    wsRef.current = ws;

    // Start polling logs
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    pollIntervalRef.current = setInterval(() => fetchLogs(newSessionId), 2000);
  };

  useEffect(() => {
    initSession();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);

  const fetchLogs = async (sid) => {
    try {
      const response = await fetch(`http://localhost:8000/api/logs/sessions/${sid}/messages`);
      if (response.ok) {
        const data = await response.json();
        setLogs(data);
      }
    } catch (e) {
      console.error("Failed to fetch logs", e);
    }
  };

  const startRecording = async () => {
    if (isStopped) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(audioBlob);
          setTimeout(() => fetchLogs(sessionId), 1000); // Fetch after short delay to let Whisper transcribe
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Mic access denied", err);
      alert("Please allow microphone access.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Completely halts the session
  const handleStopConversation = () => {
    stopRecording();
    setIsStopped(true);
    if (wsRef.current) {
      wsRef.current.close();
    }
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    setIsConnected(false);
  };

  // Restarts the entire session
  const handleRestart = () => {
    handleStopConversation();
    setTimeout(() => {
      initSession();
    }, 500);
  };

  return (
    <div className="dashboard-container">
      {/* Left Panel: Customer Interface */}
      <div className="customer-panel">
        <div className="title-group">
          <h1><span>CIMET</span> Voice</h1>
          <p style={{ color: 'var(--text-muted)' }}>Real-time Energy Assistant</p>
        </div>

        <div className="mic-container">
          <button 
            className={`mic-btn ${isRecording ? 'recording' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            disabled={!isConnected || isStopped}
          >
            {isRecording ? <Square size={40} fill="currentColor" /> : <Mic size={48} />}
          </button>
          
          <div className="status-text">
            {isStopped ? "Conversation Stopped" :
             !isConnected ? "Connecting..." : 
              isRecording ? "Listening... (Click to stop)" : 
              "Tap microphone to speak"}
          </div>

          <div className="controls-group">
            <button 
              className="control-btn btn-stop" 
              onClick={handleStopConversation}
              disabled={isStopped}
            >
              <StopCircle size={20} /> Stop
            </button>
            <button 
              className="control-btn btn-restart" 
              onClick={handleRestart}
            >
              <RefreshCw size={20} /> Restart
            </button>
          </div>
        </div>
      </div>

      {/* Right Panel: Team Observability */}
      <div className="team-panel">
        <div className="panel-header">
          <h2><Activity size={24} /> Live Observability</h2>
          <div className={`live-badge ${!isConnected || isStopped ? 'offline' : ''}`}>
            {isConnected && !isStopped ? "● LIVE" : "OFFLINE"}
          </div>
        </div>
        
        <div className="logs-container">
          {logs.length === 0 ? (
            <div style={{color: 'var(--text-muted)', textAlign: 'center', marginTop: '2rem'}}>
              {isStopped ? "Session Ended" : "Awaiting transcription..."}
            </div>
          ) : (
            logs.map((log, idx) => (
              <div key={idx} className={`log-entry ${log.speaker}`}>
                <div className="log-meta">
                  <span className="log-speaker">{log.speaker}</span>
                  <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="log-content">{log.transcript}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
