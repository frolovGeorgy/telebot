from typing import Optional

import telebot

from .all_commands import check_num, return_hotels
from .log import logger, my_log
from .const import bot
from .classes import TeleUser



@my_log
def take_hotels_num_low(call: Optional[telebot.types.CallbackQuery]):
    """
    Getting amount of hotels
    """
    TeleUser.users_dict[call.message.chat.id].current_state.go_command()
    logger.info(f'Бот чата {call.message.chat.id} перешел в состояние command')
    hotel_id = call.data
    bot.send_message(call.from_user.id, 'Сколько вывести результатов? (максимум 25)')
    bot.register_next_step_handler(call.message,
                                   check_num,
                                   next_func=return_hotels,
                                   hotel_id=hotel_id,
                                   calling_func=take_hotels_num_low)
