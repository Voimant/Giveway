import asyncio
import logging

from aiogram import types, Dispatcher, Router, F, Bot
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER, JOIN_TRANSITION
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated, FSInputFile
from aiogram.filters.state import State, StatesGroup
from dotenv import load_dotenv
import os

from DB.db_func import db_insert_new_group, db_select_all_group, db_insert_new_user, export_csv, db_select_name_group, \
    export_one_csv, db_select_users_in_group
from keyboards import admin_markup, group_builder, cancel_markup, skip_markup, group_builder_1, send_cancel

router = Router()

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER))
async def on_bot_added_to_group(event: ChatMemberUpdated, bot: Bot):
    # Логируем добавление
    db_insert_new_group(int(event.chat.id), str(event.chat.title))
    await bot.send_message(os.getenv('ADMIN'), f"Бота добавили в группу {event.chat.title} (ID: {event.chat.id})")
    print(event)




@router.callback_query(F.data == 'cancel')
async def get_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Выберете пункт меню', reply_markup=admin_markup)

@router.message(Command('start'))
async def start_handler(mess: Message, bot: Bot, state: FSMContext):

    if mess.from_user.id == int(os.getenv('ADMIN')):
        await state.clear()
        await mess.answer('Выберете пункт в меню', reply_markup=admin_markup)

    else:
        join_group = []
        user_id = mess.from_user.id
        list_groups = db_select_all_group()
        print(list_groups)

        for chat in list_groups:
            try:
                # # Проверяем, что бот является участником канала
                # bot_member = await bot.get_chat_member(chat_id=chat, user_id=bot.id)
                # if bot_member.status not in ['member', 'administrator', 'creator']:
                #     join_group.append(True)

                # Проверяем, что пользователь является участником канала
                user_member = await bot.get_chat_member(chat_id=int(chat), user_id=int(user_id))
                print(user_member)

                if user_member.status in ['member', 'administrator', 'creator']:
                    user_id = mess.from_user.id
                    name = mess.from_user.full_name
                    username = mess.from_user.username
                    db_insert_new_user(user_id, username, name, int(chat))

            except TelegramAPIError as e:
                logging.info(f"Ошибка при проверке участников канала: {e}")



        await mess.answer('Приветственное сообщение, жду информаицию')


# -----------------Отчет по всем группам
@router.callback_query(F.data == 'all_base')
async def upload_all_base(call: CallbackQuery, state: FSMContext):
    await state.clear()
    export_csv()
    file = FSInputFile('reports/report.xlsx')
    await call.message.answer_document(file, caption='Документ отправлен', reply_markup=admin_markup)


class FsmSt(StatesGroup):
    send = State()

#--------------Отчет по одному каналу
@router.callback_query(F.data == 'one_group')
async def one_group_upload(call:CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Выберете группу', reply_markup=group_builder())
    await state.set_state(FsmSt.send)


@router.callback_query(FsmSt.send)
async def send_on_group(call: CallbackQuery, state: FSMContext):
    id_group = call.data
    name = db_select_name_group(id_group)
    print(name)
    export_one_csv(id_group)
    new_name = name.replace(" ", "_")
    print(new_name)
    file = FSInputFile(f'reports/{new_name}.xlsx')
    await call.message.answer_document(file, caption='Документ отправлен', reply_markup=admin_markup)
    await state.clear()



class FsmMessage(StatesGroup):
    message = State()
    pic_skip = State()
    group = State()
    check = State()
@router.callback_query(F.data == 'send_message_on_base')
async def send_base(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Введите сообщение пользователям', reply_markup=cancel_markup())
    await state.set_state(FsmMessage.message)


@router.message(FsmMessage.message)
async def get_my_message(mess: Message, state: FSMContext):
    await state.update_data(message=mess.text)
    await mess.answer('Добавьте картинку или нажмите пропустить', reply_markup=skip_markup())
    await state.set_state(FsmMessage.pic_skip)


@router.callback_query(FsmMessage.pic_skip)
async def get_pic_skip(call: CallbackQuery, state: FSMContext):
    await state.update_data(pic_skip=None)
    await call.message.answer('По какой группе сделать рассылку?', reply_markup=group_builder_1())
    await state.set_state(FsmMessage.group)

@router.message(FsmMessage.pic_skip)
async def get_pic_skip(mess: Message, state: FSMContext):
    await state.update_data(pic_skip=mess.photo[-1].file_id)
    await mess.answer('По какой группе сделать рассылку?', reply_markup=group_builder_1())
    await state.set_state(FsmMessage.group)


@router.callback_query(FsmMessage.group)
async def get_check(call: CallbackQuery, state: FSMContext):
    await state.update_data(group=call.data)
    data = await state.get_data()
    text = (f'Проверьте правильность сообщения\n'
            f'Сообщение: {data["message"]}\n')
    match data['pic_skip']:
        case None:
            await call.message.answer(text, reply_markup=send_cancel())
            await state.set_state(FsmMessage.check)
        case _:
            await call.message.answer_photo(data['pic_skip'], caption=text, reply_markup=send_cancel())
            await state.set_state(FsmMessage.check)


@router.callback_query(FsmMessage.check, F.data == 'send')
async def send_mess(call: CallbackQuery, state: FSMContext, bot: Bot):

    data = await state.get_data()
    print(data['group'])
    base = db_select_users_in_group(int(data['group']))
    text = f'{data["message"]}\n'
    logging.info(f'Список отправлений: {base}')
    for chat_id in base:
        match data['pic_skip']:
            case None:
                try: #---------------Исключаем ошибки при блокировке пользователями
                    logging.info('Отправка кейс None')
                    await bot.send_message(chat_id, text)
                except TelegramForbiddenError as e:
                    logging.warning(f'{e}')
                    pass
            case _:
                try: #---------------Исключаем ошибки при блокировке пользователями
                    logging.info('Отправка c фоткой')
                    await bot.send_photo(chat_id, data['pic_skip'], caption=text)
                except TelegramForbiddenError as e:
                    logging.warning(f'{e}')
                    pass
        await asyncio.sleep(0.1) #---------------Обходим ограничение API
    await call.message.answer('Рассылка окончена', reply_markup=admin_markup)
    await state.clear()






