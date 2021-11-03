update_order_product_minus = \
    f'''
        UPDATE order_product
        SET amount = IF (amount = 1, 1, amount - 1)
        WHERE order_id = %(order_id)s AND prod_id = %(product_id)s;
    '''

update_order_product_plus = \
    f'''
        UPDATE order_product
        SET amount = amount + 1
        WHERE order_id = %(order_id)s AND prod_id = %(product_id)s;
    '''

update_do_admin_user = \
    f'''
        UPDATE user
        SET role_id = 1
        WHERE user_id = %(user_id)s;
    '''

update_remove_admin_user = \
    f'''
        UPDATE user
        SET role_id = 2
        WHERE user_id = %(user_id)s;
    '''
