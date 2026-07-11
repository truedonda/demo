import React from 'react';
import { Search, User, ShoppingBag, Menu } from 'lucide-react';

interface NavbarProps {
  cartItemCount: number;
  onOpenCart: () => void;
  onNavigate: (view: 'catalog' | 'account') => void;
  currentView: 'catalog' | 'account' | 'product';
}

export const Navbar: React.FC<NavbarProps> = ({ cartItemCount, onOpenCart, onNavigate, currentView }) => {
  return (
    <nav className="sticky top-0 z-50 w-full bg-[#111111]/90 backdrop-blur-md border-b border-[#2a2a2a] px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-12">
        {/* Brand */}
        <div 
          className="text-2xl font-semibold tracking-tighter uppercase cursor-pointer select-none no-underline text-white hover:text-[#ccc] transition-colors"
          onClick={() => onNavigate('catalog')}
        >
          COZYSHOP
        </div>

        {/* Main Links (Desktop) */}
        <div className="hidden md:flex items-center space-x-8 text-xs font-semibold uppercase tracking-widest text-[#a0a0a0]">
          <button 
            onClick={() => onNavigate('catalog')}
            className={`hover:text-white transition-colors ${currentView === 'catalog' ? 'text-white' : ''}`}
          >
            Shop
          </button>
          <button className="hover:text-white transition-colors">Collections</button>
          <button className="hover:text-white transition-colors">About</button>
        </div>
      </div>

      {/* Secondary Links & Actions */}
      <div className="flex items-center space-x-6 text-xs font-semibold tracking-widest text-[#a0a0a0] uppercase">
        <button className="hidden sm:flex items-center hover:text-white transition-colors">
          <span>Search</span>
        </button>
        
        <button 
          onClick={() => onNavigate('account')}
          className={`hidden sm:flex items-center hover:text-white transition-colors ${currentView === 'account' ? 'text-white' : ''}`}
        >
          <span>Account</span>
        </button>
        
        <button 
          onClick={onOpenCart}
          className="flex items-center hover:text-white transition-colors relative"
        >
          <span>Bag</span>
          {cartItemCount > 0 && (
            <span className="ml-1 text-white tabular-nums">
              [{cartItemCount}]
            </span>
          )}
        </button>
        
        {/* Mobile menu toggle */}
        <button className="md:hidden text-[#a0a0a0] hover:text-white transition-colors">
          <Menu className="w-5 h-5 stroke-[1.5]" />
        </button>
      </div>
    </nav>
  );
};
