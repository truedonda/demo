import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, X, Plus, Minus } from 'lucide-react';
import { CartItem } from '../types';

interface CartSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  cart: CartItem[];
  onRemove: (id: string) => void;
  onUpdateQuantity: (id: string, delta: number) => void;
}

export const CartSidebar: React.FC<CartSidebarProps> = ({ 
  isOpen, 
  onClose, 
  cart,
  onRemove,
  onUpdateQuantity
}) => {
  const subtotal = cart.reduce((acc, item) => acc + (item.product.price * item.quantity), 0);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            onClick={onClose}
          />
          
          {/* Sidebar */}
          <motion.div 
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed top-0 right-0 h-full w-full max-w-[320px] bg-[#1a1a1a] z-50 flex flex-col border-l border-[#2a2a2a] text-[#eee] shadow-2xl"
          >
            {/* Header */}
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xs font-semibold uppercase tracking-widest flex items-center">
                  Your Bag <span className="text-[#888] ml-2">[{cart.length}]</span>
                </h2>
                <button 
                  onClick={onClose}
                  className="text-xs uppercase tracking-widest text-[#888] hover:text-white transition-colors"
                >
                  <X className="w-4 h-4 ml-1 inline" />
                </button>
              </div>
            </div>

            {/* Cart Items */}
            <div className="flex-1 overflow-y-auto px-6 space-y-6">
              {cart.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-[#666] tracking-widest uppercase text-xs font-semibold">
                  Your bag is empty.
                </div>
              ) : (
                cart.map(item => (
                  <div key={item.id} className="flex gap-4">
                    <img 
                      src={item.product.images[0]} 
                      alt={item.product.name}
                      className="w-16 h-24 object-cover bg-[#222]"
                    />
                    <div className="flex-1 flex flex-col justify-center">
                      <p className="text-[10px] font-semibold uppercase pr-4 truncate leading-snug">
                        {item.product.name}
                      </p>
                      <p className="text-[10px] text-[#888] mt-1 space-y-0.5">
                        <span className="block">Size: {item.size} •</span>
                        <span className="block">Colour: {item.color} •</span>
                      </p>
                      
                      <div className="flex justify-between items-center mt-3 pt-2">
                        <div className="flex items-center border border-[#333]">
                          <button 
                            onClick={() => onUpdateQuantity(item.id, -1)}
                            className="p-1 px-1.5 text-[#888] hover:text-white"
                          >
                            <Minus className="w-3 h-3 stroke-[2]" />
                          </button>
                          <span className="w-6 text-center text-[10px] font-semibold">{item.quantity}</span>
                          <button 
                            onClick={() => onUpdateQuantity(item.id, 1)}
                            className="p-1 px-1.5 text-[#888] hover:text-white"
                          >
                            <Plus className="w-3 h-3 stroke-[2]" />
                          </button>
                        </div>
                        
                        <button 
                          onClick={() => onRemove(item.id)}
                          className="text-[#888] hover:text-white text-[9px] uppercase tracking-widest transition-colors font-semibold border-b border-transparent hover:border-[#888] pb-0.5"
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                    <p className="text-[10px] font-semibold">${item.product.price.toFixed(2)}</p>
                  </div>
                ))
              )}
            </div>

            {/* Footer */}
            {cart.length > 0 && (
              <div className="p-6 mt-auto bg-[#111] border-t border-[#2a2a2a]">
                  <div className="flex justify-between text-xs font-semibold uppercase tracking-widest mb-2 text-[#eee]">
                    <span>Subtotal:</span>
                    <span>${subtotal.toFixed(2)}</span>
                  </div>
                  <p className="text-[#666] text-[10px] mb-6">Taxes and shipping calculated at checkout</p>
                  <button className="w-full bg-white text-black py-4 text-[11px] font-bold uppercase tracking-widest hover:bg-[#eee] transition-colors">
                    Checkout
                  </button>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
