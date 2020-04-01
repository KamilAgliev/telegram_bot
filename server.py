from random import randint as Ra
import time

from telegram import ReplyKeyboardMarkup

from data import TOKEN
# Импортируем необходимые классы.
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler

curr_time = 0


# Обычный обработчик, как и те, которыми мы пользовались раньше.
def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.message.chat_id
    try:
        # args[0] должен содержать значение аргумента (секунды таймера)
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text(
                'Извините, но этот момент времени уже прошел...')
            return

        # Добавляем задачу в очередь
        # и останавливаем предыдущую (если она была)
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_once(task, due, context=chat_id)
        # Запоминаем созданную задачу в данных чата.
        context.chat_data['job'] = new_job
        # Присылаем сообщение о том, что всё получилось.
        global curr_time
        curr_time = due
        reply_keyboard = [["/close"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text(f'Засёк {due} секунд', reply_markup=markup)


    except (IndexError, ValueError):
        update.message.reply_text('Использование: /set_timer <секунд>')


def task(context):
    global curr_time
    res = str(curr_time) + " секунд истекло"
    job = context.job
    reply_keyboard = [["30 секунд"],
                      ["1 минута"],
                      ["5 минут"],
                      ["вернуться назад"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    context.bot.send_message(job.context, text=res, reply_markup=markup)


def unset_timer(update, context):
    # Проверяем, что задача ставилась
    if 'job' not in context.chat_data:
        reply_keyboard = [["30 секунд"],
                          ["1 минута"],
                          ["5 минут"],
                          ["вернуться назад"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

        update.message.reply_text('Нет активного таймера', reply_markup=markup)
        return
    job = context.chat_data['job']
    # планируем удаление задачи (выполнится, когда будет возможность)
    job.schedule_removal()
    # и очищаем пользовательские данные
    del context.chat_data['job']
    reply_keyboard = [["30 секунд"],
                      ["1 минута"],
                      ["5 минут"],
                      ["вернуться назад"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    update.message.reply_text('Хорошо, таймер удален!', reply_markup=markup)


def dice(update, context):
    reply_keyboard = [["кинуть один шестигранный кубик"],
                      ["кинуть 2 шестигранных кубика одновременно"],
                      ["кинуть 20-гранный кубик"],
                      ["вернуться назад"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text("Выберите вид броска", reply_markup=markup)


def timer(update, context):
    reply_keyboard = [["30 секунд"],
                      ["1 минута"],
                      ["5 минут"],
                      ["вернуться назад"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text("Выберите время таймера", reply_markup=markup)


def start(update, context):
    reply_keyboard = [["/dice"],
                      ["/timer"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text("dice - бросок костей \n"
                              "timer - установить таймер", reply_markup=markup)


def response(update, context):
    res = ""
    if update.message.text == "кинуть один шестигранный кубик":
        res = str(Ra(1, 6))
    elif update.message.text == "кинуть 2 шестигранных кубика одновременно":
        res = str(Ra(1, 6)) + " and " + str(Ra(1, 6))
    elif update.message.text == "кинуть 20-гранный кубик":
        res = str(Ra(1, 20))
    elif update.message.text == "30 секунд":
        cont1 = context
        cont1.args = [30]
        set_timer(update, cont1)
    elif update.message.text == "1 минута":
        cont1 = context
        cont1.args = [60]
        set_timer(update, cont1)
    elif update.message.text == "5 минут":
        cont1 = context
        cont1.args = [300]
        set_timer(update, cont1)
    elif update.message.text == "вернуться назад":
        start(update, context)
        return
    update.message.reply_text(res)


def main():
    REQUEST_KWARGS = {
        'proxy_url': 'socks5://localhost:9150',  # Адрес прокси сервера
    }
    updater = Updater(TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)
    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    # Регистрируем обработчик в диспетчере.
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("dice", dice))
    dp.add_handler(CommandHandler("timer", timer))
    dp.add_handler(CommandHandler("close", unset_timer))
    dp.add_handler(CommandHandler("set_timer", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset_timer", unset_timer,
                                  pass_chat_data=True))

    text_handler = MessageHandler(Filters.text, response)

    # Регистрируем обработчик в диспетчере.
    dp.add_handler(text_handler)
    # Запускаем цикл приема и обработки сообщений.
    updater.start_polling()
    # Ждём завершения приложения.
    # (например, получения сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()
    # Запускаем функцию main() в случае запуска скрипта.


if __name__ == '__main__':
    main()
