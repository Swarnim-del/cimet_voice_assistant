import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, MicOff, Bot, User, PhoneCall, PhoneOff, Loader2, Database } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_URL = API_URL.replace(/^http/, 'ws');

const AICallsPage = () => {
  const [sessionId, setSessionId] = useState('');
  const [messages, setMessages] = useState([]);
  const [journeyData, setJourneyData] = useState({});
  const [isRecording, setIsRecording] = useState(false);
  const [isAiSpeaking, setIsAiSpeaking] = useState(false);
  const [callStatus, setCallStatus] = useState('idle'); // idle, connected, error
  
  const messagesEndRef = useRef(null);
  
  const voiceWsRef = useRef(null);
  const crmWsRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Clean up WebSockets on unmount
  useEffect(() => {
    return () => {
      closeConnections();
    };
  }, []);

  const closeConnections = useCallback(() => {
    if (voiceWsRef.current) {
      voiceWsRef.current.close();
      voiceWsRef.current = null;
    }
    if (crmWsRef.current) {
      crmWsRef.current.close();
      crmWsRef.current = null;
    }
    setCallStatus('idle');
  }, []);

  const startNewCall = async () => {
    closeConnections();
    setMessages([]);
    setJourneyData({});
    
    // We prefix with L_WS_ to match the mock CRM customer in orchestrator for testing
    const newSession = `TEST-CALL-${Math.floor(Math.random() * 10000)}`;
    setSessionId(newSession);
    setCallStatus('connecting');

    // 1. Connect to Voice WebSocket (for audio streaming)
    const voiceWs = new WebSocket(`${WS_URL}/ws/voice/${newSession}`);
    voiceWs.binaryType = "blob";
    
    voiceWs.onopen = () => {
      console.log("Voice WS Connected");
      setCallStatus('connected');
    };
    
    voiceWs.onmessage = async (event) => {
      // Incoming TTS Audio from the AI
      if (event.data instanceof Blob) {
        setIsAiSpeaking(true);
        const audioUrl = URL.createObjectURL(event.data);
        const audio = new Audio(audioUrl);
        
        audio.onended = () => {
          setIsAiSpeaking(false);
          URL.revokeObjectURL(audioUrl);
        };
        
        try {
          await audio.play();
        } catch (e) {
          console.error("Audio playback failed", e);
          setIsAiSpeaking(false);
        }
      }
    };
    
    voiceWs.onerror = (err) => {
      console.error("Voice WS Error", err);
      setCallStatus('error');
    };
    
    voiceWs.onclose = () => {
      console.log("Voice WS Closed");
    };
    
    voiceWsRef.current = voiceWs;

    // 2. Connect to CRM WebSocket (for live transcripts and journey data)
    const crmWs = new WebSocket(`${WS_URL}/api/crm/live/${newSession}`);
    
    crmWs.onopen = () => {
      console.log("CRM WS Connected");
    };
    
    crmWs.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'transcript') {
          setMessages(prev => [...prev, {
            role: data.speaker === 'customer' ? 'user' : 'ai',
            content: data.text
          }]);
        } else if (data.type === 'journey_update') {
          setJourneyData(prev => ({
            ...prev,
            ...data.fields
          }));
        }
      } catch (err) {
        console.error("Failed to parse CRM WS message", err);
      }
    };
    
    crmWsRef.current = crmWs;
    
    setMessages([
      { role: 'system', content: `Session started: ${newSession}. Hold the Microphone button to speak.` }
    ]);
  };

  const startRecording = async () => {
    if (!voiceWsRef.current || voiceWsRef.current.readyState !== WebSocket.OPEN) return;
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        // Send the complete audio blob to the backend over WebSocket
        if (voiceWsRef.current && voiceWsRef.current.readyState === WebSocket.OPEN) {
          voiceWsRef.current.send(audioBlob);
          setMessages(prev => [...prev, { role: 'system', content: `Processing audio...` }]);
        }
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone", err);
      alert("Could not access microphone. Please ensure you have granted permission.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-8">
      <header className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#111827]">Voice AI Simulator</h1>
          <p className="text-[#6B7280] text-sm mt-1">Talk to the AI natively and watch PULSE update</p>
        </div>
        <div className="flex gap-4">
          {sessionId && (
            <button 
              onClick={closeConnections}
              className="flex items-center gap-2 bg-[#EF4444] text-white px-4 py-2 rounded-md font-medium shadow-sm hover:bg-red-700 transition-colors"
            >
              <PhoneOff size={16} />
              End Call
            </button>
          )}
          <button 
            onClick={startNewCall}
            className="flex items-center gap-2 bg-[#0A5BFF] text-white px-4 py-2 rounded-md font-medium shadow-sm hover:bg-blue-700 transition-colors"
          >
            <PhoneCall size={16} />
            {sessionId ? 'Restart Call' : 'Start New Call'}
          </button>
        </div>
      </header>

      <div className="grid grid-cols-3 gap-6 h-[600px]">
        {/* Left Side: Chat & Voice Interface */}
        <div className="col-span-2 crm-card bg-white flex flex-col overflow-hidden">
          {/* Chat Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
            {!sessionId ? (
              <div className="h-full flex flex-col items-center justify-center text-[#6B7280]">
                <Mic size={48} className="mb-4 opacity-20" />
                <p>Click "Start New Call" to begin a voice session.</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'system' ? (
                    <div className="w-full text-center text-xs text-[#6B7280] my-2 p-2 bg-gray-100 rounded">
                      {msg.content}
                    </div>
                  ) : (
                    <div className={`flex gap-3 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-[#0A5BFF] text-white' : 'bg-gray-200 text-gray-700'}`}>
                        {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                      </div>
                      <div className={`p-3 rounded-lg shadow-sm ${msg.role === 'user' ? 'bg-[#0A5BFF] text-white rounded-tr-none' : 'bg-white border border-[#E5E7EB] rounded-tl-none'}`}>
                        {msg.content}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
            
            {isAiSpeaking && (
              <div className="flex justify-start">
                <div className="flex gap-3 max-w-[80%] flex-row">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gray-200 text-gray-700">
                    <Bot size={16} />
                  </div>
                  <div className="p-3 bg-white border border-[#E5E7EB] rounded-lg rounded-tl-none flex items-center gap-2 text-[#6B7280]">
                    <span className="flex gap-1 h-3 items-center">
                      <span className="w-1 h-full bg-[#0A5BFF] animate-pulse rounded"></span>
                      <span className="w-1 h-2/3 bg-[#0A5BFF] animate-pulse rounded delay-75"></span>
                      <span className="w-1 h-full bg-[#0A5BFF] animate-pulse rounded delay-150"></span>
                    </span>
                    AI is speaking...
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Voice Input Area */}
          <div className="p-6 border-t border-[#E5E7EB] bg-white flex flex-col items-center justify-center">
            {callStatus === 'error' && (
              <div className="text-red-500 text-sm mb-4">Connection error. Please try restarting the call.</div>
            )}
            
            <button
              onClick={toggleRecording}
              disabled={callStatus !== 'connected'}
              className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${
                isRecording 
                  ? 'bg-red-500 text-white shadow-lg scale-110 animate-pulse' 
                  : callStatus === 'connected' 
                    ? 'bg-[#0A5BFF] text-white shadow-md hover:bg-blue-700' 
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            >
              {isRecording ? <Mic size={32} /> : <MicOff size={32} />}
            </button>
            <p className="mt-4 text-sm text-[#6B7280] font-medium">
              {isRecording ? 'Recording... Click to send.' : 'Click to speak'}
            </p>
          </div>
        </div>

        {/* Right Side: CRM Journey Data */}
        <div className="crm-card bg-white flex flex-col overflow-hidden">
          <div className="p-4 border-b border-[#E5E7EB] bg-[#F8FAFC] flex items-center gap-2">
            <Database size={18} className="text-[#0A5BFF]" />
            <h2 className="font-semibold text-sm">Extracted Journey Data</h2>
          </div>
          <div className="p-6 flex-1 overflow-y-auto">
            {Object.keys(journeyData).length === 0 ? (
              <div className="text-sm text-[#6B7280] text-center mt-10">
                No data extracted yet.
                <br />As the AI asks questions, fields will appear here.
              </div>
            ) : (
              <div className="space-y-4">
                {Object.entries(journeyData).map(([key, value]) => (
                  <div key={key} className="border-b border-gray-100 pb-2">
                    <span className="block text-xs font-medium text-[#6B7280] uppercase tracking-wider mb-1">
                      {key.replace('_', ' ')}
                    </span>
                    <span className="block text-sm font-semibold text-[#111827]">
                      {value?.toString() || '—'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AICallsPage;
