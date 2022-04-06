import sqlite3 as sql
import datetime



user_from_lis = [
    'yandex', 'google',
    'telegram', 'whatsapp',
    'vkontakte', 'friend'
]


class MainDB:
    def __init__(self, db_file = 'users.db'):
        self.con = sql.connect(db_file)
        self.cur = self.con.cursor()


    def createTable(self):
        with self.con:
            self.cur.execute("""CREATE TABLE IF NOT EXISTS users(
                            user_id INT,
                            user_balance TEXT,
                            from_name TEXT,
                            depozit TEXT, 
                            now_product TEXT,
                            now_price TEXT, 
                            product_name TEXT)""")

            self.cur.execute("""CREATE TABLE IF NOT EXISTS qiwi_bills(
                            user_id INT,
                            bill_id TEXT)""")

            self.cur.execute("""CREATE TABLE IF NOT EXISTS admins(
                            admin_id INT)""")

            self.cur.execute("""CREATE TABLE IF NOT EXISTS osago_data(
                            user_id INT,
                            fio_straxovka TEXT,
                            fio_owner_auto TEXT,
                            model_marka_auto TEXT,
                            vin_or_kuzov TEXT,
                            pts_auto TEXT,
                            gos_num_auto TEXT,
                            pass_data TEXT,
                            price TEXT)""")

            self.cur.execute("""CREATE TABLE IF NOT EXISTS dk_data(
                            user_id INT,
                            fio TEXT,
                            probeg TEXT,
                            marka_shin TEXT,
                            toplivo TEXT,
                            sts_or_pts_photo1 TEXT,
                            sts_or_pts_photo2 TEXT,
                            photo1 TEXT,
                            photo2 TEXT,
                            price TEXT)""")

            self.cur.execute("""CREATE TABLE IF NOT EXISTS karta_gai_data(
                            user_id INT,
                            prava_photo TEXT,
                            price TEXT)""")

            self.cur.execute("""CREATE TABLE IF NOT EXISTS karta_gibdd_data(
                            user_id INT,
                            gos_nomer TEXT,
                            price TEXT)""")

            self.cur.execute("""CREATE TABLE IF NOT EXISTS kasko_bank_data(
                            user_id INT,
                            fio TEXT,
                            birthday TEXT,
                            drive_pass TEXT,
                            drive_experience TEXT,
                            ts_data TEXT,
                            bank TEXT,
                            auto_price TEXT,
                            number TEXT,
                            price TEXT)""")

            self.cur.execute("""CREATE TABLE IF NOT EXISTS auto_med_data(
                            user_id INT,
                            fio TEXT,
                            birthday TEXT,
                            pass_seriya TEXT,
                            pass_who_give TEXT,
                            category TEXT,
                            price TEXT)""")

            self.cur.execute("""CREATE TABLE IF NOT EXISTS search_solary_data(
                            user_id INT,
                            fio TEXT,
                            birthday TEXT,
                            price TEXT)""")


            self.cur.execute("""CREATE TABLE IF NOT EXISTS qiwi_data(
                            qiwi_number TEXT,
                            qiwi_token TEXT)""")

            self.cur.execute("""CREATE TABLE IF NOT EXISTS user_history_data(
                            user_id INT,
                            order_name TEXT
                            price TEXT,
                            date TEXT)""")

            self.cur.execute("""CREATE TABLE IF NOT EXISTS products(
                            product_name TEXT,
                            product_price TEXT)""")


    def updateUserMoney(self, user_id, money):
        with self.con:
            self.cur.execute("UPDATE users SET user_balance = ? WHERE user_id = ?" ,(money, user_id,))


    def getFromUsersData(self):
        with self.con:
            lis = []
            for f in user_from_lis:
                self.cur.execute("SELECT count(from_name) FROM users WHERE from_name = ?", (f,))
                lis.append(self.cur.fetchone()[0])

            return lis



    def updateProductsInfo(self, rowid, sum):
        with self.con:
            self.cur.execute("UPDATE products SET product_price = ? WHERE rowid = ?", (sum, rowid,))



    def getAllUserOrderProduct(self, user_id, item):
        with self.con:
            self.cur.execute(f"SELECT * FROM {item} WHERE user_id = ?", (user_id,))
            return self.cur.fetchone()


    def clearHistory(self, user_id):
        with self.con:
            self.cur.execute("DELETE FROM user_history_data WHERE user_id = ?", (user_id,))


    def getAdminsId(self):
        with self.con:
            self.cur.execute(f"SELECT * FROM admins")
            return self.cur.fetchall()


    def getProductsInfo(self, rowid):
        with self.con:
            self.cur.execute("SELECT * FROM products WHERE rowid = ?", (rowid,))
            return self.cur.fetchone()



    def getUsers(self):
        with self.con:
            self.cur.execute(f"SELECT user_id FROM users")
            return self.cur.fetchall()


    def updateOsagoData(self, user_id, item=None, value=None):
        with self.con:
            self.cur.execute(f"SELECT * FROM osago_data WHERE user_id = ?", (user_id,))
            if self.cur.fetchone() is None:
                self.cur.execute(f"INSERT INTO osago_data (user_id) VALUES (?)", (user_id,))
            else:
                self.cur.execute(f"UPDATE osago_data SET {item} = ? WHERE user_id = ?", (value, user_id,))


    def updateDkData(self, user_id, item=None, value=None):
        with self.con:
            self.cur.execute(f"SELECT * FROM dk_data WHERE user_id = ?", (user_id,))
            if self.cur.fetchone() is None:
                self.cur.execute(f"INSERT INTO dk_data (user_id) VALUES (?)", (user_id,))
            else:
                self.cur.execute(f"UPDATE dk_data SET {item} = ? WHERE user_id = ?", (value, user_id,))



    def updateMedAutoData(self, user_id, item=None, value=None):
        with self.con:
            self.cur.execute(f"SELECT * FROM auto_med_data WHERE user_id = ?", (user_id,))
            if self.cur.fetchone() is None:
                self.cur.execute(f"INSERT INTO auto_med_data (user_id) VALUES (?)", (user_id,))
            else:
                self.cur.execute(f"UPDATE auto_med_data SET {item} = ? WHERE user_id = ?", (value, user_id,))



    def updateKaskoBankData(self, user_id, item=None, value=None):
        with self.con:
            self.cur.execute(f"SELECT * FROM kasko_bank_data WHERE user_id = ?", (user_id,))
            if self.cur.fetchone() is None:
                self.cur.execute(f"INSERT INTO kasko_bank_data (user_id) VALUES (?)", (user_id,))
            else:
                self.cur.execute(f"UPDATE kasko_bank_data SET {item} = ? WHERE user_id = ?", (value, user_id,))



    def updateKartaGibddData(self, user_id, item=None, value=None):
        with self.con:
            self.cur.execute(f"SELECT * FROM karta_gibdd_data WHERE user_id = ?", (user_id,))
            if self.cur.fetchone() is None:
                self.cur.execute(f"INSERT INTO karta_gibdd_data (user_id) VALUES (?)", (user_id,))
            else:
                self.cur.execute(f"UPDATE karta_gibdd_data SET {item} = ? WHERE user_id = ?", (value, user_id,))



    def updateKartaVUGaiData(self, user_id, item=None, value=None):
        with self.con:
            self.cur.execute(f"SELECT * FROM karta_gai_data WHERE user_id = ?", (user_id,))
            if self.cur.fetchone() is None:
                self.cur.execute(f"INSERT INTO karta_gai_data (user_id) VALUES (?)", (user_id,))
            else:
                self.cur.execute(f"UPDATE karta_gai_data SET {item} = ? WHERE user_id = ?", (value, user_id,))



    def updatePoiskSolariyData(self, user_id, item=None, value=None):
        with self.con:
            self.cur.execute(f"SELECT * FROM search_solary_data WHERE user_id = ?", (user_id,))
            if self.cur.fetchone() is None:
                self.cur.execute(f"INSERT INTO search_solary_data (user_id) VALUES (?)", (user_id,))
            else:
                self.cur.execute(f"UPDATE search_solary_data SET {item} = ? WHERE user_id = ?", (value, user_id,))



    def updateUserInfo(self, user_id, item, value):
        with self.con:
            self.cur.execute(f"UPDATE users SET {item} = ? WHERE user_id = ?", (value, user_id,))


    def updateUserBalance(self, user_id, item, value):
        with self.con:
            self.cur.execute(f"UPDATE users SET {item} = {value} WHERE user_id = ?", (user_id,))



    def getOsagoData(self, user_id):
        with self.con:
            self.cur.execute(f"SELECT * FROM osago_data WHERE user_id = ?", (user_id,))
            return self.cur.fetchone()


    def getDkData(self, user_id):
        with self.con:
            self.cur.execute(f"SELECT * FROM dk_data WHERE user_id = ?", (user_id,))
            return self.cur.fetchone()


    def updateUserHistory(self, user_id, product, price, date=datetime.datetime.today().strftime('%y.%m.%d')):
        with self.con:
            self.cur.execute("INSERT INTO user_history_data (user_id, order_name, price, date) VALUES (?, ?, ?, ?)", (user_id, product, price, date,))


    def getUserHistory(self, user_id):
        with self.con:
            self.cur.execute("SELECT * FROM user_history_data WHERE user_id = ?", (user_id,))
            return self.cur.fetchall()


    def getUserInfo(self, user_id):
        with self.con:
            self.cur.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
            return self.cur.fetchone()


    def getQiwiConfig(self):
        with self.con:
            self.cur.execute(f"SELECT * FROM qiwi_data")
            return self.cur.fetchone()


    def updateQiwiConfig(self, item, value):
        with self.con:
            self.cur.execute(f"UPDATE qiwi_data SET {item} = ?", (value,))


    def setNewAdmin(self, admin_id):
        with self.con:
            self.cur.execute(f"SELECT admin_id FROM admins WHERE admin_id = ?", (admin_id,))
            if self.cur.fetchone() is None:
                self.cur.execute(f"INSERT INTO admins (admin_id) VALUES (?)", (admin_id,))


    def delNewAdmin(self, admin_id):
        with self.con:
            self.cur.execute(f"SELECT admin_id FROM admins WHERE admin_id = ?", (admin_id,))
            if not self.cur.fetchone() is None:
                self.cur.execute(f"DELETE FROM admins WHERE admin_id = ?", (admin_id,))



    def getBotUsers(self):
        with self.con:
            self.cur.execute("SELECT count(user_id) FROM users")
            return self.cur.fetchone()


    def checkUser(self, id):
        with self.con:
            self.cur.execute("SELECT user_id FROM users WHERE user_id = ?", (id,))
            return self.cur.fetchone()


    def addUser(self, id, text):
        with self.con:
            self.cur.execute("INSERT INTO users (user_id, user_balance, from_name)VALUES(?, ?, ?)", (id, 0, text,))


    def checkPayment(self, user_id):
        with self.con:
            self.cur.execute("SELECT bill_id FROM qiwi_bills WHERE user_id = ?", (user_id,))

            return self.cur.fetchone()[0]


    def createPayment(self, user_id, bill_id):
        with self.con:
            self.cur.execute("SELECT user_id FROM qiwi_bills WHERE user_id = ?", (user_id,))
            if self.cur.fetchone() is None:
                self.cur.execute("INSERT INTO qiwi_bills (user_id, bill_id) VALUES (?, ?)", (user_id, bill_id,))

            else:
                self.cur.execute("UPDATE qiwi_bills SET bill_id = ? WHERE user_id = ?", (bill_id, user_id,))

