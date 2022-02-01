from .const import bot


def print_commands(message):
    bot.send_message(message.chat.id, 'Доступные команды:\n'
                                      '/lowprice — вывести список самых дешевых отелей в городе;\n'
                                      '/highprice — вывести список самых дорогих отелей в городе;\n'
                                      '/bestdeal — вывести список отелей, наиболее подходящих по цене и расположению '
                                      'от центра;\n'
                                      '/stop — остановить текущее действие')
