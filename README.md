# 🛒 Hilaac Grocery Management System

A robust, user-friendly Django-based platform that empowers grocery sellers with real-time sales insights, inventory control, streamlined checkout, and advanced customer reporting.

---

## 🚀 Features

- Role-based access for Sellers and Customers  
- 📦 Smart Inventory Management with automated stock tracking  
- 🧾 Add-to-Cart, Quantity Updates, and Subtotals for seamless customer orders  
- 💳 Stripe Integration for secure online payments  
- 📊 Sales Analytics Dashboard with date filters and interactive charts  
- 🖨️ Printable Reports for sales, shipments, and individual customer orders  
- 📄 Audit Logs to maintain transparency and traceability  
- 📬 Customer Insights: Searchable buyer history with contact and address info  
- 🧠 Admin-Free Automation: Original stock values preserved and updates are dynamic  
- ✏️ Seller Panel Enhancements: Responsive design, route cleanup, and reporting tools  

---

## 🧱 Tech Stack

- Backend: Django 5.0+, SQLite / PostgreSQL  
- Frontend: Bootstrap 5.3, Chart.js for visualizations  
- Authentication: Django Auth with custom roles  
- Payments: Stripe API  
- Exports: Print-optimized HTML templates (PDF support optional)

---

## 📂 Key Pages

- /seller/dashboard/ → Seller overview  
- /seller/cart/ → Customer cart interface  
- /seller/analytics/ → Sales visualization with filter range  
- /seller/customers/ → Customer purchase history  
- /seller/analytics/report/ → Printable sales summary report  

---

## 💡 Getting Started

```bash
# Clone the project
git clone https://github.com/yourusername/hilaac-grocery.git

# Navigate in
cd hilaac-grocery

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
