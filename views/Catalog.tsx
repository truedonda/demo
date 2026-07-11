import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ProductCard } from '../components/ProductCard';
import { PRODUCTS, CATEGORIES } from '../data/mock';
import { Product } from '../types';

interface CatalogProps {
  onSelectProduct: (product: Product) => void;
}

export const Catalog: React.FC<CatalogProps> = ({ onSelectProduct }) => {
  const [activeCategory, setActiveCategory] = useState<string>('All');
  
  const filteredProducts = activeCategory === 'All' 
    ? PRODUCTS 
    : PRODUCTS.filter(p => p.category === activeCategory);

  return (
    <div className="flex flex-col min-h-screen">
      {/* Page Header */}
      <div className="px-6 py-6 border-b border-[#2a2a2a] bg-[#1a1a1a]">
        <h1 className="text-2xl font-semibold tracking-tight uppercase mb-4 text-[#eee]">All Clothing</h1>
        
        {/* Filters Bar */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-[10px] sm:text-xs uppercase tracking-widest text-[#888] font-semibold">
            {CATEGORIES.map((cat, idx) => (
              <React.Fragment key={cat}>
                <button 
                  onClick={() => setActiveCategory(cat)}
                  className={`hover:text-white transition-colors ${activeCategory === cat ? 'text-white border-b border-white' : ''}`}
                >
                  {cat}
                </button>
                {idx < CATEGORIES.length - 1 && <span className="text-[#333]">|</span>}
              </React.Fragment>
            ))}
          </div>
          
          <div className="flex gap-4 text-xs font-semibold uppercase text-white hover:text-[#ccc] cursor-pointer">
             <span>Filter & Sort +</span>
          </div>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 bg-[#2a2a2a] gap-[1px] border-b border-[#2a2a2a]">
        <AnimatePresence>
          {filteredProducts.map((product, idx) => (
            <div 
               key={product.id}
               className={idx === 5 ? 'sm:col-span-2 sm:row-span-2' : ''}
            >
              <ProductCard 
                product={product} 
                onClick={onSelectProduct} 
              />
            </div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};
