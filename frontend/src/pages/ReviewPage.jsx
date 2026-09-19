import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';

const ReviewPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div className="p-8 max-w-4xl mx-auto flex flex-col gap-8 h-screen">
      <header className="flex flex-col mb-4">
        <h1 className="text-2xl font-bold text-[#111827]">Application Review</h1>
        <p className="text-[#6B7280] text-sm mt-1">Review the collected details before submitting to PULSE. Lead ID: {id}</p>
      </header>

      <div className="crm-card bg-white flex flex-col">
        <table className="w-full">
          <tbody>
            <tr><td className="font-medium text-[#6B7280] w-48 border-b-0">Customer Name</td><td className="border-b-0 font-medium">John Doe</td></tr>
            <tr><td className="font-medium text-[#6B7280] border-b-0">Address</td><td className="border-b-0 font-medium">12 King Street, Sydney NSW</td></tr>
            <tr><td className="font-medium text-[#6B7280] border-b-0">Fuel Preference</td><td className="border-b-0 font-medium">Electricity</td></tr>
            <tr><td className="font-medium text-[#6B7280] border-b-0">Solar Panel</td><td className="border-b-0 font-medium">No</td></tr>
            <tr><td className="font-medium text-[#6B7280] border-b-0">Life Support</td><td className="border-b-0 font-medium"><span className="badge badge-soft-danger">Yes</span></td></tr>
            <tr><td className="font-medium text-[#6B7280] border-b-0">Concession Card</td><td className="border-b-0 font-medium">Pending Verification</td></tr>
          </tbody>
        </table>
      </div>

      <div className="flex justify-end gap-4 mt-auto mb-16">
        <button 
          onClick={() => navigate('/')}
          className="bg-white border border-[#E5E7EB] text-[#374151] px-6 py-3 rounded-md text-sm font-medium hover:bg-gray-50 shadow-sm"
        >
          Save Draft
        </button>
        <button 
          onClick={() => {
            alert("Submitted to PULSE successfully!");
            navigate('/');
          }}
          className="flex items-center gap-2 bg-[#0A5BFF] text-white px-6 py-3 rounded-md text-sm font-medium hover:bg-blue-700 shadow-sm"
        >
          <CheckCircle size={18} />
          Submit to PULSE
        </button>
      </div>
    </div>
  );
};

export default ReviewPage;
