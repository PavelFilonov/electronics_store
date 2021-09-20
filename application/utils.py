from flask import session, redirect, url_for, request

from application.database import get_db, close_db


def calculate_total(products):
    total = 0
    for product in products:
        total += product[5] * product[6]
    return total


def get_active_user():
    name = -1
    role_name = None
    if 'user_id' in session:
        connection, cursor = get_db()
        cursor.execute(
            f'''
                SELECT user.name, role.name
                FROM user
                    JOIN role ON user.role_id = role.id
                WHERE user.id = %(user_id)s;
            '''
            , {'user_id': session['user_id']}
        )
        user = cursor.fetchall()
        if len(user) > 0:
            name = user[0][0]
            role_name = user[0][1]
    return dict(name=name, role_name=role_name)


def add_product_to_cart(connection, cursor):
    cursor.execute(
        f'''
            SELECT 1
            FROM `order`
            WHERE user_id = %(user_id)s AND date_end IS NULL;
        '''
        , {'user_id': session['user_id']}
    )
    order = cursor.fetchall()

    order_id = -1
    if len(order) == 0:
        cursor.execute(
            f'''
                INSERT INTO `order` (user_id, date_start)
                VALUES (%(user_id)s, NOW());
            '''
            , {'user_id': session['user_id']}
        )
        connection.commit()

        cursor.execute(
            f'''
                SELECT id
                FROM `order`
                ORDER BY id
                LIMIT 1;
            '''
        )
        order_id = cursor.fetchall()[0][0]

        cursor.execute(
            f'''
                INSERT INTO order_status (order_id, status_id, date_start)
                VALUES
                    (%(order_id)s, 1, NOW()),
                    (%(order_id)s, 2, NUL
                    (%(order_id)s, 3, NULL),
                    (%(order_id)s, 4, NULL)
            '''
            , {'order_id': order_id}
        )
        connection.commit()
    else:
        cursor.execute(
            f'''
                SELECT id
                FROM `order`
                WHERE user_id = %(user_id)s AND date_end IS NULL;
            '''
            , {'user_id': session['user_id']}
        )
        order_id = cursor.fetchall()[0][0]

    cursor.execute(
        f'''
            SELECT 1
            FROM order_product
            WHERE order_id = %(order_id)s AND product_id = %(product_id)s;
        '''
        , {'order_id': order_id, 'product_id': request.form['add_to_cart']}
    )
    ops = cursor.fetchall()
    if len(ops) == 0:
        cursor.execute(
            f'''
                INSERT INTO order_product (order_id, product_id)
                VALUES (%(order_id)s, %(product_id)s);
            '''
            , {'order_id': order_id, 'product_id': request.form['add_to_cart']}
        )
        connection.commit()


def delete_product(connection, cursor, product_id):
    cursor.execute(
        f'''
            DELETE FROM product
            WHERE id = %(product_id)s;
        '''
        , {'product_id': product_id}
    )
    connection.commit()
    close_db(connection, cursor)
    return redirect(url_for('main'))
