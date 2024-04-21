from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    osago_data = State()
    osago_data_photo = State()

    dk_data = State()
    dk_data_photo = State()
    dk_photos = State()

    auto_med = State()
    auto_med_photo = State()

    kasko_bank = State()
    kasko_bank_photo = State()

    karta_gibdd = State()
    karta_gibdd_photo = State()

    karta_vu_gai = State()

    search_solary = State()
    search_solary_photo = State()

    vosstanovlenie_kbm = State()
    vosstanovlenie_kbm_photo = State()

    dogovor_kupli_prodazhi = State()
    dogovor_kupli_prodazhi_photo = State()

    snyatie_ts_s_ucheta = State()
    snyatie_ts_s_ucheta_photo = State()

    depozit = State()
    check_payment = State()


class AdminStates(StatesGroup):
    sending_to_users = State()
    update_qiwi_data = State()
    update_product_price = State()
