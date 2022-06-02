# -*- coding: utf-8 -*-
# рабочее окно

import sqlite3

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox

from primary_window import QMainWindow
from task_window import Ui_MainWindow


class Task_Widget(QMainWindow, Ui_MainWindow):
    # форма task_window.ui
    def __init__(self, res, parent=None):
        self.res = res  # передача данных между модулями окон - ID ребенка из первого окна во второе
        super().__init__()
        self.setupUi(self)
        self.answers = [0] * 27  # список ответов пользователя
        # список заданий КЕГЭ
        self.tasks = []
        # подключение к БД
        self.db_connection()
        # вызов обработчика событий - в нем храним связи сигналы - слоты для второго окна
        self._connectAction2()
        # вызов метода выбора заданий в комбобоксе
        self.change_task()
        # создание объекта всплывающего окна
        self.msgBox = QMessageBox()
        # default
        self.mess = 'Error!'
        self.number = 0
        self.score = 0

    # создание подключения и курсора для работы с БД
    def db_connection(self):
        self.con = sqlite3.connect("db\ege21.db")
        self.cur = self.con.cursor()

    # связи сигналы - слоты для первого окна
    def _connectAction2(self):
        # обработка нажатия кнопки Сохранить задание
        self.pushButton.clicked.connect(self.save_ans)
        # обработка нажатия кнопки Следующее задание
        self.pushButton_2.clicked.connect(self.next_task)
        # обработка нажатия кнопки Предыдущее задание
        self.pushButton_3.clicked.connect(self.pre_task)
        # обработка нажатия кнопки Завершить тест
        self.pushButton_4.clicked.connect(self.finish)

    def change_task(self):
        # блок выбора задания из выпадающего списка комбобокса, сформированного по ID из базы данных
        self.tasks = list(
            map(lambda x: str(x[0]), self.cur.execute("""SELECT ID task FROM kege""").fetchall()))
        self.comboBox.clear()
        self.comboBox.addItems(self.tasks)
        # вызов загрузки задания - первого в списке комбобокса по умолчанию
        self.select_task('0')
        # вызов обработчика выбора задания в комбобоксе
        self.comboBox.activated.connect(self.select_task)

    def select_task(self, task):
        # обработчик выбора задания в комбобоксе
        self.number = int(task)
        task = str(self.number + 1)
        result = self.cur.execute("""SELECT task FROM kege
                                WHERE ID = ?""", (task,)).fetchone()[0]
        # отображение заголовка с номером выбранного задания
        self.label.setText(f'Выбрано задание {task}')
        # отображение текста задачи выбранного задания
        self.label_3.setWordWrap(True)
        self.label_3.setText(f"{result}")
        # запрос на файл с рисунком к задаче - если есть
        result_1 = self.cur.execute("""SELECT image FROM kege
                                WHERE ID = ?""", (task,)).fetchone()[0]
        # проверка на существование файла к задаче - если есть
        result_2 = self.cur.execute("""SELECT file FROM kege
                                                WHERE ID = ?""", (task,)).fetchone()[0]
        # если файл есть, то загрузить его
        if result_2:
            # print(result_2)
            self.label_2.setText(f"<a href={result_2}>Скачать файл задания</a>")
            self.label_2.setOpenExternalLinks(True)
        else:
            self.label_2.clear()
        # открытие рисунка к задаче
        if result_1:
            wey = result_1
        elif not result_1:
            wey = 'im.jpg'
        self.pixmap = QPixmap(f'img\{wey}')
        # увеличение размера до размера виджета
        size_window = self.label_4.size()
        self.label_4.setMaximumSize(size_window)
        # отображаем содержимое QPixmap в объекте QLabel по размерам окна
        self.label_4.setPixmap(QPixmap(self.pixmap.scaled(self.label_4.size(), Qt.KeepAspectRatio)))

    def save_ans(self):
        # обработчик сохранения ответа
        # print(self.number)
        try:
            if self.lineEdit.text():
                self.answers[self.number] = self.lineEdit.text()
                # print(self.answers)
                good_answer = self.cur.execute("""SELECT answer FROM kege
                                        WHERE ID = ?""", (str(self.number + 1),)).fetchone()[0]
            else:
                self.mess = 'Поле ответа пусто! Введите ответ, пожалуйста, и нажмите кнопку "Сохранить ответ"'
                raise ValueError(self.mess)
            # print(self.answers, good_answer, self.number + 1)
            if self.answers[self.number] == good_answer:
                self.score += 1
            # print(self.score)
            self.mess = 'Ответ успешно сохранен'
            self.message()
            self.lineEdit.clear()
        except ValueError:
            self.err()

    def next_task(self):
        # выбор следующей задачи кнопкой
        self.number = (self.number + 1) % len(self.tasks)
        self.select_task(str(self.number))

    def pre_task(self):
        # выбор следующей задачи кнопкой
        self.number = (self.number - 1) % len(self.tasks)
        self.select_task(str(self.number))

    def err(self):
        # обработка ошибок
        self.msgBox.setIcon(QMessageBox.Warning)
        self.msgBox.setWindowTitle("Ошибка!")
        self.msgBox.setText(f'{self.mess}')
        self.msgBox.exec()

    def finish(self):
        # завершение теста
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setWindowTitle("Внимание!")
        self.mess = 'Для завершения теста - ОК, для продолжения работы - Cancel'
        self.msgBox.setText(f'{self.mess}')
        self.msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        # обработка нажатия кнопок ОК/Cancel
        self.msgBox.buttonClicked.connect(self.msgbtn)
        self.msgBox.exec()

    def msgbtn(self, i):
        if i.text() == 'OK':
            # запись в базу данных первичных баллов по ID ребенка
            # print(self.res)
            self.cur.execute(
                """UPDATE students SET score = ? WHERE ID = ?""", (self.score, self.res))
            self.con.commit()
            """self.mess = 'Результат успешно внесен в базу данных!'
            self.message()"""
            # перевод первичных баллов во вторичные и запись в базу данных по ID ребенка
            data = list(map(lambda x: x.split(':'), open('data\scala.txt').read().split()))
            scala = {}
            for x in data:
                scala[int(x[0])] = int(x[1])
            self.cur.execute(
                """UPDATE students SET second_score = ? WHERE ID = ?""", (scala[self.score], self.res))
            self.con.commit()
        self.hide()

    def message(self):
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setWindowTitle("Информация")
        self.msgBox.setText(f'{self.mess}')
        self.msgBox.exec()

    def save_result(self):
        # внесение результата работы в базу данных
        self.mess = 'Результат успешно внесен в базу данных!'
        self.message()
