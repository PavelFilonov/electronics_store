from flask import request, render_template, session, url_for, redirect

from application import app
from application.database import Error, get_db, close_db
from application.queries.selecter import *
from application.queries.inserter import *
from application.queries.updater import *
from application.queries.deleter import *
from application.utils import calculate_total, get_active_user, add_product_to_cart, delete_product


@app.route('/', methods=['GET', 'POST'])
def main():
    user = get_active_user()
    connection, cursor = get_db()
    if request.method == 'POST':
        if "add_to_cart" in request.form:
            try:
                add_product_to_cart(connection, cursor)
            except Error as e:
                print(e)
                return redirect(url_for('main'))
        elif "delete" in request.form:
            return delete_product(connection, cursor, request.form['delete'])
    cursor.execute(select_products)
    products = cursor.fetchall()
    close_db(connection, cursor)
    return render_template('main.html', products=products, user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_active_user()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection, cursor = get_db()
        cursor.execute(select_user_by_email_and_pass, {'email': email, 'password': password})
        user_query = cursor.fetchall()
        close_db(connection, cursor)

        if len(user_query) == 0 or user_query[0][6] != password:
            return render_template('login.html', message="Неверные данные", user=user)
        else:
            session['user_id'] = user_query[0][0]
            return redirect(url_for('main'))
    return render_template('login.html', user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    user = get_active_user()
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        patronymic = request.form['patronymic']
        email = request.form['email']
        phone = request.form['phone']
        password1 = request.form['password1']
        password2 = request.form['password2']
        date_birthday = request.form['date']

        if password1 != password2:
            return render_template('register.html', message="Пароли не совпадают", user=user)

        if len(password1) < 8:
            return render_template('register.html', message="Минимальное количество символов в пароле: 8", user=user)

        connection, cursor = get_db()
        cursor.execute(select_user_by_email_or_phone, {'email': email, 'phone': phone})
        user = cursor.fetchall()

        if len(user) > 0:
            return render_template('register.html', message="Пользователь с введёнными данными уже существует",
                                   user=user)

        try:
            cursor.execute(insert_user, {'name': name, 'surname': surname, 'patronymic': patronymic, 'email': email,
                                         'phone': phone, 'password': password1, 'birthday': date_birthday})
            connection.commit()
            cursor.execute(select_user_by_email_and_pass, {'email': email, 'password': password1})
            user = cursor.fetchall()
            session['user_id'] = user[0][0]
            return redirect(url_for('main'))
        except Error as e:
            print(e)
            return render_template('register.html', message="Неправильный ввод", user=user)
        finally:
            close_db(connection, cursor)
    user = get_active_user()
    return render_template('register.html', user=user)


@app.route('/create', methods=['GET', 'POST'])
def create():
    user = get_active_user()
    if user['role_name'] != "Admin":
        return redirect(url_for('main'))

    if request.method == 'POST':
        code = request.form['code']
        title = request.form['title']
        description = request.form['description']
        name_category = request.form['name_category']
        name_manufacture = request.form['name_manufacture']

        try:
            price = float(request.form['price'])
            discount = int(request.form['discount'])
            weight = int(request.form['weight'])
            width = int(request.form['width'])
            height = int(request.form['height'])
            long = int(request.form['long'])
            amount = int(request.form['amount'])
        except Error as e:
            print(e)
            return render_template('create.html', message="Неправильный ввод", user=user)

        if price < 0 or discount < 0 or weight < 0 or width < 0 or height < 0 or long < 0 or amount < 0:
            return render_template('create.html', message="Отрицательные данные", user=user)

        connection, cursor = get_db()
        try:
            cursor.execute(insert_product, {'code': code, 'title': title, 'description': description,
                                            'discount': discount,'weight': weight, 'width': width, 'height': height,
                                            'long': long, 'name_category': name_category,
                                            'name_manufacture': name_manufacture})
            connection.commit()

            cursor.execute(insert_store, {'amount': amount, 'date_to': '3000-01-01 00:00:00', 'title': title})
            connection.commit()

            cursor.execute(insert_price, {'price': price, 'amount': amount, 'date_to': '3000-01-01 00:00:00',
                                          'title': title})
            connection.commit()
            return redirect(url_for('main'))
        except Error as e:
            print(e)
            return render_template('create.html', message="Неправильный ввод", user=user)
        finally:
            close_db(connection, cursor)
    return render_template('create.html', user=user)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    connection, cursor = get_db()
    if request.method == 'POST':
        if "delete" in request.form:
            keys = request.form['delete'].split(" ")
            cursor.execute(delete_order_product, {'order_id': keys[0], 'product_id': keys[1]})
            connection.commit()
        elif "-" in request.form:
            keys = request.form['-'].split(" ")
            cursor.execute(update_order_product_minus, {'order_id': keys[0], 'product_id': keys[1]})
            connection.commit()
        elif "+" in request.form:
            keys = request.form['+'].split(" ")
            cursor.execute(update_order_product_plus, {'order_id': keys[0], 'product_id': keys[1]})
            connection.commit()
        elif "buy" in request.form:
            # cursor.execute(
            #     f'''
            #         UPDATE order
            #         SET comment = %(comment)s, address = %(address)s, cost_delivery = %(cost_delivery)s,
            #         payment_type = %(payment_type)s, date_end = NOW()
            #         WHERE user_id = %(user_id)s AND date_end IS NULL;
            #     '''
            #     , {'comment': request.form['comment'], 'address': request.form['address'],
            #        'cost_delivery': request.form['cost_delivery'], 'payment_type': request.form['payment_type'],
            #        'user_id': session['user_id']}
            # )
            # connection.commit()

            # cursor.execute(
            #     f'''
            #         SELECT *
            #         FROM store
            #         WHERE NOW() BETWEEN date_from AND date_to
            #     '''
            # )
            pass

    cursor.execute(select_order, {'user_id': session['user_id']})

    cart_products = cursor.fetchall()
    close_db(connection, cursor)
    total = calculate_total(cart_products)
    user = get_active_user()
    return render_template('cart.html', cart_products=cart_products, size=len(cart_products), total=total, user=user)


@app.route('/products/<int:id>', methods=['GET', 'POST'])
def product(id):
    user = get_active_user()
    connection, cursor = get_db()
    if request.method == 'POST':
        if "add_to_cart" in request.form:
            try:
                add_product_to_cart(connection, cursor)
            except Error as e:
                return redirect(url_for('main'))
        elif "delete" in request.form:
            return delete_product(connection, cursor, id)
    cursor.execute(select_product, {'product_id': id})
    prod = cursor.fetchall()[0]
    close_db(connection, cursor)
    return render_template('product.html', user=user, product=prod)


@app.route('/users', methods=['GET', 'POST'])
def users():
    user = get_active_user()
    connection, cursor = get_db()
    if user['role_name'] != "Admin":
        return redirect(url_for('main'))
    if request.method == 'POST':
        if "delete_user" in request.form:
            cursor.execute(delete_user, {'user_id': request.form['delete_user']})
            connection.commit()
        elif "do_admin" in request.form:
            cursor.execute(update_do_admin_user, {'user_id': request.form['do_admin']})
            connection.commit()
        elif "remove_admin" in request.form:
            cursor.execute(update_remove_admin_user, {'user_id': request.form['remove_admin']})
            connection.commit()
    cursor.execute(select_user_full_info)
    all_users = cursor.fetchall()
    close_db(connection, cursor)
    return render_template('users.html', users=all_users, user=user, user_id=session['user_id'])


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    user = get_active_user()
    connection, cursor = get_db()
    cursor.execute(select_orders, {'user_id': session['user_id']})
    ords = cursor.fetchall()
    total = calculate_total(ords)
    close_db(connection, cursor)
    return render_template('orders.html', orders=ords, user=user, size=len(ords), total=total)


@app.route('/exit')
def log_out():
    session.pop('user_id', None)
    return redirect(url_for('main'))
