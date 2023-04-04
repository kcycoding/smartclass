from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice, QLineSeries, QValueAxis
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
import sys, cv2
import serial
import pymysql
import socket
from _thread import *
from queue import Queue
import threading
import numpy as np
import time
import datetime
import select
import ast


# HOST = '192.168.0.52'
# HOST = '192.168.0.17'
HOST = '192.168.0.9'
PORT = 9900

try:
    py_serial = serial.Serial(port='COM9', baudrate=115200)
except:
    pass

enclosure_queue = Queue()
lock = threading.Lock()
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket = None
server_socket = 0

data1 = 0
ac_timer = ""
li_timer = ""

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.mouse_pos = None
        self.login_ui()

        #웹캠
        self.zoom_factor = 1.0
        self.check_cam = "0"
        self.cam_toggle = "border-image: url(./QTbutton/off.png);\n"

        #전력량
        self.ac_toggle = "border-image: url(./QTbutton/off.png);\n"
        self.ac_label = "border: 1px solid #fefefe;\n"
        self.ac_timer_img = "border-image: url(./QTbutton/timer2.png);\n"
        self.ac_condition = "border-image: url(./QTbutton/heating.png);\n"

        self.li_toggle = "border-image: url(./QTbutton/off.png);\n"
        self.li_label = "border: 1px solid #fefefe;\n"
        self.li_timer_img = "border-image: url(./QTbutton/timer2.png);\n"
        self.li_condition = "border-image: url(./QTbutton/brightness.png);\n"


        self.total_usage = {"ac": [], "light": [], "beam": []}
        self.ac_power = 0
        self.li_power = 0
        # self.beam_power = 0



        # 바 x

        # 마우스로 창을 이동할 수 있도록 합니다.

    # 마우스로 창이동
    def mousePressEvent(self, event):
        self.mouse_pos = event.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.mouse_pos)

    def login_ui(self):
        self.setGeometry(300, 200, 1200, 550)  # 창의 위치와 크기
        self.setWindowTitle("main Window")  # 창 제목
        self.setStyleSheet("background-color: rgb(63, 73, 98);""font: 75 14pt 'Agency FB';""color: rgb(255, 255, 255);""border:none;\n")
        # 바 x
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #마우스로 창을 이동할 수 있도록 합니다.

        self.thread_id = None
        self.stop_thread = False
        ###########로그인#############
        self.login_frame = QFrame(self)
        self.login_frame.setGeometry(QtCore.QRect(330, 90, 330, 310))
        self.login_frame.setStyleSheet("background-color: rgb(63, 73, 98);")

        #로그인 id/pw
        self.login_id = QLineEdit(self.login_frame)
        self.login_id.setPlaceholderText("ID")
        self.login_id.setGeometry(QtCore.QRect(110, 100, 110, 30))
        self.login_id.setStyleSheet("background-color: rgba(0, 0, 0,0);\n""border-bottom:1px solid rgba(255, 255, 255);\n""color:white")

        self.login_pw = QLineEdit(self.login_frame)
        self.login_pw.setEchoMode(QLineEdit.Password)
        self.login_pw.setPlaceholderText("PW")
        self.login_pw.setGeometry(QtCore.QRect(110, 150, 110, 30))
        self.login_pw.setStyleSheet("background-color: rgba(0, 0, 0,0);\n""border-bottom:1px solid rgba(255, 255, 255,);\n""color:white")
        self.login_pw.returnPressed.connect(self.loginchek)  # 엔터

        self.login_btn = QPushButton("L o g i n", self.login_frame)
        self.login_btn.setGeometry(QtCore.QRect(110, 200, 110, 30))
        self.login_btn.setStyleSheet("background-color: rgb(0,0,0,0);\n""border-bottom:1px solid rgb(255, 255, 255);")
        self.login_btn.clicked.connect(self.loginchek)  # 로그인 확인

        hover_animation = QtCore.QPropertyAnimation(self.login_btn, b"geometry")
        hover_animation.setDuration(200)
        # 마우스 오버/리브 효과 시그널 연결
        self.login_btn.enterEvent = lambda event: hover_animation.start()
        self.login_btn.leaveEvent = lambda event: hover_animation.reverse()
        # # 버튼 이미지 변경  background-color: rgb(245, 196, 132)
        self.login_btn.enterEvent = lambda event: self.login_btn.setStyleSheet("color: rgb(254,156,29);""background-color: rgba(0, 0, 0,0);""border:none;""border-bottom:1px solid rgba(254,156,29);")
        self.login_btn.leaveEvent = lambda event: self.login_btn.setStyleSheet("color: rgb(255, 255, 255);""background-color: rgba(0, 0, 0,0);""border:none;""border-bottom:1px solid rgb(255, 255, 255);")

         # 로그인창 닫기
        self.login_close = QPushButton(self.login_frame)
        self.login_close.setGeometry(QtCore.QRect(300, 0, 30, 30))
        self.login_close.setStyleSheet("background-color: rgb(0,0,0,0);\n""border-image: url(./QTbutton/close.png);\n")
        self.login_close.clicked.connect(self.exit_frame)
        hover_animation1 = QtCore.QPropertyAnimation(self.login_close, b"geometry")
        hover_animation1.setDuration(200)
        # 마우스 오버/리브 효과 시그널 연결
        self.login_close.enterEvent = lambda event: hover_animation1.start()
        self.login_close.leaveEvent = lambda event: hover_animation1.reverse()
        # # 버튼 이미지 변경  background-color: rgb(245, 196, 132)
        self.login_close.enterEvent = lambda event: self.login_close.setStyleSheet(
            "background-color: rgb(0,0,0,0);\n""border-image: url(./QTbutton/close1.png);\n")
        self.login_close.leaveEvent = lambda event: self.login_close.setStyleSheet(
            "background-color: rgb(0,0,0,0);\n""border-image: url(./QTbutton/close.png);\n")

    #############로그인###########

    #####버튼 효과  #애니메이션######
    def on_button_clicked(self, event):
        self.animation.start()
        print("애니 확인")

    def on_button_entered(self, event):
        self.add_finger.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/fingerprint.png);\n")

    def on_button_left(self, event):
        self.add_finger.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/fingerprint1.png);\n")

    def on_button_entered1(self, event):  # user
        self.user_btn.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(254, 156, 29);""border: none;")

    def on_button_left1(self, event):  # user
        self.user_btn.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;")

    def on_button_entered2(self, event):  # user
        self.home_but.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/home1.png);\n")
        # self.home_but.clicked.connect(self.home_but)

    def on_button_left2(self, event):  # user
        self.home_but.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/home.png);\n")

    def on_button_entered3(self, event):  # user
        self.Notice_but.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/calendar1.png);\n")

    def on_button_left3(self, event):
        self.Notice_but.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/calendar.png);\n")

    def on_button_entered4(self, event):
        self.chat_but.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/search1.png);\n")

    def on_button_left4(self, event):
        self.chat_but.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/search.png);\n")

    def on_button_entered5(self, event):
        self.cam_but.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/webcam1.png);\n")

    def on_button_left5(self, event):  # user
        self.cam_but.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/webcam.png);\n")

    def on_button_entered6(self, event):
        self.att_but.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/chart1.png);\n")

    def on_button_left6(self, event):
        self.att_but.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/chart.png);\n")

    def on_button_entered7(self, event):
        self.user_join.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/add-contact1.png);\n")

    def on_button_left7(self, event):
        self.user_join.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/add-contact.png);\n")

    def on_button_entered8(self, event):
        self.set_but.setStyleSheet("background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/settings1.png);\n")

    def on_button_left8(self, event):
        self.set_but.setStyleSheet("background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/settings.png);\n")

    def on_button_entered9(self, event):
        self.exit_btn.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(254, 156, 29);""border: none;")

    def on_button_left9(self, event):
        self.exit_btn.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;")

    def on_button_entered10(self, event):
        self.join_button.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(254, 156, 29);""border: none;""border-bottom:1px solid rgb(254, 156, 29);")
    def on_button_left10(self, event):
        self.join_button.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;""border-bottom:1px solid rgb(255, 255, 255);")

    def on_button_entered11(self, event):
        self.add_but.setStyleSheet(
            "font: 75 15pt 'Agency FB';""color:rgb(254, 156, 29);""border: none;""border-bottom:1px solid rgb(254, 156, 29);")

    def on_button_left11(self, event):
        self.add_but.setStyleSheet(
            "font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;""border-bottom:1px solid rgb(255, 255, 255);")
    def on_button_entered12(self, event):
        self.delete_button.setStyleSheet(
            "font: 75 15pt 'Agency FB';""color:rgb(254, 156, 29);""border: none;""border-bottom:1px solid rgb(254, 156, 29);")

    def on_button_left12(self, event):
        self.delete_button.setStyleSheet(
            "font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;""border-bottom:1px solid rgb(255, 255, 255);")

    #######웹캠#####################
    def Webcam(self, queue):  # 카메라에서 무한으로 이미지를 캡쳐해서 threaded로 보내기
        try:
            while not self.stop_thread:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                result, imgencode = cv2.imencode('.jpg', cam, encode_param)
                data = np.array(imgencode)
                # print("data : ", data)
                bytes_data = data.tobytes()
                queue.put(bytes_data)
                client_socket.send("e".encode())
        except Exception as e:
            # print("web 오류", e)
            # QMessageBox.critical(self, '카메라 연결 안됨', "", QMessageBox.Ok)
            pass

    # 클라이언트 메세지
    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            # print(len(newbuf), ":buffsize", newbuf, "newbuf_data")
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def loginchek(self):
        global client_socket
        id = self.login_id.text()
        pw = self.login_pw.text()
        today_date = datetime.datetime.now().date()

        if id == "asdf" and pw == "asdf":
            print("관리자")
            start_new_thread(open_server, ())
            start_new_thread(Arduino, ())
            con = pymysql.connect(host='localhost', user='root', password='0000', charset='utf8')
            cur = con.cursor()
            cur.execute("SHOW DATABASES LIKE 'smartclass'")
            a = cur.fetchall()
            if len(a) == 0:
                cur.execute('CREATE DATABASE smartclass')
                con.commit()
            else:
                pass

            conn = pymysql.connect(host='localhost', user='root', password='0000', db='smartclass', charset='utf8')
            with conn:
                with conn.cursor() as curr:
                    try:
                        sql1 = '''CREATE TABLE IF NOT EXISTS classroom (
                                   num int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                                   class_name varchar(15) NOT NULL,
                                   personnel int(5),
                                   course_days int(5))'''
                        sql2 = '''CREATE TABLE IF NOT EXISTS user (
                                   id varchar(5) PRIMARY KEY,
                                   pw varchar(15) NOT NULL,
                                   name varchar(5) NOT NULL,
                                   classroom varchar(15) NOT NULL,
                                   phone varchar(12) NOT NULL)'''
                        sql3 = '''CREATE TABLE IF NOT EXISTS notice (
                                num int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                                class_name varchar(15) NOT NULL,
                                date varchar(15) NOT NULL,
                                title varchar(30) NULL,
                                content varchar(255) NULL)'''
                        sql4 = '''CREATE TABLE IF NOT EXISTS attendance (
                                num int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                                date varchar(20) NOT NULL,
                                id varchar(5) NOT NULL,
                                entry_time varchar(20) NULL,
                                exit_time varchar(20) NULL,
                                name varchar(5) NOT NULL,
                                classroom varchar(10) NOT NULL)'''
                        sql5 = '''CREATE TABLE IF NOT EXISTS total_usage (
                                date varchar(20) PRIMARY KEY,
                                ac int(10) NULL,
                                light int(10) NULL)'''

                        curr.execute(sql1)
                        curr.execute(sql2)
                        curr.execute(sql3)
                        curr.execute(sql4)
                        curr.execute(sql5)

                        sql_insert = f"INSERT INTO total_usage (date) VALUES ('{today_date}') ON DUPLICATE KEY UPDATE date='{today_date}'"
                        curr.execute(sql_insert)
                        conn.commit()

                        curr.execute("SELECT id, name, classroom ,phone FROM user")
                        user_ids = curr.fetchall()

                        curr.execute("SELECT id, date, name, classroom phone FROM attendance WHERE date=%s", (today_date,))
                        existing_records = curr.fetchall()

                        existing_ids = [r[0] for r in existing_records]
                        # 중복 제거
                        # 지문 수정
                        for user_id in user_ids:
                            if user_id[0] not in existing_ids:
                                sql = "INSERT INTO attendance (id, date, name, classroom, entry_time, exit_time ) VALUES (%s, %s, %s, %s, %s, %s)"
                                val = (user_id[0], today_date, user_id[1], user_id[2], "-", "-")
                                curr.execute(sql, val)
                                conn.commit()
                    except Exception as e:
                        conn.commit()
                        print("sql 생성", e)

                    self.login_frame.close()
                    self.start_server_ui()
        else:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("로그인 시도 : ", id, pw)
            try:
                client_socket.connect((HOST, PORT))
                client_socket.send(f"user_login/{id}/{pw}".encode())
                time.sleep(1)
                lc = client_socket.recv(1096)
                # print(lc)
                if "1" in bytes(lc).decode():
                    self.login_frame.close()
                    self.start_client_ui()
                    # start_new_thread(self.message, ())
                else:
                    self.login_id.clear()
                    self.login_pw.clear()
                    client_socket.close()
                    QMessageBox.information(self, '오류', '로그인 실패', QMessageBox.Ok)
            except:
                print("서버 오픈 안함")
                QMessageBox.information(self, '서버', '서버 오픈 안함', QMessageBox.Ok)
                self.login_id.clear()
                self.login_pw.clear()
                client_socket.close()
                pass

    ##############버튼#######################

    # 메인 프레임 카테고리 버튼
    def start_server_ui(self):
        try:
            self.start_frame = QFrame(self) #전체적 프레임
            self.start_frame.setGeometry(QtCore.QRect(0, 0, 1000, 550))
            self.start_frame.setStyleSheet("background-color: rgb(63, 73, 98);""color: rgb(255, 255, 255);")

            # 카테고리 라벨 사이드
            self.title_label = QLabel(self.start_frame)
            self.title_label.setGeometry(QtCore.QRect(0, 100, 80, 440))
            self.title_label.setStyleSheet("border-right:1px solid rgb(254,156,29);")

            # 상단라벨 라벨
            self.top_label = QLabel(self.start_frame)
            self.top_label.setGeometry(QtCore.QRect(0, 0, 1000, 101))
            self.top_label.setStyleSheet(
                "background-color:rgb(63, 73, 98);\n""border-bottom:1px solid  rgb(254,156,29);")

            # 임시 출석 %
            self.label_color = QLabel(self.start_frame)
            self.label_color.setGeometry(QtCore.QRect(0, 96, 1000, 5))
            self.label_color.setStyleSheet("background-color: rgb(254,156,29);")

            self.progress = QLabel("0%", self.start_frame)
            self.progress.setGeometry(QtCore.QRect(805, 57, 40, 30))
            self.progress.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;")
            # self.user_btn.clicked.connect(self.logout)

            # user라벨
            self.user_btn = QPushButton("LOGOUT", self.start_frame)
            self.user_btn.setGeometry(QtCore.QRect(865, 20, 50, 30))
            self.user_btn.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;")
            self.user_btn.clicked.connect(self.logout)

            self.animation = QtCore.QPropertyAnimation(self.user_btn, b"geometry")
            # self.user_but.mousePressEvent = self.on_button_clicked
            self.user_btn.enterEvent = self.on_button_entered1
            self.user_btn.leaveEvent = self.on_button_left1

            # user id 라벨
            self.user_label = QLabel(self.login_id.text(), self.start_frame)  # 로그인시 유저 아이디나 이름
            self.user_label.setGeometry(QtCore.QRect(805, 20, 40, 30))
            self.user_label.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);")
            # self.user_label.setAlignment(QtCore.Qt.AlignCenter)  # 글씨가운데
            #self.user_label.setAlignment(QtCore.Qt.AlignCenter)  # 글씨가운데

            ###########카테고리 버튼###############
            # 홈
            self.home_but = QPushButton(self.start_frame)
            self.home_but.setGeometry(QtCore.QRect(20, 120, 40, 30))
            self.home_but.setStyleSheet(
                "border-image: url(./QTbutton/home.png);\n""background-color: rgba(0, 0, 0,0);\n""border:none;")
            self.home_but.clicked.connect(self.open_home_frame)

            self.animation = QtCore.QPropertyAnimation(self.home_but, b"geometry")
            self.home_but.enterEvent = self.on_button_entered2
            self.home_but.leaveEvent = self.on_button_left2

            # 공지
            self.Notice_but = QPushButton(self.start_frame)
            self.Notice_but.setGeometry(QtCore.QRect(20, 180, 40, 30))
            self.Notice_but.setStyleSheet(
                "border-image: url(./QTbutton/calendar.png);\n""background-color: rgba(0, 0, 0,0);\n""border:none;")
            self.Notice_but.clicked.connect(self.open_Notice_frame)

            self.animation = QtCore.QPropertyAnimation(self.Notice_but, b"geometry")
            self.Notice_but.enterEvent = self.on_button_entered3
            self.Notice_but.leaveEvent = self.on_button_left3

            # user 관리
            self.chat_but = QPushButton(self.start_frame)
            self.chat_but.setGeometry(QtCore.QRect(20, 240, 40, 30))
            self.chat_but.setStyleSheet(
                "border-image: url(./QTbutton/search.png);\n""background-color: rgba(0, 0, 0,0);\n""border:none;")
            self.chat_but.clicked.connect(self.open_chat_frame)

            self.animation = QtCore.QPropertyAnimation(self.chat_but, b"geometry")
            self.chat_but.enterEvent = self.on_button_entered4
            self.chat_but.leaveEvent = self.on_button_left4

            # 영상수업
            self.cam_but = QPushButton(self.start_frame)
            self.cam_but.setGeometry(QtCore.QRect(20, 300, 40, 30))
            self.cam_but.setStyleSheet(
                "border-image: url(./QTbutton/webcam.png);\n""background-color: rgba(0, 0, 0,0);\n""border:none;")
            self.cam_but.clicked.connect(self.open_cam_frame)

            self.animation = QtCore.QPropertyAnimation(self.cam_but, b"geometry")
            self.cam_but.enterEvent = self.on_button_entered5
            self.cam_but.leaveEvent = self.on_button_left5

            # 출결 현황
            self.att_but = QPushButton(self.start_frame)
            self.att_but.setGeometry(QtCore.QRect(20, 360, 40, 30))
            self.att_but.setStyleSheet(
                "border-image: url(./QTbutton/chart.png);\n""background-color: rgba(0, 0, 0,0);\n""border:none;")
            self.att_but.clicked.connect(self.open_att_frame)

            self.animation = QtCore.QPropertyAnimation(self.att_but, b"geometry")
            self.att_but.enterEvent = self.on_button_entered6
            self.att_but.leaveEvent = self.on_button_left6

            # 학생 관리 및 등록
            self.user_join = QPushButton(self.start_frame)
            self.user_join.setGeometry(QtCore.QRect(20, 420, 40, 30))
            self.user_join.setStyleSheet(
                "border-image: url(./QTbutton/add-contact.png);\n""background-color: rgba(0, 0, 0,0);\n""border:none;")
            self.user_join.clicked.connect(self.open_user_frame)

            self.animation = QtCore.QPropertyAnimation(self.user_join, b"geometry")
            self.user_join.enterEvent = self.on_button_entered7
            self.user_join.leaveEvent = self.on_button_left7

            # 리모컨작동 에어컨/빔프로젝트 setting
            self.set_but = QPushButton(self.start_frame)
            self.set_but.setGeometry(QtCore.QRect(20, 480, 40, 30))
            self.set_but.setStyleSheet(
                "border-image: url(./QTbutton/settings.png);\n""background-color: rgba(0, 0, 0,0);\n""border:none;")
            self.set_but.clicked.connect(self.open_set_frame)

            self.animation = QtCore.QPropertyAnimation(self.set_but, b"geometry")
            self.set_but.enterEvent = self.on_button_entered8
            self.set_but.leaveEvent = self.on_button_left8

            # 반 선택 로그인
            self.combobox1 = QComboBox(self.start_frame)
            self.combobox1.setGeometry(QtCore.QRect(864, 56, 100, 30))
            self.combobox1.setStyleSheet("color: rgb(255, 255, 255);""selection-background-color: rgb(112, 131, 175);""border:none;""font: 75 14pt 'Agency FB';")

            con = pymysql.connect(host='localhost', user='root', password='0000', charset='utf8')
            cur = con.cursor()
            cur.execute("SHOW DATABASES LIKE 'smartclass'")
            a = cur.fetchall()
            if len(a) == 0:
                cur.execute('CREATE DATABASE smartclass')
                con.commit()
            else:
                pass
            con = pymysql.connect(host='localhost', user='root', password='0000', db='smartclass', charset='utf8')
            with con:
                with con.cursor() as cur:
                    try:
                        sql5 = "SELECT * FROM "
                        x = "smartclass.classroom"
                        cur.execute(sql5 + x)
                        result = list(cur.fetchall())
                        for i in result:
                            # print(i)
                            self.combobox1.addItem(i[1])
                        con.commit()
                    except Exception as e:
                        print("sql : ", e)
                        pass

            self.combobox1.currentIndexChanged.connect(self.combobox1_value)

            # 나가기  #아이콘 임시
            self.exit_btn = QPushButton("EXIT",self.start_frame)
            self.exit_btn.setGeometry(QtCore.QRect(940,20, 20, 30))
            self.exit_btn.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;")
            self.exit_btn.clicked.connect(self.exit_frame)

            self.animation = QtCore.QPropertyAnimation(self.exit_btn, b"geometry")
            self.exit_btn.enterEvent = self.on_button_entered9
            self.exit_btn.leaveEvent = self.on_button_left9

            self.start_frame.show()
        except Exception as e:
            print("v버튼", e)

    def combobox1_value(self):
        self.label_color.deleteLater()

        total_process = 0
        current_progress = 0

        if self.combobox1.count() > 0:
            con = pymysql.connect(host='localhost', user='root', password='0000', db='smartclass', charset='utf8')
            cur = con.cursor()
            try:
                cur.execute("SELECT class_name, course_days FROM classroom")
                course_days = cur.fetchall()
                # print(course_days)
                if len(course_days) > 0:
                    for i in course_days:
                        if i[0] == self.combobox1.currentText():
                            total_process = i[1]
                print(total_process)

                cur.execute("SELECT COUNT(DISTINCT date) FROM attendance")
                result = cur.fetchone()
                current_progress = result[0]
                print(current_progress)
                progress_percent = round((current_progress / total_process) * 100, 1)

                # 임시 출석 %
                self.label_color = QLabel(self.start_frame)
                self.label_color.setGeometry(
                    QtCore.QRect(0, 96, 1000 - int(((current_progress / total_process) * 1000)), 5))
                self.label_color.setStyleSheet("background-color: rgb(254,156,29);")

                self.progress.setText(f"{progress_percent}%")

                self.label_color.show()
            except Exception as e:
                print("수업 진행률", e)
                pass
        else:
            self.progress.setText("0.0%")
            self.label_color.setGeometry(QtCore.QRect(0, 96, 1000, 5))
            self.label_color.setStyleSheet("background-color: rgb(254,156,29);")

    ########sever frame 서버 프레임########################
    # 서버 나가기
    def exit_frame(self):  # d임시
        self.close()

    def open_home_frame(self):
        self.home_frame = QFrame(self)
        self.home_frame.setGeometry(QtCore.QRect(100, 130, 880, 410))
        self.home_frame.setStyleSheet("background-color: rgb(63, 73, 98);")

        # 검색
        self.search_date = QComboBox(self.home_frame)
        self.search_date.setGeometry(QtCore.QRect(20, 30, 140, 30))
        self.search_date.setStyleSheet(
            "color: rgb(255, 255, 255);""selection-background-color: rgb(112, 131, 175);""border-bottom:1px solid rgba(255, 255, 255,);""font: 75 14pt 'Agency FB';")
        self.search_date.activated.connect(self.att_show)

        # 조회 버튼
        self.att_button = QPushButton("CHANGE", self.home_frame)
        self.att_button.setGeometry(QtCore.QRect(180, 30, 50, 30))
        self.att_button.setStyleSheet("font: 75 14pt 'Agency FB';""border:none;")
        self.att_button.clicked.connect(self.att_change)

        hover_animation = QtCore.QPropertyAnimation(self.att_button, b"geometry")
        hover_animation.setDuration(200)

        self.att_button.enterEvent = lambda event: hover_animation.start()
        self.att_button.leaveEvent = lambda event: hover_animation.reverse()
        # # 버튼 이미지 변경  background-color: rgb(245, 196, 132)
        self.att_button.enterEvent = lambda event: self.att_button.setStyleSheet(
            "color: rgb(254,156,29);""background-color: rgba(0, 0, 0,0);""border:none;""border-bottom:1px solid rgba(254,156,29);")
        self.att_button.leaveEvent = lambda event: self.att_button.setStyleSheet(
            "color: rgb(255, 255, 255);""background-color: rgba(0, 0, 0,0);""border:none;""border-bottom:1px solid rgb(255, 255, 255);")

        # 조회목록  조회
        home_colum = ["DAY","ID", "ENTRY_TIME", "EXIT_TIME", "NAME", "classname"]  # CHECK
        self.home_colum = QTableWidget(self.home_frame)
        self.home_colum.setGeometry(QtCore.QRect(20, 70, 630, 330))
        self.home_colum.setStyleSheet(
            "font: 75 14pt 'Agency FB';""border:none;""color:rgb(255,255,255);""border-bottom:1px solid rgb(255, 255, 255);")
        self.home_colum.setColumnCount(6)
        self.home_colum.setHorizontalHeaderLabels(home_colum)
        self.home_colum.setColumnWidth(0, 100)
        self.home_colum.setColumnWidth(1, 100)
        self.home_colum.setColumnWidth(2, 100)
        self.home_colum.setColumnWidth(3, 100)
        self.home_colum.setColumnWidth(4, 100)
        self.home_colum.setColumnWidth(5, 100)

        self.home_colum.setSelectionMode(QAbstractItemView.NoSelection)
        # self.home_colum.setEditTriggers(QAbstractItemView.NoEditTriggers)


        self.home_colum.verticalHeader().setVisible(False)  # 헤더 X
        header = self.home_colum.horizontalHeader()
        # header.setSectionResizeMode(QHeaderView.Stretch)  # 열의 크기를 채우기 위한 옵션
        header.setStyleSheet("QHeaderView:section { background-color: transparent };")

        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()

        sql1 = "SELECT * FROM "
        x = "smartclass.attendance"
        cur.execute(sql1 + x)
        result = list(cur.fetchall())

        try:
            for i, row in enumerate(result):
                self.home_colum.setRowCount(i + 1)
                # print(row[4])
                for j, item in enumerate(row[1:]):
                    a = QTableWidgetItem(str(item))
                    a.setTextAlignment(Qt.AlignCenter)
                    self.home_colum.setItem(i, j, a)

            # 빈칸제거
            for i in range(self.home_colum.rowCount() - 1, -1, -1):
                empty_row = True
                for j in range(self.home_colum.columnCount()):
                    if self.home_colum.item(i, j) is not None:
                        empty_row = False
                        break
                if empty_row:
                    self.home_colum.removeRow(i)
            con.commit()
        except Exception as e:
            print("출결 관리 : ", e)
            con.commit()

        date_col = 0
        data = []
        for row in range(self.home_colum.rowCount()):
            # QTableWidgetItem에서 텍스트 데이터를 가져옴
            text = self.home_colum.item(row, date_col).text()
            # 문자열을 datetime 객체로 변환
            date = datetime.datetime.strptime(text, "%Y-%m-%d").date()
            # 날짜와 다른 데이터를 하나의 튜플로 묶음
            row_data = (date,) + tuple(
                self.home_colum.item(row, col).text() for col in range(self.home_colum.columnCount()) if col != date_col)
            data.append(row_data)

        # 날짜 역순으로 정렬
        sorted_data = sorted(data, key=lambda x: x[0], reverse=True)

        # 정렬된 데이터를 테이블 위젯에 적용
        self.home_colum.setRowCount(len(sorted_data))
        self.home_colum.setColumnCount(len(sorted_data[0]))
        for row, row_data in enumerate(sorted_data):
            for col, value in enumerate(row_data):
                # item = QTableWidgetItem(str(value))
                # self.home_colum.setItem(row, col, item)
                if col == 2 or col == 3:
                    a = QTableWidgetItem(str(value))
                    a.setTextAlignment(Qt.AlignCenter)
                    a.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)  # 수정 가능한 열에 대해서만 플래그 추가
                    self.home_colum.setItem(row, col, a)
                else:
                    a = QTableWidgetItem(str(value))
                    a.setTextAlignment(Qt.AlignCenter)
                    a.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # 수정 불가능한 열에 대해서는 플래그 추가하지 않음
                    self.home_colum.setItem(row, col, a)

        dates = []
        try:
            sql2 = "SELECT DISTINCT date FROM attendance"
            cur.execute(sql2)
            result = list(cur.fetchall())
            if len(result) > 0:
                for i in result:
                    date = datetime.datetime.strptime(i[0], "%Y-%m-%d")
                    dates.append(date)
                sorted_dates = sorted(dates, reverse=True)
                for j in sorted_dates:
                    self.search_date.addItem(str(j.date()))

                con.commit()
        except Exception as e:
            print("출결 콤보박스", e)

        self.home_frame.show()

    def att_show(self):
        print(self.search_date.currentText())

        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()

        self.home_colum.clearContents()
        self.home_colum.setRowCount(0)

        sql1 = "SELECT * FROM "
        x = "smartclass.attendance"
        cur.execute(sql1 + x)
        result = list(cur.fetchall())

        try:
            for i, row in enumerate(result):
                if row[1] == self.search_date.currentText():
                    self.home_colum.setRowCount(i + 1)
                    # print(row[4])
                    for j, item in enumerate(row[1:6]):
                        if j in [2, 3]:  # 2번째 열과 3번째 열만 편집 가능하도록 설정
                            a = QTableWidgetItem(str(item))
                            a.setTextAlignment(Qt.AlignCenter)
                            a.setFlags(
                                Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)  # 수정 가능한 열에 대해서만 플래그 추가
                            self.home_colum.setItem(i, j, a)
                        else:
                            a = QTableWidgetItem(str(item))
                            a.setTextAlignment(Qt.AlignCenter)
                            a.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # 수정 불가능한 열에 대해서는 플래그 추가하지 않음
                            self.home_colum.setItem(i, j, a)
            # 빈칸제거
            for i in range(self.home_colum.rowCount() - 1, -1, -1):
                empty_row = True
                for j in range(self.home_colum.columnCount()):
                    if self.home_colum.item(i, j) is not None:
                        empty_row = False
                        break
                if empty_row:
                    self.home_colum.removeRow(i)
                con.commit()
        except Exception as e:
            print("출결 관리 : ", e)
            con.commit()

    def att_change(self):
        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()

        # 수정된 데이터 저장
        updated_data = {}

        per_item = []

        row = self.home_colum.currentRow()
        for i in range(self.home_colum.columnCount()):  #클릭한 행의 값 출력
            # per_item = (self.home_colum.item(row, i)).text()
            per_item.append((self.home_colum.item(row, i)).text())
        print(per_item)

        # 지문 수정
        date = per_item[0]
        id = per_item[1]
        entry_time = per_item[2]
        exit_time = per_item[3]
        name = per_item[4]
        classroom = per_item[5]

        updated_data[(date, id, name, classroom)] = (entry_time, exit_time)
        print(updated_data)

        try:
            # 수정된 데이터를 SQL로 업데이트합니다.
            for (date, id, name, classroom), (entry_time, exit_time) in updated_data.items():
                sql = f"UPDATE attendance SET entry_time = '{entry_time}', exit_time = '{exit_time}' WHERE date = '{date}' AND id = '{id}' AND name = '{name}' AND classroom = '{classroom}'"
                cur.execute(sql)
                con.commit()
        except Exception as e:
            print("출결 수정", e)


    # 서버 공지
    def open_Notice_frame(self):  # 공지사항
        self.Notice_frame = QFrame(self)
        self.Notice_frame.setGeometry(QtCore.QRect(100, 130, 880, 410))
        self.Notice_frame.setStyleSheet("background-color: rgb(63, 73, 98);")

        # 달력
        self.calendar = QCalendarWidget(self.Notice_frame)
        self.calendar.setGeometry(QtCore.QRect(10, 10, 380, 390))
        self.calendar.setStyleSheet(
            "selection-background-color: rgb(254, 156, 29);\n""alternate-background-color: rgb(216,216,216,150);" "color:rgb(255, 255, 255);""font: 75 13pt 'Agency FB';")
        self.calendar.setVerticalHeaderFormat(0)  # vertical header 숨기기
        self.calendar.selectionChanged.connect(self.show_dialog)


        # 날짜  캘릭터 클릭시 날짜 표시
        self.day_label = QLabel(self.Notice_frame)
        self.day_label.setGeometry(QtCore.QRect(410, 10, 180, 30))
        self.day_label.setStyleSheet(
            "color:rgb(255, 255, 255);""border:none;""border-bottom:1px solid rgba(255, 255, 255,);""font: 75 13pt 'Agency FB';")

        # 제목
        self.title_edit = QLineEdit(self.Notice_frame)
        self.title_edit.setGeometry(QtCore.QRect(410, 50, 180, 30))
        self.title_edit.setPlaceholderText('제목')  # setPlaceholderText 글을 쓰면 사라짐
        self.title_edit.setStyleSheet(
            "color:rgb(255, 255, 255);""border:none;""border-bottom:1px solid rgba(255, 255, 255,);")

        # 내용
        self.content_edit = QTextEdit(self.Notice_frame)  # 내용
        self.content_edit.setGeometry(QtCore.QRect(410, 100, 450, 260))
        self.content_edit.setStyleSheet(
            "color:rgb(255, 255, 255);""border: 1px solid #fefefe;")

        # 등록 버튼
        self.add_but = QPushButton("O K", self.Notice_frame)
        self.add_but.setGeometry(QtCore.QRect(760, 370, 30, 30))
        self.add_but.setStyleSheet("border-bottom: 1px solid #fefefe;")
        self.add_but.clicked.connect(self.upload_notice)

        self.animation = QtCore.QPropertyAnimation(self.add_but, b"geometry")
        self.add_but.enterEvent = self.on_button_entered11
        self.add_but.leaveEvent = self.on_button_left11

        # 공지 삭제
        self.delete_button = QPushButton("DELETE", self.Notice_frame)
        self.delete_button.setGeometry(QtCore.QRect(800, 370, 50, 30))
        self.delete_button.setStyleSheet(
            "font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.delete_button.clicked.connect(self.del_notice)

        self.animation = QtCore.QPropertyAnimation(self.delete_button, b"geometry")
        self.delete_button.enterEvent = self.on_button_entered12
        self.delete_button.leaveEvent = self.on_button_left12

        date_format = QTextCharFormat()

        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()

        cur.execute("SELECT class_name, date FROM notice")
        x = list(cur.fetchall())
        for i in x:
            if i[0] == self.combobox1.currentText():
                a = i[1].split("-")
                date_format.setBackground(QColor(130, 142, 174))
                # self.calendar.setDateTextFormat(self.calendar.selectedDate(), date_format)
                self.calendar.setDateTextFormat(QtCore.QDate(int(a[0]), int(a[1]), int(a[2])), date_format)
            else:
            # # db에 데이터가 없는 경우, 배경색을 원래대로 설정  #달력
                date_format.setBackground(QColor(216, 216, 216, 150))
        con.commit()

        self.Notice_frame.show()

    # 글쓰기 다이얼로그를 열기 위해 호출되는 함수
    def show_dialog(self):
        # print("버튼 확인용")
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.day_label.setText(date)
        self.title_edit.clear()
        self.content_edit.clear()
        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()

        sql = "SELECT * FROM "
        x = "smartclass.notice"
        cur.execute(sql + x)
        result = list(cur.fetchall())
        try:
            for i in result:
                # print(i)h
                if i[2] == date and i[1] == self.combobox1.currentText():
                    print("날짜 똑같음")
                    self.title_edit.setText(i[3])
                    self.content_edit.setText(i[4])
            con.commit()
        except Exception as e:
            print("공지관리 : ", e)
            con.commit()

    def upload_notice(self):
        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()

        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        notice_title = self.title_edit.text()
        notice_content = self.content_edit.toPlainText()
        class_ = self.combobox1.currentText()

        print(date)
        print(notice_title)
        print(notice_content)
        print(class_)

        sql = "INSERT INTO notice(class_name, date, title, content) VALUES(%s,%s,%s,%s)"
        val = [(class_, date, notice_title, notice_content)]
        try:
            print("try 안")
            cur.executemany(sql, val)
            con.commit()
            date_format = QTextCharFormat()
            date_format.setBackground(QColor(130, 142, 174))
            self.calendar.setDateTextFormat(self.calendar.selectedDate(), date_format)
        except Exception as ex:
            print('upload_notice 오류 : ', ex)

        con.commit()

    def del_notice(self):
        reply = QMessageBox.question(self, '', '삭제하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # reply.setStyleSheet("border:none;")
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")

        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()
        if reply == QMessageBox.Yes:
            sql = "DELETE FROM smartclass.notice WHERE date=%s"
            cur.execute(sql, date)
            date_format = QTextCharFormat()
            date_format.setBackground(QColor(63, 73, 98))
            self.calendar.setDateTextFormat(self.calendar.selectedDate(), date_format)

        con.commit()

    def open_chat_frame(self):
        self.search_frame = QFrame(self)
        self.search_frame.setGeometry(QtCore.QRect(100, 130, 880, 410))
        self.search_frame.setStyleSheet("background-color: rgb(63, 73, 98);")

        # 학생조회
        # 검색
        self.search_user = QComboBox(self.search_frame)
        self.search_user.setGeometry(QtCore.QRect(20, 30, 140, 30))
        self.search_user.setStyleSheet(
            "color: rgb(255, 255, 255);""selection-background-color: rgb(112, 131, 175);""border-bottom:1px solid rgba(255, 255, 255,);""font: 75 14pt 'Agency FB';")

        # 조회 버튼
        self.search_button = QPushButton("SEARCH", self.search_frame)
        self.search_button.setGeometry(QtCore.QRect(170, 30, 50, 30))
        self.search_button.setStyleSheet("font: 75 14pt 'Agency FB';""border:none;")
        self.search_button.clicked.connect(self.click_search)

        hover_animation = QtCore.QPropertyAnimation(self.search_button, b"geometry")
        hover_animation.setDuration(200)

        self.search_button.enterEvent = lambda event: hover_animation.start()
        self.search_button.leaveEvent = lambda event: hover_animation.reverse()
        # # 버튼 이미지 변경  background-color: rgb(245, 196, 132)
        self.search_button.enterEvent = lambda event: self.search_button.setStyleSheet(
            "color: rgb(254,156,29);""background-color: rgba(0, 0, 0,0);""border:none;""border-bottom:1px solid rgba(254,156,29);")
        self.search_button.leaveEvent = lambda event: self.search_button.setStyleSheet(
            "color: rgb(255, 255, 255);""background-color: rgba(0, 0, 0,0);""border:none;""border-bottom:1px solid rgb(255, 255, 255);")

        # user 삭제 버튼
        self.delete_button = QPushButton("DELETE", self.search_frame)
        self.delete_button.setGeometry(QtCore.QRect(240, 30, 50, 30))
        self.delete_button.setStyleSheet(
            "font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.delete_button.clicked.connect(self.del_user)

        self.animation = QtCore.QPropertyAnimation(self.delete_button, b"geometry")
        self.delete_button.enterEvent = self.on_button_entered12
        self.delete_button.leaveEvent = self.on_button_left12

        # 조회목록  조회
        table_colum = ["ID", "PW", "NAME", "CLASSROOM", "PHONE", "ck", ]  # CHECK
        self.user_table = QTableWidget(self.search_frame)
        self.user_table.setGeometry(QtCore.QRect(20, 70, 550, 330))
        self.user_table.setStyleSheet(
            "font: 75 14pt 'Agency FB';""border:none;""color:rgb(255,255,255);""border-bottom:1px solid rgb(255, 255, 255);")
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels(table_colum)
        self.user_table.setColumnWidth(0, 100)  # 체크박스 여기
        self.user_table.setColumnWidth(1, 100)  # PW
        self.user_table.setColumnWidth(2, 100)  # NAME
        self.user_table.setColumnWidth(3, 100)  # num
        self.user_table.setColumnWidth(4, 100)  # class?+
        self.user_table.setColumnWidth(5, 20)

        self.user_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.user_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.user_table.verticalHeader().setVisible(False)  # 헤더 X
        header = self.user_table.horizontalHeader()
        # header.setSectionResizeMode(QHeaderView.Stretch)  # 열의 크기를 채우기 위한 옵션
        header.setStyleSheet("QHeaderView:section { background-color: transparent };")

        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()

        sql2 = "SELECT * FROM "
        x = "smartclass.classroom"
        cur.execute(sql2 + x)
        result = list(cur.fetchall())
        try:
            for i in result:
                self.search_user.addItem(i[1])
            con.commit()
        except Exception as e:
            print("학생관리 : ", e)
            con.commit()

        self.search_frame.show()

    def open_att_frame(self):
        total_process = 0
        current_progress = 0
        user_name = []

        self.att_frame = QFrame(self)
        self.att_frame.setGeometry(QtCore.QRect(100, 130, 880, 410))
        self.att_frame.setStyleSheet("background-color: rgb(63, 73, 98);")

        self.att_label = QLabel(self.att_frame)
        self.att_label.setGeometry(QtCore.QRect(250, 0, 600, 400))
        self.att_label.setStyleSheet("background-color: transparent;")

        self.att_label2 = QLabel(self.att_frame)
        self.att_label2.setGeometry(QtCore.QRect(250, 0, 600, 400))
        self.att_label2.setStyleSheet("background-color: transparent;")

        # 학생자 명단 목록
        table_colum = ["Student List"]
        self.att_table = QTableWidget(self.att_frame)
        self.att_table.setGeometry(QtCore.QRect(20, 20, 110, 380)) # "gridline-color: rgba(255, 255, 255);"
        self.att_table.setStyleSheet("font: 75 14pt 'Agency FB';""border:none;""color:rgb(255,255,255);")
        self.att_table.setColumnCount(1)
        self.att_table.setHorizontalHeaderLabels(table_colum)
        #self.att_table.horizontalHeader().setStyleSheet("color : rgb(255,255,255);""border-bottom:1px solid rgba(255, 255, 255,);" )

        header = self.att_table.horizontalHeader()
        #header.setSectionResizeMode(QHeaderView.Stretch)  # 열의 크기를 채우기 위한 옵션
        header.setStyleSheet("QHeaderView::section { background-color: transparent };")  # 열의 배경색을 설정


        self.att_table.setColumnWidth(0, 100)
        self.att_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.att_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 표 행 수정 불가능
        self.att_table.cellClicked.connect(self.cell_click)

        try:  # 현재 선택한 반과 일치하는 학생 출력
            con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
            cur = con.cursor()

            sql = "SELECT * FROM "
            cur.execute("SELECT class_name, course_days FROM classroom")
            x = cur.fetchall()
            for i in x:  # 선택한 반과 일치하는 반의 기간 불러오기
                if i[0] == self.combobox1.currentText():
                    total_process = i[1]
            print(total_process)

            cur.execute("SELECT name, classroom FROM user")
            y = cur.fetchall()
            for i in y:
                if i[1] == self.combobox1.currentText():
                    user_name.append(i[0])
            print(user_name)

            cur.execute("SELECT COUNT(DISTINCT date) FROM attendance")
            result = cur.fetchone()
            current_progress = result[0]
            print(current_progress)

            q = "smartclass.user"
            cur.execute(sql + q)
            result = list(cur.fetchall())
        except Exception as e:
            print(e)
            pass

        try:
            for i, row in enumerate(result):
                self.att_table.setRowCount(i + 1)
                # print(row[4])
                if row[3] == self.combobox1.currentText():  # row[4]
                    for j, item in enumerate(row[2:]):
                        a = QTableWidgetItem(str(item))
                        a.setTextAlignment(Qt.AlignCenter)
                        self.att_table.setItem(i, j, a)

            # 빈칸제거
            for i in range(self.att_table.rowCount() - 1, -1, -1):
                empty_row = True
                for j in range(self.att_table.columnCount()):
                    if self.att_table.item(i, j) is not None:
                        empty_row = False
                        break
                if empty_row:
                    self.att_table.removeRow(i)
            con.commit()
            self.att_table.verticalHeader().setVisible(False)  # 순서 삭제
        except Exception as e:
            print("출결 관리 : ", e)
            pass
            con.commit()
        try:
            # QGraphicsView 생성
            progress = QGraphicsView(self.att_frame)
            progress.setFrameStyle(progress.NoFrame)
            progress.setGeometry(450, 400, 250, 50)

            # QGraphicsScene 생성
            scene = QGraphicsScene()

            # 가로 긴 직사각형 모양의 막대 생성
            rect = QGraphicsRectItem(30, 100, 200, 20)

            # 일부분만 색칠할 영역 생성
            brush = QBrush(QColor(254, 156, 29))  # 붉은색
            rect_part = QGraphicsRectItem(30, 100, 200 * (current_progress / total_process),
                                          20)  # 위치 (0,0), 크기 (100,20)
            rect_part.setBrush(brush)

            # QGraphicsScene에 아이템 추가
            scene.addItem(rect)
            scene.addItem(rect_part)

            # QGraphicsView에 QGraphicsScene 설정
            progress.setScene(scene)
            progress.setRenderHint(QPainter.Antialiasing)

            self.create_piechart()
        except Exception as e:
            print("open_att_frame", e)
            pass
        self.att_frame.show()

    def create_piechart(self):  #전체 출결 현황
        # progress.setGeometry(450,350,250,50)
        total_result = {"출석": 0, "지각": 0, "조퇴": 0, "결석": 0}
        a = []

        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()
        cur.execute("SELECT entry_time, exit_time FROM attendance")
        x = list(cur.fetchall())
        for i in x:
            a.append(list(i))
        try:
            for i in a:
                # 지문 수정
                if i[0] is not None and i[0] != "-" and i[1] is not None and i[1] != "-":
                    en = datetime.datetime.strptime(i[0], "%H:%M:%S")
                    ex = datetime.datetime.strptime(i[1], "%H:%M:%S")
                    if en <= datetime.datetime.strptime("09:00:00", "%H:%M:%S") and ex >= datetime.datetime.strptime(
                            "17:50:00", "%H:%M:%S"):
                        total_result["출석"] += 1
                    elif en > datetime.datetime.strptime("09:00:00", "%H:%M:%S") and ex >= datetime.datetime.strptime(
                            "17:50:00", "%H:%M:%S"):
                        total_result["지각"] += 1
                    elif en <= datetime.datetime.strptime("09:00:00", "%H:%M:%S") and ex < datetime.datetime.strptime(
                            "17:50:00", "%H:%M:%S"):
                        total_result["조퇴"] += 1
                    elif en > datetime.datetime.strptime("09:00:00", "%H:%M:%S") and ex < datetime.datetime.strptime(
                            "17:50:00", "%H:%M:%S"):
                        total_result["조퇴"] += 1
                elif i[0] is None or i[0] == "-" or i[1] is None or i[1] == "-":
                    total_result["결석"] += 1
            print(total_result)
            con.commit()
        except Exception as e:
            pass
            print("총 출결", e)

        series = QPieSeries()
        series.append("출석", total_result["출석"])
        series.append("지각", total_result["지각"])
        series.append("조퇴", total_result["조퇴"])
        series.append("결석", total_result["결석"])
        # series.append("PHP", 30)

        # adding slice
        slice = QPieSlice()
        slice = series.slices()[0]
        slice1 = series.slices()[1]
        slice2 = series.slices()[2]
        slice3 = series.slices()[3]
        slice.setExploded(True)
        slice.setLabelVisible(True)

        # slice1.setExploded(True)
        slice1.setLabelVisible(True)
        slice1.setLabelColor(Qt.white)
        # slice2.setExploded(True)
        slice2.setLabelVisible(True)
        slice2.setLabelColor(Qt.white)
        # slice3.setExploded(True)
        slice3.setLabelVisible(True)
        slice3.setLabelColor(Qt.white)

        slice.setPen(QPen(Qt.white, 2))
        slice.setLabelColor(Qt.white)
        # slice.setBrush(Qt.green)
        color = QColor()
        color.setRgb(102, 104, 198)
        slice.setBrush(color)

        chart = QChart()
        chart.legend().hide()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle(f"{self.combobox1.currentText()} 출결 현황")
        chart.setTitleFont(QFont("Arial", 14, QFont.Bold))
        chart.setTitleBrush(QBrush(Qt.white))

        legend = chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignBottom)
        legend.setLabelColor(Qt.white)

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)
        chartview.setBackgroundBrush(Qt.transparent)

        # set up layout
        layout = QVBoxLayout(self.att_label)
        # layout.addWidget(chartview, alignment=Qt.AlignRight | Qt.AlignTop)
        layout.addWidget(chartview)
        chartview.setGeometry(250, 0, 600, 370)

        chart.setBackgroundBrush(Qt.transparent)

    def cell_click(self):
        self.att_label.hide()

        try:
            layout = self.att_label2.layout()
            if layout is not None:
                for i in range(layout.count()):
                    widget = layout.itemAt(i).widget()
                    if isinstance(widget, QChartView):
                        layout.removeWidget(widget)
                        widget.chart().removeAllSeries()
                        widget.chart().deleteLater()
                        widget.deleteLater()
        except Exception as e:
            pass
            print(e)
        self.att_label2 = QLabel(self.att_frame)
        self.att_label2.setGeometry(QtCore.QRect(250, 0, 600, 400))
        self.att_label2.setStyleSheet("background-color: transparent;")
        self.att_label2.show()

        row = self.att_table.currentRow()
        for i in range(self.att_table.columnCount()):  #클릭한 행의 값 출력
            per_item = (self.att_table.item(row, i)).text()
        # print(per_item)

        per_result = {"출석" : 0, "지각" : 0, "조퇴" : 0,"결석" : 0}
        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()
        cur.execute("SELECT entry_time, exit_time, name FROM attendance")
        x = list(cur.fetchall())
        for i in x:
            # print(i)
            if per_item == i[2]:
                try:
                    #지문 수정
                    if i[0] is not None and i[0] != "-" and i[1] is not None and i[1] != "-":
                        en = datetime.datetime.strptime(i[0], "%H:%M:%S")
                        ex = datetime.datetime.strptime(i[1], "%H:%M:%S")
                        if en <= datetime.datetime.strptime("09:00:00",
                                                           "%H:%M:%S") and ex >= datetime.datetime.strptime("17:50:00", "%H:%M:%S"):
                            per_result["출석"] += 1
                        elif en > datetime.datetime.strptime("09:00:00",
                                                            "%H:%M:%S") and ex >= datetime.datetime.strptime("17:50:00", "%H:%M:%S"):
                           per_result["지각"] += 1
                        elif en <= datetime.datetime.strptime("09:00:00",
                                                             "%H:%M:%S") and ex < datetime.datetime.strptime("17:50:00", "%H:%M:%S"):
                           per_result["조퇴"] += 1
                        elif en > datetime.datetime.strptime("09:00:00",
                                                            "%H:%M:%S") and ex < datetime.datetime.strptime("17:50:00", "%H:%M:%S"):
                           per_result["조퇴"] += 1
                    elif i[0] is None or i[0] == "-" or i[1] is None or i[1] == "-":
                        per_result["결석"] += 1
                except Exception as e:
                    pass
                    print("개인 출결", e)
        print(per_result)

        seriess = QPieSeries()
        seriess.append("출석", per_result["출석"])
        seriess.append("지각", per_result["지각"])
        seriess.append("조퇴", per_result["조퇴"])
        seriess.append("결석", per_result["결석"])

        # adding slice
        slice = QPieSlice()
        slice = seriess.slices()[0]
        slice1 = seriess.slices()[1]
        slice2 = seriess.slices()[2]
        slice3 = seriess.slices()[3]
        slice.setExploded(True)
        slice.setLabelVisible(True)

        # slice1.setExploded(True)
        slice1.setLabelVisible(True)
        slice1.setLabelColor(Qt.white)
        # slice2.setExploded(True)
        slice2.setLabelVisible(True)
        slice2.setLabelColor(Qt.white)
        # slice3.setExploded(True)
        slice3.setLabelVisible(True)
        slice3.setLabelColor(Qt.white)

        slice.setPen(QPen(Qt.white, 2))
        slice.setLabelColor(Qt.white)
        # slice.setBrush(Qt.green)
        color = QColor()
        color.setRgb(102, 104, 198)
        slice.setBrush(color)

        chart = QChart()
        chart.legend().hide()
        chart.addSeries(seriess)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle(f"{per_item} 출결 현황")
        chart.setTitleFont(QFont("Arial", 14, QFont.Bold))
        chart.setTitleBrush(QBrush(Qt.white))

        legend = chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignBottom)
        legend.setLabelColor(Qt.white)

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)
        chartview.setBackgroundBrush(Qt.transparent)

        # set up layout
        layout = QVBoxLayout(self.att_label2)
        # layout.addWidget(chartview, alignment=Qt.AlignRight | Qt.AlignTop)
        layout.addWidget(chartview)
        chartview.setGeometry(0, 0, 600, 400)

        chart.setBackgroundBrush(Qt.transparent)

    # 학생(유저)추가및 관리
    def open_user_frame(self):
        self.user_frame = QFrame(self)
        self.user_frame.setGeometry(QtCore.QRect(100, 130, 880, 410))
        self.user_frame.setStyleSheet("background-color: rgb(63, 73, 98);")

        # 학생 라벨
        self.add_label = QLabel("Student ADD", self.user_frame)
        self.add_label.setGeometry(QtCore.QRect(20, 40, 82, 20))
        self.add_label.setStyleSheet("border: 1px solid #fefefe;""color: rgb(255, 255, 255);")
        # 반 추가 틀
        self.add_label1 = QLabel("CLASS ADD", self.user_frame)
        self.add_label1.setGeometry(QtCore.QRect(20, 270, 80, 20))
        self.add_label1.setStyleSheet("border: 1px solid #fefefe;""color: rgb(255, 255, 255);")

        # 반 추가 텍스트  QLineEdit
        self.add_text = QLineEdit(self.user_frame)
        self.add_text.setPlaceholderText('CLASS ADD')  # setPlaceholderText 글을 쓰면 사라짐
        self.add_text.setGeometry(QtCore.QRect(120, 310, 140, 30))
        self.add_text.setStyleSheet(
            "font: 75 14pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgb(255, 255, 255);")  # 버튼?

        self.spinbox_label1 = QLabel("Person", self.user_frame)
        self.spinbox_label1.setGeometry(QtCore.QRect(320, 310, 50, 30))
        self.spinbox_label1.setStyleSheet(
            "font: 75 14pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border-bottom:1px solid rgba(255, 255, 255,);")
        self.spinbox_label1.setAlignment(QtCore.Qt.AlignCenter)  # 글씨 가운데

        self.spinbox_label2 = QLabel("Day", self.user_frame)  # 영? DAY
        self.spinbox_label2.setGeometry(QtCore.QRect(400, 310, 30, 30))
        self.spinbox_label2.setStyleSheet(
            "font: 75 14pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border-bottom:1px solid rgba(255, 255, 255,);")
        self.spinbox_label2.setAlignment(QtCore.Qt.AlignCenter)  # 중앙

        # 정원 마우스 휠 이벤트
        self.spinbox = QSpinBox(self.user_frame)
        self.spinbox.setGeometry(290, 310, 30, 30)
        self.spinbox.setStyleSheet(
            "font: 75 10pt 'Arial';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.spinbox.setRange(1, 30)
        self.spinbox.setAlignment(QtCore.Qt.AlignCenter)  # 중앙
        self.spinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)  # 버튼 x
        self.spinbox.valueChanged.connect(self.spin_text)

        # 일수
        self.spinbox1 = QSpinBox(self.user_frame)
        self.spinbox1.setGeometry(370, 310, 30, 30)
        self.spinbox1.setStyleSheet(
            "font: 75 10pt 'Arial';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.spinbox1.setRange(1, 180)

        self.spinbox1.setAlignment(QtCore.Qt.AlignCenter)
        self.spinbox1.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spinbox1.valueChanged.connect(self.spin_text)

        ######################################
        # 추가버튼
        self.add_but = QPushButton("O K", self.user_frame)
        self.add_but.setGeometry(QtCore.QRect(460, 360, 40, 30))
        self.add_but.setStyleSheet(
            "font: 75 14pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgb(255, 255, 255);")  # 이미지
        self.add_but.clicked.connect(self.add_classroom)

        self.animation = QtCore.QPropertyAnimation(self.add_but, b"geometry")
        # self.add_finger.mousePressEvent = self.on_button_clicked
        self.add_but.enterEvent = self.on_button_entered11
        self.add_but.leaveEvent = self.on_button_left11

        # ID #여기 까지
        self.add_id = QLineEdit(self.user_frame)
        self.add_id.setPlaceholderText("ID")
        self.add_id.setGeometry(QtCore.QRect(120, 120, 140, 30))
        self.add_id.setStyleSheet(
            "font: 75 10pt 'Arial';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.add_id.returnPressed.connect(self.enroll)

        # PW
        self.add_pw = QLineEdit(self.user_frame)
        self.add_pw.setPlaceholderText("PW")
        self.add_pw.setGeometry(QtCore.QRect(290, 120, 140, 30))
        self.add_pw.setStyleSheet(
            "font: 75 10pt 'Arial';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgb(255, 255, 255);")

        # 이름
        self.add_name = QLineEdit(self.user_frame)
        self.add_name.setPlaceholderText("NAME")
        self.add_name.setGeometry(QtCore.QRect(120, 170, 140, 30))
        self.add_name.setStyleSheet(
            "font: 75 10pt 'Arial';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgb(255, 255, 255);")

        # 폰번호
        self.add_num = QLineEdit(self.user_frame)
        self.add_num.setPlaceholderText("PHONE NUMBER  - X")
        self.add_num.setGeometry(QtCore.QRect(290, 170, 140, 30))
        self.add_num.setStyleSheet(
            "font: 75 10pt 'Arial';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgb(255, 255, 255);")

        #학생추가 반 선택
        self.room_box = QComboBox(self.user_frame)
        self.room_box.setGeometry(QtCore.QRect(20, 80, 140, 30))
        self.room_box.setPlaceholderText("CLASS SELECTION")
        self.room_box.setStyleSheet(
            "color: rgb(255, 255, 255);""selection-background-color: rgb(112, 131, 175);""border-bottom:1px solid rgba(255, 255, 255,);""font: 75 14pt 'Agency FB';")

        # 지문추가
        self.add_finger = QPushButton(self.user_frame)  # 수정
        self.add_finger.setGeometry(QtCore.QRect(20, 120, 70, 80))
        self.add_finger.setStyleSheet(
            "background-color: rgb(0,0,0,0);""border-image: url(./QTbutton/fingerprint1.png);\n")
        self.add_finger.clicked.connect(self.enroll)

        self.animation = QtCore.QPropertyAnimation(self.add_finger, b"geometry")
        # self.add_finger.mousePressEvent = self.on_button_clicked
        self.add_finger.enterEvent = self.on_button_entered
        self.add_finger.leaveEvent = self.on_button_left

        # 등록
        self.join_button = QPushButton("O K", self.user_frame)
        self.join_button.setGeometry(QtCore.QRect(460, 190, 40, 30))
        self.join_button.setStyleSheet(
            "font: 75 14pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.join_button.clicked.connect(self.add_user)

        self.animation = QtCore.QPropertyAnimation(self.join_button, b"geometry")
        # self.add_finger.mousePressEvent = self.on_button_clicked
        self.join_button.enterEvent = self.on_button_entered10
        self.join_button.leaveEvent = self.on_button_left10

        ###### 교실 목록 ######################
        class_colum = ["class_name", "personnel", "course_days","ck"]
        self.classroom_table = QTableWidget(self.user_frame)
        self.classroom_table.setGeometry(QtCore.QRect(530, 30, 300, 320))
        self.classroom_table.setStyleSheet(
            "font: 75 14pt 'Agency FB';""border:none;""color:rgb(255,255,255);""border-bottom:1px solid rgb(255, 255, 255);")
        self.classroom_table.setColumnCount(4)
        self.classroom_table.setHorizontalHeaderLabels(class_colum)
        self.classroom_table.setColumnWidth(0, 100)  # 교실 이름
        self.classroom_table.setColumnWidth(1, 80)  # 인원 수
        self.classroom_table.setColumnWidth(2, 80)  # 수업일 수
        self.classroom_table.setColumnWidth(3, 30)

        self.classroom_table.verticalHeader().setVisible(False)  # 헤더 X
        header1 = self.classroom_table.horizontalHeader()
        header1.setStyleSheet("QHeaderView:section { background-color: transparent };")

        # user 삭제 버튼
        self.delete_button = QPushButton("DELETE", self.user_frame)
        self.delete_button.setGeometry(QtCore.QRect(790, 360, 50, 30))
        self.delete_button.setStyleSheet(
            "font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.delete_button.clicked.connect(self.del_classroom)

        self.animation = QtCore.QPropertyAnimation(self.delete_button, b"geometry")
        self.delete_button.enterEvent = self.on_button_entered12
        self.delete_button.leaveEvent = self.on_button_left12

        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()
        sql2 = "SELECT * FROM "
        x = "smartclass.classroom"
        cur.execute(sql2 + x)
        result = list(cur.fetchall())
        try:
            for i, row in enumerate(result):
                self.classroom_table.setRowCount(i + 1)
                # print(row[4])
                for j, item in enumerate(row[1:4]):
                    a = QTableWidgetItem(str(item))
                    a.setTextAlignment(Qt.AlignCenter)
                    self.classroom_table.setItem(i, j, a)

                    self.checkbox = QCheckBox()
                    self.checkbox.setStyleSheet("border: none;")
                    self.checkbox.setChecked(False)
                    self.classroom_table.setCellWidget(i, 3, self.checkbox)

            # 빈칸제거
            for i in range(self.classroom_table.rowCount() - 1, -1, -1):
                empty_row = True
                for j in range(self.classroom_table.columnCount()):
                    if self.classroom_table.item(i, j) is not None:
                        empty_row = False
                        break
                if empty_row:
                    self.classroom_table.removeRow(i)
            con.commit()
        except Exception as e:
            print("교실 관리 : ", e)
            con.commit()

        self.user_frame.show()

        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()

        sql6 = "SELECT * FROM "
        x = "smartclass.classroom"
        cur.execute(sql6 + x)
        result = list(cur.fetchall())
        try:
            for i in result:
                # print(i)
                self.room_box.addItem(i[1])
            con.commit()
        except Exception as e:
            print("학생관리 : ", e)
            con.commit()

    def del_classroom(self):  # 여기
        reply = QMessageBox.question(self, '', '삭제하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            selected_rows = []
            for row in range(self.classroom_table.rowCount()):
                item = self.classroom_table.cellWidget(row, 3)
                if item and item.isChecked():
                    selected_rows.append(row)
            if selected_rows:
                try:
                    con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
                    cur = con.cursor()

                    for i in sorted(selected_rows, reverse=True):
                        row_id = self.classroom_table.item(i, 0).text()
                        sql = "DELETE FROM smartclass.classroom WHERE class_name=%s"
                        cur.execute(sql, row_id)

                        sql2 = "DELETE FROM smartclass.user WHERE classroom=%s"
                        cur.execute(sql2, row_id)

                        sql3 = "DELETE FROM smartclass.notice WHERE class_name=%s"
                        cur.execute(sql3, row_id)

                        sql4 = "DELETE FROM smartclass.attendance WHERE classroom=%s"
                        cur.execute(sql4, row_id)

                        self.classroom_table.removeRow(i)
                        self.combobox1.removeItem(self.combobox1.findText(f"{row_id}"))
                        self.room_box.removeItem(self.room_box.findText(f"{row_id}"))

                    con.commit()

                except Exception as e:
                    print("classroom 삭제",e)
                    con.rollback()
        else:
            pass

    def open_cam_frame(self):
        self.cam_frame = QFrame(self)
        self.cam_frame.setGeometry(QtCore.QRect(100, 130, 880, 410))
        self.cam_frame.setStyleSheet("background-color: rgb(63, 73, 98);")

        # 웹캠 영상용
        self.cam_label = QLabel(self.cam_frame)
        self.cam_label.setGeometry(QtCore.QRect(10, 10, 860, 380))
        self.cam_label.setStyleSheet("border:none;")


        # 줌 버튼 임시 77
        self.zoomin_button = QPushButton(self.cam_frame)
        self.zoomin_button.setGeometry(QtCore.QRect(770, 340, 40, 30))
        self.zoomin_button.setStyleSheet("background-color: rgb(0, 0, 0,0);\n""border-image: url(./QTbutton/zoom.png);\n")
        self.zoomin_button.clicked.connect(self.zoom_in)

        self.zoomout_button = QPushButton(self.cam_frame)
        self.zoomout_button.setGeometry(QtCore.QRect(820, 340, 40, 30))
        self.zoomout_button.setStyleSheet("background-color: rgb(0, 0, 0,0);\n""border-image: url(./QTbutton/zoomout.png);\n")
        self.zoomout_button.clicked.connect(self.zoom_out)

        self.on_button = QPushButton(self.cam_frame)
        self.on_button.setGeometry(QtCore.QRect(720, 340, 40, 30))
        self.on_button.setStyleSheet("background-color: rgb(0, 0, 0,0);\n"f"{self.cam_toggle}")
        self.on_button.setCheckable(True)
        self.on_button.clicked.connect(self.start_cam)

        self.cam_frame.show()
        #self.stack.addWidget(self.cam_frame)

    def start_cam(self):
            try:
                if self.cam_toggle != "border-image: url(./QTbutton/on.png);\n":
                    print("on")
                    self.check_cam = "1"
                    self.cam_toggle = "border-image: url(./QTbutton/on.png);\n"
                    self.on_button.setStyleSheet("background-color: rgb(0, 0, 0,0);\n"f"{self.cam_toggle}")
                    self.cpt = cv2.VideoCapture(0)
                    self.cpt.set(cv2.CAP_PROP_FRAME_WIDTH, 860)  # 해상도
                    self.cpt.set(cv2.CAP_PROP_FRAME_HEIGHT, 380)
                    self.timer = QtCore.QTimer()
                    self.timer.timeout.connect(self.nextFrameSlot)
                    self.timer.start(41)
                else:
                    self.check_cam = "0"
                    self.cam_toggle = "border-image: url(./QTbutton/off.png);\n"
                    self.on_button.setStyleSheet(f"{self.cam_toggle}")
                    # self.set_label1.setStyleSheet("border: 2px solid #fefefe;")
                    self.cam_label.setPixmap(QPixmap.fromImage(QImage()))
                    self.timer.stop()
                    self.stop_thread = True
                    if self.thread_id:
                        exit_thread()
            except Exception as e:
                print("카메라 연결", e)
                QMessageBox.critical(self, '카메라 연결 안됨', "", QMessageBox.Ok)
                pass

    def nextFrameSlot(self):
        global cam
        try:
            _, cam = self.cpt.read()
            cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)
            h, w, _ = cam.shape
            zoomed_h, zoomed_w = int(h * self.zoom_factor), int(w * self.zoom_factor)
            resized_cam = cv2.resize(cam, (zoomed_w, zoomed_h))
            # cam = cv2.cvtColor(resized_cam, cv2.COLOR_BGR2RGB)
            img = QImage(resized_cam, zoomed_w, zoomed_h, QImage.Format_RGB888)
            pix = QPixmap.fromImage(img)
            # img = QImage(cam, cam.shape[1], cam.shape[0], QImage.Format_RGB888)
            # pix = QPixmap.fromImage(img).scaled(self.cam_label.width(), self.cam_label.height())  # 캠 라벨 사이즈에 맞게 영상 조절
            self.cam_label.setPixmap(pix)
            self.stop_thread = False
            start_new_thread(self.Webcam, (enclosure_queue,))
        except:
            pass

    def zoom_in(self):
        print("zoom_in")
        try:
            self.zoom_factor += 0.1
            if self.zoom_factor > 4.0:
                self.zoom_factor = 4.0
        except Exception as e:
            print("zoom_in", e)
            pass

    def zoom_out(self):
        print("zoom_out")
        try:
            self.zoom_factor -= 0.1
            if self.zoom_factor < 0.5:
                self.zoom_factor = 0.5
        except Exception as e:
            print("zoom_out", e)
            pass

    def open_set_frame(self):
        # self.stack.setCurrentIndex(6)
        self.set_frame = QFrame(self)
        self.set_frame.setGeometry(QtCore.QRect(100, 130, 880, 410))
        self.set_frame.setStyleSheet("background-color: rgb(63, 73, 98);")
        self.set_frame.setVisible(False)

        self.cal_usage = QPushButton(self.set_frame)
        self.cal_usage.setGeometry(QtCore.QRect(180, 40, 40, 30))
        self.cal_usage.setStyleSheet("border-image: url(./QTbutton/lightning.png);\n")
        self.cal_usage.setCheckable(True)
        self.cal_usage.clicked.connect(self.cal_power)

        hover_animation = QtCore.QPropertyAnimation(self.cal_usage, b"geometry")
        hover_animation.setDuration(200)

        # 마우스 오버/리브 효과 시그널 연결
        self.cal_usage.enterEvent = lambda event: hover_animation.start()
        self.cal_usage.leaveEvent = lambda event: hover_animation.reverse()

        # 버튼 이미지 변경  background-color: rgb(245, 196, 132)
        self.cal_usage.enterEvent = lambda event: self.cal_usage.setStyleSheet("border-image: url(./QTbutton/lightning1.png);\n")
        self.cal_usage.leaveEvent = lambda event: self.cal_usage.setStyleSheet("border-image: url(./QTbutton/lightning.png);\n")

        # 에어컨 라벨 &버튼
        self.set_label1 = QLabel(self.set_frame)
        self.set_label1.setGeometry(QtCore.QRect(10, 80, 210, 60))
        self.set_label1.setStyleSheet(f"{self.ac_label}")

        # 에어컨
        self.set_button1 = QPushButton(self.set_frame)
        self.set_button1.setGeometry(QtCore.QRect(20, 90, 50, 40))
        self.set_button1.setStyleSheet(
             "border-image: url(./QTbutton/air.png);\n")  # "background-color: rgba(0, 0, 0,0);\n"

        # 에어컨 토글 on/off
        self.all_button1 = QPushButton(self.set_frame)
        self.all_button1.setGeometry(QtCore.QRect(80, 105, 40, 30))
        self.all_button1.setStyleSheet(f"{self.ac_toggle}")
        self.all_button1.setCheckable(True)
        self.all_button1.clicked.connect(self.set_toggle1)
        self.all_button1.clicked.connect(lambda: self.add_tiem_to_dict("ac"))

        #냉난방 토글
        self.ac_ht = QPushButton(self.set_frame)
        self.ac_ht.setGeometry(QtCore.QRect(170, 100, 40, 30))
        self.ac_ht.setStyleSheet(f"{self.ac_condition}")
        self.ac_ht.setCheckable(True)
        self.ac_ht.clicked.connect(self.ac_ht_condition)

        # 에어컨 알람1
        self.alarm_button1 = QPushButton(self.set_frame)
        self.alarm_button1.setGeometry(QtCore.QRect(130, 110, 30, 20))
        self.alarm_button1.setStyleSheet(
            f"{self.ac_timer_img}")
        self.alarm_button1.clicked.connect(self.ac_alarm)

        # 조명 라벨
        self.set_label2 = QLabel(self.set_frame)
        self.set_label2.setGeometry(QtCore.QRect(10, 150, 210, 60))
        self.set_label2.setStyleSheet(f"{self.li_label}")

        # 조명 이미지
        self.set_button2 = QPushButton(self.set_frame)
        self.set_button2.setGeometry(QtCore.QRect(20, 160, 50, 40))
        self.set_button2.setCheckable(True)
        self.set_button2.setStyleSheet("border-image: url(./QTbutton/lamp.png);\n")

        # 조명 토글 on/off
        self.all_button2 = QPushButton(self.set_frame)
        self.all_button2.setGeometry(QtCore.QRect(80, 175, 40, 30))
        self.all_button2.setStyleSheet(f"{self.li_toggle}")
        self.all_button2.setCheckable(True)
        self.all_button2.clicked.connect(self.set_toggle2)
        self.all_button2.clicked.connect(lambda: self.add_tiem_to_dict("light"))


        # 조명 알람2
        self.alarm_button2 = QPushButton(self.set_frame)
        self.alarm_button2.setGeometry(QtCore.QRect(130, 180, 30, 20))
        self.alarm_button2.setStyleSheet(f"{self.li_timer_img}")
        self.alarm_button2.clicked.connect(self.li_alarm)

        # 0401 #밝기 토글
        self.lamp_btn = QPushButton(self.set_frame)
        self.lamp_btn.setGeometry(QtCore.QRect(170, 170, 40, 30))
        self.lamp_btn.setStyleSheet(f"{self.li_condition}")
        self.lamp_btn.setCheckable(True)
        self.lamp_btn.clicked.connect(self.lamp_bright_condition)

        # # 제품3 라벨  QPushButton
        # self.set_label3 = QLabel(self.set_frame)
        # self.set_label3.setGeometry(QtCore.QRect(20, 220, 210, 60))
        # self.set_label3.setStyleSheet("border: 2px solid #fefefe;")
        # # 버튼  라벨..
        # self.set_button3 = QLabel(self.set_frame)
        # self.set_button3.setGeometry(QtCore.QRect(30, 230, 50, 40))
        # self.set_button3.setStyleSheet("border-image: url(./QTbutton/vim.png);\n")
        # # 토글
        # self.all_button3 = QPushButton(self.set_frame)
        # self.all_button3.setGeometry(QtCore.QRect(90, 230, 50, 40))
        # self.all_button3.setStyleSheet("border-image: url(./QTbutton/off.png);\n")
        # self.all_button3.setCheckable(True)
        # self.all_button3.clicked.connect(self.set_toggle3)
        # self.all_button3.clicked.connect(lambda: self.add_tiem_to_dict("beam"))
        #
        # # 알람
        # self.alarm_button3 = QPushButton(self.set_frame)
        # self.alarm_button3.setGeometry(QtCore.QRect(150, 230, 30, 20))
        # self.alarm_button3.setStyleSheet(
        #     "border-image: url(./QTbutton/timer.png);\n")  # "background-color: rgba(0, 0, 0,0);\n"
        # self.alarm_button3.clicked.connect(self.alarm)

        self.usage_chart = QLabel(self.set_frame)
        self.usage_chart.setGeometry(QtCore.QRect(240, 0, 600, 450))
        # self.usage_chart.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.usage_chart.setStyleSheet("background-color: rgb(63, 73, 98);")

        self.set_frame.show()

    def set_toggle1(self):
        if self.ac_toggle != "border-image: url(./QTbutton/on.png);\n":
            print("에어컨 on")
            py_serial.write("acon".encode())
            self.ac_toggle = "border-image: url(./QTbutton/on.png);\n"
            self.ac_label = "border: 1px solid #f09d3e;\n"
            self.ac_condition = "border-image: url(./QTbutton/ht.png);\n"
            self.all_button1.setStyleSheet(f"{self.ac_toggle}")
            self.set_label1.setStyleSheet(f"{self.ac_label}")
            self.ac_ht.setStyleSheet(f"{self.ac_condition}")
        else:
            print("에어컨 off")
            # py_serial.write("acoff".encode())
            self.ac_toggle = "border-image: url(./QTbutton/off.png);\n"
            self.ac_label = "border: 1px solid #fefefe;\n"
            self.ac_condition = "border-image: url(./QTbutton/heating.png);\n"
            self.all_button1.setStyleSheet(f"{self.ac_toggle}")
            self.set_label1.setStyleSheet(f"{self.ac_label}")
            self.ac_ht.setStyleSheet(f"{self.ac_condition}")

    def set_toggle2(self):
        if self.li_toggle != "border-image: url(./QTbutton/on.png);\n":
            print("전등 on")
            # py_serial.write("donn".encode())
            self.li_toggle = "border-image: url(./QTbutton/on.png);\n"
            self.li_label = "border: 1px solid #f09d3e;\n"
            self.all_button2.setStyleSheet(f"{self.li_toggle}")
            self.set_label2.setStyleSheet(f"{self.li_label}")
        else:
            print("전등 off")
            # py_serial.write("doff".encode())
            self.li_toggle = "border-image: url(./QTbutton/off.png);\n"
            self.li_label = "border: 1px solid #fefefe;"
            self.li_condition = "border-image: url(./QTbutton/brightness.png);\n"
            self.all_button2.setStyleSheet(f"{self.li_toggle}")
            self.set_label2.setStyleSheet(f"{self.li_label}")
            self.lamp_btn.setStyleSheet(f"{self.li_condition}")

    # def set_toggle3(self, state):
    #     if state:
    #         print("빔프로젝트 on")
    #         self.all_button3.setStyleSheet("border-image: url(./QTbutton/on.png);\n")
    #         self.set_label3.setStyleSheet("border: 2px solid #f09d3e;\n")
    #         # self.all_button.setStyleSheet("border-image: url(./QTbutton/on.png);\n")
    #     else:
    #         print("빔프로젝트 off")
    #         # self.all_on.setStyleSheet("border-image: url(./QTbutton/off.png);\n")
    #         self.all_button3.setStyleSheet("border-image: url(./QTbutton/off.png);\n")
    #         self.set_label3.setStyleSheet("border: 2px solid #fefefe;")

    def add_tiem_to_dict(self, key):
        # 현재 시간을 포맷팅하여 딕셔너리에 추가
        check_time = str(datetime.datetime.now().time().replace(microsecond=0))
        self.total_usage[key].append(check_time)
        print(self.total_usage)

    def cal_power(self):
        try:
            layout = self.usage_chart.layout()
            if layout is not None:
                for i in range(layout.count()):
                    widget = layout.itemAt(i).widget()
                    if isinstance(widget, QChartView):
                        layout.removeWidget(widget)
                        widget.chart().removeAllSeries()
                        widget.chart().deleteLater()
                        widget.deleteLater()
        except Exception as e:
            pass
            print(e)

        self.usage_chart = QLabel(self.set_frame)
        self.usage_chart.setGeometry(QtCore.QRect(240, 0, 600, 450))
        self.usage_chart.setStyleSheet("background-color: rgb(63, 73, 98);")
        self.usage_chart.show()

        today_date = str(datetime.datetime.now().date())
        ac_result = []
        li_result = []
        # beam_result = []

        ac = self.total_usage["ac"]
        li = self.total_usage["light"]
        # beam = self.total_usage["beam"]

        if len(self.total_usage["ac"]) % 2 == 0:
            for i in range(1, len(ac), 2):
                time1 = datetime.datetime.strptime(ac[i - 1], "%H:%M:%S")
                time2 = datetime.datetime.strptime(ac[i], "%H:%M:%S")
                time_diff = int((time2 - time1).total_seconds())
                ac_result.append(time_diff)
                # print(ac_result)
                for i in ac_result:
                    self.ac_power += i
                    # print(self.ac_power)
                    ac_result.clear()
                    self.total_usage["ac"] = []
        else:
            pass
            # QMessageBox.information(self, '오류', '에어컨', QMessageBox.Ok)

        if len(self.total_usage["light"]) % 2 == 0:
            for i in range(1, len(li), 2):
                time1 = datetime.datetime.strptime(li[i - 1], "%H:%M:%S")
                time2 = datetime.datetime.strptime(li[i], "%H:%M:%S")
                time_diff = int((time2 - time1).total_seconds())
                li_result.append(time_diff)
                # print(li_result)
                for i in li_result:
                    self.li_power += i
                    # print(self.li_power)
                    li_result.clear()
                    self.total_usage["light"] = []
        else:
            pass
            # QMessageBox.information(self, '오류', '전등', QMessageBox.Ok)

        # if len(self.total_usage["beam"]) % 2 == 0:
        #     for i in range(1, len(beam), 2):
        #         time1 = datetime.datetime.strptime(beam[i - 1], "%H:%M:%S")
        #         time2 = datetime.datetime.strptime(beam[i], "%H:%M:%S")
        #         time_diff = int((time2 - time1).total_seconds())
        #         beam_result.append(time_diff)
        #         # print(beam_result)
        #         for i in beam_result:
        #             self.beam_power += i
        #             # print(self.beam_power)
        #             beam_result.clear()
        #             self.total_usage["beam"] = []
        # else:
        #     pass
        #     # QMessageBox.information(self, '오류', '빔 프로젝트', QMessageBox.Ok)

        print(self.ac_power)
        print(self.li_power)
        # print(self.beam_power)

        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()
        cur.execute("SELECT * FROM total_usage")
        x = list(cur.fetchall())
        for i in x:
            # print(i)
            ac_value = i[1]
            li_value = i[2]
            # beam_value = i[3]
            if i[0] == today_date:
                if ac_value is None or ac_value == '':
                    ac_value = self.ac_power
                else:
                    ac_value = int(ac_value) + self.ac_power

                if li_value is None or li_value == '':
                    li_value = self.li_power
                else:
                    li_value = int(li_value) + self.li_power
                # if beam_value is None or beam_value == '':
                #     beam_value = self.beam_power
                # else:
                #     beam_value = int(beam_value) + self.beam_power
                with con.cursor() as cursor:
                    cursor.execute("UPDATE total_usage SET ac=%s, light=%s WHERE date=%s",
                                   (ac_value, li_value, today_date))
                    con.commit()
                    self.ac_power = 0
                    self.li_power = 0
                    # self.beam_power = 0

        total_date = []
        ac_data = []
        li_data = []
        # beam_data = []

        cur.execute("SELECT * FROM total_usage")
        x = list(cur.fetchall())
        for i in x:
            # print(i)
            total_date.append(i[0].replace("-", ""))
            ac_data.append(i[1])
            li_data.append(i[2])
            # beam_data.append(i[3])
        con.commit()

        ac_data = [0 if x is None or x == "" else x for x in ac_data]
        li_data = [0 if x is None or x == "" else x for x in li_data]
        # beam_data = [0 if x is None or x == "" else x for x in beam_data]

        print(total_date)
        print(ac_data)
        print(li_data)
        # print(beam_data)

        range_data = []
        range_data.append(max(ac_data))
        range_data.append(max(li_data))
        # range_data.append(max(beam_data))

        try:
            series1 = QLineSeries(self)
            series2 = QLineSeries(self)
            # series3 = QLineSeries(self)

            for i in range(len(total_date)):
                if i < len((ac_data)):
                    series1.append(int(total_date[i]), int(ac_data[i]))

            for i in range(len(total_date)):
                if i < len((li_data)):
                    series2.append(int(total_date[i]), int(li_data[i]))

            # for i in range(len(total_date)):
            #     if i < len((beam_data)):
            #         series3.append(int(total_date[i]), int(beam_data[i]))

            chart = QChart()
            chart.setBackgroundBrush(Qt.transparent)

            x_axis = QValueAxis()
            x_axis.setLabelsColor(Qt.white)
            x_axis.setTitleText("날짜")
            brush = QBrush(Qt.white)
            x_axis.setTitleBrush(brush)
            x_axis.setLabelFormat("%d")  # x축 레이블 형식 설정
            # x_axis.setTickCount(len(total_date))  # x축에 표시되는 눈금 수 설정
            x_axis.setRange(int(min(total_date)), int(max(total_date)))
            chart.addAxis(x_axis, Qt.AlignBottom)  # x축을 차트에 추가

            y_axis = QValueAxis()
            y_axis.setLabelsColor(Qt.white)
            y_axis.setTitleText("전력량")
            brush = QBrush(Qt.white)
            y_axis.setTitleBrush(brush)
            y_axis.setRange(0, max(range_data))
            y_axis.setLabelFormat("%d")  # y축 레이블 형식 설정
            # y_axis.setTickCount(6)
            chart.addAxis(y_axis, Qt.AlignLeft)  # y축을 차트에 추가

            chart.addSeries(series1)
            chart.addSeries(series2)
            # chart.addSeries(series3)

            series1.attachAxis(x_axis)
            series1.attachAxis(y_axis)
            # series1.setPointLabelsVisible(True)

            series2.attachAxis(x_axis)
            series2.attachAxis(y_axis)

            # series3.attachAxis(x_axis)
            # series3.attachAxis(y_axis)

            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.setTitle(" 총 전 력 량 ")
            chart.setTitleBrush(Qt.white)

            legend = chart.legend()
            legend.setVisible(True)
            legend.setAlignment(Qt.AlignBottom)
            markers = legend.markers()
            markers[0].setLabel("ac")
            markers[0].setLabelBrush(Qt.white)
            markers[1].setLabel("light")
            markers[1].setLabelBrush(Qt.white)
            # markers[2].setLabel("beam")
            # markers[2].setLabelBrush(Qt.white)

            chartview = QChartView(chart)
            chartview.setRenderHint(QPainter.Antialiasing)

            # chartview.setRubberBand(QChartView.RectangleRubberBand)
            # chartview.setDragMode(QGraphicsView.ScrollHandDrag)
            chartview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            chartview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            chartview.setInteractive(True)

            layout = QVBoxLayout(self.usage_chart)
            layout.addWidget(chartview)
            chartview.setGeometry(0, 0, 600, 500)

        except Exception as e:
            print("전력량 차트", e)

    def ac_alarm(self):#0401
        self.ac_alarm_frame = QFrame(self.set_frame)
        self.ac_alarm_frame.setGeometry(QtCore.QRect(230, 80, 150, 80))
        self.ac_alarm_frame.setStyleSheet(
            "border: 1px solid #fefefe;""font: 14pt 'Agency FB';""color: rgb(255, 255, 255);")

        self.ac_label = QLabel("H", self.ac_alarm_frame)
        self.ac_label.setGeometry(QtCore.QRect(50, 10, 20, 30))
        self.ac_label.setStyleSheet(
            "font: 75 15pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border: none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.ac_label.setAlignment(QtCore.Qt.AlignCenter)  # 글씨 가운데

        self.ac_label1 = QLabel("M", self.ac_alarm_frame)  # 영? DAY
        self.ac_label1.setGeometry(QtCore.QRect(110, 10, 20, 30))
        self.ac_label1.setStyleSheet(
            "font: 75 15pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border: none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.ac_label1.setAlignment(QtCore.Qt.AlignCenter)  # 중앙
        # 여기
        self.ac_spinbox = QSpinBox(self.ac_alarm_frame)
        self.ac_spinbox.setGeometry(20, 10, 30, 30)
        self.ac_spinbox.setStyleSheet(
            "font: 75 15pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border: none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.ac_spinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.ac_spinbox.setRange(0, 23)
        self.ac_spinbox.setAlignment(QtCore.Qt.AlignCenter)
        # 여기
        self.ac_spinbox2 = QSpinBox(self.ac_alarm_frame)
        self.ac_spinbox2.setGeometry(70, 10, 40, 30)
        self.ac_spinbox2.setStyleSheet(
            "font: 75 15pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border: none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.ac_spinbox2.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.ac_spinbox2.setRange(0, 59)
        self.ac_spinbox2.setAlignment(QtCore.Qt.AlignCenter)

        self.button_box = QDialogButtonBox(Qt.Horizontal, self.ac_alarm_frame)
        self.button_box.setGeometry(QtCore.QRect(70, 50, 60, 20))
        self.button_box.setStyleSheet(
            "font: 75 14pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgba(255, 255, 255,);")
        self.button_box.setCenterButtons(True)
        self.button_box.addButton("O K", QDialogButtonBox.AcceptRole)
        self.button_box.addButton("Close", QDialogButtonBox.RejectRole)
        self.button_box.accepted.connect(
            lambda: self.ac_alarm_click(QDialogButtonBox.AcceptRole))
        self.button_box.rejected.connect(
            lambda: self.ac_alarm_click(QDialogButtonBox.RejectRole))

        layout = QVBoxLayout()
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.ac_alarm_frame.show()

    def li_alarm(self):
        self.li_alarm_frame = QFrame(self.set_frame)
        self.li_alarm_frame.setGeometry(QtCore.QRect(230, 80, 150, 80))
        self.li_alarm_frame.setStyleSheet(
            "border: 1px solid #fefefe;""font: 14pt 'Agency FB';""color: rgb(255, 255, 255);")

        self.li_label = QLabel("H", self.li_alarm_frame)
        self.li_label.setGeometry(QtCore.QRect(50, 10, 20, 30))
        self.li_label.setStyleSheet(
            "font: 75 15pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border: none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.li_label.setAlignment(QtCore.Qt.AlignCenter)  # 글씨 가운데

        self.li_label1 = QLabel("M", self.li_alarm_frame)
        self.li_label1.setGeometry(QtCore.QRect(110, 10, 20, 30))
        self.li_label1.setStyleSheet(
            "font: 75 15pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border: none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.li_label1.setAlignment(QtCore.Qt.AlignCenter)  # 중앙

        self.li_spinbox = QSpinBox(self.li_alarm_frame)
        self.li_spinbox.setGeometry(20, 10, 30, 30)
        self.li_spinbox.setStyleSheet(
            "font: 75 15pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border: none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.li_spinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.li_spinbox.setRange(0, 23)
        self.li_spinbox.setAlignment(QtCore.Qt.AlignCenter)

        self.li_spinbox2 = QSpinBox(self.li_alarm_frame)
        self.li_spinbox2.setGeometry(70, 10, 40, 30)
        self.li_spinbox2.setStyleSheet(
            "font: 75 15pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border: none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.li_spinbox2.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.li_spinbox2.setRange(0, 59)
        self.li_spinbox2.setAlignment(QtCore.Qt.AlignCenter)

        self.li_button_box = QDialogButtonBox(Qt.Horizontal, self.li_alarm_frame)
        self.li_button_box.setGeometry(QtCore.QRect(70, 50, 60, 20))
        self.li_button_box.setStyleSheet(
            "font: 75 14pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgba(255, 255, 255,);")
        self.li_button_box.setCenterButtons(True)
        self.li_button_box.addButton("O K", QDialogButtonBox.AcceptRole)
        self.li_button_box.addButton("Close", QDialogButtonBox.RejectRole)
        self.li_button_box.accepted.connect(
            lambda: self.li_alarm_click(QDialogButtonBox.AcceptRole))
        self.li_button_box.rejected.connect(
            lambda: self.li_alarm_click(QDialogButtonBox.RejectRole))

        layout = QVBoxLayout()
        layout.addWidget(self.li_button_box)
        self.setLayout(layout)

        self.li_alarm_frame.show()

    def ac_alarm_click(self, button_role):
        global ac_timer
        hour = self.ac_spinbox.text()
        min = self.ac_spinbox2.text()

        if button_role == QDialogButtonBox.AcceptRole:
            ac_timer = f"{hour}:{min}:00"
            print(ac_timer)
            QMessageBox.information(self, "에어컨 설정", f"{ac_timer} 알람 설정 완료")

            self.ac_timer_img = "border-image: url(./QTbutton/timer1.png);\n"
            self.alarm_button1.setStyleSheet(f"{self.ac_timer_img}")
            time.sleep(0.5)
            self.ac_alarm_frame.hide()
        elif button_role == QDialogButtonBox.RejectRole:
            self.ac_alarm_frame.hide()
            # QMessageBox.information(self, "Information", "Close button clicked!")
        else:
            pass

    def li_alarm_click(self, button_role):
        global li_timer
        hour = self.li_spinbox.text()
        min = self.li_spinbox2.text()

        if button_role == QDialogButtonBox.AcceptRole:
            li_timer = f"{hour}:{min}:00"
            print(li_timer)
            self.li_timer_img = "border-image: url(./QTbutton/timer1.png);\n"
            self.alarm_button2.setStyleSheet(f"{self.li_timer_img}")
            QMessageBox.information(self, "전등 설정", f"{li_timer} 알람 설정 완료")
            time.sleep(0.5)
            self.li_alarm_frame.hide()
        elif button_role == QDialogButtonBox.RejectRole:
            self.li_alarm_frame.hide()
            # QMessageBox.information(self, "Information", "Close button clicked!")
        else:
            pass

    def ac_ht_condition(self):
        if self.ac_condition == "border-image: url(./QTbutton/ht.png);\n":
            self.ac_condition = "border-image: url(./QTbutton/ac.png);\n"
            # py_serial.write("cool".encode())
            self.ac_ht.setStyleSheet(f"{self.ac_condition}")
        elif self.ac_condition == "border-image: url(./QTbutton/ac.png);\n":
            self.ac_condition = "border-image: url(./QTbutton/ht.png);\n"
            # py_serial.write("heater".encode())
            self.ac_ht.setStyleSheet(f"{self.ac_condition}")
        else:
            QMessageBox.information(self, '', '전원 확인 요청', QMessageBox.Ok)

    def lamp_bright_condition(self):
        if self.li_toggle == "border-image: url(./QTbutton/on.png);\n":
            if self.li_condition == "border-image: url(./QTbutton/brightness.png);\n":
                # py_serial.write("brightness".encode())
                self.li_condition = "border-image: url(./QTbutton/brightness1.png);\n"
                self.lamp_btn.setStyleSheet(f"{self.li_condition}")
            elif self.li_condition == "border-image: url(./QTbutton/brightness1.png);\n":
                # py_serial.write("brightness".encode())
                self.li_condition = "border-image: url(./QTbutton/brightness.png);\n"
                self.lamp_btn.setStyleSheet(f"{self.li_condition}")
        else:
            QMessageBox.information(self, '', '전원 확인 요청', QMessageBox.Ok)

    # 학생(유저) 추가 이벤트
    def enroll(self):
        py_serial.write("e".encode())
        QMessageBox.information(self, '등록 시작', '지문센서에 지문 등록 요청', QMessageBox.Ok)

    def add_user(self):
        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()

        today_date = str(datetime.datetime.now().date())
        add_id = self.add_id.text()
        add_pw = self.add_pw.text()
        add_name = self.add_name.text()
        select_class = self.room_box.currentText()
        add_num = self.add_num.text()

        user_list = []

        cur.execute("SELECT id FROM user")
        x = list(cur.fetchall())
        if len(x) != 0:
            for i in x:
                user_list.append(i[0])
        else:
            pass

        if add_id not in user_list:
            if add_id.isdigit():
                if 1 <= int(add_id) <= 127:
                    if add_pw != "" and add_name != "" and select_class != "" and add_num != "":
                        if len(add_pw) >= 8:
                            if add_num.isdigit() and len(add_num) == 11:
                                py_serial.write(add_id.encode())
                                sql1 = "INSERT INTO user(id, pw, name, classroom,phone) VALUES(%s,%s,%s,%s,%s)"
                                val = [(add_id, add_pw, add_name, select_class, add_num)]
                                try:
                                    print("try 안")
                                    cur.executemany(sql1, val)
                                    con.commit()

                                    cur.execute("SELECT id, name ,classroom FROM user")
                                    user_ids = cur.fetchall()

                                    cur.execute("SELECT id, date, name, classroom FROM attendance WHERE date=%s", (today_date,))
                                    existing_records = cur.fetchall()

                                    existing_ids = [r[0] for r in existing_records]
                                    # 중복 제거
                                    for user_id in user_ids:
                                        if user_id[0] not in existing_ids:
                                            sql = "INSERT INTO attendance (id, date, name, classroom) VALUES (%s, %s, %s,%s)"
                                            val = (user_id[0], today_date, user_id[1], user_id[2])
                                            cur.execute(sql, val)
                                    con.commit()
                                except Exception as ex:
                                    con.commit()
                                    print('add_user 오류 : ', ex)
                            else:
                                QMessageBox.warning(self, '오류', '휴대폰 번호 확인', QMessageBox.Ok)
                        else:
                            QMessageBox.warning(self, '오류', '비밀번호 8자 이상', QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, '오류', '입력칸 확인', QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, '오류', 'id 1부터 127까지 입력', QMessageBox.Ok)
            else:
                QMessageBox.warning(self, '오류', 'id 숫자로만 입력', QMessageBox.Ok)
        else:
            QMessageBox.warning(self, '오류', 'id 중복', QMessageBox.Ok)

    # user 조회
    def click_search(self):
        self.user_table.setRowCount(0)

        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()

        sql = "SELECT * FROM "
        x = "smartclass.user"
        cur.execute(sql + x)
        result = list(cur.fetchall())

        try:
            for i, row in enumerate(result):
                self.user_table.setRowCount(i + 1)
                # print(row[4])
                if row[3] == self.search_user.currentText():  # row[4]
                    for j, item in enumerate(row[:6]):
                        a = QTableWidgetItem(str(item))
                        a.setTextAlignment(Qt.AlignCenter)
                        self.user_table.setItem(i, j, a)
                        self.checkbox = QCheckBox()
                        self.checkbox.setStyleSheet("border: none;")
                        self.checkbox.setChecked(False)
                        self.user_table.setCellWidget(i, 5,self.checkbox) #여기 체크
            # 빈칸제거
            for i in range(self.user_table.rowCount() - 1, -1, -1):
                empty_row = True
                for j in range(self.user_table.columnCount()):
                    if self.user_table.item(i, j) is not None:
                        empty_row = False
                        break
                if empty_row:
                    self.user_table.removeRow(i)
            con.commit()
        except Exception as e:
            print("user 조회 : ", e)
            con.commit()

    def del_user(self):
        reply = QMessageBox.question(self, '', '삭제하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        #reply.setStyleSheet("border:none;")

        if reply == QMessageBox.Yes:
            selected_rows = []
            for row in range(self.user_table.rowCount()):
                item = self.user_table.cellWidget(row, 5)
                if item and item.isChecked():
                    selected_rows.append(row)

            if selected_rows:
                try:
                    con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
                    cur = con.cursor()

                    for i in sorted(selected_rows, reverse=True):
                        row_id = self.user_table.item(i, 0).text()
                        sql = "DELETE FROM smartclass.user WHERE id=%s"
                        cur.execute(sql, row_id)

                        sql2 = "DELETE FROM smartclass.attendance WHERE id=%s"
                        cur.execute(sql2, row_id)

                        self.user_table.removeRow(i)

                    con.commit()

                except Exception as e:
                    print(e)
                    con.rollback()

                finally:
                    cur.close()
                    con.close()

    def spin_text(self):
        person = self.spinbox.text()
        days = self.spinbox1.text()
        # print(person)
        # print(days)

    # 교실 추가
    def add_classroom(self):
        con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
        cur = con.cursor()

        add_class = self.add_text.text()
        person = self.spinbox.text()
        days = self.spinbox1.text()

        class_list = []

        cur.execute("SELECT class_name FROM classroom")
        x = list(cur.fetchall())
        if len(x) != 0:
            for i in x:
                class_list.append(i[0])
        else:
            pass

        if self.add_text.text() != "":
            if add_class not in class_list:
                sql1 = "INSERT INTO classroom (class_name, personnel, course_days) VALUES (%s, %s, %s)"
                val = [(add_class, person, days)]
                # a = "SELECT * FROM classroom;"
                try:
                    cur.executemany(sql1, val)
                    con.commit()
                except Exception as ex:
                    con.commit()
                    print('add_classroom 오류', ex)
                print(add_class)

                self.room_box.clear()
                self.combobox1.clear()
                self.classroom_table.clear()
                self.add_text.clear()
                self.spinbox.clear()
                self.spinbox1.clear()

                QMessageBox.information(self, '교실 개설 성공', f'{add_class} 추가', QMessageBox.Ok)
                sql6 = "SELECT * FROM "
                x = "smartclass.classroom"
                cur.execute(sql6 + x)
                result = list(cur.fetchall())
                try:
                    for i in result:
                        # print(i)
                        self.room_box.addItem(i[1])
                        self.combobox1.addItem(i[1])
                        # self.search_user.addItem(i[1])
                    con.commit()
                except Exception as e:
                    print("학생관리 : ", e)
                    pass
                    con.commit()

                try:
                    class_colum = ["class_name", "personnel", "course_days", "ck"]
                    self.classroom_table.setHorizontalHeaderLabels(class_colum)
                    for i, row in enumerate(result):
                        self.classroom_table.setRowCount(i + 1)
                        # print(row[4])
                        for j, item in enumerate(row[1:4]):
                            a = QTableWidgetItem(str(item))
                            a.setTextAlignment(Qt.AlignCenter)
                            self.classroom_table.setItem(i, j, a)
                            self.checkbox = QCheckBox()
                            self.checkbox.setStyleSheet("border: none;")
                            self.checkbox.setChecked(False)
                            self.classroom_table.setCellWidget(i, 3, self.checkbox)
                    # 빈칸제거
                    for i in range(self.classroom_table.rowCount() - 1, -1, -1):
                        empty_row = True
                        for j in range(self.classroom_table.columnCount()):
                            if self.classroom_table.item(i, j) is not None:
                                empty_row = False
                                break
                        if empty_row:
                            self.classroom_table.removeRow(i)
                    con.commit()
                except Exception as e:
                    print("교실 관리 : ", e)
                    pass
                    con.commit()
            else:
                QMessageBox.warning(self, '오류', '교실 추가 실패/중복 확인', QMessageBox.Ok)
                self.add_text.clear()
        else:
            QMessageBox.warning(self, '오류', '교실 이름을 입력해 주세요', QMessageBox.Ok)

################ 클라이언트 ui  버튼 #######################
    def logout1(self):
        self.start_frame1.close()
        self.login_frame.show()
        self.login_id.clear()
        self.login_pw.clear()
        try:
            self.home_frame1.close()
        except:
            pass
        try:
            self.Notice_frame1.close()
        except:
            pass
        try:
            self.att_frame1.close()
        except:
            pass
        try:
            self.cam_frame1.close()
        except:
            pass

    def logout(self):
        try:
            self.home_frame.close()
        except:
            pass
        try:
            self.Notice_frame.close()
        except:
            pass
        try:
            self.search_frame.close()
        except:
            pass
        try:
            self.att_frame.close()
        except:
            pass
        try:
            self.user_frame.close()
        except:
            pass
        try:
            self.cam_frame.close()
        except:
            pass
        try:
            self.set_frame.close()
        except:
            pass
        self.start_frame.close()
        self.login_frame.show()
        self.login_id.clear()
        self.login_pw.clear()

    def start_client_ui(self):
        try:
            client_socket.send((f"client_att/{self.login_id.text()}").encode('utf-8'))
            time.sleep(1)
            progress = client_socket.recv(1096).decode('utf-8')
            print(progress)
            if progress == "-":
                pass
            else:
                class_progress = progress.split('/')
                current_pro = int(class_progress[0])
                total_pro = int(class_progress[1])
            progress_percent = round((current_pro / total_pro) * 100, 1)

            self.start_frame1 = QFrame(self)  # 전체적 프레임
            self.start_frame1.setGeometry(QtCore.QRect(0, 0, 1000, 550))
            self.start_frame1.setStyleSheet("background-color: rgb(63, 73, 98);""color: rgb(255, 255, 255);")

            # 카테고리 라벨 사이드
            self.title_label = QLabel(self.start_frame1)
            self.title_label.setGeometry(QtCore.QRect(0, 100, 80, 440))
            self.title_label.setStyleSheet("border-right:1px solid rgb(254,156,29);")

            # 상단라벨 라벨
            self.top_label1 = QLabel(self.start_frame1)
            self.top_label1.setGeometry(QtCore.QRect(0, 0, 1000, 101))
            self.top_label1.setStyleSheet(
                "background-color:rgb(63, 73, 98);\n""border-bottom:1px solid  rgb(254,156,29);")

            # 임시 출석 %
            self.label_color1 = QLabel(self.start_frame1)
            self.label_color1.setGeometry(QtCore.QRect(0, 96, 1000 - int(((current_pro / total_pro) * 1000)), 5))
            self.label_color1.setStyleSheet("background-color: rgb(254,156,29);")

            # 수업 진행률
            self.user_btn = QLabel("0.0%", self.start_frame1)
            self.user_btn.setGeometry(QtCore.QRect(805, 57, 40, 30))
            self.user_btn.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;")
            self.user_btn.setText(f"{progress_percent}%")

            # user라벨
            self.user_btn = QPushButton("LOGOUT", self.start_frame1)
            self.user_btn.setGeometry(QtCore.QRect(865, 20, 50, 30))
            self.user_btn.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;")
            self.user_btn.clicked.connect(self.logout1)
            self.animation = QtCore.QPropertyAnimation(self.user_btn, b"geometry")
            # self.user_but.mousePressEvent = self.on_button_clicked
            self.user_btn.enterEvent = self.on_button_entered1
            self.user_btn.leaveEvent = self.on_button_left1

            # user id 라벨
            self.user_label = QLabel(self.login_id.text(), self.start_frame1)  # 로그인시 유저 아이디나 이름
            self.user_label.setGeometry(QtCore.QRect(805, 20, 40, 30))
            self.user_label.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);")
            self.user_label.setAlignment(QtCore.Qt.AlignCenter) #여기

            # 카테고리 버튼
            # 홈
            self.home_but = QPushButton(self.start_frame1)
            self.home_but.setGeometry(QtCore.QRect(20, 120, 40, 30))
            self.home_but.setStyleSheet(
                "border-image: url(./QTbutton/home.png);\n""background-color: rgba(0, 0, 0,0);\n""border:none;")
            self.home_but.clicked.connect(self.open_home_frame1)

            self.animation = QtCore.QPropertyAnimation(self.home_but, b"geometry")
            self.home_but.enterEvent = self.on_button_entered2
            self.home_but.leaveEvent = self.on_button_left2

            # 공지
            self.Notice_but = QPushButton(self.start_frame1)
            self.Notice_but.setGeometry(QtCore.QRect(20, 180, 40, 30))
            self.Notice_but.setStyleSheet(
                "border-image: url(./QTbutton/calendar.png);\n""background-color: rgba(0, 0, 0,0);\n""border:none;")
            self.Notice_but.clicked.connect(self.open_Notice_frame1)

            self.animation = QtCore.QPropertyAnimation(self.Notice_but, b"geometry")
            self.Notice_but.enterEvent = self.on_button_entered3
            self.Notice_but.leaveEvent = self.on_button_left3

            # 출결
            self.chat_but = QPushButton(self.start_frame1)
            self.chat_but.setGeometry(QtCore.QRect(20, 240, 40, 30))
            self.chat_but.setStyleSheet(
                "border-image: url(./QTbutton/search.png);\n""background-color: rgba(0, 0, 0,0);\n""border:none;")
            self.chat_but.clicked.connect(self.open_att_frame1)

            self.animation = QtCore.QPropertyAnimation(self.chat_but, b"geometry")
            self.chat_but.enterEvent = self.on_button_entered4
            self.chat_but.leaveEvent = self.on_button_left4

            # 애니메이션
            self.animation = QtCore.QPropertyAnimation(self.chat_but, b"geometry")
            self.chat_but.enterEvent = self.on_button_entered4
            self.chat_but.leaveEvent = self.on_button_left4

            # 영상수업
            self.cam_but = QPushButton(self.start_frame1)
            self.cam_but.setGeometry(QtCore.QRect(20, 300, 40, 30))
            self.cam_but.setStyleSheet(
                "border-image: url(./QTbutton/webcam.png);\n""background-color: rgba(0, 0, 0,0);\n""border:none;")
            self.cam_but.clicked.connect(self.open_cam_frame1)
            self.animation = QtCore.QPropertyAnimation(self.cam_but, b"geometry")
            self.cam_but.enterEvent = self.on_button_entered5
            self.cam_but.leaveEvent = self.on_button_left5

            # 나가기  #아이콘 임시
            self.exit_btn = QPushButton("EXIT", self.start_frame1)
            self.exit_btn.setGeometry(QtCore.QRect(940, 20, 20, 30))
            self.exit_btn.setStyleSheet("font: 75 15pt 'Agency FB';""color:rgb(255, 255, 255);""border: none;")
            self.exit_btn.clicked.connect(self.exit_frame)
            #
            self.animation = QtCore.QPropertyAnimation(self.exit_btn, b"geometry")
            self.exit_btn.enterEvent = self.on_button_entered9
            self.exit_btn.leaveEvent = self.on_button_left9

            self.start_frame1.show()
        except Exception as e:
            print("v버튼 클라", e)

    def open_home_frame1(self):
        self.home_frame1 = QFrame(self)
        self.home_frame1.setGeometry(QtCore.QRect(100, 130, 880, 410))
        self.home_frame1.setStyleSheet("background-color: rgb(63, 73, 98);")
        self.home_frame1.show()

    def open_Notice_frame1(self):
        try:
            if self.timer1.isActive():
                self.timer1.stop()
            else:
                pass
        except:
            pass

        self.Notice_frame1 = QFrame(self)
        self.Notice_frame1.setGeometry(QtCore.QRect(100, 130, 880, 410))
        self.Notice_frame1.setStyleSheet("background-color: rgb(63, 73, 98);")

        # 달력
        self.calendar1 = QCalendarWidget(self.Notice_frame1)
        self.calendar1.setGeometry(QtCore.QRect(10, 10, 380, 390))
        self.calendar1.setStyleSheet(
            "selection-background-color: rgb(254, 156, 29);\n""alternate-background-color: rgb(216,216,216,150);" "color:rgb(255, 255, 255);")
        self.calendar1.setVerticalHeaderFormat(0)  # vertical header 숨기기
        self.calendar1.selectionChanged.connect(self.show_dialog1)

        # 날짜  캘릭터 클릭시 날짜 표시
        self.day_label1 = QLabel(self.Notice_frame1)
        self.day_label1.setGeometry(QtCore.QRect(410, 30, 180, 30))
        self.day_label1.setStyleSheet(
            "color:rgb(255, 255, 255);""border:none;""border-bottom:1px solid rgba(255, 255, 255,);""font: 75 13pt 'Agency FB';")

        # 제목
        self.title_edit1 = QLineEdit(self.Notice_frame1)
        self.title_edit1.setGeometry(QtCore.QRect(410, 80, 180, 30))
        self.title_edit1.setPlaceholderText('제목')  # setPlaceholderText 글을 쓰면 사라짐
        self.title_edit1.setStyleSheet(
            "color:rgb(255, 255, 255);""border:none;""border-bottom:1px solid rgba(255, 255, 255,);""font: 75 13pt 'Agency FB';")

        # 내용
        self.content_edit1 = QTextEdit(self.Notice_frame1)  # 내용
        self.content_edit1.setGeometry(QtCore.QRect(410, 130, 450, 200))
        self.content_edit1.setStyleSheet(
            "color:rgb(255, 255, 255);""border: 1px solid #fefefe;""font: 75 13pt 'Agency FB';")

        self.Notice_frame1.show()

    def show_dialog1(self):
        global client_socket
        date = self.calendar1.selectedDate().toString("yyyy-MM-dd")
        self.day_label1.setText(date)
        print(date)
        client_socket.send(f"notice/{date}".encode())
        time.sleep(0.1)
        note = client_socket.recv(1096)
        note = note.decode("utf-8")
        note = note.replace("-", "")
        try:
            a = note.split('/')
            self.title_edit1.setText(a[0])
            self.content_edit1.setText(a[1])
            print(note)
        except:
            self.title_edit1.clear()
            self.content_edit1.clear()

    def open_cam_frame1(self):
        #웹캠 프레임
        self.cam_frame1 = QFrame(self)
        self.cam_frame1.setGeometry(QtCore.QRect(100, 130, 880, 410))
        self.cam_frame1.setStyleSheet("background-color: rgb(63, 73, 98);")

        # 웹캠 영상용
        self.cam_label1 = QLabel(self.cam_frame1)
        self.cam_label1.setGeometry(QtCore.QRect(10, 10, 860, 380))
        self.cam_label1.setStyleSheet("border:none;")

        # 버튼 카테고리
        self.on_button1 = QPushButton("ON", self.cam_frame1)
        self.on_button1.setGeometry(QtCore.QRect(740, 340, 40, 30))
        self.on_button1.setStyleSheet(
            "font: 75 14pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.on_button1.clicked.connect(self.start_cam1)

        self.off_button1 = QPushButton("OFF", self.cam_frame1)
        self.off_button1.setGeometry(QtCore.QRect(790, 340, 40, 30))
        self.off_button1.setStyleSheet(
            "font: 75 14pt 'Agency FB';\n""color: rgb(255, 255, 255);\n""border:none;""border-bottom:1px solid rgb(255, 255, 255);")
        self.off_button1.clicked.connect(self.stop_cam1)

        self.cam_frame1.show()

    def start_cam1(self):
        try:
            self.timer1 = QtCore.QTimer()
            self.timer1.timeout.connect(self.sss)
            self.timer1.start(10)
        except Exception as e:
            print("카메라 연결 안됨", e)
            QMessageBox.critical(self, '카메라 연결 안됨', "", QMessageBox.Ok)
            pass

    def sss(self):
        global data1
        try:
            message = 'web'
            client_socket.send(message.encode())
            length = self.recvall(client_socket, 16)
            stringData = self.recvall(client_socket, int(length))
            data = np.frombuffer(stringData, dtype='uint8')
            data1 = cv2.imdecode(data, 1)

            img = QImage(data1.data, data1.shape[1], data1.shape[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(img).scaled(self.cam_label1.width(), self.cam_label1.height())  # 캠 라벨 사이즈에 맞게 영상 조절
            self.cam_label1.setPixmap(pix)
            self.stop_thread = False

        except Exception as e:
            print("sss", e)

    def stop_cam1(self):
        try:
            self.cam_label1.setPixmap(QPixmap.fromImage(QImage()))
            self.timer1.stop()
            self.stop_thread = True
            if self.thread_id:
                exit_thread()
        except Exception as e:
            print("stop_cam", e)
            QMessageBox.critical(self, '카메라 연결 안됨', "", QMessageBox.Ok)
            pass

    def open_att_frame1(self):
        user_result = {"출석": 0, "지각": 0, "조퇴": 0, "결석":0}
        try:
            if self.timer1.isActive():
                self.timer1.stop()
            else:
                pass
        except:
            pass

        self.att_frame1 = QFrame(self)
        self.att_frame1.setGeometry(QtCore.QRect(100, 130, 880, 410))
        self.att_frame1.setStyleSheet("background-color: rgb(63, 73, 98);")

        self.att_label1 = QLabel(self.att_frame1)
        self.att_label1.setGeometry(QtCore.QRect(0, 0, 700, 400))
        self.att_label1.setStyleSheet("background-color: transparent;")
        # self.att_label1.setStyleSheet("background-color: rgb(255, 255, 255);")

        client_socket.send(f"att/{self.login_id.text()}".encode())
        user_att = client_socket.recv(1096).decode('utf-8')
        try:
            user_att = ast.literal_eval(user_att)
            print(user_att)
        except Exception as e:
            print("user 출결", e)
        try:
            for i in range(1, len(user_att), 2):
                en = user_att[i-1]
                ex = user_att[i]
                if en is not None and en != "" and ex is not None and ex != "":
                    en = datetime.datetime.strptime(user_att[i -1], "%H:%M:%S")
                    ex = datetime.datetime.strptime(user_att[i], "%H:%M:%S")
                    if en <= datetime.datetime.strptime("09:00:00", "%H:%M:%S") and ex >= datetime.datetime.strptime(
                            "17:50:00", "%H:%M:%S"):
                        user_result["출석"] += 1
                    elif en > datetime.datetime.strptime("09:00:00", "%H:%M:%S") and ex >= datetime.datetime.strptime(
                            "17:50:00", "%H:%M:%S"):
                        user_result["지각"] += 1
                    elif en <= datetime.datetime.strptime("09:00:00", "%H:%M:%S") and ex < datetime.datetime.strptime(
                            "17:50:00", "%H:%M:%S"):
                        user_result["조퇴"] += 1
                    elif en > datetime.datetime.strptime("09:00:00", "%H:%M:%S") and ex < datetime.datetime.strptime(
                            "17:50:00", "%H:%M:%S"):
                        user_result["조퇴"] += 1
                elif en is None or en == "" or ex is None or ex == "":
                    user_result["결석"] += 1
            print(user_result)
        except Exception as e:
            print("user_result",e)
        series = QPieSeries()
        series.append("출석", user_result["출석"])
        series.append("지각", user_result["지각"])
        series.append("조퇴", user_result["조퇴"])
        series.append("결석", user_result["결석"])
        # series.append("PHP", 30)

        # adding slice
        slice = QPieSlice()
        slice = series.slices()[0]
        slice1 = series.slices()[1]
        slice2 = series.slices()[2]
        slice3 = series.slices()[3]
        slice.setExploded(True)
        slice.setLabelVisible(True)

        # slice1.setExploded(True)
        slice1.setLabelVisible(True)
        slice1.setLabelColor(Qt.white)
        # slice2.setExploded(True)
        slice2.setLabelVisible(True)
        slice2.setLabelColor(Qt.white)
        # slice3.setExploded(True)
        slice3.setLabelVisible(True)
        slice3.setLabelColor(Qt.white)

        slice.setPen(QPen(Qt.white, 2))
        slice.setLabelColor(Qt.white)
        # slice.setBrush(Qt.green)
        color = QColor()
        color.setRgb(102, 104, 198)
        slice.setBrush(color)

        chart = QChart()
        chart.legend().hide()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle("나의 출석 현황")
        chart.setTitleFont(QFont("Arial", 14, QFont.Bold))
        chart.setTitleBrush(QBrush(Qt.white))

        legend = chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignBottom)
        legend.setLabelColor(Qt.white)

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)
        chartview.setBackgroundBrush(Qt.transparent)

        # set up layout
        layout = QVBoxLayout(self.att_label1)
        # layout.addWidget(chartview, alignment=Qt.AlignRight | Qt.AlignTop)
        layout.addWidget(chartview)
        chartview.setGeometry(0, 0, 700, 400)

        chart.setBackgroundBrush(Qt.transparent)

        self.att_frame1.show()

    def open_exit_frame(self):
        self.close()

##########서버######################################
def Threaded(client_socket, addr, queue):  # 서버쓰레드
    print("연결 주소 : ", addr[0], "-", addr[1])
    while True:
        try:
            con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
            cur = con.cursor()
            ready_to_read, _, _ = select.select([client_socket], [], [], 0)
            if not ready_to_read:
                continue
            data = client_socket.recv(4096)
            print(data)
            if not data:
                break

            elif 'user_login' in bytes(data).decode():
                print("if 안")
                try_login = bytes(data).decode().split('/')
                # print(a)
                sql = "SELECT * FROM "
                x = "smartclass.user"
                cur.execute(sql + x)
                db_data = list(cur.fetchall())
                for i in db_data:
                    # print(i)
                    if window.combobox1.currentText() == i[3]:
                        if i[0] == try_login[1] and try_login[1] == try_login[2]:
                            client_socket.send("1".encode())
                        else:
                            client_socket.send("0".encode())
                    else:
                        client_socket.send("0".encode())

            elif 'client_att' in bytes(data).decode():
                try:
                    cli_classroom = ""
                    total_pro = 0
                    current_pro = 0
                    c = bytes(data).decode().split('/')
                    cur.execute("SELECT id, classroom FROM user")
                    db_data = list(cur.fetchall())
                    for i in db_data:
                        if c[1] == i[0]:
                            cli_classroom = i[1]
                            print(i[0])
                    print(cli_classroom)
                    cur.execute("SELECT class_name, course_days FROM classroom")
                    db_data = list(cur.fetchall())
                    for i in db_data:
                        if cli_classroom == i[0]:
                            total_pro = i[1]
                    print(total_pro)
                    cur.execute("SELECT COUNT(DISTINCT date) FROM attendance")
                    result = cur.fetchone()
                    current_pro = result[0]
                    print(current_pro)
                    client_socket.send(f"{current_pro}/{total_pro}".encode('utf-8'))
                except:
                    client_socket.send("-".encode())
                    pass

            elif 'notice' in bytes(data).decode():
                n = bytes(data).decode().split('/')
                sql = "SELECT * FROM "
                x = "smartclass.notice"
                cur.execute(sql + x)
                db_data = list(cur.fetchall())
                # print(db_data)
                if len(db_data) != 0:
                    for i in db_data:
                        # print(i)
                        if i[1] == window.combobox1.currentText() and i[2] == n[1]:
                            client_socket.send(f"{i[3]}/{i[4]}".encode('utf-8'))
                        else:
                            client_socket.send("-".encode())
                else:
                    client_socket.send("-".encode())

            elif 'att' in bytes(data).decode():
                a = []
                att = bytes(data).decode().split('/')
                sql = "SELECT * FROM "
                x = "smartclass.attendance"
                cur.execute(sql + x)
                db_data = list(cur.fetchall())
                for i in db_data:
                    if att[1] == i[2]:
                        a.append(i[3])
                        a.append(i[4])
                client_socket.send(str(a).encode('utf-8'))

            elif 'web' in bytes(data).decode():
                if window.check_cam == "1":
                    string_data = queue.get()
                    client_socket.send(str(len(string_data)).ljust(16).encode())  # 16칸으로 맞춘다(규격)
                    client_socket.send(string_data)
                else:
                    client_socket.send(str(len("camX")).ljust(16).encode())
                    client_socket.send("camX".encode('utf-8'))
            con.commit()

        except Exception as e:
            print("Threaded 에러", e)
            break

    client_socket.close()

def open_server():
    print("함수 server")
    try:
        while True:
            print("클라이언트 접속 대기 while 문")
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            client_socket, addr = server_socket.accept()
            start_new_thread(Threaded, (client_socket, addr, enclosure_queue,))
    except:
        pass

def Arduino():
    global ac_timer
    global li_timer
    while True:
        now_time = str(datetime.datetime.now().time().replace(microsecond=0))
        check_time = datetime.datetime.strptime(now_time, "%H:%M:%S")
        today_date = str(datetime.datetime.now().date())
        read_adu = py_serial.readline().decode()
        read_adu = read_adu.replace("\n", "")
        read_adu = read_adu.replace("\r", "")
        print(read_adu)
        # print(now_time)
        # print(ac_timer)
        # print(li_timer)

        if ac_timer != "":
            ac_timer_on = datetime.datetime.strptime(ac_timer, "%H:%M:%S")
            ac_timer_be = ac_timer_on - datetime.timedelta(seconds=5)
            ac_timer_af = ac_timer_on + datetime.timedelta(seconds=5)
            # print(ac_timer_be)
            # print(ac_timer_af)
            if ac_timer_be <= check_time and check_time <= ac_timer_af:
                py_serial.write("acoff".encode())
                # check_time = str(datetime.datetime.now().time().replace(microsecond=0))
                window.ac_toggle = "border-image: url(./QTbutton/off.png);\n"
                window.ac_label = "border: 2px solid #fefefe;"
                window.ac_timer_img = "border-image: url(./QTbutton/timer2.png);\n"
                window.ac_condition = "border-image: url(./QTbutton/heating.png);\n"
                if len(window.total_usage["ac"]) % 2 !=0:
                    window.total_usage["ac"].append(now_time)
                    print(window.total_usage)
                try:
                    window.all_button1.setStyleSheet(f"{window.ac_toggle}")
                    window.set_label1.setStyleSheet(f"{window.ac_label}")
                    window.alarm_button1.setStyleSheet(f"{window.ac_timer_img}")
                    window.ac_ht.setStyleSheet(f"{self.ac_condition}")
                except:
                    pass
                else:
                    pass

        if li_timer != "":
            li_timer_on = datetime.datetime.strptime(li_timer, "%H:%M:%S")
            li_timer_be = li_timer_on - datetime.timedelta(seconds=5)
            li_timer_af = li_timer_on + datetime.timedelta(seconds=5)
            # print(li_timer_be)
            # print(li_timer_af)
            if li_timer_be <= check_time and check_time <= li_timer_af:
                print("if 안")
                py_serial.write("doff".encode())
                window.li_toggle = "border-image: url(./QTbutton/off.png);\n"
                window.li_label = "border: 2px solid #fefefe;"
                window.li_timer_img = "border-image: url(./QTbutton/timer2.png);\n"
                window.li_condition = "border-image: url(./QTbutton/brightness.png);\n"
                if len(window.total_usage["light"]) % 2 != 0:
                    window.total_usage["light"].append(now_time)
                    print(window.total_usage)
                try:
                    window.all_button2.setStyleSheet(f"{window.li_toggle}")
                    window.set_label2.setStyleSheet(f"{window.li_label}")
                    window.alarm_button2.setStyleSheet(f"{window.li_timer_img}")
                    window.lamp_btn.setStyleSheet(f"{self.li_condition}")
                except:
                    pass
            else:
                pass

        check_id = ""
        if "Found ID" in read_adu:
            for i in read_adu:
                if i.isdigit():
                    check_id += i
                    check_id = str(i).zfill(3)
            # print(check_id)
            con = pymysql.connect(host='localhost', user='root', password='0000', db="smartclass", charset='utf8')
            cur = con.cursor()
            sql = "SELECT * FROM "
            x = "smartclass.attendance"
            cur.execute(sql + x)
            result = list(cur.fetchall())
            for j in result:
                # a = j[1]
                # b = j[2]
                if j[1] == today_date and j[2] == check_id:
                    #지문 수정
                    if j[3] == "-":
                        cur.execute("UPDATE attendance SET entry_time = %s WHERE num = %s", (now_time, j[0]))
                        con.commit()
                    elif j[4] == "-":
                        cur.execute("UPDATE attendance SET exit_time = %s WHERE num = %s", (now_time, j[0]))
                        con.commit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
