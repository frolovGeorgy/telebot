from typing import Dict, Optional

import telebot

from .log import logger, my_log
from .handlers import change_state
from .const import bot
from .classes import TeleUser
from . import chose_hotel


@my_log
def ask_city(message: Optional[telebot.types.Message]) -> None:
    logger.info(f'Пользователь ввел команду {message.text}')
    bot.send_message(message.chat.id, f'В каком городе ищем?')
    bot.register_next_step_handler(message, check_city)


@my_log
@change_state(bot)
def check_city(message: Optional[telebot.types.Message]) -> None:
    logger.info(f'Поиск города: {message.text}')
    try:
        cities_dict = chose_hotel.search_city(searching_city=message.text)

    except Exception as e:
        logger.error(f'Произошла ошибка в функции check_city. {e}')
        bot.send_message(message.chat.id, 'Произошла ошибка. Текущее действие остановлено')
        TeleUser.users_dict[message.chat.id].current_state.go_none()
        logger.info(f'Бот чата {message.chat.id} перешел в состояние none')

    else:

        if cities_dict == {}:
            bot.send_message(message.chat.id, 'Такой город не найден. Пожалуйста, введите название города '
                                              'еще раз:')
            logger.info(f'Город {message.text} не найден')
            bot.register_next_step_handler(message, check_city)

        elif not cities_dict:
            bot.send_message(message.chat.id, 'Ошибка подключения.')
            logger.info(f'Ошибка подключения')
            TeleUser.users_dict[message.chat.id].current_state.go_none()
            logger.info(f'Бот чата {message.chat.id} перешел в состояние none')

        else:
            create_keyboard(message, cities_dict=cities_dict)


@my_log
@change_state(bot)
def create_keyboard(message: Optional[telebot.types.Message], cities_dict: Dict[str, str]) -> None:
    """
    Creating a keyboard with different cities
    """
    user_chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup()

    for i_city in cities_dict:
        key = telebot.types.InlineKeyboardButton(text=i_city, callback_data=cities_dict[i_city])
        keyboard.add(key)
        logger.info(f'В клавиатуру добавлен город {key.text}')

    TeleUser.users_dict[user_chat_id].current_state.go_keyboard()
    logger.info(f'Бот чата {message.chat.id} перешел в состояние keyboard')
    bot.send_message(user_chat_id, text='Пожалуйста, выберите город:', reply_markup=keyboard)


@my_log
@change_state(bot)
def check_num(message: Optional[telebot.types.Message], **kwargs) -> None:
    """
    Checking number for integer
    """
    try:
        int(message.text)

    except ValueError:
        bot.send_message(message.from_user.id, 'Введены некорректные данные, введите число:')
        logger.info(f'Функция {kwargs["calling_func"]} ожидала int, но введено {message.text}')
        bot.register_next_step_handler(message, check_num, **kwargs)

    else:
        logger.info(f'Пользователь ввел число: {message.text}')
        kwargs['next_func'](message, **kwargs)


@my_log
def return_hotels(message: Optional[telebot.types.Message], **kwargs) -> None:
    """
    Getting hotel search results
    """
    command = {'lowprice': 'PRICE', 'highprice': 'PRICE_HIGHEST_FIRST', 'bestdeal': 'DISTANCE_FROM_LANDMARK'}
    user_curr_state = TeleUser.users_dict[message.chat.id].current_state.curr_command
    sorting_way = command[user_curr_state]

    try:
        if user_curr_state in ['lowprice', 'highprice']:
            hotels_list = chose_hotel.search_hotel(city_id=kwargs['hotel_id'],
                                                   hotels_num=message.text,
                                                   sort_order=sorting_way)
        else:
            hotels_list = []
            page_num = 1
            while len(hotels_list) < int(message.text) and page_num < 3:
                page_num += 1
                hotels_list.extend(chose_hotel.search_hotel(city_id=kwargs['hotel_id'],
                                                            sort_order=sorting_way,
                                                            max_price=kwargs['max_price'],
                                                            min_price=kwargs['min_price'],
                                                            page_num=str(page_num)))
                min_dist = float(kwargs['min_distance'])
                max_dist = float(kwargs['max_distance'])

                if hotels_list:
                    logger.info(f'Длина списка до фильтрации по расстоянию: {len(hotels_list)}')
                    # filtering list of hotels for distance
                    hotels_list = list(filter(
                        lambda dist:
                        min_dist <= float(dist['distance'].replace(',', '.').replace(' км', '')) <= max_dist,
                        hotels_list))
                    if len(hotels_list) > int(message.text):
                        hotels_list = hotels_list[:int(message.text)]
                    logger.info(f'Длина списка после фильтрации по расстоянию: {len(hotels_list)}')

                else:
                    bot.send_message(message.chat.id, 'Результатов не найдено. Попробуйте изменить фильтр.')
                    logger.info(f'Бот не нашел подходящих результатов')

        if hotels_list:
            for i_value in hotels_list:
                result = f'Отель {i_value["name"]}, адрес: {i_value["address"]}, цена: {i_value["price"]},' \
                         f' расстояние до центра: {i_value["distance"]}'
                bot.send_message(message.chat.id, result)
            logger.info(f'Бот успешно вывел результаты поиска в чате {message.chat.id}')

        else:
            bot.send_message(message.chat.id, 'Результатов не найдено. Попробуйте изменить фильтр.')
            logger.info(f'Бот не нашел подходящих результатов')

    except Exception as e:
        logger.error(f'Произошла ошибка в функции return_hotels. {e}')
        bot.send_message(message.chat.id, 'Произошла ошибка. Текущее действие остановлено')

    finally:
        logger.info(f'Бот чата {message.chat.id} перешел в состояние none')
        TeleUser.users_dict[message.chat.id].current_state.go_none()
