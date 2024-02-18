# -*- coding:utf-8 -*-
# @Date: "2024-02-18"
# @Description: flask admin


from app.admin import admin_bp


@admin_bp.route('/get_token/<user_name>', methods=['GET', 'POST'])
def get_token(user_name):
    return 'get_token'