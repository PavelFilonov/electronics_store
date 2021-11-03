insert_user = \
    f'''
        INSERT INTO user (name, surname, patronymic, email, phone, password, birthday)
        VALUES (%(name)s, %(surname)s, %(patronymic)s, %(email)s, %(phone)s, %(password)s, %(birthday)s);
    '''

insert_product = \
    f'''
        INSERT INTO product (code, title, description, ctgr_id, manuf_id, discount, weight, 
        width, height, `long`)
        SELECT %(code)s, %(title)s, %(description)s, ctgr_id, manuf_id, %(discount)s, 
        %(weight)s, %(width)s, %(height)s, %(long)s
        FROM category, manufacture
        WHERE category.name = %(name_category)s AND manufacture.name = %(name_manufacture)s;
    '''

insert_store = \
    f'''
        INSERT INTO store (prod_id, amount, date_from, date_to)
        SELECT prod_id, %(amount)s, NOW(), %(date_to)s
        FROM product
        WHERE title = %(title)s;
    '''

insert_price = \
    f'''
        INSERT INTO price (price, prod_id, date_from, date_to)
        SELECT %(price)s, prod_id, NOW(), %(date_to)s
        FROM product
        WHERE title = %(title)s;
    '''
