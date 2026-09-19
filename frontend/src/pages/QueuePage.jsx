import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Users, RefreshCw } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const QueuePage = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/crm/leads`);
      setLeads(response.data);
    } catch (err) {
      console.error("Failed to fetch leads", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <header className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#111827]">Sales Queue</h1>
          <p className="text-[#6B7280] text-sm mt-1">Active AI handoffs waiting for an agent</p>
        </div>
        <button 
          onClick={fetchLeads}
          className="flex items-center gap-2 bg-white border border-[#E5E7EB] px-4 py-2 rounded-md shadow-sm text-sm font-medium hover:bg-gray-50"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </header>

      <div className="crm-card overflow-hidden">
        <div className="p-4 border-b border-[#E5E7EB] bg-white flex items-center gap-2">
          <Users size={18} className="text-[#0A5BFF]" />
          <span className="font-semibold text-sm">{leads.length} Waiting</span>
        </div>
        
        {loading ? (
          <div className="p-8 text-center text-[#6B7280]">Loading queue...</div>
        ) : (
          <table className="w-full">
            <thead className="bg-[#F8FAFC]">
              <tr>
                <th className="w-24">ID</th>
                <th>Customer</th>
                <th>Journey</th>
                <th>Reason</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {leads.map(lead => (
                <tr 
                  key={lead.session_id}
                  onClick={() => navigate(`/workspace/${lead.session_id}`)}
                  className="cursor-pointer"
                >
                  <td className="font-medium">{lead.session_id}</td>
                  <td>{lead.customer}</td>
                  <td>{lead.journey}</td>
                  <td>{lead.reason}</td>
                  <td>
                    <span className={`badge ${lead.status === 'Waiting' ? 'badge-soft-danger' : 'badge-soft-warning'}`}>
                      {lead.status}
                    </span>
                  </td>
                </tr>
              ))}
              {leads.length === 0 && (
                <tr>
                  <td colSpan="5" className="text-center py-8 text-[#6B7280]">No active handoffs in the queue.</td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default QueuePage;
