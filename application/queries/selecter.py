select_products = \
    f'''
        SELECT *
        FROM product
        JOIN price USING (prod_id)
    '''

select_user_by_email_and_pass = \
    f'''
        SELECT * 
        FROM user
        WHERE email = %(email)s AND password = %(password)s;
    '''

select_user_by_email_or_phone = \
    f'''
        SELECT * 
        FROM user
        WHERE email = %(email)s OR phone = %(phone)s;
    '''

select_order = \
    f'''
        SELECT title, price.price, discount, `order`.order_id, prod_id, amount, ROUND(price - (price * discount / 100), 2) AS new_price
        FROM `order`
            JOIN order_product USING (order_id)
            JOIN product USING (prod_id)
            JOIN price USING (prod_id)
        WHERE user_id = %(user_id)s AND date_end IS NULL;
    '''

select_product = \
    f'''
        SELECT code, title, price.price, description, category.name, manufacture.name, discount, weight, width, height, `long`
        FROM product
            JOIN category USING (ctgr_id)
            JOIN manufacture USING (manuf_id)
            JOIN price USING (prod_id)
        WHERE prod_id = %(product_id)s;
    '''

select_user_full_info = \
    f'''
        SELECT user_id, user.name, surname, patronymic, email, phone, role.name, password, birthday
        FROM user
            JOIN role USING (role_id)
    '''

select_orders = \
    f'''
        SELECT title, price.price, discount, comment, address, amount, ROUND(price - (price * discount / 100), 2) AS new_price,
        cost_delivery, payment_type, date_start, date_end
        FROM product 
            JOIN order_product USING (prod_id)
            JOIN `order` USING (order_id)
            JOIN user USING (user_id)
            JOIN price USING (prod_id)
        WHERE user_id = %(user_id)s AND date_end IS NOT NULL
        ORDER BY date_start DESC;
    '''
