import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from Kiwoom import *
import time
#ui에 연결
form_class = uic.loadUiType("pytrader.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.trade_stocks_done = False
        #키움에 연결
        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()
        # 현시간 확인
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout)
        #타이머 2 10초후 연결
        self.timer2 = QTimer(self)
        self.timer2.start(1000 *10)
        self.timer2.timeout.connect(self.timeout2)
        #계좌정보 얻기 (지금은 모의계좌)
        accouns_num = int(self.kiwoom.get_login_info("ACCOUNT_CNT"))
        accounts = self.kiwoom.get_login_info("ACCNO")
        #계좌번호는 ;로 분리되어있어서 ; 기준으로 분류해서 저장
        accounts_list = accounts.split(';')[0:accouns_num]
        self.w_account.addItems(accounts_list)
        #연결 사실 잘 모르겠음 아마 접속하는 버튼 누르는거임
        self.w_event_code.textChanged.connect(self.code_changed)
        self.w_orderbutton.clicked.connect(self.send_order)
        self.w_lookup.clicked.connect(self.check_balance)

        self.load_buy_sell_list()
    # 파일 buy리스트와 sell리스트를 들고와서 변수에 값 저장
    def trade_stocks(self):
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        f = open("buy_list.txt", 'rt')
        buy_list = f.readlines()
        f.close()

        f = open("sell_list.txt", 'rt')
        sell_list = f.readlines()
        f.close()

        # account
        account = self.w_account.currentText()

        # buy list 에서 살 주식 주문
        for row_data in buy_list:
            split_row_data = row_data.split(';')
            hoga = split_row_data[2]
            code = split_row_data[1]
            num = split_row_data[3]
            price = split_row_data[4]

            if split_row_data[-1].rstrip() == '매수전':
                self.kiwoom.send_order("send_order_req", "0101", account, 1, code, num, price, hoga_lookup[hoga], "")

        # sell list 팔 주식 주문
        for row_data in sell_list:
            split_row_data = row_data.split(';')
            hoga = split_row_data[2]
            code = split_row_data[1]
            num = split_row_data[3]
            price = split_row_data[4]

            if split_row_data[-1].rstrip() == '매도전':
                self.kiwoom.send_order("send_order_req", "0101", account, 2, code, num, price, hoga_lookup[hoga], "")

        # buy list 삿을경우 매수전을 주문완료로
        for i, row_data in enumerate(buy_list):
            buy_list[i] = buy_list[i].replace("매수전", "주문완료")

        # file update 사야할 목록 업데이트
        f = open("buy_list.txt", 'wt')
        for row_data in buy_list:
            f.write(row_data)
        f.close()

        # sell list 팔았을 경우 주문완료로
        for i, row_data in enumerate(sell_list):
            sell_list[i] = sell_list[i].replace("매도전", "주문완료")

        # file update 팔아야할 목록 업데이트 이는 pymon에서 들고올거
        f = open("sell_list.txt", 'wt')
        for row_data in sell_list:
            f.write(row_data)
        f.close()

    # 산 주식의 리스트를 가져온다
    def load_buy_sell_list(self):
        f = open("buy_list.txt", 'rt')
        buy_list = f.readlines()
        f.close()

        f = open("sell_list.txt", 'rt')
        sell_list = f.readlines()
        f.close()

        row_count = len(buy_list) + len(sell_list)
        self.tableWidget_4.setRowCount(row_count)

        # buy list
        for j in range(len(buy_list)):
            row_data = buy_list[j]
            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoom.get_master_code_name(split_row_data[1].rsplit())

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.tableWidget_4.setItem(j, i, item)

        # sell list
        for j in range(len(sell_list)):
            row_data = sell_list[j]
            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoom.get_master_code_name(split_row_data[1].rstrip())

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.tableWidget_4.setItem(len(buy_list) + j, i, item)

        self.tableWidget_4.resizeRowsToContents()
    #이건 주식 코드를 치면 코드의 이름을 받아온다.
    def code_changed(self):
        code = self.w_event_code.text()
        name = self.kiwoom.get_master_code_name(code)
        self.w_event_name.setText(name)
    #주문하는창
    def send_order(self):
        order_type_lookup = {'신규매수': 1, '신규매도': 2, '매수취소': 3, '매도취소': 4}
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        account = self.w_account.currentText()
        order_type = self.w_order.currentText()
        code = self.w_event_code.text()
        hoga = self.w_kinds.currentText()
        num = self.w_quantity.value()
        price = self.w_price.value()

        self.kiwoom.send_order("send_order_req", "0101", account, order_type_lookup[order_type], code, num, price, hoga_lookup[hoga], "")
    #시간이 9시가 되면 자동으로 사게하는 함수
    def timeout(self):
        market_start_time = QTime(9, 0, 0)
        current_time = QTime.currentTime()
        #현재시간이 마켓이 시작했고, trade_stocks_done이라는 변수는 맨처음에 false로 저장해놓는데 첫번째로 시작했으면 trade_stocks를 실행하는 코드
        if current_time > market_start_time and self.trade_stocks_done is False:
            self.trade_stocks()
            self.trade_stocks_done = True

        text_time = current_time.toString("hh:mm:ss")
        time_msg = "현재시간: " + text_time
        #연결상태
        state = self.kiwoom.get_connect_state()
        if state == 1:
            state_msg = "서버 연결 중"
        else:
            state_msg = "서버 미 연결 중"

        self.statusbar.showMessage(state_msg + " | " + time_msg)

    def timeout2(self):
        if self.checkBox.isChecked():
            self.check_balance()
    #이름은 잔고확인인데 계좌에서 데이터 뽑아온다 (이는 opw00018이다.)
    def check_balance(self):
        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")

        while self.kiwoom.remained_data:
            time.sleep(0.2)
            self.kiwoom.set_input_value("계좌번호", account_number)
            self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 2, "2000")

        # opw00001
        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00001_req", "opw00001", 0, "2000")

        # balance
        item = QTableWidgetItem(self.kiwoom.d2_deposit)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.tableWidget.setItem(0, 0, item)

        for i in range(1, 6):
            item = QTableWidgetItem(self.kiwoom.opw00018_output['single'][i - 1])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.tableWidget.setItem(0, i, item)

        self.tableWidget.resizeRowsToContents()

        # Item list
        item_count = len(self.kiwoom.opw00018_output['multi'])
        self.tableWidget_2.setRowCount(item_count)

        for j in range(item_count):
            row = self.kiwoom.opw00018_output['multi'][j]
            for i in range(len(row)):
                item = QTableWidgetItem(row[i])
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.tableWidget_2.setItem(j, i, item)

        self.tableWidget_2.resizeRowsToContents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()