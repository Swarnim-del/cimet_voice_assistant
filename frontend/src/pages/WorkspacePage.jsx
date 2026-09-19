import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const WorkspacePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/crm/session/${id}`);
        setData(response.data);
      } catch (err) {
        console.error("Failed to load session", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();

    // Setup WebSocket
    const wsUrl = API_URL.replace('http', 'ws') + `/crm/live/${id}`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'transcript') {
          setData(prev => {
            if (!prev) return prev;
            return {
              ...prev,
              transcript: [...prev.transcript, { speaker: payload.speaker, text: payload.text }]
            };
          });
        }
      } catch (e) {
        console.error("WS Parse Error", e);
      }
    };

    return () => {
      ws.close();
    };
  }, [id]);

  if (loading) {
    return <div className="p-8 text-center">Loading workspace...</div>;
  }

  if (!data) {
    return <div className="p-8 text-center text-red-500">Failed to load data.</div>;
  }

  return (
    <div className="p-8 max-w-7xl mx-auto h-screen flex flex-col">
      <header className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-xl font-bold text-[#111827]">Customer Workspace</h1>
          <p className="text-[#6B7280] text-sm mt-1">Lead ID: {id}</p>
        </div>
        <button 
          onClick={() => navigate(`/review/${id}`)}
          className="bg-[#0A5BFF] text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
        >
          Review & Complete
        </button>
      </header>

      <div className="grid grid-cols-12 gap-6 flex-1 min-h-0">
        {/* Left Panel - Customer Info */}
        <div className="col-span-3 flex flex-col gap-6">
          <div className="crm-card bg-white p-0">
            <div className="p-4 border-b border-[#E5E7EB] font-semibold text-[#0A5BFF]">
              Customer Information
            </div>
            <table className="w-full">
              <tbody>
                <tr><td className="font-medium text-[#6B7280] w-24 border-b-0">Name</td><td className="border-b-0">{data.customer.name}</td></tr>
                <tr><td className="font-medium text-[#6B7280] border-b-0">Phone</td><td className="border-b-0">{data.customer.phone}</td></tr>
                <tr><td className="font-medium text-[#6B7280] border-b-0">Journey</td><td className="border-b-0">{data.customer.journey}</td></tr>
                <tr><td className="font-medium text-[#6B7280] border-b-0">Status</td><td className="border-b-0"><span className="badge badge-soft-success">{data.customer.status}</span></td></tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Middle Panel - Journey Data */}
        <div className="col-span-5 crm-card bg-white flex flex-col">
          <div className="p-4 border-b border-[#E5E7EB] font-semibold text-[#0A5BFF]">
            Collected Journey Data
          </div>
          <table className="w-full">
            <tbody>
              <tr><td className="font-medium text-[#6B7280] w-32 border-b-0">Moving</td><td className="border-b-0">{data.journey_data.moving}</td></tr>
              <tr><td className="font-medium text-[#6B7280] border-b-0">Address</td><td className="border-b-0">{data.journey_data.address}</td></tr>
              <tr><td className="font-medium text-[#6B7280] border-b-0">Fuel Type</td><td className="border-b-0">{data.journey_data.fuel_type}</td></tr>
              <tr><td className="font-medium text-[#6B7280] border-b-0">Solar</td><td className="border-b-0">{data.journey_data.solar}</td></tr>
              <tr><td className="font-medium text-[#6B7280] border-b-0">Life Support</td><td className="border-b-0"><span className={`badge ${data.journey_data.life_support === 'Yes' ? 'badge-soft-danger' : 'badge-soft-success'}`}>{data.journey_data.life_support}</span></td></tr>
              <tr><td className="font-medium text-[#6B7280] border-b-0">Concession</td><td className="border-b-0">{data.journey_data.concession}</td></tr>
            </tbody>
          </table>
        </div>

        {/* Right Panel - AI Summary & Transcript */}
        <div className="col-span-4 flex flex-col gap-6 h-full">
          {/* AI Summary */}
          <div className="crm-card bg-white p-4">
            <div className="font-semibold text-[#0A5BFF] mb-2">AI Handoff Summary</div>
            <p className="text-sm text-[#374151] leading-relaxed">
              {data.summary}
            </p>
          </div>

          {/* Live Transcript */}
          <div className="crm-card bg-white flex-1 flex flex-col overflow-hidden">
            <div className="p-4 border-b border-[#E5E7EB] font-semibold text-[#0A5BFF]">
              Live Transcript
            </div>
            <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-4 text-sm bg-[#F9FAFB]">
              {data.transcript.map((msg, idx) => (
                <div key={idx} className="flex flex-col gap-1">
                  <span className={`font-semibold ${msg.speaker === 'ai' ? 'text-[#0A5BFF]' : 'text-[#374151]'}`}>
                    {msg.speaker === 'ai' ? 'AI Assistant' : 'Customer'}
                  </span>
                  <div className={`p-3 rounded-lg border shadow-sm ${msg.speaker === 'ai' ? 'bg-white border-[#E5E7EB]' : 'bg-[#DBEAFE] border-[#BFDBFE]'}`}>
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkspacePage;
