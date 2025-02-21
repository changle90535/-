from flask import Flask, render_template, request, redirect, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# 設定文件上傳
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# 首頁
@app.route('/')
def home():
    return render_template('index.html')

# 新增客戶
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        google_map_url = request.form['google_map_url']

        conn = sqlite3.connect('customer.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customers (name, address, phone, email, google_map_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, address, phone, email, google_map_url))
        conn.commit()
        conn.close()
        return redirect(url_for('customers'))
    return render_template('add_customer.html')

# 查看客戶列表
@app.route('/customers')
def customers():
    conn = sqlite3.connect('customer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customers')
    customers = cursor.fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)

# 編輯客戶
@app.route('/edit_customer/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    conn = sqlite3.connect('customer.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        google_map_url = request.form['google_map_url']

        cursor.execute('''
            UPDATE customers
            SET name = ?, address = ?, phone = ?, email = ?, google_map_url = ?
            WHERE id = ?
        ''', (name, address, phone, email, google_map_url, id))
        conn.commit()
        conn.close()
        return redirect(url_for('customers'))
    else:
        cursor.execute('SELECT * FROM customers WHERE id = ?', (id,))
        customer = cursor.fetchone()
        conn.close()
        return render_template('edit_customer.html', customer=customer)

# 刪除客戶
@app.route('/delete_customer/<int:id>')
def delete_customer(id):
    conn = sqlite3.connect('customer.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM customers WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('customers'))

# 新增報修紀錄
@app.route('/add_repair/<int:customer_id>', methods=['GET', 'POST'])
def add_repair(customer_id):
    if request.method == 'POST':
        description = request.form['description']
        status = request.form['status']
        photo = request.files.get('photo')

        conn = sqlite3.connect('customer.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO repairs (customer_id, description, status)
            VALUES (?, ?, ?)
        ''', (customer_id, description, status))

        if photo and photos.file_allowed(photo, photo.filename):
            filename = secure_filename(photo.filename)
            unique_filename = f"{customer_id}_{filename}"
            photos.save(photo, name=unique_filename)
            cursor.execute('''
                UPDATE repairs
                SET photo_path = ?
                WHERE id = ?
            ''', (unique_filename, cursor.lastrowid))

        conn.commit()
        conn.close()
        return redirect(url_for('view_repairs', customer_id=customer_id))
    return render_template('add_repair.html', customer_id=customer_id)

# 查看報修紀錄
@app.route('/view_repairs/<int:customer_id>')
def view_repairs(customer_id):
    conn = sqlite3.connect('customer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM repairs WHERE customer_id = ?', (customer_id,))
    repairs = cursor.fetchall()
    conn.close()
    return render_template('view_repairs.html', repairs=repairs, customer_id=customer_id)

# 編輯報修紀錄 (修正重點)
@app.route('/edit_repair/<int:repair_id>', methods=['GET', 'POST'])
def edit_repair(repair_id):
    conn = sqlite3.connect('customer.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        description = request.form['description']
        status = request.form['status']
        cursor.execute('''
            UPDATE repairs
            SET description = ?, status = ?
            WHERE id = ?
        ''', (description, status, repair_id))
        conn.commit()
        conn.close()
        cursor.execute('SELECT customer_id FROM repairs WHERE id = ?', (repair_id,))
        customer_id = cursor.fetchone()[0]
        return redirect(url_for('view_repairs', customer_id=customer_id))
    else:
        cursor.execute('SELECT * FROM repairs WHERE id = ?', (repair_id,))
        repair = cursor.fetchone()
        conn.close()
        if repair:
            return render_template('edit_repair.html', repair=repair)  # 確保傳遞 repair
        else:
            return redirect(url_for('home'))

# 刪除報修紀錄
@app.route('/delete_repair/<int:repair_id>')
def delete_repair(repair_id):
    conn = sqlite3.connect('customer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT customer_id FROM repairs WHERE id = ?', (repair_id,))
    customer_id = cursor.fetchone()[0]
    cursor.execute('DELETE FROM repairs WHERE id = ?', (repair_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_repairs', customer_id=customer_id))

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)