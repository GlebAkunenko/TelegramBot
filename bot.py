from telegram import *
from telegram.ext import Updater, Filters, CallbackContext, MessageHandler, CallbackQueryHandler
from telegramcalendar import create_calendar, process_calendar_selection
from threading import Thread
from random import choice, randint
import json, time, os

config = json.loads(open('data.json', 'r', encoding='utf-8').read())
lottery = json.loads(open('lottery.json', 'r', encoding='utf-8').read())

start_keyboard = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text='Сделать заказ')],
		[KeyboardButton(text='Диалог'), KeyboardButton(text='Случайное слово')]
	],
	resize_keyboard=True
	)

price_list = []
new_list = [ [InlineKeyboardButton(text="Товар" + str(i), callback_data="ORD.prod."+str(i))] for i in range(1, 6) ]
new_list.append([InlineKeyboardButton(text='>', callback_data="ORD.to.2")])
price_list.append(InlineKeyboardMarkup(inline_keyboard=new_list))

new_list = [ [InlineKeyboardButton(text="Товар" + str(i), callback_data="ORD.prod."+str(i))] for i in range(6, 11) ]
new_list.append([InlineKeyboardButton(text='<', callback_data="ORD.to.1"), InlineKeyboardButton(text='>', callback_data="ORD.to.3")])
price_list.append(InlineKeyboardMarkup(inline_keyboard=new_list))

new_list = [ [InlineKeyboardButton(text="Товар" + str(i), callback_data="ORD.prod."+str(i))] for i in range(11, 16) ]
new_list.append([InlineKeyboardButton(text='<', callback_data="ORD.to.2")])
price_list.append(InlineKeyboardMarkup(inline_keyboard=new_list))

FAQ_keyboard = InlineKeyboardMarkup(
	inline_keyboard=[
		[InlineKeyboardButton(text='Опробовать', callback_data="FAQ.start")]
		]
	)


yn_keyboard = InlineKeyboardMarkup(
	[[InlineKeyboardButton(text='Подтвердить', callback_data='Y/N.Y')], [InlineKeyboardButton(text='Отмена', callback_data='Y/N.N')]]
	)

def find(string, tags):
    """ Функция возвращающая True, если в string найдётся tag """
    ret = False
    for tag in tags:
        if string.lower().count(tag) != 0:
            ret = True
    return ret

def random_word(chat_id, about):
	global score, lottery
	lottery = json.loads(open('lottery.json', 'r', encoding='utf-8').read())
	local_bot = Bot(token=token)
	moon = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']
	message = local_bot.send_message(chat_id, text='Ищем рандомное слово ' + moon[0])
	for i in range(1, randint(15, 25)):
		local_bot.edit_message_text(chat_id=chat_id, message_id=message.message_id,
			text='Ищем рандомное слово ' + moon[i%8])
		time.sleep(0.2)
	word = choice(lottery['word'])
	local_bot.edit_message_text(chat_id=chat_id,message_id=message.message_id,
	 text='🌚 '+word+ ' 🌝')
	if not about:
		time.sleep(3)
		local_bot.send_message(chat_id, text="Разработчик:\nПризнаюсь честно эту функцию я добавил только потому что мне очень нравится эта анимация вращения луны)\nНу, блин, она такая классная!")

def get_confirmation_keyboard(yes_callback, no_callback):
	return InlineKeyboardMarkup([[InlineKeyboardButton(text='Подтвердить', callback_data=yes_callback)],
	 [InlineKeyboardButton(text='Отмена', callback_data=no_callback)]])

def get_cancel_keyboard(callback):
	return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отмена', callback_data=callback)]])

users_data = {}

def message_handler(update: Update, context: CallbackContext):
	text = update.message.text
	chat_id = update.message.chat.id
	if not users_data.get(chat_id):
		users_data[chat_id] = {'state': "", 'list': 1, 'rand_info': False}

	if text:

		if users_data[chat_id]['state'] == 'FAQ':

			if find(text, config['okey']) or text.lower() == 'отмена' or text.lower() == 'назад':
				update.message.reply_text(text="Продолжим", reply_markup=start_keyboard)
				users_data[chat_id]['state'] = ""
				return

			for question in config['questions']:
				if find(text, question['tags']):
					update.message.reply_text(text=question['answer'])
					return
			update.message.reply_text(text=config['spech']['i_dont_know'])
			return


		if text == '/start' or text == '/help':
			update.message.reply_text(text=config['spech']['start'], reply_markup=start_keyboard)
			return

		if text == "Диалог":
			update.message.reply_text(text=config['spech']['asking_questions1'], reply_markup=FAQ_keyboard)
			return

		if text == "Сделать заказ":
			keyboard = price_list[0]
			update.message.reply_text(text="Выберите товар", reply_markup=price_list[0])

		if text == "Случайное слово":
			r = Thread(target=random_word, args=[chat_id, users_data[chat_id]['rand_info']])
			r.run()
			users_data[chat_id]['rand_info'] = True
			return



def callback_query_handler(update: Update, context: CallbackContext):
	data_type = update.callback_query.data[:3]
	chat_id = update.callback_query.from_user.id
	callback_query_id = update.callback_query.id
	if not users_data.get(chat_id):
		users_data[chat_id] = {'state': "", 'list': 1, 'rand_info': False}

	if data_type == 'ORD':
		data = update.callback_query.data[4:]
		data = data.split('.')

		if data[0] == 'to':
			bot.edit_message_text(chat_id=chat_id, message_id=update.callback_query.message.message_id,
				text="Выберите товар", reply_markup=price_list[int(data[1])-1])
			users_data[chat_id]['list'] = int(data[1])

		if data[0] == 'prod':
			bot.edit_message_text(chat_id=chat_id, message_id=update.callback_query.message.message_id,
				text="Вы выбрали товар {}\n\nЭто такой-то такой-то товар, делает он то-то то-то, стоит солько-то солько-то\nПодтвердить покупку?".format(data[1]),
				 reply_markup=get_confirmation_keyboard('ORD.yes.'+str(data[1]), 'ORD.no.'+str(data[1])))

		if data[0] == 'yes':
			bot.edit_message_text(chat_id=chat_id, message_id=update.callback_query.message.message_id,
				text="Отлично! Теперь определимся с датой. Выберите день, кода вам будет удобно забрать заказ.",
				reply_markup=create_calendar())
		
		if data[0] == 'no':
			bot.edit_message_text(chat_id=chat_id, message_id=update.callback_query.message.message_id,
				text="Выберите товар", reply_markup=price_list[int(users_data[chat_id]['list'])-1])

	elif data_type == 'FAQ':
		data = update.callback_query.data[4:].split('.')

		if data[0] == 'start':
			bot.answer_callback_query(callback_query_id=callback_query_id)
			bot.edit_message_reply_markup(chat_id=chat_id, message_id=update.callback_query.message.message_id)
			bot.send_message(chat_id,
				text=config['spech']['asking_questions2'], reply_markup=ReplyKeyboardRemove())
			bot.send_message(chat_id,
				text=config['spech']['ready_to_questing'], reply_markup=get_cancel_keyboard('FAQ.stop'))
			users_data[chat_id]['state'] = 'FAQ'

		if data[0] == 'stop':
			bot.answer_callback_query(callback_query_id=callback_query_id)
			bot.send_message(chat_id, text='Продолжим', reply_markup=start_keyboard)
			users_data[chat_id]['state'] = ""
			return

	else:
		selected, date = process_calendar_selection(bot, update)
		if selected:
			bot.edit_message_text(chat_id=chat_id, message_id=update.callback_query.message.message_id,
				text="Отлично ваш заказ будет ждать вас %s с 7:00 до 22:00. Вот место, где вы можите его забрать" % (date.strftime("%d/%m/%Y")))
			bot.send_location(chat_id, 55.916224, 37.887642)
			time.sleep(2)
			bot.send_message(chat_id=chat_id,
				text=config['spech']['order_finish'])


token = os.environ.get("TOKEN")

updater = Updater(
	token=token,
	use_context=True
	)

bot = Bot(token=token)

updater.dispatcher.add_handler(MessageHandler(filters=Filters.all ,callback=message_handler))
# updater.dispatcher.add_handler(CallbackQueryHandler(callback=callback_query_handler))
updater.dispatcher.add_handler(CallbackQueryHandler(callback=callback_query_handler))

print("started")
updater.start_polling()
updater.idle()
