import React from 'react';
import { motion } from 'framer-motion';

export const Account: React.FC = () => {
  return (
    <motion.div 
      className="min-h-screen bg-[#111111] text-[#f4f4f4] pt-8 lg:pt-16 px-6 lg:px-24 xl:px-48 grid grid-cols-1 md:grid-cols-12 gap-12"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
        <div className="md:col-span-3 lg:col-span-2">
            <h1 className="text-xl font-semibold tracking-tight uppercase mb-8">Account</h1>
            <nav className="flex flex-col space-y-4 text-xs font-semibold uppercase tracking-widest text-[#888]">
                <button className="text-left text-white">Dashboard</button>
                <button className="text-left hover:text-white transition-colors">Orders</button>
                <button className="text-left hover:text-white transition-colors">Addresses</button>
                <button className="text-left hover:text-white transition-colors">Preferences</button>
                <button className="text-left hover:text-white transition-colors pt-8">Log Out</button>
            </nav>
        </div>
        
        <div className="md:col-span-9 lg:col-span-10 border-l border-[#222] pl-0 md:pl-12 lg:pl-24">
           <h2 className="text-lg font-semibold tracking-tight uppercase mb-8">Welcome back.</h2>
           
           <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
              <div className="border border-[#2a2a2a] p-8 bg-[#1a1a1a]">
                  <h3 className="text-xs font-semibold uppercase tracking-widest text-[#888] mb-4">Default Address</h3>
                  <p className="text-sm font-semibold mb-2">Jane Doe</p>
                  <p className="text-sm text-[#888] leading-relaxed">
                     123 Fashion Ave<br/>
                     Apt 4B<br/>
                     New York, NY 10012<br/>
                     United States
                  </p>
                  <button className="mt-6 text-xs border-b border-[#555] text-white hover:border-white transition-all pb-0.5">Edit Address</button>
              </div>
              <div className="border border-[#2a2a2a] p-8 bg-[#1a1a1a]">
                  <h3 className="text-xs font-semibold uppercase tracking-widest text-[#888] mb-4">Account Details</h3>
                  <p className="text-sm font-semibold mb-2">Jane Doe</p>
                  <p className="text-sm text-[#888] mb-6">jane.doe@example.com</p>
                  <button className="text-xs border-b border-[#555] text-white hover:border-white transition-all pb-0.5">Change Password</button>
              </div>
           </div>
           
           <h2 className="text-lg font-semibold tracking-tight uppercase mb-6">Recent Orders</h2>
           <div className="border-t border-[#2a2a2a]">
              <div className="py-12 text-center text-[#888] text-sm italic">
                  You haven't placed any orders yet.
              </div>
           </div>
        </div>
    </motion.div>
  );
};
