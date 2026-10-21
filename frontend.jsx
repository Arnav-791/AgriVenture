import React, { useState } from 'react';
import { BarChart3, Users, TrendingUp, Package, ShoppingCart, MapPin, Award, Leaf, Building2, Menu, X } from 'lucide-react';

const AgriVenturePlatform = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Sample data
  const [products, setProducts] = useState([
    { id: 1, name: 'Organic Tomatoes', farmer: 'Green Valley Farm', quantity: 500, unit: 'kg', price: 45, location: 'Karnataka', category: 'Vegetables' },
    { id: 2, name: 'Basmati Rice', farmer: 'Sunrise Fields', quantity: 1000, unit: 'kg', price: 80, location: 'Punjab', category: 'Grains' },
    { id: 3, name: 'Fresh Mangoes', farmer: 'Tropical Orchards', quantity: 300, unit: 'kg', price: 120, location: 'Maharashtra', category: 'Fruits' },
    { id: 4, name: 'Organic Wheat', farmer: 'Golden Harvest', quantity: 2000, unit: 'kg', price: 35, location: 'Uttar Pradesh', category: 'Grains' },
  ]);

  const [cart, setCart] = useState([]);
  const [orders, setOrders] = useState([]);
  const [newProduct, setNewProduct] = useState({
    name: '', quantity: '', unit: 'kg', price: '', location: '', category: 'Vegetables'
  });

  const algorithms = [
    { name: 'Greedy', efficiency: 85, fairness: 70, speed: 95 },
    { name: 'Max-Flow', efficiency: 92, fairness: 75, speed: 80 },
    { name: 'Min-Cost Max-Flow', efficiency: 88, fairness: 85, speed: 70 },
    { name: 'Fair Min-Cost Max-Flow', efficiency: 90, fairness: 95, speed: 65 },
    { name: 'Hungarian', efficiency: 87, fairness: 80, speed: 75 },
    { name: 'Fair Hungarian', efficiency: 89, fairness: 92, speed: 68 },
  ];

  const addToCart = (product) => {
    setCart([...cart, { ...product, orderedQty: 50 }]);
  };

  const placeOrder = () => {
    if (cart.length > 0) {
      setOrders([...orders, { id: orders.length + 1, items: cart, date: new Date().toLocaleDateString(), status: 'Pending' }]);
      setCart([]);
      alert('Order placed successfully!');
    }
  };

  const addProduct = () => {
    if (newProduct.name && newProduct.quantity && newProduct.price) {
      setProducts([...products, { 
        id: products.length + 1, 
        ...newProduct, 
        farmer: 'Your Farm',
        quantity: parseInt(newProduct.quantity, 10),
        price: parseFloat(newProduct.price)
      }]);
      setNewProduct({ name: '', quantity: '', unit: 'kg', price: '', location: '', category: 'Vegetables' });
      alert('Product listed successfully!');
    }
  };

  const Navigation = () => (
    <nav className="bg-gradient-to-r from-green-600 to-green-700 text-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-2">
            <Leaf className="w-8 h-8" />
            <h1 className="text-2xl font-bold">AgriVenture</h1>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex space-x-1">
            {[
              { id: 'home', label: 'Home', icon: Leaf },
              { id: 'farmer', label: 'Farmer Portal', icon: Users },
              { id: 'company', label: 'Company Portal', icon: Building2 },
              { id: 'admin', label: 'Admin Dashboard', icon: BarChart3 }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-all ${
                  activeTab === tab.id 
                    ? 'bg-white text-green-700 shadow-md' 
                    : 'hover:bg-green-500'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <button 
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden pb-4 space-y-2">
            {[
              { id: 'home', label: 'Home', icon: Leaf },
              { id: 'farmer', label: 'Farmer Portal', icon: Users },
              { id: 'company', label: 'Company Portal', icon: Building2 },
              { id: 'admin', label: 'Admin Dashboard', icon: BarChart3 }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  setMobileMenuOpen(false);
                }}
                className={`w-full px-4 py-2 rounded-lg flex items-center space-x-2 transition-all ${
                  activeTab === tab.id 
                    ? 'bg-white text-green-700' 
                    : 'hover:bg-green-500'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </nav>
  );

  const HomePage = () => (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 text-white py-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-6">Welcome to AgriVenture</h1>
          <p className="text-xl mb-8 opacity-90">Connecting Farmers with Companies through Intelligent Allocation</p>
          <div className="flex flex-wrap justify-center gap-4">
            <button 
              onClick={() => setActiveTab('farmer')}
              className="bg-white text-green-700 px-8 py-3 rounded-lg font-semibold hover:bg-green-50 transition shadow-lg"
            >
              I'm a Farmer
            </button>
            <button 
              onClick={() => setActiveTab('company')}
              className="bg-green-800 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-900 transition shadow-lg"
            >
              I'm a Company
            </button>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="max-w-6xl mx-auto py-16 px-4">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">Why Choose AgriVenture?</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition">
            <TrendingUp className="w-12 h-12 text-green-600 mb-4" />
            <h3 className="text-xl font-bold mb-3">Smart Allocation</h3>
            <p className="text-gray-600">Advanced algorithms ensure fair and efficient product distribution</p>
          </div>
          <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition">
            <Award className="w-12 h-12 text-green-600 mb-4" />
            <h3 className="text-xl font-bold mb-3">Fair Trading</h3>
            <p className="text-gray-600">Prioritizes small farmers and ensures equitable opportunities</p>
          </div>
          <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition">
            <MapPin className="w-12 h-12 text-green-600 mb-4" />
            <h3 className="text-xl font-bold mb-3">Optimized Logistics</h3>
            <p className="text-gray-600">Minimizes transport distance and costs for better margins</p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="bg-green-700 text-white py-12">
        <div className="max-w-6xl mx-auto grid md:grid-cols-4 gap-8 px-4 text-center">
          <div>
            <div className="text-4xl font-bold mb-2">500+</div>
            <div className="opacity-90">Active Farmers</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">150+</div>
            <div className="opacity-90">Partner Companies</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">10K+</div>
            <div className="opacity-90">Tons Traded</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">95%</div>
            <div className="opacity-90">Satisfaction Rate</div>
          </div>
        </div>
      </div>
    </div>
  );

  const FarmerPortal = () => (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Farmer Portal</h2>
        <p className="text-gray-600">List your products and manage your inventory</p>
      </div>

      {/* Add Product Form */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <h3 className="text-xl font-bold mb-4 text-gray-800">List New Product</h3>
        <div className="grid md:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Product Name"
            value={newProduct.name}
            onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
          <input
            type="number"
            placeholder="Quantity"
            value={newProduct.quantity}
            onChange={(e) => setNewProduct({...newProduct, quantity: e.target.value})}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
          <select
            value={newProduct.unit}
            onChange={(e) => setNewProduct({...newProduct, unit: e.target.value})}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            <option value="kg">kg</option>
            <option value="ton">ton</option>
            <option value="quintal">quintal</option>
          </select>
          <input
            type="number"
            placeholder="Price per unit (₹)"
            value={newProduct.price}
            onChange={(e) => setNewProduct({...newProduct, price: e.target.value})}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
          <input
            type="text"
            placeholder="Location"
            value={newProduct.location}
            onChange={(e) => setNewProduct({...newProduct, location: e.target.value})}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
          <select
            value={newProduct.category}
            onChange={(e) => setNewProduct({...newProduct, category: e.target.value})}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
          >
            <option value="Vegetables">Vegetables</option>
            <option value="Fruits">Fruits</option>
            <option value="Grains">Grains</option>
            <option value="Pulses">Pulses</option>
          </select>
        </div>
        <button
          onClick={addProduct}
          className="mt-4 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition font-semibold"
        >
          Add Product
        </button>
      </div>

      {/* My Products */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4 text-gray-800">My Listed Products</h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {products.filter(p => p.farmer === 'Your Farm').map(product => (
            <div key={product.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-bold text-lg text-gray-800">{product.name}</h4>
                <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm">{product.category}</span>
              </div>
              <p className="text-gray-600 text-sm mb-2">
                <MapPin className="w-4 h-4 inline mr-1" />
                {product.location}
              </p>
              <div className="flex justify-between items-center">
                <span className="text-2xl font-bold text-green-600">₹{product.price}</span>
                <span className="text-gray-600">{product.quantity} {product.unit}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const CompanyPortal = () => (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Company Portal</h2>
        <p className="text-gray-600">Browse and purchase products from farmers</p>
      </div>

      {/* Shopping Cart */}
      {cart.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <ShoppingCart className="w-5 h-5 text-green-700" />
              <span className="font-semibold text-green-700">{cart.length} items in cart</span>
            </div>
            <button
              onClick={placeOrder}
              className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition font-semibold"
            >
              Place Order
            </button>
          </div>
        </div>
      )}

      {/* Products Grid */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <h3 className="text-xl font-bold mb-4 text-gray-800">Available Products</h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map(product => (
            <div key={product.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h4 className="font-bold text-lg text-gray-800">{product.name}</h4>
                  <p className="text-sm text-gray-500">{product.farmer}</p>
                </div>
                <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">{product.category}</span>
              </div>
              <p className="text-gray-600 text-sm mb-3">
                <MapPin className="w-4 h-4 inline mr-1" />
                {product.location}
              </p>
              <div className="flex justify-between items-center mb-3">
                <span className="text-2xl font-bold text-green-600">₹{product.price}</span>
                <span className="text-gray-600">{product.quantity} {product.unit} available</span>
              </div>
              <button
                onClick={() => addToCart(product)}
                className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition font-semibold"
              >
                Add to Cart
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Orders */}
      {orders.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4 text-gray-800">My Orders</h3>
          <div className="space-y-4">
            {orders.map(order => (
              <div key={order.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold">Order #{order.id}</span>
                  <span className="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full text-sm">{order.status}</span>
                </div>
                <p className="text-sm text-gray-600">{order.date} • {order.items.length} items</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const AdminDashboard = () => (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Admin Dashboard</h2>
        <p className="text-gray-600">Monitor platform performance and algorithm efficiency</p>
      </div>

      {/* Stats Overview */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl p-6 shadow-lg">
          <Package className="w-8 h-8 mb-2 opacity-90" />
          <div className="text-3xl font-bold mb-1">{products.length}</div>
          <div className="text-sm opacity-90">Total Products</div>
        </div>
        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl p-6 shadow-lg">
          <ShoppingCart className="w-8 h-8 mb-2 opacity-90" />
          <div className="text-3xl font-bold mb-1">{orders.length}</div>
          <div className="text-sm opacity-90">Active Orders</div>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl p-6 shadow-lg">
          <Users className="w-8 h-8 mb-2 opacity-90" />
          <div className="text-3xl font-bold mb-1">247</div>
          <div className="text-sm opacity-90">Active Farmers</div>
        </div>
        <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-xl p-6 shadow-lg">
          <Building2 className="w-8 h-8 mb-2 opacity-90" />
          <div className="text-3xl font-bold mb-1">89</div>
          <div className="text-sm opacity-90">Companies</div>
        </div>
      </div>

      {/* Algorithm Comparison */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <h3 className="text-xl font-bold mb-6 text-gray-800">Allocation Algorithms Performance</h3>
        <div className="space-y-6">
          {algorithms.map((algo, idx) => (
            <div key={idx} className="border-b border-gray-100 pb-4 last:border-0">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-semibold text-gray-800">{algo.name}</h4>
                <span className="text-sm text-gray-500">Overall Score: {Math.round((algo.efficiency + algo.fairness + algo.speed) / 3)}%</span>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Efficiency</span>
                    <span className="font-semibold">{algo.efficiency}%</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-500 rounded-full h-2" style={{width: `${algo.efficiency}%`}}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Fairness</span>
                    <span className="font-semibold">{algo.fairness}%</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 rounded-full h-2" style={{width: `${algo.fairness}%`}}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Speed</span>
                    <span className="font-semibold">{algo.speed}%</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div className="bg-purple-500 rounded-full h-2" style={{width: `${algo.speed}%`}}></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4 text-gray-800">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm font-semibold">New product listed</p>
              <p className="text-xs text-gray-600">Organic Tomatoes by Green Valley Farm</p>
            </div>
            <span className="text-xs text-gray-500">2m ago</span>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm font-semibold">Order placed</p>
              <p className="text-xs text-gray-600">Company ABC ordered 500kg of rice</p>
            </div>
            <span className="text-xs text-gray-500">15m ago</span>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm font-semibold">Algorithm optimization</p>
              <p className="text-xs text-gray-600">Fair Hungarian improved by 3%</p>
            </div>
            <span className="text-xs text-gray-500">1h ago</span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      {activeTab === 'home' && <HomePage />}
      {activeTab === 'farmer' && <FarmerPortal />}
      {activeTab === 'company' && <CompanyPortal />}
      {activeTab === 'admin' && <AdminDashboard />}
    </div>
  );
};

// If this file is included directly in a web page that has a '#root' element,
// automatically mount the component. This keeps the module usable both as a
// standalone script (for simple demos) and as an importable component.
try {
  const rootEl = typeof document !== 'undefined' ? document.getElementById('root') : null;
  if (rootEl) {
    createRoot(rootEl).render(<AgriVenturePlatform />);
  }
} catch (e) {
  // If mounting fails, we silently continue so the module can still be imported.
  // Intended errors here are typically absence of a DOM (SSR) or incompatible runtime.
  // console.warn('Auto-mount skipped:', e);
}

export default AgriVenturePlatform;
