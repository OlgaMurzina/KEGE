# окно с данными ребенка

import sqlite3

from PyQt5.QtWidgets import QMainWindow, QMessageBox

import secondary_window
from main_window import Ui_mainWindow


class MyWidget(QMainWindow, Ui_mainWindow):
    # форма main_window.ui
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # вызов обработчика событий - в нем храним связи сигналы - слоты
        self._connectAction()
        # подключение к БД
        self.db_connection()
        # self.label_8.setWordWrap(True)
        self.msgBox = QMessageBox()  # всплывающие окна обработчика действий
        # default
        self.pushButton_2.setText('Показать результат')
        self.flag = True
        self.fam = None
        self.mess = 'Error!'
        self.res = ''

    # создание подключения и курсора для работы с БД
    def db_connection(self):
        self.con = sqlite3.connect("db\ege21.db")
        self.cur = self.con.cursor()

    # связи сигналы - слоты для первого окна
    def _connectAction(self):
        # обработка нажатия кнопки ОК - подтверждения ввода данных ребенка
        self.pushButton.clicked.connect(self.ok)
        # обработка нажатия кнопки Начать работу
        self.pushButton_3.clicked.connect(self.show_window_2)
        # обработка нажатия кнопки Внести результат в базу данных
        self.pushButton_2.clicked.connect(self.result)

    def ok(self):
        # ввод фамилии ребенка
        self.fam = self.lineEdit.text()
        # ввод имени ребенка
        self.name = self.lineEdit_2.text()
        # проверка корректности ввода фамилии и имени
        try:
            if not self.fam and self.name:
                self.mess = 'Не введены фамилия и имя ребенка!'
                raise ValueError(self.mess)
            elif not self.fam:
                self.mess = 'Не введена фамилия ребенка!'
                raise ValueError(self.mess)
            elif not self.name:
                self.mess = 'Не введено имя ребенка!'
                raise ValueError(self.mess)
            elif not self.fam.isalpha() and not self.name.isalpha():
                self.mess = 'Ошибка при вводе имени и фамилии: присутствуют посторонние символы!'
                raise ValueError(self.mess)
            elif self.fam.isalpha() and not self.name.isalpha():
                self.mess = 'Ошибка при вводе имени: присутствуют посторонние символы!'
                raise ValueError(self.mess)
            elif self.name.isalpha() and not self.fam.isalpha():
                self.mess = 'Ошибка при вводе фамилии: присутствуют посторонние символы!'
                raise ValueError(self.mess)
            else:
                # поиск ребенка по базе - если есть, то фиксируем ID, если нет, то добавляем в базу новый ID и данные
                self.res = self.cur.execute("""SELECT ID FROM students WHERE surname = ? and name = ?""",
                                            (self.fam, self.name)).fetchone()[0]
                print(self.res)
                if not self.res:
                    # внесение ребенка в базу данных
                    self.con.execute(
                        """INSERT INTO students(surname, name) VALUES (?, ?)""",
                        (self.fam, self.name))
                    self.mess = 'Фамилия и имя успешно внесены в базу данных!'
                else:
                    # приветствие, если ребенок уже есть в базе данных
                    self.mess = 'Рады видеть Вас снова!'
                # обновление базы данных
                self.con.commit()
            # вызов обработчика - всплывающего окна
            self.msgBox.setIcon(QMessageBox.Information)
            self.msgBox.setWindowTitle("Ввод данных")
            self.msgBox.setText(f'{self.mess}')
            self.msgBox.exec()
            self.wind_2 = secondary_window.Task_Widget(self.res)
        except ValueError:
            # обработка ошибок
            self.err()

    def err(self):
        # обработка ошибок
        self.msgBox.setIcon(QMessageBox.Warning)
        self.msgBox.setWindowTitle("Ошибка!")
        self.msgBox.setText(f'{self.mess}')
        self.msgBox.exec()

    def result(self):
        # внесение результата работы в базу данных
        score = self.cur.execute(
            """SELECT score, second_score FROM students WHERE ID = ?""",
            str(self.res)).fetchone()
        # print(score)
        self.con.commit()
        if self.flag:
            self.label_4.setText(f'{score[0]}')
            self.label_6.setText(f'{score[1]}')
            self.pushButton_2.setText('Сохранить результат')
            self.flag = False
        else:
            self.mess = 'Результат успешно внесен в базу данных!'
            self.message()
            self.pushButton_2.setText('Показать результат')
            self.flag = True

    def show_window_2(self):
        # открытие рабочего окна
        if not self.res:
            self.mess = "Некорректно введены данные ребенка! Введите данные и нажмите кнопку ОК для проверки!"
            self.err()
        else:
            self.wind_2.show()

    def message(self):
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setWindowTitle("Информация")
        self.msgBox.setText(f'{self.mess}')
        self.msgBox.exec()
