import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, PhoneCall, Loader2 } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const AICallsPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startNewCall = () => {
    const newSession = `TEST-CALL-${Math.floor(Math.random() * 10000)}`;
    setSessionId(newSession);
    setMessages([
      { role: 'system', content: `Session started: ${newSession}. Say hello to begin.` }
    ]);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || !sessionId) return;

    const userMessage = inputValue;
    setInputValue('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        session_id: sessionId,
        message: userMessage
      });
      
      setMessages(prev => [...prev, { role: 'ai', content: response.data.response }]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [...prev, { role: 'system', content: `Error: Could not connect to AI. Is the backend running?` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-8">
      <header className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#111827]">AI Conversation Simulator</h1>
          <p className="text-[#6B7280] text-sm mt-1">Test the AI qualifier flow before handoff</p>
        </div>
        <button 
          onClick={startNewCall}
          className="flex items-center gap-2 bg-[#0A5BFF] text-white px-4 py-2 rounded-md font-medium shadow-sm hover:bg-blue-700 transition-colors"
        >
          <PhoneCall size={16} />
          {sessionId ? 'Restart Call' : 'Start New Call'}
        </button>
      </header>

      <div className="crm-card bg-white h-[600px] flex flex-col overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
          {!sessionId ? (
            <div className="h-full flex flex-col items-center justify-center text-[#6B7280]">
              <Bot size={48} className="mb-4 opacity-20" />
              <p>Click "Start New Call" to begin a simulated conversation.</p>
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
          {loading && (
            <div className="flex justify-start">
              <div className="flex gap-3 max-w-[80%] flex-row">
                <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gray-200 text-gray-700">
                  <Bot size={16} />
                </div>
                <div className="p-3 bg-white border border-[#E5E7EB] rounded-lg rounded-tl-none flex items-center gap-2 text-[#6B7280]">
                  <Loader2 size={16} className="animate-spin" />
                  AI is typing...
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <form onSubmit={handleSendMessage} className="p-4 border-t border-[#E5E7EB] bg-white flex gap-2">
          <input 
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={!sessionId || loading}
            placeholder={sessionId ? "Type your message..." : "Start a call first..."}
            className="flex-1 border border-[#E5E7EB] rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#0A5BFF] focus:border-transparent disabled:bg-gray-100"
          />
          <button 
            type="submit"
            disabled={!sessionId || !inputValue.trim() || loading}
            className="bg-[#0A5BFF] text-white px-4 py-2 rounded-md font-medium shadow-sm hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send size={16} />
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default AICallsPage;
