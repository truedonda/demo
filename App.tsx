import { useState } from 'react';
import { Navbar } from './components/Navbar';
import { CartSidebar } from './components/CartSidebar';
import { Catalog } from './views/Catalog';
import { ProductDetail } from './views/ProductDetail';
import { Account } from './views/Account';
import { Product, CartItem } from './types';

export default function App() {
  const [currentView, setCurrentView] = useState<'catalog' | 'product' | 'account'>('catalog');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [cart, setCart] = useState<CartItem[]>([]);

  const handleNavigate = (view: 'catalog' | 'account') => {
    setCurrentView(view);
    if (view === 'catalog') setSelectedProduct(null);
  };

  const handleSelectProduct = (product: Product) => {
    setSelectedProduct(product);
    setCurrentView('product');
    window.scrollTo({ top: 0, behavior: 'auto' });
  };

  const handleAddToCart = (product: Product, size: string, color: string) => {
    const existingItemIndex = cart.findIndex(
      item => item.product.id === product.id && item.size === size && item.color === color
    );

    if (existingItemIndex >= 0) {
      const newCart = [...cart];
      newCart[existingItemIndex].quantity += 1;
      setCart(newCart);
    } else {
      setCart([...cart, {
        id: `${product.id}-${size}-${color}-${Date.now()}`,
        product,
        quantity: 1,
        size,
        color
      }]);
    }
    setIsCartOpen(true);
  };

  const updateCartQuantity = (id: string, delta: number) => {
    setCart(prev => prev.map(item => {
      if (item.id === id) {
        const newQ = item.quantity + delta;
        return { ...item, quantity: Math.max(1, newQ) }; // Prevent going below 1 via this function
      }
      return item;
    }));
  };

  const removeFromCart = (id: string) => {
    setCart(prev => prev.filter(item => item.id !== id));
  };

  const cartItemCount = cart.reduce((acc, item) => acc + item.quantity, 0);

  return (
    <div className="min-h-screen bg-[#111111] font-sans flex flex-col text-white">
      <Navbar 
        cartItemCount={cartItemCount} 
        onOpenCart={() => setIsCartOpen(true)} 
        onNavigate={handleNavigate}
        currentView={currentView}
      />
      
      <main className="flex-1 w-full mx-auto max-w-[1600px]">
        {currentView === 'catalog' && (
          <Catalog onSelectProduct={handleSelectProduct} />
        )}
        {currentView === 'product' && selectedProduct && (
          <ProductDetail 
            product={selectedProduct} 
            onBack={() => setCurrentView('catalog')}
            onAddToCart={handleAddToCart}
          />
        )}
        {currentView === 'account' && (
          <Account />
        )}
      </main>

      <CartSidebar 
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        cart={cart}
        onUpdateQuantity={updateCartQuantity}
        onRemove={removeFromCart}
      />

      {/* Simple Footer */}
      <footer className="border-t border-[#2a2a2a] px-6 py-12 text-center md:text-left text-xs uppercase tracking-widest text-[#666] flex flex-col md:flex-row justify-between items-center gap-4">
        <div>© 2026 COZYSHOP. ALL RIGHTS RESERVED.</div>
        <div className="flex space-x-6 text-[#888] font-semibold tracking-widest">
          <a href="#" className="hover:text-white transition-colors">Instagram</a>
          <a href="#" className="hover:text-white transition-colors">Twitter</a>
          <a href="#" className="hover:text-white transition-colors">Terms</a>
          <a href="#" className="hover:text-white transition-colors">Privacy</a>
        </div>
      </footer>
    </div>
  );
}
