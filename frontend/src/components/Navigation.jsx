import React from 'react';
import { NavLink } from 'react-router-dom';

const Navigation = () => {
  return (
    <nav className="bg-white border-b border-[#E5E7EB] px-8 py-4 mb-8">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-8">
          <div className="text-xl font-bold text-[#0A5BFF]">CIMET CRM</div>
          <div className="flex gap-4">
            <NavLink 
              to="/" 
              className={({ isActive }) => 
                `text-sm font-medium px-3 py-2 rounded-md transition-colors ${isActive ? 'bg-[#0A5BFF] text-white' : 'text-[#6B7280] hover:bg-gray-100 hover:text-[#111827]'}`
              }
            >
              Sales Queue
            </NavLink>
            <NavLink 
              to="/ai-calls" 
              className={({ isActive }) => 
                `text-sm font-medium px-3 py-2 rounded-md transition-colors ${isActive ? 'bg-[#0A5BFF] text-white' : 'text-[#6B7280] hover:bg-gray-100 hover:text-[#111827]'}`
              }
            >
              AI Calls
            </NavLink>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
