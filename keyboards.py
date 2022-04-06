from aiogram import types
from models import MainDB


db = MainDB()

remove = types.ReplyKeyboardRemove()



user_from_btn = types.InlineKeyboardMarkup(row_width=3)
ufb1 = types.InlineKeyboardButton("Yandex", callback_data="yandex")
ufb2 = types.InlineKeyboardButton("Google", callback_data="google")
ufb3 = types.InlineKeyboardButton("Telegram", callback_data="telegram")
ufb4 = types.InlineKeyboardButton("WhatsApp", callback_data="whatsapp")
ufb5 = types.InlineKeyboardButton("Vkontakte", callback_data="vkontakte")
ufb6 = types.InlineKeyboardButton("От друга", callback_data="friend")
user_from_btn.add(ufb1, ufb2, ufb3, ufb4, ufb5, ufb6)


menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.row('📂 Наши услуги', '👤 Профиль')
menu.row('☎️ Обратная связь', '💥Телеграм канал')
# menu.row('📑 Инструкция по боту')


history_back_btn = types.InlineKeyboardMarkup()
history_back_btn.row(types.InlineKeyboardButton('Очистить', callback_data='clear_history'))
history_back_btn.row(types.InlineKeyboardButton('Назад', callback_data='back_to_profile'))


user_profile_btn = types.InlineKeyboardMarkup()
user_profile_btn.row(types.InlineKeyboardButton("💳 Пополнить баланс", callback_data="depozit"))
user_profile_btn.row(types.InlineKeyboardButton("🧰 История заказов", callback_data="myHistory"))


service_products_btn = types.InlineKeyboardMarkup(row_width=2)
me1 = types.InlineKeyboardButton("📑Купить ОСАГО", callback_data="buy_osago")
me2 = types.InlineKeyboardButton("📋Техосмотр", callback_data="buy_dk")
me3 = types.InlineKeyboardButton("📃Мед Справка на права", callback_data="medAuto")
me5 = types.InlineKeyboardButton("🏦КАСКО для банка", callback_data="kaskoBank")
me6 = types.InlineKeyboardButton("🏪Карта учета ГИБДД", callback_data="kartaGibdd")
me7 = types.InlineKeyboardButton("🚓Карта ВУ по базе ГАИ", callback_data="kartaVUgai")
me8 = types.InlineKeyboardButton("🔎Поиск по базе Солярис", callback_data="poiskSolariy")
service_products_btn.add(me1, me2, me3, me5, me6, me7, me8)



admin_panel_btn = types.InlineKeyboardMarkup()
admin_panel_btn.row(types.InlineKeyboardButton('💵 Изменить цены', callback_data='change_prices'), types.InlineKeyboardButton('🔑 Изменить Qiwi данные', callback_data='change_qiwi_configs'))
admin_panel_btn.row(types.InlineKeyboardButton('📮 Рассылка юзерам', callback_data='sending_all'), types.InlineKeyboardButton('👥 Список админов', callback_data='all_admins'))



back_btn = types.InlineKeyboardButton("🔙 Назад", callback_data="back")

cencel_btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
cencel_btn.row("❌ Отменить")



buy_osago_btn = types.InlineKeyboardMarkup(row_width=1)
buy_osago_btn1 = types.InlineKeyboardButton(f"Е-осаго на 1 ГОД | {db.getProductsInfo(rowid=1)[1]} RUB", callback_data="buy_osago_year")
buy_osago_btn2 = types.InlineKeyboardButton(f"Е-осаго на 3 МЕС | {db.getProductsInfo(rowid=2)[1]} RUB", callback_data="buy_osago_month")
buy_osago_btn3 = types.InlineKeyboardButton(f"Е-осаго БЕЗ БАЗЫ | {db.getProductsInfo(rowid=3)[1]} RUB", callback_data="buy_osago_nodb")
buy_osago_btn.add(buy_osago_btn1, buy_osago_btn2, buy_osago_btn3, back_btn)


buy_Dk = types.InlineKeyboardMarkup(row_width=1)
bd2 = types.InlineKeyboardButton(f"Диагностическая карта без базы 1 ГОД | {db.getProductsInfo(rowid=5)[1]} RUB", callback_data="buy_texosmotr_no_db")
bd3 = types.InlineKeyboardButton(f"Диагностическая карта B | {db.getProductsInfo(rowid=6)[1]} RUB", callback_data="buy_texosmotr_b")
bd4 = types.InlineKeyboardButton(f"Диагностическая карта C | {db.getProductsInfo(rowid=7)[1]} RUB", callback_data="buy_texosmotr_c")
buy_Dk.add(bd2, bd3, bd4, back_btn)





med_auto_btn = types.InlineKeyboardMarkup(row_width=1)
med_auto_btn.row(types.InlineKeyboardButton(f'Купить Мед Справку на права | {db.getProductsInfo(rowid=9)[1]} RUB', callback_data='buy_med_auto'))
med_auto_btn.add(back_btn)


kasko_bank_btn = types.InlineKeyboardMarkup(row_width=1)
kasko_bank_btn.row(types.InlineKeyboardButton(f'Купить КАСКО {db.getProductsInfo(rowid=8)[1]} RUB', callback_data='buy_kasko_bank'))
kasko_bank_btn.add(back_btn)


karta_gibdd_btn = types.InlineKeyboardMarkup(row_width=1)
karta_gibdd_btn.row(types.InlineKeyboardButton(f'Купить Карта учета ГИБДД {db.getProductsInfo(rowid=10)[1]} RUB', callback_data='buy_karta_gibdd'))
karta_gibdd_btn.add(back_btn)


karta_vu_gai_btn = types.InlineKeyboardMarkup(row_width=1)
karta_vu_gai_btn.row(types.InlineKeyboardButton(f'Купить ВУ по базе ГАИ {db.getProductsInfo(rowid=11)[1]} RUB', callback_data='buy_karta_vu_gai'))
karta_vu_gai_btn.add(back_btn)


poisk_solariy_btn = types.InlineKeyboardMarkup(row_width=1)
poisk_solariy_btn.row(types.InlineKeyboardButton(f'Купить Поиск по базе Солярис {db.getProductsInfo(rowid=12)[1]} RUB', callback_data='buy_poisk_solariy'))
poisk_solariy_btn.add(back_btn)



pay_btn = types.InlineKeyboardMarkup()



send_order_btn = types.InlineKeyboardMarkup(row_width=1)




change_service_products_btn = types.InlineKeyboardMarkup(row_width=1)
chsp1 = types.InlineKeyboardButton(f"Е-осаго на 1 ГОД | {db.getProductsInfo(rowid=1)[1]} RUB", callback_data="change_1")
chsp2 = types.InlineKeyboardButton(f"Е-осаго на 3 МЕС | {db.getProductsInfo(rowid=2)[1]} RUB", callback_data="change_2")
chsp3 = types.InlineKeyboardButton(f"Е-осаго БЕЗ БАЗЫ | {db.getProductsInfo(rowid=3)[1]} RUB", callback_data="change_3")
chsp6 = types.InlineKeyboardButton(f"Диагностическая карта без базы 1 ГОД | {db.getProductsInfo(rowid=5)[1]} RUB", callback_data="change_5")
chsp7 = types.InlineKeyboardButton(f"Диагностическая карта B | {db.getProductsInfo(rowid=6)[1]} RUB", callback_data="change_6")
chsp8 = types.InlineKeyboardButton(f"Диагностическая карта C | {db.getProductsInfo(rowid=7)[1]} RUB", callback_data="change_7")
chsp9 = types.InlineKeyboardButton(f'Купить Мед Справку на права | {db.getProductsInfo(rowid=9)[1]} RUB', callback_data='change_8')
chsp10 = types.InlineKeyboardButton(f'Купить КАСКО {db.getProductsInfo(rowid=8)[1]} RUB', callback_data='change_9')
chsp11 = types.InlineKeyboardButton(f'Купить Карта учета ГИБДД {db.getProductsInfo(rowid=10)[1]} RUB', callback_data='change_10')
chsp12 = types.InlineKeyboardButton(f'Купить ВУ по базе ГАИ {db.getProductsInfo(rowid=11)[1]} RUB', callback_data='change_11')
chsp13 = types.InlineKeyboardButton(f'Купить Поиск по базе Солярис {db.getProductsInfo(rowid=12)[1]} RUB', callback_data='change_12')
change_service_products_btn.add(chsp1, chsp2, chsp3, chsp6, chsp7, chsp8, chsp9, chsp10, chsp11, chsp12, chsp13)
change_service_products_btn.row(types.InlineKeyboardButton('🔙 Назад', callback_data='back_to_admin_panel'))




