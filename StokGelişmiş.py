import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
import sqlite3
import random
import string

class Product:
    def __init__(self, name, stock_quantity):
        self.name = name
        self.stock_quantity = stock_quantity

class Stock:
    def __init__(self):
        self.connection = sqlite3.connect("stock_management.db")
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT,
                                stock_quantity INTEGER
                            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                product_name TEXT,
                                quantity INTEGER,
                                order_number TEXT
                            )''')
        self.connection.commit()

    def add_product(self, product):
        self.cursor.execute("INSERT INTO products (name, stock_quantity) VALUES (?, ?)", (product.name, product.stock_quantity))
        self.connection.commit()

    def get_products(self):
        self.cursor.execute("SELECT name, stock_quantity FROM products")
        return self.cursor.fetchall()

    def update_stock(self, product_name, quantity):
        self.cursor.execute("UPDATE products SET stock_quantity = ? WHERE name = ?", (quantity, product_name))
        self.connection.commit()

    def create_order(self, product_name, quantity):
        order_number = self.generate_order_number()
        self.cursor.execute("INSERT INTO orders (product_name, quantity, order_number) VALUES (?, ?, ?)",
                            (product_name, quantity, order_number))
        self.connection.commit()
        
        # Stoktan düşme işlemi
        current_stock = self.cursor.execute("SELECT stock_quantity FROM products WHERE name = ?", (product_name,)).fetchone()[0]
        new_stock = current_stock - quantity
        self.cursor.execute("UPDATE products SET stock_quantity = ? WHERE name = ?", (new_stock, product_name))
        self.connection.commit()
        
        return order_number

    def delete_product(self, product_name):
        self.cursor.execute("DELETE FROM products WHERE name = ?", (product_name,))
        self.connection.commit()

    def generate_order_number(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    def get_order_by_number(self, order_number):
        self.cursor.execute("SELECT product_name, quantity FROM orders WHERE order_number = ?", (order_number,))
        return self.cursor.fetchone()

class StockManagementApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stok Takip Sistemi")
        self.setGeometry(100, 100, 400, 300)

        self.stock = Stock()

        self.init_ui()

    def init_ui(self):
        # Widgets
        self.product_name_label = QLabel("Ürün Adı:")
        self.product_name_input = QLineEdit()
        self.stock_quantity_label = QLabel("Stok Miktarı:")
        self.stock_quantity_input = QLineEdit()

        self.add_product_button = QPushButton("Ürün Ekle")
        self.add_product_button.clicked.connect(self.add_product)

        self.update_stock_button = QPushButton("Stok Güncelle")
        self.update_stock_button.clicked.connect(self.update_stock)

        self.delete_product_button = QPushButton("Ürün Sil")
        self.delete_product_button.clicked.connect(self.delete_product)

        self.product_list_label = QLabel("Ürün Listesi")
        self.product_list = QTextEdit()

        self.order_form_label = QLabel("Sipariş Oluştur")
        self.order_product_name_label = QLabel("Ürün Adı:")
        self.order_product_name_input = QLineEdit()
        self.order_quantity_label = QLabel("Adet:")
        self.order_quantity_input = QLineEdit()
        self.create_order_button = QPushButton("Sipariş Oluştur")
        self.create_order_button.clicked.connect(self.create_order)

        self.check_order_label = QLabel("Sipariş Sorgula")
        self.order_number_label = QLabel("Sipariş Numarası:")
        self.order_number_input = QLineEdit()
        self.check_order_button = QPushButton("Siparişi Sorgula")
        self.check_order_button.clicked.connect(self.check_order)

        # Layout
        self.layout = QVBoxLayout()
        
        self.form_layout = QVBoxLayout()
        self.form_layout.addWidget(self.product_name_label)
        self.form_layout.addWidget(self.product_name_input)
        self.form_layout.addWidget(self.stock_quantity_label)
        self.form_layout.addWidget(self.stock_quantity_input)
        self.form_layout.addWidget(self.add_product_button)
        self.form_layout.addWidget(self.update_stock_button)
        self.form_layout.addWidget(self.delete_product_button)

        self.layout.addWidget(self.product_list_label)
        self.layout.addWidget(self.product_list)
        self.layout.addLayout(self.form_layout)

        self.order_form_layout = QVBoxLayout()
        self.order_form_layout.addWidget(self.order_form_label)
        self.order_form_layout.addWidget(self.order_product_name_label)
        self.order_form_layout.addWidget(self.order_product_name_input)
        self.order_form_layout.addWidget(self.order_quantity_label)
        self.order_form_layout.addWidget(self.order_quantity_input)
        self.order_form_layout.addWidget(self.create_order_button)

        self.check_order_form_layout = QVBoxLayout()
        self.check_order_form_layout.addWidget(self.check_order_label)
        self.check_order_form_layout.addWidget(self.order_number_label)
        self.check_order_form_layout.addWidget(self.order_number_input)
        self.check_order_form_layout.addWidget(self.check_order_button)

        self.layout.addLayout(self.order_form_layout)
        self.layout.addLayout(self.check_order_form_layout)

        self.setLayout(self.layout)

        self.update_product_list()

    def add_product(self):
        name = self.product_name_input.text()
        stock_quantity = self.stock_quantity_input.text()

        try:
            stock_quantity = int(stock_quantity)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Stok miktarı sayı olmalıdır.")
            return

        if name and stock_quantity:
            product = Product(name, stock_quantity)
            self.stock.add_product(product)
            self.product_name_input.clear()
            self.stock_quantity_input.clear()
            self.update_product_list()
        else:
            QMessageBox.warning(self, "Hata", "Ürün adı ve stok miktarı boş olamaz.")

    def update_stock(self):
        name = self.product_name_input.text()
        new_stock_quantity = self.stock_quantity_input.text()

        try:
            new_stock_quantity = int(new_stock_quantity)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Yeni stok miktarı sayı olmalıdır.")
            return

        if name and new_stock_quantity:
            self.stock.update_stock(name, new_stock_quantity)
            self.product_name_input.clear()
            self.stock_quantity_input.clear()
            self.update_product_list()
        else:
            QMessageBox.warning(self, "Hata", "Ürün adı ve yeni stok miktarı boş olamaz.")

    def delete_product(self):
        name = self.product_name_input.text()
        if name:
            self.stock.delete_product(name)
            self.product_name_input.clear()
            self.update_product_list()
        else:
            QMessageBox.warning(self, "Hata", "Ürün adı boş olamaz.")

    def create_order(self):
        product_name = self.order_product_name_input.text()
        quantity = self.order_quantity_input.text()

        try:
            quantity = int(quantity)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Sipariş adedi sayı olmalıdır.")
            return

        if product_name and quantity:
            order_number = self.stock.create_order(product_name, quantity)
            QMessageBox.information(self, "Başarılı", f"{quantity} adet {product_name} siparişi oluşturuldu. Sipariş numarası: {order_number}")
            self.order_product_name_input.clear()
            self.order_quantity_input.clear()
        else:
            QMessageBox.warning(self, "Hata", "Ürün adı ve sipariş adedi boş olamaz.")

    def check_order(self):
        order_number = self.order_number_input.text()
        if order_number:
            order_info = self.stock.get_order_by_number(order_number)
            if order_info:
                QMessageBox.information(self, "Sipariş Bilgisi", f"Sipariş Numarası: {order_number}\nÜrün Adı: {order_info[0]}\nAdet: {order_info[1]}")
            else:
                QMessageBox.warning(self, "Hata", "Sipariş bulunamadı.")
        else:
            QMessageBox.warning(self, "Hata", "Sipariş numarası boş olamaz.")

    def update_product_list(self):
        products = self.stock.get_products()
        product_text = "\n".join([f"{name}: {quantity}" for name, quantity in products])
        self.product_list.setText(product_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockManagementApp()
    window.show()
    sys.exit(app.exec_())
