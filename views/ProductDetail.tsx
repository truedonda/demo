import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Product } from '../types';

interface ProductDetailProps {
  product: Product;
  onBack: () => void;
  onAddToCart: (product: Product, size: string, color: string) => void;
}

export const ProductDetail: React.FC<ProductDetailProps> = ({ product, onBack, onAddToCart }) => {
  const [selectedSize, setSelectedSize] = useState<string>(product.sizes?.[0] || '');
  const [selectedColor, setSelectedColor] = useState<string>(product.colors?.[0] || '');

  // Reset selections when product changes
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setSelectedSize(product.sizes?.[0] || '');
    setSelectedColor(product.colors?.[0] || '');
  }, [product]);

  return (
    <motion.div 
      className="min-h-screen bg-[#111111] text-[#f4f4f4] pt-4 pb-20 px-6 xl:px-12"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <button 
        onClick={onBack}
        className="text-xs uppercase tracking-widest text-[#888] hover:text-white mb-8 transition-colors font-semibold"
      >
        ← Back to Shop
      </button>

      <div className="flex flex-col lg:flex-row gap-12 lg:gap-24">
        {/* Images */}
        <div className="w-full lg:w-[60%] space-y-4">
          <div className="aspect-[4/5] md:aspect-auto md:h-[80vh] bg-[#1a1a1a] flex items-center justify-center overflow-hidden">
            <img 
              src={product.images[0]} 
              alt={product.name} 
              className="w-full h-full object-cover"
            />
          </div>
          {product.images.slice(1).map((img, idx) => (
             <div key={idx} className="aspect-[4/5] md:aspect-auto md:h-[80vh] bg-[#1a1a1a] flex items-center justify-center overflow-hidden">
             <img 
               src={img} 
               alt={`${product.name} ${idx + 2}`} 
               className="w-full h-full object-cover"
             />
           </div>
          ))}
        </div>

        {/* Info */}
        <div className="w-full lg:w-[40%] sticky top-24 self-start flex flex-col text-sm">
          <div className="flex justify-between items-start mb-2">
            <h1 className="text-xl md:text-2xl font-semibold tracking-tight uppercase leading-snug">
              {product.name}
            </h1>
            {product.isNew && <span className="text-xs border border-[#333] px-2 py-1 tracking-wider uppercase ml-4 whitespace-nowrap bg-[#111]">New</span>}
          </div>
          
          <div className="text-lg font-semibold mb-10 text-[#aaa]">
            ${product.price.toFixed(2)}
          </div>

          {/* Color Selection */}
          {product.colors && product.colors.length > 0 && (
            <div className="mb-8">
              <div className="text-xs uppercase tracking-widest text-[#888] mb-4 font-semibold">Color: {selectedColor}</div>
              <div className="flex space-x-3">
                {product.colors.map(color => (
                  <button
                    key={color}
                    onClick={() => setSelectedColor(color)}
                    className={`w-8 h-8 rounded-full border-2 transition-all ${selectedColor === color ? 'border-white scale-110' : 'border-transparent'} flex items-center justify-center`}
                    aria-label={`Select color ${color}`}
                  >
                    <div 
                      className="w-6 h-6 rounded-full border border-[#333]" 
                      style={{ 
                        backgroundColor: color.toLowerCase() === 'charcoal' ? '#333' 
                        : color.toLowerCase() === 'tan' ? '#d2b48c'
                        : color.toLowerCase() === 'cream' ? '#f5f5f0'
                        : color.toLowerCase() === 'olive' ? '#556b2f'
                        : color.toLowerCase() === 'navy' ? '#000080'
                        : color.toLowerCase()
                      }} 
                    />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Size Selection */}
          {product.sizes && product.sizes.length > 0 && (
            <div className="mb-8">
              <div className="flex justify-between items-center mb-4">
                <div className="text-xs uppercase tracking-widest text-[#888] font-semibold">Size</div>
                <button className="text-xs border-b border-[#333] text-[#888] hover:text-white hover:border-white transition-all pb-0.5">Find my fit</button>
              </div>
              <div className="flex flex-wrap gap-3">
                {product.sizes.map(size => (
                  <button 
                    key={size}
                    onClick={() => setSelectedSize(size)}
                    className={`w-12 h-12 flex items-center justify-center text-xs tracking-wider border transition-colors font-semibold ${
                      selectedSize === size 
                      ? 'border-white bg-white text-black' 
                      : 'border-[#333] hover:border-[#888] text-white bg-[#111]'
                    }`}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Add to Cart */}
          <button 
            onClick={() => onAddToCart(product, selectedSize, selectedColor)}
            className="w-full bg-white text-black py-4 text-xs font-bold uppercase tracking-widest hover:bg-[#eee] transition-colors mb-12"
          >
            Add to Bag
          </button>

          {/* Description & Details Accordion (Simplified) */}
          <div className="border-t border-[#2a2a2a]">
             <div className="flex space-x-6 text-xs uppercase tracking-widest pt-4 mb-4 font-semibold">
                <button className="text-white border-b border-white pb-1">Description</button>
                <button className="text-[#666] hover:text-[#aaa] transition-colors">Size & Fit</button>
                <button className="text-[#666] hover:text-[#aaa] transition-colors">Material</button>
             </div>
             <p className="text-[#aaa] leading-relaxed mb-6 whitespace-pre-line text-sm pb-6 border-b border-[#2a2a2a]">
               {product.description}
             </p>
             <p className="text-[#777] text-xs">
               True to size. Recommended to take your normal size. Model is 178 / 5'10" and is wearing a size S.
             </p>
          </div>
          
          <div className="mt-8 pt-4 border-t border-[#2a2a2a] flex justify-between text-[10px] text-[#888] font-semibold uppercase tracking-widest">
            <button className="hover:text-white transition-colors">Need Help?</button>
            <span className="text-[#888]">Free Worldwide Shipping</span>
          </div>

        </div>
      </div>
    </motion.div>
  );
};
