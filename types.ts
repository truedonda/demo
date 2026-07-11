export interface Product {
  id: string;
  name: string;
  price: number;
  images: string[];
  category: string;
  description: string;
  isNew?: boolean;
  colors?: string[];
  sizes?: string[];
}

export interface CartItem {
  id: string; // unique ID for the cart entry
  product: Product;
  quantity: number;
  size: string;
  color: string;
}

export interface User {
  name: string;
  email: string;
  orders: any[];
}
