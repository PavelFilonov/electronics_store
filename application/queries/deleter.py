delete_order_product = \
    f'''
        DELETE FROM order_product
        WHERE order_id = %(order_id)s AND prod_id = %(product_id)s;
    '''

delete_user = \
    f'''
        DELETE FROM user
        WHERE user_id = %(user_id)s;
    '''
