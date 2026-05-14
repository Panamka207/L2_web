import pymysql
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import (QApplication, QLineEdit, QMainWindow, QHeaderView,
                             QPushButton, QTableWidgetItem, QDialog, QMessageBox)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QBrush


# ─────────────────────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────────────────────
class Database:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host='127.0.0.1',
                port=3307,
                user='root',
                password='123456',
                database='airport_tracking',
                charset='utf8',
            )
            print('БД подключена')
        except Exception as e:
            self.connection = None
            print('БД не подключена:', e)

    def select(self, table):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `{table}`;")
            return cursor.fetchall()

    def get_flights_with_details(self):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT f.flight_id, f.flight_number, a.name, p.model,
                       f.departure_time, f.arrival_time, f.departure_date, f.status,
                       f.economy_seats, f.business_seats, f.first_class_seats
                FROM flight f
                JOIN airport a ON f.airport_id = a.airport_id
                JOIN airplane p ON f.airplane_id = p.airplane_id
            ''')
            return cursor.fetchall()

    def get_tickets_with_details(self):
        with self.connection.cursor() as cursor:
            cursor.execute('''
                SELECT t.ticket_id,
                       CONCAT(p.last_name, ' ', p.first_name, ' ', COALESCE(p.middle_name, '')) AS passenger_name,
                       f.flight_number, t.ticket_number, t.purchase_date,
                       t.travel_class, t.seat, t.price, t.status
                FROM ticket t
                JOIN passenger p ON t.passenger_id = p.passenger_id
                JOIN flight f ON t.flight_id = f.flight_id
                ORDER BY t.ticket_id
            ''')
            return cursor.fetchall()

    # ── CRUD: Flight ──────────────────────────────────────────
    def insert_flight(self, data):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO flight (flight_number, airport_id, airplane_id,
                                    departure_time, arrival_time, departure_date, status,
                                    economy_seats, business_seats, first_class_seats)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (data['flight_number'], data['airport_id'], data['airplane_id'],
                  data['departure_time'], data['arrival_time'],
                  data['departure_date'], data['status'],
                  data['economy_seats'], data['business_seats'], data['first_class_seats']))
        self.connection.commit()

    def update_flight(self, flight_id, data):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                UPDATE flight
                SET
                    flight_number=%s,
                    airport_id=%s,
                    airplane_id=%s,
                    departure_time=%s,
                    arrival_time=%s,
                    departure_date=%s,
                    status=%s,
                    economy_seats=%s,
                    business_seats=%s,
                    first_class_seats=%s
                WHERE flight_id=%s
            """, (
                data['flight_number'],
                data['airport_id'],
                data['airplane_id'],
                data['departure_time'],
                data['arrival_time'],
                data['departure_date'],
                data['status'],
                data['economy_seats'],
                data['business_seats'],
                data['first_class_seats'],
                flight_id
            ))
        self.connection.commit()

    def delete_flight(self, flight_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM flight WHERE flight_id=%s", (flight_id,))
        self.connection.commit()

    def check_available_seats(self, flight_id, travel_class):
        with self.connection.cursor() as cursor:
            if travel_class == 'Эконом':
                field = 'economy_seats'
            elif travel_class == 'Бизнес':
                field = 'business_seats'
            else:
                field = 'first_class_seats'

            cursor.execute(f"""
                SELECT {field}
                FROM flight
                WHERE flight_id=%s
            """, (flight_id,))
            total = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM ticket
                WHERE flight_id=%s
                AND travel_class=%s
            """, (flight_id, travel_class))
            sold = cursor.fetchone()[0]

            return sold < total

    # ── CRUD: Passenger ───────────────────────────────────────
    def insert_passenger(self, data):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO passenger (last_name, first_name, middle_name, passport_data, phone_number)
                VALUES (%s,%s,%s,%s,%s)
            """, (data['last_name'], data['first_name'], data['middle_name'],
                  data['passport_data'], data['phone_number']))
        self.connection.commit()

    def update_passenger(self, passenger_id, data):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                UPDATE passenger SET last_name=%s, first_name=%s, middle_name=%s,
                    passport_data=%s, phone_number=%s
                WHERE passenger_id=%s
            """, (data['last_name'], data['first_name'], data['middle_name'],
                  data['passport_data'], data['phone_number'], passenger_id))
        self.connection.commit()

    def delete_passenger(self, passenger_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM passenger WHERE passenger_id=%s", (passenger_id,))
        self.connection.commit()

    # ── CRUD: Ticket ──────────────────────────────────────────
    def insert_ticket(self, data):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ticket (passenger_id, flight_id, ticket_number, purchase_date,
                                    travel_class, seat, price, status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (data['passenger_id'], data['flight_id'], data['ticket_number'],
                  data['purchase_date'], data['travel_class'],
                  data['seat'], data['price'], data['status']))
        self.connection.commit()

    def update_ticket(self, ticket_id, data):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                UPDATE ticket SET passenger_id=%s, flight_id=%s, ticket_number=%s,
                    purchase_date=%s, travel_class=%s, seat=%s, price=%s, status=%s
                WHERE ticket_id=%s
            """, (data['passenger_id'], data['flight_id'], data['ticket_number'],
                  data['purchase_date'], data['travel_class'],
                  data['seat'], data['price'], data['status'], ticket_id))
        self.connection.commit()

    def delete_ticket(self, ticket_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ticket WHERE ticket_id=%s", (ticket_id,))
        self.connection.commit()

    # ── CRUD: Airport ─────────────────────────────────────────
    def insert_airport(self, data):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO airport (name, city, country) VALUES (%s,%s,%s)",
                           (data['name'], data['city'], data['country']))
        self.connection.commit()

    def update_airport(self, airport_id, data):
        with self.connection.cursor() as cursor:
            cursor.execute("UPDATE airport SET name=%s, city=%s, country=%s WHERE airport_id=%s",
                           (data['name'], data['city'], data['country'], airport_id))
        self.connection.commit()

    def delete_airport(self, airport_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM airport WHERE airport_id=%s", (airport_id,))
        self.connection.commit()

    # ── CRUD: Airplane ────────────────────────────────────────
    def insert_airplane(self, data):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO airplane (model, registration_number, capacity) VALUES (%s,%s,%s)",
                           (data['model'], data['registration_number'], data['capacity']))
        self.connection.commit()

    def update_airplane(self, airplane_id, data):
        with self.connection.cursor() as cursor:
            cursor.execute("UPDATE airplane SET model=%s, registration_number=%s, capacity=%s WHERE airplane_id=%s",
                           (data['model'], data['registration_number'], data['capacity'], airplane_id))
        self.connection.commit()

    def delete_airplane(self, airplane_id):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM airplane WHERE airplane_id=%s", (airplane_id,))
        self.connection.commit()

    # ── CRUD: Crew ────────────────────────────────────────────
    def insert_crew(self, data):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO crew (last_name, first_name, middle_name, qualification,
                                  position, gender, date_of_birth)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (data['last_name'], data['first_name'], data['middle_name'],
                  data['qualification'], data['position'],
                  data['gender'], data['date_of_birth']))
        self.connection.commit()

    def update_crew(self, crew_id, data):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                UPDATE crew SET last_name=%s, first_name=%s, middle_name=%s,
                    qualification=%s, position=%s, gender=%s, date_of_birth=%s
                WHERE crew_id=%s
            """, (data['last_name'], data['first_name'], data['middle_name'],
                  data['qualification'], data['position'],
                  data['gender'], data['date_of_birth'], crew_id))
        self.connection.commit()

    def delete_crew(self, crew_id):
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM crew WHERE crew_id=%s", (crew_id,))
        self.connection.commit()

    # ── Combo helpers ─────────────────────────────────────────
    def get_airports(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT airport_id, name FROM airport")
            return cursor.fetchall()

    def get_airplanes(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT airplane_id, model FROM airplane")
            return cursor.fetchall()

    def get_passengers(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT passenger_id,
                       CONCAT(last_name, ' ', first_name, ' ', COALESCE(middle_name, ''))
                FROM passenger
            """)
            return cursor.fetchall()

    def get_flights_simple(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT flight_id, flight_number FROM flight")
            return cursor.fetchall()

    def check_user(self, login, password):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT role
                FROM users
                WHERE login=%s AND password=%s
            """, (login, password))
            return cursor.fetchone()

    def close(self):
        if self.connection:
            self.connection.close()


# ─────────────────────────────────────────────────────────────
#  LOGIN WINDOW
# ─────────────────────────────────────────────────────────────
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('./ui/vhod.ui', self)
        self.lineEdit_2.setEchoMode(QLineEdit.EchoMode.Password)
        self.pushButton_2.clicked.connect(self.check_login)
        self.pushButton.clicked.connect(self.close)
        self.setWindowTitle("Авторизация")
        self.db = Database()

    def check_login(self):
        login = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        result = self.db.check_user(login, password)

        if result:
            role = result[0]
            QMessageBox.information(
                self,
                "Успех",
                f"Добро пожаловать, {login}\nРоль: {role}"
            )
            self.main_window = MyWidget()
            self.main_window.show()
            self.close()
        else:
            QMessageBox.critical(
                self,
                "Ошибка",
                "Неверный логин или пароль"
            )


# ─────────────────────────────────────────────────────────────
#  DIALOGS
# ─────────────────────────────────────────────────────────────
class FlightDialog(QDialog):
    def __init__(self, db, flight_id=None, parent=None):
        super().__init__(parent)
        uic.loadUi('./ui/flight.ui', self)
        self.db = db
        self.flight_id = flight_id
        self.pushButton.setText("Сохранить" if flight_id else "Добавить")
        self.pushButton.clicked.connect(self.save)
        self.setWindowTitle(
            "Редактирование рейса" if flight_id else "Добавление рейса")
        self._load_combos()
        if not flight_id:
            # Дата по умолчанию — сегодня
            self.dateEdit.setDate(QDate.currentDate())
        if flight_id:
            self._fill_data()

    def _load_combos(self):
        self.airport_comboBox.clear()
        for aid, name in self.db.get_airports():
            self.airport_comboBox.addItem(name, aid)
        self.airplane_comboBox.clear()
        for pid, model in self.db.get_airplanes():
            self.airplane_comboBox.addItem(model, pid)
        self.status_comboBox.clear()
        self.status_comboBox.addItems(
            ['По расписанию', 'Задержан', 'Отменён', 'Выполнен'])

    def _fill_data(self):
        with self.db.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM flight WHERE flight_id=%s", (self.flight_id,))
            row = cursor.fetchone()
        # row: flight_id, airport_id, airplane_id, flight_number,
        #       departure_time, arrival_time, departure_date, status,
        #       economy_seats, business_seats, first_class_seats
        if row:
            self.flight_number_lineEdit.setText(str(row[3]))
            idx = self.airport_comboBox.findData(row[1])
            if idx >= 0:
                self.airport_comboBox.setCurrentIndex(idx)
            idx = self.airplane_comboBox.findData(row[2])
            if idx >= 0:
                self.airplane_comboBox.setCurrentIndex(idx)
            self.time_lineEdit.setText(str(row[4]))
            self.time2_lineEdit.setText(str(row[5]))
            self.dateEdit.setDate(row[6])
            idx = self.status_comboBox.findText(str(row[7]))
            if idx >= 0:
                self.status_comboBox.setCurrentIndex(idx)
            # Заполняем поля мест
            self.economy_seats_lineEdit.setText(str(row[8]))
            self.business_seats_lineEdit.setText(str(row[9]))
            self.first_class_seats_lineEdit.setText(str(row[10]))

    def save(self):
        # Валидация мест
        try:
            economy = int(self.economy_seats_lineEdit.text().strip() or 0)
            business = int(self.business_seats_lineEdit.text().strip() or 0)
            first_cl = int(self.first_class_seats_lineEdit.text().strip() or 0)
        except ValueError:
            QMessageBox.warning(
                self, "Ошибка", "Количество мест должно быть числом")
            return

        data = {
            'flight_number': self.flight_number_lineEdit.text().strip(),
            'airport_id': self.airport_comboBox.currentData(),
            'airplane_id': self.airplane_comboBox.currentData(),
            'departure_time': self.time_lineEdit.text().strip(),
            'arrival_time': self.time2_lineEdit.text().strip(),
            'departure_date': self.dateEdit.date().toString("yyyy-MM-dd"),
            'status': self.status_comboBox.currentText(),
            'economy_seats': economy,
            'business_seats': business,
            'first_class_seats': first_cl,
        }
        if not data['flight_number']:
            QMessageBox.warning(self, "Ошибка", "Введите номер рейса")
            return
        try:
            if self.flight_id:
                self.db.update_flight(self.flight_id, data)
                QMessageBox.information(
                    self, "Успех", "Рейс успешно обновлён!")
            else:
                self.db.insert_flight(data)
                QMessageBox.information(
                    self, "Успех", "Рейс успешно добавлен!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при сохранении:\n{e}")


class PassengerDialog(QDialog):
    def __init__(self, db, passenger_id=None, parent=None):
        super().__init__(parent)
        uic.loadUi('./ui/passenger.ui', self)
        self.db = db
        self.passenger_id = passenger_id
        self.pushButton.setText("Сохранить" if passenger_id else "Добавить")
        self.pushButton.clicked.connect(self.save)
        self.setWindowTitle(
            "Редактирование пассажира" if passenger_id else "Добавление пассажира")
        if passenger_id:
            self._fill_data()

    def _fill_data(self):
        with self.db.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM passenger WHERE passenger_id=%s", (self.passenger_id,))
            row = cursor.fetchone()
        if row:
            self.last_name_lineEdit.setText(str(row[1]))
            self.first_name_lineEdit.setText(str(row[2]))
            self.middle_name_lineEdit_2.setText(str(row[3]) if row[3] else '')
            self.passport_lineEdit_3.setText(str(row[4]))
            self.phone_lineEdit_4.setText(str(row[5]))

    def save(self):
        data = {
            'last_name': self.last_name_lineEdit.text().strip(),
            'first_name': self.first_name_lineEdit.text().strip(),
            'middle_name': self.middle_name_lineEdit_2.text().strip() or None,
            'passport_data': self.passport_lineEdit_3.text().strip(),
            'phone_number': self.phone_lineEdit_4.text().strip()
        }
        if not all([data['last_name'], data['first_name'], data['passport_data'], data['phone_number']]):
            QMessageBox.warning(
                self, "Ошибка", "Заполните все обязательные поля")
            return
        try:
            if self.passenger_id:
                self.db.update_passenger(self.passenger_id, data)
                QMessageBox.information(
                    self, "Успех", "Пассажир успешно обновлён!")
            else:
                self.db.insert_passenger(data)
                QMessageBox.information(
                    self, "Успех", "Пассажир успешно добавлен!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при сохранении:\n{e}")


class TicketDialog(QDialog):
    def __init__(self, db, ticket_id=None, parent=None):
        super().__init__(parent)
        uic.loadUi('./ui/ticket.ui', self)
        self.db = db
        self.ticket_id = ticket_id
        self.pushButton.setText("Сохранить" if ticket_id else "Добавить")
        self.pushButton.clicked.connect(self.save)
        self.setWindowTitle(
            "Редактирование билета" if ticket_id else "Добавление билета")
        self._load_combos()
        if not ticket_id:
            # Дата покупки — сегодня
            self.dateEdit.setDate(QDate.currentDate())
        if ticket_id:
            self._fill_data()

    def _load_combos(self):
        self.passanger_comboBox.clear()
        for pid, name in self.db.get_passengers():
            self.passanger_comboBox.addItem(name, pid)
        self.flight_comboBox.clear()
        for fid, number in self.db.get_flights_simple():
            self.flight_comboBox.addItem(number, fid)
        self.comboBox.clear()
        self.comboBox.addItems(['Эконом', 'Бизнес', 'Первый'])
        self.comboBox_2.clear()
        self.comboBox_2.addItems(['Активен', 'Отменён', 'Использован'])

    def _fill_data(self):
        with self.db.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM ticket WHERE ticket_id=%s", (self.ticket_id,))
            row = cursor.fetchone()
        if row:
            idx = self.passanger_comboBox.findData(row[1])
            if idx >= 0:
                self.passanger_comboBox.setCurrentIndex(idx)
            idx = self.flight_comboBox.findData(row[2])
            if idx >= 0:
                self.flight_comboBox.setCurrentIndex(idx)
            self.ticket_lineEdit.setText(str(row[3]))
            self.dateEdit.setDate(row[4])
            idx = self.comboBox.findText(str(row[5]))
            if idx >= 0:
                self.comboBox.setCurrentIndex(idx)
            self.place_lineEdit_2.setText(str(row[6]))
            self.price_lineEdit_3.setText(str(row[7]))
            idx = self.comboBox_2.findText(str(row[8]))
            if idx >= 0:
                self.comboBox_2.setCurrentIndex(idx)

    def save(self):
        data = {
            'passenger_id': self.passanger_comboBox.currentData(),
            'flight_id': self.flight_comboBox.currentData(),
            'ticket_number': self.ticket_lineEdit.text().strip(),
            'purchase_date': self.dateEdit.date().toString("yyyy-MM-dd"),
            'travel_class': self.comboBox.currentText(),
            'seat': self.place_lineEdit_2.text().strip(),
            'price': self.price_lineEdit_3.text().strip(),
            'status': self.comboBox_2.currentText()
        }
        if not data['passenger_id']:
            QMessageBox.warning(self, "Ошибка", "Выберите пассажира")
            return
        if not data['flight_id']:
            QMessageBox.warning(self, "Ошибка", "Выберите рейс")
            return
        if not data['ticket_number']:
            QMessageBox.warning(self, "Ошибка", "Введите номер билета")
            return

        # Проверка наличия свободных мест (только при добавлении нового билета)
        if not self.ticket_id:
            if not self.db.check_available_seats(data['flight_id'], data['travel_class']):
                QMessageBox.warning(
                    self, "Нет мест",
                    f"На данный рейс нет свободных мест в классе «{data['travel_class']}».\n"
                    "Выберите другой класс или другой рейс."
                )
                return

        try:
            if self.ticket_id:
                self.db.update_ticket(self.ticket_id, data)
                QMessageBox.information(
                    self, "Успех", "Билет успешно обновлён!")
            else:
                self.db.insert_ticket(data)
                QMessageBox.information(
                    self, "Успех", "Билет успешно добавлен!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при сохранении:\n{e}")


class AirportDialog(QDialog):
    def __init__(self, db, airport_id=None, parent=None):
        super().__init__(parent)
        uic.loadUi('./ui/airport.ui', self)
        self.db = db
        self.airport_id = airport_id
        self.pushButton.setText("Сохранить" if airport_id else "Добавить")
        self.pushButton.clicked.connect(self.save)
        self.setWindowTitle(
            "Редактирование аэропорта" if airport_id else "Добавление аэропорта")
        if airport_id:
            self._fill_data()

    def _fill_data(self):
        with self.db.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM airport WHERE airport_id=%s", (self.airport_id,))
            row = cursor.fetchone()
        if row:
            self.name_lineEdit.setText(str(row[1]))
            self.city_lineEdit_2.setText(str(row[2]))
            self.country_lineEdit_3.setText(str(row[3]))

    def save(self):
        data = {
            'name': self.name_lineEdit.text().strip(),
            'city': self.city_lineEdit_2.text().strip(),
            'country': self.country_lineEdit_3.text().strip()
        }
        if not all(data.values()):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        try:
            if self.airport_id:
                self.db.update_airport(self.airport_id, data)
                QMessageBox.information(
                    self, "Успех", "Аэропорт успешно обновлён!")
            else:
                self.db.insert_airport(data)
                QMessageBox.information(
                    self, "Успех", "Аэропорт успешно добавлен!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при сохранении:\n{e}")


class AirplaneDialog(QDialog):
    def __init__(self, db, airplane_id=None, parent=None):
        super().__init__(parent)
        uic.loadUi('./ui/airplane.ui', self)
        self.db = db
        self.airplane_id = airplane_id
        self.pushButton.setText("Сохранить" if airplane_id else "Добавить")
        self.pushButton.clicked.connect(self.save)
        self.setWindowTitle(
            "Редактирование самолёта" if airplane_id else "Добавление самолёта")
        if airplane_id:
            self._fill_data()

    def _fill_data(self):
        with self.db.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM airplane WHERE airplane_id=%s", (self.airplane_id,))
            row = cursor.fetchone()
        if row:
            self.model_lineEdit.setText(str(row[1]))
            self.number_lineEdit_2.setText(str(row[2]))
            self.size_lineEdit_3.setText(str(row[3]))

    def save(self):
        data = {
            'model': self.model_lineEdit.text().strip(),
            'registration_number': self.number_lineEdit_2.text().strip(),
            'capacity': self.size_lineEdit_3.text().strip()
        }
        if not all(data.values()):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        try:
            if self.airplane_id:
                self.db.update_airplane(self.airplane_id, data)
                QMessageBox.information(
                    self, "Успех", "Самолёт успешно обновлён!")
            else:
                self.db.insert_airplane(data)
                QMessageBox.information(
                    self, "Успех", "Самолёт успешно добавлен!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при сохранении:\n{e}")


class CrewDialog(QDialog):
    def __init__(self, db, crew_id=None, parent=None):
        super().__init__(parent)
        uic.loadUi('./ui/sotrudnik.ui', self)
        self.db = db
        self.crew_id = crew_id
        self.pushButton.setText("Сохранить" if crew_id else "Добавить")
        self.pushButton.clicked.connect(self.save)
        self.setWindowTitle(
            "Редактирование сотрудника" if crew_id else "Добавление сотрудника")
        self.gender_comboBox.clear()
        self.gender_comboBox.addItems(['Мужской', 'Женский'])
        if crew_id:
            self._fill_data()

    def _fill_data(self):
        with self.db.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM crew WHERE crew_id=%s", (self.crew_id,))
            row = cursor.fetchone()
        if row:
            self.last_name_lineEdit.setText(str(row[1]))
            self.first_name_lineEdit.setText(str(row[2]))
            self.middle_name_lineEdit_2.setText(str(row[3]) if row[3] else '')
            self.kval_lineEdit_3.setText(str(row[4]) if row[4] else '')
            self.work_lineEdit_4.setText(str(row[5]))
            idx = self.gender_comboBox.findText(str(row[6]))
            if idx >= 0:
                self.gender_comboBox.setCurrentIndex(idx)
            self.dateEdit.setDate(row[7])

    def save(self):
        data = {
            'last_name': self.last_name_lineEdit.text().strip(),
            'first_name': self.first_name_lineEdit.text().strip(),
            'middle_name': self.middle_name_lineEdit_2.text().strip() or None,
            'qualification': self.kval_lineEdit_3.text().strip() or None,
            'position': self.work_lineEdit_4.text().strip(),
            'gender': self.gender_comboBox.currentText(),
            'date_of_birth': self.dateEdit.date().toString("yyyy-MM-dd")
        }
        if not all([data['last_name'], data['first_name'], data['position']]):
            QMessageBox.warning(
                self, "Ошибка", "Заполните все обязательные поля")
            return
        try:
            if self.crew_id:
                self.db.update_crew(self.crew_id, data)
                QMessageBox.information(
                    self, "Успех", "Сотрудник успешно обновлён!")
            else:
                self.db.insert_crew(data)
                QMessageBox.information(
                    self, "Успех", "Сотрудник успешно добавлен!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при сохранении:\n{e}")


# ─────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────
class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('./ui/interface.ui', self)

        self.db = Database()
        self.current_table = 'Flight'

        self._raw = {}

        self.menu_buttons = [
            self.flights_menuBtn, self.passenger_menuBtn, self.ticket_menuBtn,
            self.airport_menuBtn, self.airplane_menuBtn,
            self.sotrudnik_menuBtn, self.otchet_menuBtn
        ]

        self._setup_tables()
        self._connect_signals()
        self._load_all_data()

        self.dateFrom.setDate(QDate.currentDate())
        self.dateTo.setDate(QDate.currentDate())

        self.flights_menuBtn.setChecked(True)
        self.stackedWidget.setCurrentWidget(self.pageReys)
        self.filterStack.setCurrentWidget(self.filterPageFlights)

    # ── Table setup ───────────────────────────────────────────
    def _setup_tables(self):
        cfg = {
            self.tableReys:      ['ID', 'Номер рейса', 'Аэропорт', 'Самолёт',
                                  'Время вылета', 'Время прилёта', 'Дата', 'Статус',
                                  'Мест эконом', 'Мест бизнес', 'Мест первый'],
            self.tablePassenger: ['ID', 'Фамилия', 'Имя', 'Отчество', 'Паспорт', 'Телефон'],
            self.tableTickets:   ['ID', 'Пассажир', 'Рейс', 'Номер билета',
                                  'Дата покупки', 'Класс', 'Место', 'Цена', 'Статус'],
            self.tableAirport:   ['ID', 'Название', 'Город', 'Страна'],
            self.tablePlane:     ['ID', 'Модель', 'Рег. номер', 'Вместимость'],
            self.tableStaff:     ['ID', 'Фамилия', 'Имя', 'Отчество',
                                  'Квалификация', 'Должность', 'Пол', 'Дата рождения']
        }
        for tw, headers in cfg.items():
            tw.setColumnCount(len(headers))
            tw.setHorizontalHeaderLabels(headers)
            tw.setColumnHidden(0, True)
            tw.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            tw.setSortingEnabled(True)

    # ── Signal connections ────────────────────────────────────
    def _connect_signals(self):
        self.flights_menuBtn.clicked.connect(
            lambda: self._switch(self.pageReys, 'Flight', self.filterPageFlights, self.flights_menuBtn))
        self.passenger_menuBtn.clicked.connect(
            lambda: self._switch(self.pagePassenger, 'Passenger', self.filterPagePassengers, self.passenger_menuBtn))
        self.ticket_menuBtn.clicked.connect(
            lambda: self._switch(self.pageTickets, 'Ticket', self.filterPageTickets, self.ticket_menuBtn))
        self.airport_menuBtn.clicked.connect(
            lambda: self._switch(self.pageAirport, 'Airport', self.filterPageAirports, self.airport_menuBtn))
        self.airplane_menuBtn.clicked.connect(
            lambda: self._switch(self.pagePlane, 'Airplane', self.filterPageAirplanes, self.airplane_menuBtn))
        self.sotrudnik_menuBtn.clicked.connect(
            lambda: self._switch(self.pageStaff, 'Crew', self.filterPageStaff, self.sotrudnik_menuBtn))
        self.otchet_menuBtn.clicked.connect(
            lambda: self._switch(self.pageReports, 'Reports', self.filterPageReports, self.otchet_menuBtn))

        self.btnSearch.clicked.connect(self._apply_filters)
        self.searchField.returnPressed.connect(self._apply_filters)
        self.btnReset.clicked.connect(self._reset_filters)
        self.btnRefresh.clicked.connect(self._hard_refresh)

        self.cmbFlightStatus.currentTextChanged.connect(self._apply_filters)
        self.cmbTicketStatus.currentTextChanged.connect(self._apply_filters)
        self.cmbTicketClass.currentTextChanged.connect(self._apply_filters)
        self.cmbAirportCountry.currentTextChanged.connect(self._apply_filters)
        self.cmbStaffGender.currentTextChanged.connect(self._apply_filters)
        self.lineEditPosition.textChanged.connect(self._apply_filters)

        self.btnAdd.clicked.connect(self._add_record)
        self.btnEdit.clicked.connect(self._edit_record)
        self.btnDelete.clicked.connect(self._delete_record)

        self.btnGenerateReport.clicked.connect(self._generate_report)

    # ── Page switch ───────────────────────────────────────────
    def _switch(self, page, table_name, filter_page, btn):
        for b in self.menu_buttons:
            b.setChecked(False)
        btn.setChecked(True)
        self.stackedWidget.setCurrentWidget(page)
        self.filterStack.setCurrentWidget(filter_page)
        self.current_table = table_name
        titles = {
            'Flight': 'Рейсы', 'Passenger': 'Пассажиры', 'Ticket': 'Билеты',
            'Airport': 'Аэропорты', 'Airplane': 'Самолёты',
            'Crew': 'Сотрудники', 'Reports': 'Отчёты'
        }
        self.pageTitle.setText(titles.get(table_name, ''))

    # ── Load data ─────────────────────────────────────────────
    def _load_all_data(self):
        self._raw['Flight'] = self.db.get_flights_with_details()
        self._raw['Passenger'] = self.db.select('passenger')
        self._raw['Ticket'] = self.db.get_tickets_with_details()
        self._raw['Airport'] = self.db.select('airport')
        self._raw['Airplane'] = self.db.select('airplane')
        self._raw['Crew'] = self.db.select('crew')

        self._fill_table(self.tableReys,      self._raw['Flight'])
        self._fill_table(self.tablePassenger, self._raw['Passenger'])
        self._fill_table(self.tableTickets,   self._raw['Ticket'])
        self._fill_table(self.tableAirport,   self._raw['Airport'])
        self._fill_table(self.tablePlane,     self._raw['Airplane'])
        self._fill_table(self.tableStaff,     self._raw['Crew'])

        self._refresh_country_combo()

    def _refresh_country_combo(self):
        current = self.cmbAirportCountry.currentText()
        self.cmbAirportCountry.blockSignals(True)
        self.cmbAirportCountry.clear()
        self.cmbAirportCountry.addItem("Все страны")
        countries = sorted({str(row[3])
                           for row in self._raw.get('Airport', [])})
        self.cmbAirportCountry.addItems(countries)
        idx = self.cmbAirportCountry.findText(current)
        if idx >= 0:
            self.cmbAirportCountry.setCurrentIndex(idx)
        self.cmbAirportCountry.blockSignals(False)

    def _fill_table(self, tw, data):
        tw.setSortingEnabled(False)

        tw.clearContents()
        tw.setRowCount(len(data))

        for r, row in enumerate(data):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val is not None else '')
                tw.setItem(r, c, item)

        tw.setSortingEnabled(True)
    # ── Filtering ─────────────────────────────────────────────
    # ── Filtering ─────────────────────────────────────────────

    def _apply_filters(self):
        search = self.searchField.text().strip().lower()

        table_map = {
            'Flight': self.tableReys,
            'Passenger': self.tablePassenger,
            'Ticket': self.tableTickets,
            'Airport': self.tableAirport,
            'Airplane': self.tablePlane,
            'Crew': self.tableStaff,
        }

        tw = table_map.get(self.current_table)

        if not tw:
            return

        for row in range(tw.rowCount()):
            show_row = True

            # Поиск
            if search:
                show_row = False

                for col in range(tw.columnCount()):
                    item = tw.item(row, col)

                    if item and search in item.text().lower():
                        show_row = True
                        break

            # Дополнительные фильтры
            if self.current_table == 'Flight':
                status = self.cmbFlightStatus.currentText()

                if status != "Все":
                    item = tw.item(row, 7)

                    if item and item.text() != status:
                        show_row = False

            elif self.current_table == 'Ticket':
                status = self.cmbTicketStatus.currentText()
                travel_class = self.cmbTicketClass.currentText()

                if status != "Все":
                    item = tw.item(row, 8)

                    if item and item.text() != status:
                        show_row = False

                if travel_class != "Все":
                    item = tw.item(row, 5)

                    if item and item.text() != travel_class:
                        show_row = False

            elif self.current_table == 'Airport':
                country = self.cmbAirportCountry.currentText()

                if country != "Все страны":
                    item = tw.item(row, 3)

                    if item and item.text() != country:
                        show_row = False

            elif self.current_table == 'Crew':
                gender = self.cmbStaffGender.currentText()
                position = self.lineEditPosition.text().strip().lower()

                if gender != "Все":
                    item = tw.item(row, 6)

                    if item and item.text() != gender:
                        show_row = False

                if position:
                    item = tw.item(row, 5)

                    if not item or position not in item.text().lower():
                        show_row = False

            # Показываем / скрываем строку
            tw.setRowHidden(row, not show_row)

        tw.clearSelection()

        # ── Reset ─────────────────────────────────────────────────
    # ── Reset ─────────────────────────────────────────────────
    def _reset_filters(self):
        self.searchField.clear()

        self.cmbFlightStatus.setCurrentIndex(0)
        self.cmbTicketStatus.setCurrentIndex(0)
        self.cmbTicketClass.setCurrentIndex(0)
        self.cmbAirportCountry.setCurrentIndex(0)
        self.cmbStaffGender.setCurrentIndex(0)

        self.lineEditPosition.clear()

        table_map = {
            'Flight': self.tableReys,
            'Passenger': self.tablePassenger,
            'Ticket': self.tableTickets,
            'Airport': self.tableAirport,
            'Airplane': self.tablePlane,
            'Crew': self.tableStaff,
        }

        for tw in table_map.values():
            for row in range(tw.rowCount()):
                tw.setRowHidden(row, False)

        self._hard_refresh()

    # ── Hard refresh ──────────────────────────────────────────
    def _hard_refresh(self):
        self._load_all_data()

    # ── Helpers ───────────────────────────────────────────────
    def _current_table_widget(self):
        return {
            'Flight':    self.tableReys,
            'Passenger': self.tablePassenger,
            'Ticket':    self.tableTickets,
            'Airport':   self.tableAirport,
            'Airplane':  self.tablePlane,
            'Crew':      self.tableStaff,
        }.get(self.current_table)

    def _get_selected_id(self):
        tw = self._current_table_widget()
        if tw is None:
            return None
        rows = tw.selectedItems()
        if not rows:
            QMessageBox.warning(self, "Предупреждение",
                                "Пожалуйста, выберите запись")
            return None
        row = rows[0].row()
        id_item = tw.item(row, 0)
        return int(id_item.text()) if id_item else None

    # ── CRUD ──────────────────────────────────────────────────
    def _add_record(self):
        if self.current_table == 'Reports':
            QMessageBox.information(
                self, "Информация", "На странице отчётов нельзя добавлять записи")
            return
        dialogs = {
            'Flight': FlightDialog, 'Passenger': PassengerDialog, 'Ticket': TicketDialog,
            'Airport': AirportDialog, 'Airplane': AirplaneDialog, 'Crew': CrewDialog
        }
        if self.current_table in dialogs:
            dlg = dialogs[self.current_table](self.db, parent=self)
            if dlg.exec():
                self._hard_refresh()

    def _edit_record(self):
        dialogs = {
            'Flight': FlightDialog, 'Passenger': PassengerDialog, 'Ticket': TicketDialog,
            'Airport': AirportDialog, 'Airplane': AirplaneDialog, 'Crew': CrewDialog
        }
        if self.current_table in dialogs:
            rec_id = self._get_selected_id()
            if rec_id:
                dlg = dialogs[self.current_table](self.db, rec_id, self)
                if dlg.exec():
                    self._hard_refresh()

    def _delete_record(self):
        delete_funcs = {
            'Flight':    self.db.delete_flight,
            'Passenger': self.db.delete_passenger,
            'Ticket':    self.db.delete_ticket,
            'Airport':   self.db.delete_airport,
            'Airplane':  self.db.delete_airplane,
            'Crew':      self.db.delete_crew,
        }
        if self.current_table in delete_funcs:
            rec_id = self._get_selected_id()
            if rec_id:
                reply = QMessageBox.question(
                    self, "Подтверждение", "Вы уверены, что хотите удалить эту запись?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        delete_funcs[self.current_table](rec_id)
                        QMessageBox.information(
                            self, "Успех", "Запись успешно удалена!")
                        self._hard_refresh()
                    except Exception as e:
                        QMessageBox.critical(
                            self, "Ошибка", f"Ошибка при удалении:\n{e}")

    # ── Reports ───────────────────────────────────────────────
    def _generate_report(self):
        report_type = self.comboReportType.currentText()
        date_from = self.dateFrom.date().toString("yyyy-MM-dd")
        date_to = self.dateTo.date().toString("yyyy-MM-dd")

        if date_from > date_to:
            QMessageBox.warning(
                self, "Ошибка", "Дата 'С' не может быть позже даты 'По'")
            return

        try:
            with self.db.connection.cursor() as cursor:
                if report_type == "Рейсы по датам":
                    cursor.execute("""
                        SELECT f.flight_number, a.name, p.model,
                               f.departure_date, f.departure_time, f.status
                        FROM flight f
                        JOIN airport  a ON f.airport_id  = a.airport_id
                        JOIN airplane p ON f.airplane_id = p.airplane_id
                        WHERE f.departure_date BETWEEN %s AND %s
                        ORDER BY f.departure_date, f.departure_time
                    """, (date_from, date_to))
                    headers = ["Номер рейса", "Аэропорт", "Самолёт",
                               "Дата вылета", "Время вылета", "Статус"]

                elif report_type == "Продажи билетов":
                    cursor.execute("""
                        SELECT f.flight_number,
                               COUNT(t.ticket_id)    AS tickets_sold,
                               SUM(t.price)          AS total_revenue,
                               ROUND(AVG(t.price),2) AS avg_price
                        FROM ticket t
                        JOIN flight f ON t.flight_id = f.flight_id
                        WHERE t.purchase_date BETWEEN %s AND %s
                        GROUP BY f.flight_id, f.flight_number
                        ORDER BY total_revenue DESC
                    """, (date_from, date_to))
                    headers = ["Рейс", "Продано билетов",
                               "Выручка", "Средняя цена"]

                elif report_type == "Загруженность самолётов":
                    cursor.execute("""
                        SELECT p.model,
                               COUNT(DISTINCT f.flight_id) AS flights_count,
                               COUNT(t.ticket_id)          AS total_passengers
                        FROM airplane p
                        LEFT JOIN flight f ON p.airplane_id = f.airplane_id
                        LEFT JOIN ticket t ON f.flight_id   = t.flight_id
                        WHERE f.departure_date BETWEEN %s AND %s
                        GROUP BY p.airplane_id, p.model
                        ORDER BY total_passengers DESC
                    """, (date_from, date_to))
                    headers = ["Модель", "Кол-во рейсов", "Всего пассажиров"]
                else:
                    return

                data = cursor.fetchall()

            self.tableReport.setColumnCount(len(headers))
            self.tableReport.setHorizontalHeaderLabels(headers)
            self.tableReport.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch)
            self._fill_table(self.tableReport, data)

            if not data:
                QMessageBox.information(
                    self, "Информация", "За выбранный период данных не найдено")

        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при формировании отчёта:\n{e}")


# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
