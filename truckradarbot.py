import logging
import os
import re
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
import datetime
import io
import httplib2
from googleapiclient import discovery
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

data_user = dict()
data_order = dict()
data_money = dict()
data_folders = dict()
data_files = dict()
due_order = 280
due_money = 310
max_attempts = 3

comment_status = ''
folder_dict = {
    "folder": "",
    "order": "",
    "order_sign": "",
    "zerk": "",
    "zerk_sign": "",
    "docs": "",
    "ttn": "",
    "pp": "",
}


reply_keyboard_main = [["Создать заказ", "Подать заявку на оплату"]]
reply_keyboard_menu = [["Начать сначала"]]
reply_keyboard_warning = [
    ["Сохранить данные", "Да, хочу внести данные заново"]]
reply_keyboard_warning_user = [
    ["Запомнить меня", "Да, хочу внести данные заново"]]
reply_keyboard_cancel = [["Сохранить данные", "Отмена"]]
reply_keyboard_user = [["Запомнить меня", "Отмена"]]
reply_keyboard_yesno = [["Да", "Нет"]]
id = ""
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
secret_file = "cred.json"
spreadsheet_id = "1lEksxmMI4CvQA7I5nyA3enAA1zqqlZNciG60Muur_0w"
folder_id = "1PifbJ3x_gEQLwviJwRplbZ3OBrlwH7o9"
credentials = service_account.Credentials.from_service_account_file(
    secret_file, scopes=scopes
)
DISCOVERY_SERVICE_URL = "https://sheets.googleapis.com/$discovery/rest?version=v4"
service = discovery.build(
    "sheets", "v4", credentials=credentials, discoveryServiceUrl=DISCOVERY_SERVICE_URL
)
servicefile = discovery.build(
    "drive", "v3", credentials=credentials, cache_discovery=False
)
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
(
    FIO,
    EMAIL,
    ACTION,
    TYPEORDER,
    ATICUSTOMER,
    EMAILCUSTOMER,
    PHONECUSTOMER,
    ADDRESSCUSTOMER,
    FOLDERLINK,
    FOLDERDOCS,
    ATICARRIER,
    FIODRIVER,
    FINALACTION,
    NUMBERAUTO,
    NUMBERTRAILER,
    AMOUNTCUSTOMER,
    AMOUNTCARRIER,
    TAXATION,
    ADDRESSLOADING,
    DATELOADING,
    THERMOGRAPHER,
    MORE15,
    ADDRESSUNLOADING,
    RETROBONUS,
    ORDERCOMMENT,
    STATUSCOMMENT,
    SAVEDATA,
    TYPEMONEY,
    MONEYAMOUNT,
    MONEYLINK,
    MONEYDETAILS,
    GETORDER,
    SAVEMONEYDATA,
    TTNLINK,
    WARNING,
    STARTOVER,
    SAVEUSER,
    COMMENT,
    CANCEL,
    WHEREFROM,
    TYPEAGREE,
    GETORGANIZATION,
    INNGARANT,
    ATIGARANT,
    INNCUSTOMER

) = range(45)
# Рассылка уведомлений по заказам


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:

    order_dict = search_for_alarm("Заказы!A:AD", str(context._chat_id), [
                                  "Зеркалка создана", "Отмена"], [0, 1, 2, 29, 3, 4])
    file_list = list()
    if order_dict != {}:
        for key, value in order_dict.items():
            body = {'values': [
                [str(context._chat_id), key, value[0], value[1], value[4], value[5], value[6]]]}
            resp = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range="Уведомления!A:J",
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )
        job = context.job

        for key, value in order_dict.items():
            if value[0] == "Отмена":
                text = "ВАШ ЗАКАЗ " + key + " ОТМЕНЕН по причине: " + value[1]
                await context.bot.send_message(job.chat_id, text=text)
            else:
                text = "ВАШ ЗАКАЗ: " + key + ". Заявка подписана, зеркалка сформирована"
                await context.bot.send_message(job.chat_id, text=text)
                id = value[4]
                results = servicefile.files().list(q="'{}' in parents and trashed = False".format(
                    id), fields='nextPageToken, files(id, name)', pageToken=None).execute()
                print(results)
                items = results.get('files', [])
                for f in range(0, len(items)):
                    fId = items[f].get('id')
                    fname = items[f].get('name')
                    fileRequest = servicefile.files().get_media(fileId=fId)
                    fh = io.FileIO(fname, 'wb')
                    downloader = MediaIoBaseDownload(fh, fileRequest)
                    done = False
                    try:
                        while done is False:
                            status, done = downloader.next_chunk()
                            print(F'Download {int(status.progress() * 100)}.')
                        print(fh)
                        doc_file = open(fname, 'rb')
                        await context.bot.send_document(job.chat_id, doc_file)
                        file_list.append(fname)
                        doc_file.close()
                        print(fh)
                    except:
                        print("Something went wrong.")
                    id = value[5]
                    results = servicefile.files().list(q="'{}' in parents and trashed = False".format(
                        id), fields='nextPageToken, files(id, name)', pageToken=None).execute()
                    print(results)
                    items = results.get('files', [])
                    for f in range(0, len(items)):
                        fId = items[f].get('id')
                        fname = items[f].get('name')
                        fileRequest = servicefile.files().get_media(fileId=fId)
                        fh = io.FileIO(fname, 'wb')
                        downloader = MediaIoBaseDownload(fh, fileRequest)
                        done = False
                        try:
                            while done is False:
                                status, done = downloader.next_chunk()
                                print(F'Download {
                                      int(status.progress() * 100)}.')
                                print(fh)
                                doc_file = open(fname, 'rb')
                                await context.bot.send_document(job.chat_id, doc_file)
                                file_list.append(fname)
                                doc_file.close()
                                print(fh)
                        except:
                            # Return False if something went wrong
                            print("Something went wrong.")

# Рассылка уведомлений по заявкам на оплату


async def alarm_money(context: ContextTypes.DEFAULT_TYPE) -> None:
    order_dict_money = search_for_alarm("Оплаты!A:J", str(context._chat_id), [
                                        "Оплата произведена", "Отмена"], [0, 1, 3, 8, 2, 4])
    if order_dict_money != {}:
        for key, value in order_dict_money.items():
            body = {'values': [
                [str(context._chat_id), key, value[0], value[1], value[4], value[5], value[6]]]}
            resp = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range="Уведомления!A:J",
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )
        job = context.job
        for key, value in order_dict_money.items():
            if value[0] == "Отмена":
                text = "ВАША ЗАЯВКА НА ОПЛАТУ " + key + " ПО ЗАКАЗУ " + \
                    value[2] + " ОТМЕНЕНА по причине: " + value[1]
                await context.bot.send_message(job.chat_id, text=text)
            else:
                text = "ВАШ ЗАКАЗ: " + \
                    value[2] + ". Заявка на оплату "+key + \
                    " , " + value[3]+" " + "выполнена"
                await context.bot.send_message(job.chat_id, text=text)
                id = value[6]
                results = servicefile.files().list(q="'{}' in parents and trashed = False".format(
                    id), fields='nextPageToken, files(id, name)', pageToken=None).execute()
                print(results)
                items = results.get('files', [])
                for f in range(0, len(items)):
                    fId = items[f].get('id')
                    fname = items[f].get('name')
                    fileRequest = servicefile.files().get_media(fileId=fId)
                    fh = io.FileIO(fname, 'wb')
                    downloader = MediaIoBaseDownload(fh, fileRequest)
                    done = False
                    try:
                        while done is False:
                            status, done = downloader.next_chunk()
                            print(F'Download {int(status.progress() * 100)}.')
                        print(fh)
                        doc_file = open(fname, 'rb')
                        await context.bot.send_document(job.chat_id, doc_file)
                        doc_file.close()
                    except:
                        # Return False if something went wrong
                        print("Something went wrong.")

# Проверка наличия включенных уведомлений


def job_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    else:
        return True

# Старт бота


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_exist = search_for_value(
        "Пользователи!A:B", str(update.message.chat_id), 0)
    if user_exist != []:
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start'",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard_main, one_time_keyboard=True),
        )
        return ACTION
    else:
        data_user[str(update.message.chat_id)] = []
        user = update.effective_user
        await update.message.reply_html(
            rf"Здравствуйте {
                user.mention_html()}! Представьтесь, пожалуйста (ФИО)",
            reply_markup=ReplyKeyboardRemove(),
        )
        return FIO

# возврат к началу по команде /start


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if update.message.text == "Да, хочу внести данные заново" or update.message.text == "Да" or update.message.text == "/start" or update.message.text == "старт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        data_user.clear()
        data_order.clear()
        data_folders.clear()
        data_money.clear()

        user_exist = search_for_value(
            "Пользователи!A:B", str(update.message.chat_id), 0)
        if user_exist != []:
            await update.message.reply_text(
                "Выберите действие из меню. Для возврата в главное меню введите '/start'",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard_main, one_time_keyboard=True),
            )
            return ACTION
        else:
            user = update.effective_user
            await update.message.reply_html(
                rf"Здравствуйте {
                    user.mention_html()}! Представьтесь, пожалуйста (ФИО)",
                reply_markup=ReplyKeyboardRemove(),
            )
            return FIO
    else:
        return True

# ввод корпоративной почты


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    result = re.fullmatch(
        r'[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?', update.message.text)
    if bool(result) == True:

        data_user[str(update.message.chat_id)].append(update.message.chat_id)
        data_user[str(update.message.chat_id)].append(
            update.message.from_user.username)
        data_user[str(update.message.chat_id)].append(update.message.text)
        await update.message.reply_text(
            "Введите корп. почту",
            reply_markup=ReplyKeyboardRemove(),
        )
        return EMAIL
    else:
        await update.message.reply_text(
            "ФИО не соответствует образцу 'Фамилия Имя Отчество'. Представьтесь, пожалуйста (ФИО)",
            reply_markup=ReplyKeyboardRemove(),
        )
        return FIO

# выбор действия из главного меню


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        data_user[str(update.message.chat_id)].clear()
        user = update.effective_user
        await update.message.reply_html(
            rf"Здравствуйте {
                user.mention_html()}! Представьтесь, пожалуйста (ФИО)",
            reply_markup=ReplyKeyboardRemove(),
        )
        return FIO
    else:
        result = re.fullmatch(
            r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', update.message.text)
        if bool(result) == True:
            data_user[str(update.message.chat_id)].append(update.message.text)
            await update.message.reply_text(
                "Выберите действие из меню",  reply_markup=ReplyKeyboardMarkup(reply_keyboard_user, one_time_keyboard=True),
            )
            return SAVEUSER
        else:
            await update.message.reply_text(
                "Некорректный ввод. Введите корп. почту",
                reply_markup=ReplyKeyboardRemove(),
            )
            return EMAIL


# сохранение данных о пользователе в гугл таблице (лист "Пользователи")
async def save_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == "Запомнить меня":
        chat_id = update.effective_message.chat_id
        context.job_queue.run_repeating(
            alarm, due_order, chat_id=chat_id, name=str(chat_id), data=due_order)
        context.job_queue.run_repeating(
            alarm_money, due_money, chat_id=chat_id, name=str(chat_id), data=due_money)
        text = "Ожидайте обратной связи"
        body = {"values": [data_user[str(update.message.chat_id)]]}
        if data_user[str(update.message.chat_id)] != []:
            resp = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range="Пользователи!A1",
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )
        await update.message.reply_text(
            "Спасибо! Теперь всё готово к работе. Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    elif update.message.text == "Отмена":
        await update.message.reply_text(
            "Вы уверены, что хотите отменить ввод данных?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_warning_user, one_time_keyboard=True),)
        return SAVEUSER

    elif update.message.text == "Да, хочу внести данные заново":
        data_user[str(update.message.chat_id)] = []
        user = update.effective_user
        await update.message.reply_html(
            rf"Здравствуйте {
                user.mention_html()}! Представьтесь, пожалуйста (ФИО)",
            reply_markup=ReplyKeyboardRemove(),
        )
        return FIO
    elif update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        data_user[str(update.message.chat_id)].clear()
        user = update.effective_user
        await update.message.reply_html(
            rf"Здравствуйте {
                user.mention_html()}! Представьтесь, пожалуйста (ФИО)",
            reply_markup=ReplyKeyboardRemove(),
        )
        return FIO
    else:
        await update.message.reply_text(
            "Необходимо выбрать действие из меню",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard_user, one_time_keyboard=True),
        )
        return SAVEUSER

# действия при выборе пункта главного меню


async def get_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.message.chat_id
    logger.info(f"User {chat_id} get action: {update.message.text}")
    if job_exists(str(chat_id), context) == False:
        due = 300
        context.job_queue.run_repeating(
            alarm, due_order, chat_id=chat_id, name=str(chat_id), data=due_order)
        context.job_queue.run_repeating(
            alarm_money, due_money, chat_id=chat_id, name=str(chat_id), data=due_money)
    data_order[str(chat_id)] = []
    data_money[str(chat_id)] = []
    data_folders[str(chat_id)] = []
    data_files[str(chat_id)] = [[], []]
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    elif update.message.text == "/cancel":
        await start(update, context)
        return
    elif update.message.text == "Создать заказ":
        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''

        reply_keyboard = [["Новый", "Переподписание"]]
        await update.message.reply_text(
            "Укажите тип заказа",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        data_order[str(update.message.chat_id)].append(update.message.chat_id)
        data_order[str(update.message.chat_id)].append("")
        data_order[str(update.message.chat_id)].append("Новая")
        return TYPEORDER
    elif update.message.text == "Подать заявку на оплату":
        data_money[str(update.message.chat_id)].append(update.message.chat_id)

        data_money[str(update.message.chat_id)].append("")
        order_list = search_for_value(
            "Заказы!A:B", str(update.message.chat_id), 1)
        order_list_final = ",".join(order_list)

        if order_list == []:
            await update.message.reply_text(
                "Нет ни одного заказа для оплаты. Выберите пункт меню 'Создать заказ'",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard_main, one_time_keyboard=True),
            )
            return ACTION
        else:
            await update.message.reply_text(
                "Ваши заказы: "
                + order_list_final
                + ". Введите внутренний идентификатор заказа, по которому нужна оплата",
                reply_markup=ReplyKeyboardRemove(),
            )
            return GETORDER
    else:
        await update.message.reply_text(
            "Необходимо выбрать действие из меню",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard_main, one_time_keyboard=True),
        )
        return ACTION

# ЗАЯВКА НА ОПЛАТУ
# ввод типа оплаты


async def get_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get order: {
                update.message.text}")
    order_list = search_for_value("Заказы!A:B", str(update.message.chat_id), 1)
    order_list_final = ",".join(order_list)
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    elif update.message.text not in order_list:
        order_list_final = ",".join(order_list)
        await update.message.reply_text(
            "Необходимо ввести внутренний идентификатор заказа из списка: "+order_list_final,
            reply_markup=ReplyKeyboardRemove(),
        )
        return GETORDER
    else:
        reply_keyboard = [["Предоплата", "Доплата"]]
        await update.message.reply_text(
            "Выберите тип оплаты",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        data_money[str(update.message.chat_id)].append(update.message.text)
        data_money[str(update.message.chat_id)].append("Новая")
        return TYPEMONEY

# ввод суммы оплаты


async def get_type_money(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get type money: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION

    elif update.message.text == "Предоплата" or update.message.text == "Доплата":
        await update.message.reply_text(
            "Введите сумму оплаты",
            reply_markup=ReplyKeyboardRemove(),
        )
        data_money[str(update.message.chat_id)].append(update.message.text)
        return MONEYAMOUNT
    else:
        reply_keyboard = [["Предоплата", "Доплата"]]
        await update.message.reply_text(
            "Необходимо выбрать действие из меню",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        return TYPEMONEY

# ввод реквизитов перевозчика


async def get_money_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get money amount: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.text.isdigit():
            await update.message.reply_text(
                "Введите реквизиты перевозчика для оплаты",
                reply_markup=ReplyKeyboardRemove(),
            )
            data_money[str(update.message.chat_id)].append(update.message.text)
            return MONEYDETAILS
        else:
            await update.message.reply_text(
                "Некорректный ввод. Введите сумму оплаты (только цифры)",
                reply_markup=ReplyKeyboardRemove(),
            )
            return MONEYAMOUNT


# загрузка документов (зеркалка подписанная)
async def get_money_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get money details: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        reply_keyboard = [["Продолжить"]]
        await update.message.reply_text(
            "Загрузите зеркалку (подписанную). После загрузки всех файлов нажмите 'Продолжить'",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        data_money[str(update.message.chat_id)].append(update.message.text)
        return MONEYLINK

# загрузка документов (ТТН)
# запись зеркалки на google drive


async def get_money_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get money link: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.document:
            file = await context.bot.getFile(update.message.document.file_id)
            await file.download_to_drive(update.message.document.file_name)
            doc = update.message.document
            file_name = doc.file_name
            data_files[str(update.message.chat_id)][0].append(file_name)
            if len(data_money[str(update.message.chat_id)]) < 8:
                data_money[str(update.message.chat_id)].append("")
            return MONEYLINK
        elif update.message.photo:
            file = await context.bot.getFile(update.message.photo[len(update.message.photo)-1].file_id)
            file_name = update.message.photo[len(
                update.message.photo)-1].file_id+".jpg"
            await file.download_to_drive(file_name)
            data_files[str(update.message.chat_id)][0].append(file_name)
            if len(data_money[str(update.message.chat_id)]) < 8:
                data_money[str(update.message.chat_id)].append("")
            return MONEYLINK
        elif update.message.text == "Продолжить" and len(data_money[str(update.message.chat_id)]) == 8:
            reply_keyboard = [["Продолжить"]]
            await update.message.reply_text(
                "Загрузите ТТН. После загрузки всех файлов нажмите 'Продолжить'",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            return TTNLINK

        else:
            reply_keyboard = [["Продолжить"]]
            await update.message.reply_text(
                "Это не файл. Загрузите файл",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            return MONEYLINK

# запись ТТН на google drive


async def get_ttn_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get ttn link: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.document:
            file = await context.bot.getFile(update.message.document.file_id)
            await file.download_to_drive(update.message.document.file_name)
            doc = update.message.document
            file_name = doc.file_name
            data_files[str(update.message.chat_id)][1].append(file_name)
            return TTNLINK
        elif update.message.photo:
            file = await context.bot.getFile(update.message.photo[len(update.message.photo)-1].file_id)
            file_name = update.message.photo[len(
                update.message.photo)-1].file_id+".jpg"
            await file.download_to_drive(file_name)
            data_files[str(update.message.chat_id)][1].append(file_name)
            return TTNLINK
        elif update.message.text == "Продолжить" and len(data_files[str(update.message.chat_id)][1]) != 0:
            await update.message.reply_text(
                "Выберите действие",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard_cancel,

                    one_time_keyboard=True,
                ),
            )
            return SAVEMONEYDATA
        elif update.message.text == "Отмена":
            await update.message.reply_text(
                "Отмена отправки",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard_main, one_time_keyboard=True),)
            return ACTION
        else:
            reply_keyboard = [["Продолжить"]]
            await update.message.reply_text(
                "Это не файл. Загрузите файл",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            return TTNLINK

# сохранение данных заявки на оплату


async def save_money_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"User {update.message.chat_id} save money data: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.text == "Сохранить данные":
            await update.message.reply_text(
                "Данные обрабатываются. Пожалуйста, подождите...",
            )
            for attempt in [0, 1, 2]:
                try:
                    range = "Оплаты!B1:B"
                    response = (
                        service.spreadsheets()
                        .values()
                        .get(spreadsheetId=spreadsheet_id, range=range)
                        .execute()
                    )
                    id_last = response["values"][-1]
                    if id_last[0] == "id":
                        id = "2-1"
                    else:
                        number_last = int(id_last[0].split("-")[1])
                        id_number = number_last + 1
                    id = "2-" + str(id_number)
                    data_money[str(update.message.chat_id)][1] = id
                    data_money[str(update.message.chat_id)].append("Нет")
                    data_money[str(update.message.chat_id)].append("Нет")
                    folder_dict = search_for_value_dict("Папки!A:H", data_money[str(
                        update.message.chat_id)][2], [0, 1, 2, 3, 4, 5, 6, 7])
                    folder_link = save_money_files(
                        folder_dict, data_files[str(update.message.chat_id)])
                    data_money[str(update.message.chat_id)][7] = folder_link
                    body = {"values": [
                        data_money[str(update.message.chat_id)]]}
                    resp = (
                        service.spreadsheets()
                        .values()
                        .append(
                            spreadsheetId=spreadsheet_id,
                            range="Оплаты!A1",
                            valueInputOption="RAW",
                            body=body,
                        )
                        .execute()
                    )
                    break
                except:
                    pass

            for file in data_files[str(update.message.chat_id)][0]:
                try:
                    os.remove(file)
                except:
                    pass
            for file in data_files[str(update.message.chat_id)][1]:
                try:
                    os.remove(file)
                except:
                    pass
            await update.message.reply_text(
                "Спасибо! Данные отправлены. Внутренний номер - " +
                data_money[str(update.message.chat_id)][1] +
                ". Ожидайте обратной связи",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard_main, one_time_keyboard=True),
            )
            return ACTION
        elif update.message.text == "Отмена":
            await update.message.reply_text(
                "Вы уверены, что хотите отменить ввод данных?",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard_warning, one_time_keyboard=True),)
            return SAVEMONEYDATA

        elif update.message.text == "Да, хочу внести данные заново":

            await update.message.reply_text(
                "Отмена отправки",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard_main, one_time_keyboard=True),)
            return ACTION

# ЗАКАЗ
# ввод кода откуда заявка


async def get_type_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    elif update.message.text == "Новый" or update.message.text == "Переподписание":
        reply_keyboard = [["От перевозчика"], ["От экспедитора"], [
            "Подбор менеджера"], ["Не установлено"]]
        await update.message.reply_text(
            "Откуда заявка",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        data_order[str(update.message.chat_id)].append(update.message.text)
        return WHEREFROM
    else:
        reply_keyboard = [["Новый", "Переподписание"]]
        await update.message.reply_text(
            "Необходимо выбрать действие из меню",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        return TYPEORDER
# ввод договор цессии


async def get_order_from(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    elif update.message.text == "От перевозчика" or update.message.text == "От экспедитора" or update.message.text == "Подбор менеджера" or update.message.text == "Не установлено":
        reply_keyboard = [["Да", "Нет"]]
        await update.message.reply_text(
            "Договор цессии",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        data_order[str(update.message.chat_id)].append(update.message.text)
        return TYPEAGREE
    else:
        reply_keyboard = [["От перевозчика", "От экспедитора",
                           "Подбор менеджера", "Не установлено"]]
        await update.message.reply_text(
            "Необходимо выбрать действие из меню",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        return WHEREFROM
# ввод наша организация


async def get_type_agree(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    elif update.message.text == "Да" or update.message.text == "Нет":
        reply_keyboard = [[]]
        org_list = search_list("Организации!A:A")
        for item in org_list:
            reply_keyboard[0].append(item[0])
        await update.message.reply_text(
            "Выберите нашу организацию для заказчика",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        data_order[str(update.message.chat_id)].append(update.message.text)
        return GETORGANIZATION
    else:
        reply_keyboard = [["Да", "Нет"]]
        await update.message.reply_text(
            "Необходимо выбрать действие из меню",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        return TYPEAGREE
# ввод ИНН гаранта


async def get_organization(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        org_list = search_list("Организации!A:A")
        for item in org_list:
            if update.message.text == item[0]:
                reply_keyboard = [["Продолжить"]]
                await update.message.reply_text(
                    "Введите ИНН гаранта или нажмите 'Продолжить'",
                    reply_markup=ReplyKeyboardMarkup(
                        reply_keyboard, one_time_keyboard=True),
                )
                data_order[str(update.message.chat_id)].append(
                    update.message.text)
                return INNGARANT
        else:
            reply_keyboard = [[]]
            org_list = search_list("Организации!A:A")
            for item in org_list:
                reply_keyboard[0].append(item[0])
            await update.message.reply_text(
                "Необходимо выбрать нашу организацию для заказчика",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            return GETORGANIZATION
# ввод АТИ гаранта


async def get_inn_garant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.text == 'Продолжить':
            reply_keyboard = [["Продолжить"]]
            await update.message.reply_text(
                "Введите код ATI гаранта или нажмите 'Продолжить'",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            data_order[str(update.message.chat_id)].append('')
            return ATIGARANT
        elif update.message.text.isdigit() and (len(update.message.text) == 10 or len(update.message.text) == 12):
            reply_keyboard = [["Продолжить"]]
            await update.message.reply_text(
                "Введите код ATI гаранта или нажмите 'Продолжить'",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            data_order[str(update.message.chat_id)].append(
                'update.message.text')
            return ATIGARANT
        else:
            reply_keyboard = [["Продолжить"]]
            await update.message.reply_text(
                "Некорректный ввод. ИНН должен состоять из 10 или 12 цифр. Введите ИНН гаранта или нажмите 'Продолжить'",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            return INNGARANT
# ввод код АТИ гаранта


async def get_ati_garant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.text.isdigit():
            await update.message.reply_text(
                "Введите ИНН заказчика",
                reply_markup=ReplyKeyboardRemove(),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return INNCUSTOMER
        elif update.message.text == 'Продолжить':
            await update.message.reply_text(
                "Введите ИНН заказчика",
                reply_markup=ReplyKeyboardRemove(),
            )
            data_order[str(update.message.chat_id)].append('')
            return INNCUSTOMER
        else:
            reply_keyboard = [["Продолжить"]]
            await update.message.reply_text(
                "Введенный код должен состоять только из цифр. Введите код ATI гаранта или нажмите 'Продолжить'",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            return ATIGARANT
# ввод ИНН заказчика


async def get_inn_customer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get ati customer: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.text.isdigit() and (len(update.message.text) == 10 or len(update.message.text) == 12):
            await update.message.reply_text(
                "Введите код ATI заказчика",
                reply_markup=ReplyKeyboardRemove(),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return ATICUSTOMER
        else:
            await update.message.reply_text(
                "Некорректный ввод. ИНН должен состоять из 10 или 12 цифр.. Введите ИНН заказчика",
                reply_markup=ReplyKeyboardRemove(),
            )
            return INNCUSTOMER
# ввод кода ATI заказчика


async def get_ati_customer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get ati customer: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.text.isdigit():
            await update.message.reply_text(
                "Введите email заказчика",
                reply_markup=ReplyKeyboardRemove(),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return EMAILCUSTOMER
        else:
            await update.message.reply_text(
                "Введенный код должен состоять только из цифр. Введите код ATI заказчика",
                reply_markup=ReplyKeyboardRemove(),
            )
            return ATICUSTOMER


# ввод телефона заказчика
async def get_email_customer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get email customer: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        result = re.fullmatch(
            r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', update.message.text)
        if bool(result) == True:
            await update.message.reply_text(
                "Введите телефон заказчика по образцу +7XXXXXXXXXX",
                reply_markup=ReplyKeyboardRemove(),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return PHONECUSTOMER
        else:
            await update.message.reply_text(
                "Некорректный ввод. Введите email заказчика",
                reply_markup=ReplyKeyboardRemove(),
            )
            return EMAILCUSTOMER

# ввод кода почтового адреса заказчика


async def get_phone_customer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get phone customer: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        result = re.match(
            r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', update.message.text)
        if bool(result) == True:
            await update.message.reply_text(
                "Введите почтовый адрес заказчика",
                reply_markup=ReplyKeyboardRemove(),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return ADDRESSCUSTOMER
        else:
            await update.message.reply_text(
                "Введенный номер не соответствует образцу +7XXXXXXXXXX",
                reply_markup=ReplyKeyboardRemove(),
            )
            return PHONECUSTOMER

# загрузка заявки неподписанной


async def get_address_customer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get address customer: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        result = re.match(r'[0-9]+(?:[,])?+\s+\D', update.message.text)
        if bool(result) == True:
            reply_keyboard = [["Продолжить"]]
            await update.message.reply_text(
                "Загрузите заявку (не подписанную). После загрузки всех файлов нажмите 'Продолжить'",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return FOLDERLINK
        else:
            await update.message.reply_text(
                "Почтовый адрес не соответствует образцу 'индекс адрес'. Введите почтовый адрес заказчика",
                reply_markup=ReplyKeyboardRemove(),
            )
        return ADDRESSCUSTOMER
# загрузка подтверждающих документов
# запись заявки на google drive


async def get_folderlink(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get folder link: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.document:
            file = await context.bot.getFile(update.message.document.file_id)
            await file.download_to_drive(update.message.document.file_name)
            doc = update.message.document
            file_name = doc.file_name
            data_files[str(update.message.chat_id)][0].append(file_name)
            if len(data_order[str(update.message.chat_id)]) < 15:
                data_order[str(update.message.chat_id)].append("")
            return FOLDERLINK
        elif update.message.photo:
            file = await context.bot.getFile(update.message.photo[len(update.message.photo)-1].file_id)
            file_name = update.message.photo[len(
                update.message.photo)-1].file_id+".jpg"
            await file.download_to_drive(file_name)
            data_files[str(update.message.chat_id)][0].append(file_name)
            if len(data_order[str(update.message.chat_id)]) < 15:
                data_order[str(update.message.chat_id)].append("")
            return FOLDERLINK
        elif update.message.text == "Продолжить" and len(data_order[str(update.message.chat_id)]) == 15:
            reply_keyboard = [["Продолжить"]]
            await update.message.reply_text(
                "Загрузите подтверждающие документы к заявке. После загрузки всех файлов нажмите 'Продолжить'",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            return FOLDERDOCS
        else:
            reply_keyboard = [["Продолжить"]]
            await update.message.reply_text(
                "Это не файл. Загрузите файл",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            return FOLDERLINK

# запись подтверждающих документов на google drive


async def get_folder_docs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get folder docs: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.document:
            file = await context.bot.getFile(update.message.document.file_id)
            await file.download_to_drive(update.message.document.file_name)
            doc = update.message.document
            file_name = doc.file_name
            data_files[str(update.message.chat_id)][1].append(file_name)
            return FOLDERDOCS
        elif update.message.photo:
            file = await context.bot.getFile(update.message.photo[len(update.message.photo)-1].file_id)
            file_name = update.message.photo[len(
                update.message.photo)-1].file_id+".jpg"
            await file.download_to_drive(file_name)
            data_files[str(update.message.chat_id)][1].append(file_name)
            return FOLDERDOCS
        elif update.message.text == "Продолжить":
            if len(data_folders) == 3:
                data_folders[str(update.message.chat_id)].append("")
            await update.message.reply_text(
                "Введите код ATI перевозчика",
                reply_markup=ReplyKeyboardRemove(),
            )
            return ATICARRIER
        else:
            reply_keyboard = [["Продолжить"]]
            await update.message.reply_text(
                "Это не файл. Загрузите файл",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            return FOLDERDOCS

# ввод ФИО водителя


async def get_ati_carrier(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get ati carrier: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.text.isdigit():
            await update.message.reply_text(
                "Введите ФИО Водителя",
                reply_markup=ReplyKeyboardRemove(),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return FIODRIVER
        else:
            await update.message.reply_text(
                "Введенный код должен состоять только из цифр. Введите код ATI перевозчик",
                reply_markup=ReplyKeyboardRemove(),
            )
        return ATICARRIER


# ввод Гос.номер Авто/Тягача
async def get_fio_driver(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get fio driver: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:

        result = re.fullmatch(
            r'[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?', update.message.text)
        if bool(result) == True:
            await update.message.reply_text(
                "Введите Гос.номер Авто/Тягача",
                reply_markup=ReplyKeyboardRemove(),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return NUMBERAUTO
        else:
            await update.message.reply_text(
                "ФИО не соответствует образцу 'Фамилия Имя Отчество'. Введите ФИО Водителя",
                reply_markup=ReplyKeyboardRemove(),
            )
            return FIODRIVER


# ввод Гос.номер Прицепа
async def get_number_auto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get number auto: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:

        result = re.match(r'\w', update.message.text)
        if bool(result) == True:
            await update.message.reply_text(
                "Введите Гос.номер Прицепа",
                reply_markup=ReplyKeyboardRemove(),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return NUMBERTRAILER
        else:
            await update.message.reply_text(
                "Введенный номер содержит спецсимволы. Введите Гос.номер Авто/Тягача ",
                reply_markup=ReplyKeyboardRemove(),
            )
            return NUMBERAUTO


# ввод суммы заказчика
async def get_number_trailer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get number trailer: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:

        result = re.match(r'\w', update.message.text)
        if bool(result) == True:
            await update.message.reply_text(
                "Введите сумму заказчика",
                reply_markup=ReplyKeyboardRemove(),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return AMOUNTCUSTOMER
        else:
            await update.message.reply_text(
                "Введенный номер содержит спецсимволы. Введите Гос.номер Авто/Тягача ",
                reply_markup=ReplyKeyboardRemove(),
            )
            return NUMBERTRAILER


# ввод суммы перевозчика
async def get_amount_customer(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    logger.info(f"User {update.message.chat_id} get amount customer: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.text.isdigit():
            await update.message.reply_text(
                "Введите сумму перевозчика",
                reply_markup=ReplyKeyboardRemove(),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return AMOUNTCARRIER
        else:
            await update.message.reply_text(
                "Некорректный ввод. Введите сумму заказчика(только цифры)",
                reply_markup=ReplyKeyboardRemove(),
            )
            return AMOUNTCUSTOMER


# ввод режима налогообложения
async def get_amount_carrier(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get amount carrier: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:

        if update.message.text.isdigit():
            reply_keyboard = [
                ["Без НДС-Без НДС"], ["С НДС-Без НДС"], ["Без НДС-С НДС"], ["С НДС-С НДС"]
            ]
            await update.message.reply_text(
                "Выберите режим налогообложения",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return TAXATION
        else:
            await update.message.reply_text(
                "Некорректный ввод. Введите сумму перевозчика(только цифры)",
                reply_markup=ReplyKeyboardRemove(),
            )
            return AMOUNTCARRIER


# ввод адреса загрузки
async def get_taxation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get taxation: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    elif update.message.text == "Без НДС-Без НДС" or update.message.text == "С НДС-Без НДС" or update.message.text == "Без НДС-С НДС" or update.message.text == "С НДС-С НДС":
        await update.message.reply_text(
            "Введите адрес загрузки",
            reply_markup=ReplyKeyboardRemove(),
        )
        data_order[str(update.message.chat_id)].append(update.message.text)
        return ADDRESSLOADING
    else:
        reply_keyboard = [
            ["Без НДС-Без НДС", "С НДС-Без НДС", "Без НДС-С НДС", "С НДС-С НДС"]
        ]
        await update.message.reply_text(
            "Необходимо выбрать действие из меню",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        return TAXATION

# ввод даты отгрузки


async def get_address_loading(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    logger.info(f"User {update.message.chat_id} get address loading: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:

        await update.message.reply_text(
            "Введите планируемую дату отгрузки в формате 'дд.мм.гггг'",
            reply_markup=ReplyKeyboardRemove(),
        )
        data_order[str(update.message.chat_id)].append(update.message.text)
        return DATELOADING

# ввод Термописец


async def get_date_loading(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get date loading: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        try:
            result = datetime.datetime.strptime(
                update.message.text, '%d.%m.%Y')
            reply_keyboard = [["Да", "Нет"]]
            await update.message.reply_text(
                "Термописец",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return THERMOGRAPHER
        except:
            await update.message.reply_text(
                "Да не соответствует формату 'дд.мм.гггг'. Введите планируемую дату отгрузки в формате 'дд.мм.гггг'",
                reply_markup=ReplyKeyboardRemove(),
            )
            return DATELOADING

# ввод Груз свыше 15 млн


async def get_thermographer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get thermographer: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    elif update.message.text == "Да" or update.message.text == "Нет":
        reply_keyboard = [["Да", "Нет"]]
        await update.message.reply_text(
            "Груз свыше 15 млн?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        data_order[str(update.message.chat_id)].append(update.message.text)
        return MORE15
    else:
        reply_keyboard = [["Да", "Нет"]]
        await update.message.reply_text(
            "Необходимо выбрать действие из меню",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        return THERMOGRAPHER

# ввод адреса выгрузки


async def get_more15(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get more15: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    elif update.message.text == "Да" or update.message.text == "Нет":
        await update.message.reply_text(
            "Введите адрес выгрузки",
            reply_markup=ReplyKeyboardRemove(),
        )
        data_order[str(update.message.chat_id)].append(update.message.text)
        return ADDRESSUNLOADING
    else:
        reply_keyboard = [["Да", "Нет"]]
        await update.message.reply_text(
            "Необходимо выбрать действие из меню",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True),
        )
        return MORE15

# ввод ретро бонуса


async def get_adress_unloading(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    logger.info(f"User {update.message.chat_id} get adress unloading: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        await update.message.reply_text(
            "Введите ретро бонус (если нет - введите 0)",
            reply_markup=ReplyKeyboardRemove(),
        )
        data_order[str(update.message.chat_id)].append(update.message.text)
        return RETROBONUS

# предложение ввода комментария к заявке


async def get_retro_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get retro bonus: {
                update.message.text}")
    if update.message.text == "/start" or update.message.text == "старт" or update.message.text == "Cтарт":

        folder_dict["folder"] = ''
        folder_dict["order"] = ''
        folder_dict["order_sign"] = ''
        folder_dict["zerk"] = ''
        folder_dict["zerk_sign"] = ''
        folder_dict["docs"] = ''
        folder_dict["ttn"] = ''
        folder_dict["pp"] = ''
        await update.message.reply_text(
            "Выберите действие из меню. Для возврата в главное меню введите '/start' ",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main),
        )
        return ACTION
    else:
        if update.message.text.isdigit():
            await update.message.reply_text(
                "Добавить комментарий к заявке",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard_yesno,
                    one_time_keyboard=True,
                ),
            )
            data_order[str(update.message.chat_id)].append(update.message.text)
            return COMMENT
        else:
            await update.message.reply_text(
                "Некорректный ввод. Введите ретро бонус (только цифры)",
                reply_markup=ReplyKeyboardRemove(),
            )
            return RETROBONUS


# ввод комментария к заявке
async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get comment: {
                update.message.text}")
    if update.message.text == "Да":
        await update.message.reply_text(
            "Добавьте комментарий к заявке",
            reply_markup=ReplyKeyboardRemove()
        ),
        return FINALACTION
    elif update.message.text == "Нет":
        await update.message.reply_text(
            "Выберите действие из меню",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard_cancel,
                one_time_keyboard=True,
            ),
        )
        data_order[str(update.message.chat_id)].append(update.message.text)
        return SAVEDATA
    else:
        await update.message.reply_text(
            "Добавить комментарий к заявке",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard_yesno,
                one_time_keyboard=True,
            ),
        )
        return COMMENT

# предложение о сохранении данных


async def get_final_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"User {update.message.chat_id} get final action: {
                update.message.text}")
    await update.message.reply_text(
        "Выберите действие из меню",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard_cancel,
            one_time_keyboard=True,
        ),
    )
    data_order[str(update.message.chat_id)].append(update.message.text)
    return SAVEDATA

# сохранение данных заказа, создание папок для заявок на оплату


async def save_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"User {update.message.chat_id} save data: {
                update.message.text}")
    if update.message.text == "Сохранить данные":
        await update.message.reply_text(
            "Данные обрабатываются. Пожалуйста, подождите...",
        )
        for attempt in [0, 1, 2]:
            try:
                range = "Заказы!B1:B"
                response = (
                    service.spreadsheets()
                    .values()
                    .get(spreadsheetId=spreadsheet_id, range=range)
                    .execute()
                )
                id_last = response["values"][-1]
                if id_last[0] == "id":
                    id = "1-1"
                else:
                    number_last = int(id_last[0].split("-")[1])
                    id_number = number_last + 1
                    id = "1-" + str(id_number)
                data_order[str(update.message.chat_id)][1] = id
                folder_link = save_order_files(
                    str(update.message.chat_id), data_files, data_folders, id)
                data_order[str(update.message.chat_id)][14] = folder_link
                body_folders = {"values": [
                    data_folders[str(update.message.chat_id)]]}
                data_order[str(update.message.chat_id)].append("Нет")
                data_order[str(update.message.chat_id)].append("Нет")

                body = {"values": [data_order[str(update.message.chat_id)]]}
                resp = (
                    service.spreadsheets()
                    .values()
                    .append(
                        spreadsheetId=spreadsheet_id,
                        range="Заказы!A1",
                        valueInputOption="RAW",
                        body=body,
                    )
                    .execute()
                )

                resp = (
                    service.spreadsheets()
                    .values()
                    .append(
                        spreadsheetId=spreadsheet_id,
                        range="Папки!A1",
                        valueInputOption="RAW",
                        body=body_folders,
                    )
                    .execute()
                )
                break
            except:
                pass

        for file in data_files[str(update.message.chat_id)][0]:
            try:
                os.remove(file)
            except:
                pass
        for file in data_files[str(update.message.chat_id)][1]:
            try:
                os.remove(file)
            except:
                pass
        await update.message.reply_text(
            "Спасибо! Данные записаны. Внутренний номер - " +
            data_order[str(update.message.chat_id)][1],
            # await update.effective_message.reply_text(text),
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard_main, one_time_keyboard=True),
        )
        return ACTION
    elif update.message.text == "Отмена":
        await update.message.reply_text(
            "Вы уверены, что хотите отменить ввод данных?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_warning, one_time_keyboard=True),)
        return SAVEDATA

    elif update.message.text == "Да, хочу внести данные заново":
        await update.message.reply_text(
            "Отмена отправки",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard_main, one_time_keyboard=True),)
        return ACTION
    else:
        data_order.append(update.message.text)
        await update.message.reply_text(
            "Необходимо выбрать действие из меню",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard_cancel,
                one_time_keyboard=True,
            ),
        )
    return SAVEDATA

# завершение разговора


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"{query.data}")

# получает на вход диапазон ячеек, ключевое слово для поиска и номер столбца для возврата; возвращает массив значенийб удовлетворяющий критериям поиска


def search_for_value(range, keyword, pos):
    result_list = list()
    response = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range)
        .execute()["values"]
    )
    for item in response:
        if item[0] == keyword:
            result_list.append(item[pos])
    return result_list

# получает на вход диапазон ячеек, возвращает массив значений


def search_list(range):
    response = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range)
        .execute()["values"]
    )
    return response

# получает на вход диапазон ячеек, ключевое слово для поиска, список статусов, список колонок для возврата
# ищет заказы/заявки с необходимыми статусами, id необходимых папок документов
# проверяет наличие соответствующих записей уведомлений
# возвращает словарь для рассылки уведомлений


def search_for_alarm(range, keyword, status_list, range_list):

    result_dict = dict()
    result_dict_orders = dict()
    response = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range)
        .execute()["values"]
    )
    for item in response:
        if item[range_list[0]] == keyword:

            if item[range_list[2]] in status_list:
                range = "Папки!A:I"
                response = (
                    service.spreadsheets()
                    .values()
                    .get(spreadsheetId=spreadsheet_id, range=range)
                    .execute()["values"])
                for item1 in response:
                    if item1[0] == item[range_list[1]] or item1[0] == item[range_list[4]]:
                        result_dict_orders[item[range_list[1]]] = [
                            item[range_list[2]], item[range_list[3]], item[range_list[4]], item[range_list[5]], item1[4], item1[5], item1[8]]

    if result_dict_orders != {}:
        range = "Уведомления!A:J"
        response = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range)
            .execute()["values"]
        )
        for key, value in result_dict_orders.items():
            search_list = response[1:]
            if [keyword, key, value[0], value[1], value[4], value[5], value[6]] not in search_list:
                result_dict[key] = [value[0], value[1], value[2],
                                    value[3], value[4], value[5], value[6]]
    return result_dict

# получает на вход диапазон ячеек, ключевое слово для поиска, список колонок для возврата
# возвращает словарь с Id папок


def search_for_value_dict(range, keyword, range_list):
    result_dict = dict()
    response = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range)
        .execute()["values"]
    )
    for item in response:
        if item[range_list[0]] == keyword:
            result_dict["folder"] = item[range_list[1]]
            result_dict["order"] = item[range_list[2]]
            result_dict["docs"] = item[range_list[3]]
            result_dict["order"] = item[range_list[4]]
            result_dict["zerk"] = item[range_list[5]]
            result_dict["zerk_sign"] = item[range_list[6]]
            result_dict["ttn"] = item[range_list[7]]
            return result_dict

# сохранение файла в google drive


def save_file(file_name, name_folder, name_folder_orders, type_folder, folder_dict):
    if folder_dict["folder"] == "":
        folder_metadata = {
            "name": name_folder,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [folder_id],
        }
        folder = servicefile.files().create(body=folder_metadata, fields="id").execute()
        id_folder = folder.get("id")
        folder_dict['folder'] = id_folder
    else:
        id_folder = folder_dict["folder"]
    if folder_dict[type_folder] == "":
        folder_metadata_order = {
            "name": name_folder_orders,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [id_folder],
        }
        folder_order = (
            servicefile.files()
            .create(body=folder_metadata_order, fields="id")
            .execute()
        )
        id_folder_order = folder_order.get("id")
        folder_dict[type_folder] = id_folder_order
    else:
        id_folder_order = folder_dict[type_folder]
    if file_name != "":
        file_metadata = {"name": file_name, "parents": [id_folder_order]}
        file_order_media = MediaFileUpload(file_name, resumable=True)
        file_order = (
            servicefile.files()
            .create(body=file_metadata, media_body=file_order_media, fields="id")
            .execute()
        )

    return [id_folder, id_folder_order]

# сохранение файлов заказа в google drive


def save_order_files(id, files, folders, num):
    folders[id].append(num)

    folder_metadata = {
        "name": id+"_"+num,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [folder_id],
    }
    folder = servicefile.files().create(body=folder_metadata, fields="id").execute()
    id_folder_main = folder.get("id")
    result = "https://drive.google.com/drive/folders/"+id_folder_main
    folders[id].append(id_folder_main)

    folder_metadata = {
        "name": "Заявка неподписанная",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [id_folder_main],
    }
    folder = servicefile.files().create(body=folder_metadata, fields="id").execute()
    id_folder = folder.get("id")
    folders[id].append(id_folder)
    for file in files[id][0]:
        file_metadata = {"name": file, "parents": [id_folder]}
        file_order_media = MediaFileUpload(file, resumable=True)
        file_order = (
            servicefile.files()
            .create(body=file_metadata, media_body=file_order_media, fields="id")
            .execute()
        )

    if len(files[id][1]) != 0:
        folder_metadata = {
            "name": "Подтверждающие документы",
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [id_folder_main],
        }
        folder = servicefile.files().create(body=folder_metadata, fields="id").execute()
        id_folder = folder.get("id")
        folders[id].append(id_folder)
        for file in files[id][1]:
            file_metadata = {"name": file, "parents": [id_folder]}
            file_order_media = MediaFileUpload(file, resumable=True)
            file_order = (
                servicefile.files()
                .create(body=file_metadata, media_body=file_order_media, fields="id")
                .execute()
            )

    else:
        folders[id].append("")
    folder_metadata = {
        "name": "Заявка подписанная",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [id_folder_main],
    }
    folder = servicefile.files().create(body=folder_metadata, fields="id").execute()
    folders[id].append(folder.get("id"))

    folder_metadata = {
        "name": "Зеркалка неподписанная",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [id_folder_main],
    }
    folder = servicefile.files().create(body=folder_metadata, fields="id").execute()
    folders[id].append(folder.get("id"))

    folder_metadata = {
        "name": "Зеркалка подписанная",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [id_folder_main],
    }
    folder = servicefile.files().create(body=folder_metadata, fields="id").execute()
    folders[id].append(folder.get("id"))

    folder_metadata = {
        "name": "ТТН",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [id_folder_main],
    }
    folder = servicefile.files().create(body=folder_metadata, fields="id").execute()
    folders[id].append(folder.get("id"))

    folder_metadata = {
        "name": "Платежные поручения",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [id_folder_main],
    }
    folder = servicefile.files().create(body=folder_metadata, fields="id").execute()
    folders[id].append(folder.get("id"))
    return result


def save_money_files(folder_dict, files):

    for file in files[0]:
        file_metadata = {"name": file, "parents": [folder_dict['zerk_sign']]}
        file_order_media = MediaFileUpload(file, resumable=True)
        file_order = (
            servicefile.files()
            .create(body=file_metadata, media_body=file_order_media, fields="id")
            .execute()
        )
    for file in files[1]:
        file_metadata = {"name": file, "parents": [folder_dict['ttn']]}
        file_order_media = MediaFileUpload(file, resumable=True)
        file_order = (
            servicefile.files()
            .create(body=file_metadata, media_body=file_order_media, fields="id")
            .execute()
        )
    result = "https://drive.google.com/drive/folders/"+folder_dict['folder']
    return result


def main() -> None:
    application = (
        Application.builder()
        .token("6604497275:AAHF5jHn0Pm4rF8AM2ONpH5PQJIUZFsws90")
        .build()
    )
    application.add_handler(CallbackQueryHandler(button))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIO: [
                MessageHandler(None, get_name),
            ],
            EMAIL: [
                MessageHandler(None, get_email),
            ],
            # EMAIL: [MessageHandler(filters.Regex("^(Создать заказ|Отправить данные)$"), get_email),],
            # ACTION: [MessageHandler(filters.Regex("^(Отправить данные|Отмена)$"), get_action),],
            ACTION: [
                MessageHandler(None, get_action),
            ],
            FINALACTION: [
                MessageHandler(None, get_final_action),
            ],
            SAVEDATA: [
                MessageHandler(None, save_data),
            ],
            TYPEORDER: [
                MessageHandler(None, get_type_order),
            ],
            WHEREFROM: [
                MessageHandler(None, get_order_from),
            ],
            TYPEAGREE: [
                MessageHandler(None, get_type_agree),
            ],
            GETORGANIZATION: [
                MessageHandler(None, get_organization),
            ],
            INNGARANT: [
                MessageHandler(None, get_inn_garant),
            ],
            ATIGARANT: [
                MessageHandler(None, get_ati_garant),
            ],
            INNCUSTOMER: [
                MessageHandler(None, get_inn_customer),
            ],
            ATICUSTOMER: [
                MessageHandler(None, get_ati_customer),
            ],
            EMAILCUSTOMER: [
                MessageHandler(None, get_email_customer),
            ],
            PHONECUSTOMER: [
                MessageHandler(None, get_phone_customer),
            ],
            ADDRESSCUSTOMER: [
                MessageHandler(None, get_address_customer),
            ],
            FOLDERLINK: [
                MessageHandler(None, get_folderlink),
            ],
            ATICARRIER: [
                MessageHandler(None, get_ati_carrier),
            ],
            FIODRIVER: [
                MessageHandler(None, get_fio_driver),
            ],
            NUMBERAUTO: [
                MessageHandler(None, get_number_auto),
            ],
            NUMBERTRAILER: [
                MessageHandler(None, get_number_trailer),
            ],
            AMOUNTCUSTOMER: [
                MessageHandler(None, get_amount_customer),
            ],
            AMOUNTCARRIER: [
                MessageHandler(None, get_amount_carrier),
            ],
            TAXATION: [
                MessageHandler(None, get_taxation),
            ],
            ADDRESSLOADING: [
                MessageHandler(None, get_address_loading),
            ],
            DATELOADING: [
                MessageHandler(None, get_date_loading),
            ],
            THERMOGRAPHER: [
                MessageHandler(None, get_thermographer),
            ],
            MORE15: [
                MessageHandler(None, get_more15),
            ],
            ADDRESSUNLOADING: [
                MessageHandler(None, get_adress_unloading),
            ],
            RETROBONUS: [
                MessageHandler(None, get_retro_bonus),
            ],
            GETORDER: [
                MessageHandler(None, get_order),
            ],
            TYPEMONEY: [
                MessageHandler(None, get_type_money),
            ],
            MONEYAMOUNT: [
                MessageHandler(None, get_money_amount),
            ],
            MONEYDETAILS: [
                MessageHandler(None, get_money_details),
            ],
            MONEYLINK: [
                MessageHandler(None, get_money_link),
            ],
            TTNLINK: [
                MessageHandler(None, get_ttn_link),
            ],
            SAVEMONEYDATA: [
                MessageHandler(None, save_money_data),
            ],
            FOLDERDOCS: [
                MessageHandler(None, get_folder_docs),
            ],
            STARTOVER: [
                MessageHandler(None, start_over),
            ],
            SAVEUSER: [
                MessageHandler(None, save_user),
            ],
            COMMENT: [
                MessageHandler(None, get_comment),
            ],
            CANCEL: [
                MessageHandler(None, cancel),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
