from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, WebAppInfo, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from DB.db_func import db_select_all_group, db_select_group

admin_button = [[InlineKeyboardButton(text='Скачать всю базу', callback_data='all_base')],
                [InlineKeyboardButton(text='Скачать базу по группам', callback_data='one_group')],
                [InlineKeyboardButton(text='Рассылка', callback_data='send_message_on_base')],
                [InlineKeyboardButton(text='Удалить группы', callback_data='dell_group')]
                ]


admin_markup = InlineKeyboardMarkup(inline_keyboard=admin_button)


def cancel_markup():
    builder = InlineKeyboardBuilder()
    builder.button(text='Отмена', callback_data='cancel')
    builder.adjust(1)
    return builder.as_markup()


def skip_markup():
    builder = InlineKeyboardBuilder()
    builder.button(text='Отмена', callback_data='cancel')
    builder.button(text='Пропустить', callback_data='skip')
    builder.adjust(1)
    return builder.as_markup()



def group_builder():
    group_list = db_select_group()
    builder = InlineKeyboardBuilder()
    for one in group_list:
        builder.button(text=one['name'], callback_data=str(one['groups_id']))
    builder.adjust(1)
    return builder.as_markup()

#--------------------------генератор клавиатур группы
def group_builder_1():
    group_list = db_select_group()
    builder = InlineKeyboardBuilder()
    for one in group_list:
        builder.button(text=one['name'], callback_data=str(one['groups_id']))
    builder.button(text="Отмена", callback_data='cancel')
    builder.adjust(1)
    return builder.as_markup()


def send_cancel():
    builder = InlineKeyboardBuilder()
    builder.button(text='Отправить', callback_data='send')
    builder.button(text='Отмена', callback_data='cancel')
    builder.adjust(1)
    return builder.as_markup()