import React from 'react';
import { motion } from 'framer-motion';
import { Product } from '../types';

interface ProductCardProps {
  product: Product;
  onClick: (product: Product) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product, onClick }) => {
  return (
    <motion.div 
      className="group cursor-pointer flex flex-col h-full bg-[#111111] hover:bg-[#1a1a1a] transition-colors"
      onClick={() => onClick(product)}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="relative flex-1 overflow-hidden bg-[#222] aspect-[3/4]">
        {product.isNew && (
          <div className="absolute top-3 right-3 z-10 bg-[#e5e5e5] text-black text-[10px] px-2 py-0.5 tracking-widest font-bold uppercase border border-[#fff]">
            New in
          </div>
        )}
        <img 
          src={product.images[0]} 
          alt={product.name}
          className="absolute inset-0 object-cover w-full h-full transition-transform duration-700 group-hover:scale-105"
        />
        {product.images[1] && (
          <img 
            src={product.images[1]} 
            alt={product.name + ' alternate'}
            className="absolute inset-0 object-cover w-full h-full opacity-0 transition-opacity duration-500 group-hover:opacity-100"
          />
        )}
      </div>
      <div className="px-4 py-3 flex justify-between items-center sm:items-start flex-row border-t border-[#2a2a2a] shrink-0">
        <h3 className="text-[10px] sm:text-[11px] font-bold tracking-widest uppercase text-[#eee] max-w-[75%] leading-snug">
          {product.name}
        </h3>
        <span className="text-[10px] sm:text-[11px] font-bold text-[#eee]">
          ${product.price.toFixed(2)}
        </span>
      </div>
    </motion.div>
  );
};
