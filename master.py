#!/usr/bin/env python
import re
import pika
import json
import time
import threading
import time

import ibapi.wrapper
import ibapi.client
import ibapi.contract
import ibapi.order_state
#from rpc_client import RpcClient
import json

#pika.ConnectionParameters(host=host,socket_timeout=1, stack_timeout=1, blocked_connection_timeout=1))
#myhost='amqps://ppapnglh:anS8VpRjtAenIzJqaRN6MYLTBoiH16zm@whale.rmq.cloudamqp.com/ppapnglh'
myhost='amqps://hcdfnopi:QrnJs_rKX_kGxmgMFHoSevUTgrsqIPuh@roedeer.rmq.cloudamqp.com/hcdfnopi'
pos_queue='Stock.IB.Master.Positions'
order_queue='Stock.IB.Master.Order.Create'
order_active_queue='Stock.IB.Master.Orders.Active'
order_completed_queue='Stock.IB.Master.Orders.Completed'
pika.SelectConnection()
connection = pika.BlockingConnection(
    pika.URLParameters(myhost)

)

channel = connection.channel()


channel.queue_declare(queue='rpc_queue')
class MyWrapper_order_active (ibapi.wrapper.EWrapper):
    def __init__(self):
        self.nvid = 0

        self.positionsList = []
        self.positionsReceived = False

        self.ordersList = []
        self.ordersReceived = False

        self.ordersCompletedList = []
        self.ordersCompletedReceived = False

    def error(self, reqId: int, errorCode: int, errorString: str):
        #if reqId != -1:
        print(f"[{reqId}] код: {errorCode} || {errorString}")

    def connectAck(self):
        print('connectAck(): подключение установлено')

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nvid = orderId
        print('nextValidId(): новый ID = {}'.format(self.nvid))

    def reqAllOpenOrders(self):
        self.ordersList = []
        self.ordersReceived = False
        self.reqPositions()

    def openOrder(self, account: str, contract: ibapi.contract.Contract, position: float, avgCost: float):
        print("Position.", "ID:", contract.conId, "Date:", contract.lastTradeDateOrContractMonth, "Account:", account, "Symbol:", contract.symbol, "SecType:",
                contract.secType, "Currency:", contract.currency,
                "Position:", position, "Avg cost:", avgCost)

    def orderStatus(self, orderId, status:str, filled:float,
                    remaining:float, avgFillPrice:float, permId:int,
                    parentId:int, lastFillPrice:float, clientId:int,
                    whyHeld:str, mktCapPrice: float):
        super().orderStatus()
        self.ordersReceived = True
        print("PositionEnd")

    def openOrderEnd(self):
        super().openOrderEnd()
        self.ordersReceived = True
        print("PositionEnd")

class MyWrapper_order(ibapi.wrapper.EWrapper):
    def __init__(self):
        self.nvid = 0

    def error(self, reqId: int, errorCode: int, errorString: str):
        #if reqId != -1:
        print(f"[{reqId}] код: {errorCode} || {errorString}")

    def connectAck(self):
        print('connectAck(): подключение установлено')

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nvid = orderId
        print('nextValidId(): новый ID = {}'.format(self.nvid))


class MyWrapper(ibapi.wrapper.EWrapper):
    def __init__(self):
        self.nvid = 0

        self.positionsList = []
        self.positionsReceived = False

    def error(self, reqId: int, errorCode: int, errorString: str):
        #if reqId != -1:
        print(f"[{reqId}] код: {errorCode} || {errorString}")

    def connectAck(self):
        print('connectAck(): подключение установлено')

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nvid = orderId
        print('nextValidId(): новый ID = {}'.format(self.nvid))

    def reqPositions(self):
        self.positionsList = []
        self.positionsReceived = False
        self.reqPositions()

    def position(self, account: str, contract: ibapi.contract.Contract, position: float, avgCost: float):
        super().position(account, contract, position, avgCost)
        self.positionsList.append({
            "ID": contract.conId,
            "Account": account, "Symbol": contract.symbol,
            "SecurityType": contract.secType, "Position": position, "Amount": avgCost, "Currency": contract.currency})

        print("Position.", "ID:", contract.conId, "Account:", account, "Symbol:", contract.symbol, "SecType:",
                contract.secType, "Currency:", contract.currency,
                "Position:", position, "Avg cost:", avgCost)

    def positionEnd(self):
        super().positionEnd()
        self.positionsReceived = True
        print("PositionEnd")

def on_request(ch, method, props, body):
    is_error=False
    try:
        queue_name = method.routing_key
    except:
        is_error=True
        queue_name='test1'


    response = ''
    if not is_error:
        if queue_name == order_active_queue:
            print(body)
            tws = ibapi.client.EClient(MyWrapper_order_active())
            tws.connect('127.0.0.1', 7496, 1)
            dict1={'Result':None}
            if tws.isConnected():
                print('Успешно подключились к TWS')
                th = threading.Thread(target=tws.run) # Без threading — загрузка CPU 100%
                th.start()
                th.join(timeout=2)

                while tws.wrapper.nvid == 0:
                    time.sleep(0.5)

                tws.reqAllOpenOrders()

                while not tws.wrapper.ordersReceived:
                    time.sleep(0.5)

                print(tws.wrapper.ordersList)
                dict1={'Result':tws.wrapper.positionsList ,'Errors':[]}
            response=dict1
            tws.done = True
            tws.disconnect()
        if queue_name == order_queue:
            try:
                j=json.loads(body)
            except:
                print('JSON corrupt')
                print(body)
            print (j)
            #{'Symbol': 'AAPL', 'SecType': 'STK', 'Type': 'MKT', 'Tif': 'DAY', 'Exchange': 'SMART',
            #'Action': 'BUY', 'Quantity': 1, 'Currency': 'USD'}

            tws = ibapi.client.EClient(MyWrapper_order())
            tws.connect('127.0.0.1', 7496, 1)

            if tws.isConnected():
                print('Успешно подключились к TWS')
                th = threading.Thread(target=tws.run) # Без threading — загрузка CPU 100%
                th.start()
                th.join(timeout=5)

                while tws.wrapper.nvid == 0:
                    time.sleep(1)

                contract = ibapi.client.Contract()
                contract.symbol = j.get('Symbol')
                contract.secType = j.get('SecType')
                contract.currency = j.get('Currency')
                contract.exchange = j.get('Exchange')

                order = ibapi.client.Order()
                order.action = j.get('Action') # BUY — покупка, SELL — продажа
                order.orderType = j.get('Type')
                order.tif = j.get('Tif')
                order.totalQuantity = j.get('Quantity') # Кол-во

                tws.placeOrder(tws.wrapper.nvid, contract, order)

            tws.done = True
            tws.disconnect()
            dict1={'Result': j}
            response = dict1#json.loads('{"result":[]}')
        elif queue_name == pos_queue:
            #print (body)
            #j = json.loads(body)
            #r =  j['a']*j['b']
            dict1={'Result':None}
            tws = ibapi.client.EClient(MyWrapper())
            tws.connect('127.0.0.1', 7496, 1)

            if tws.isConnected():
                print('Успешно подключились к TWS')
                th = threading.Thread(target=tws.run) # Без threading — загрузка CPU 100%s
                th.start()
                th.join(timeout=2)

                while tws.wrapper.nvid == 0:
                    time.sleep(0.5)

                tws.reqPositions()

                while not tws.wrapper.positionsReceived:
                    time.sleep(0.5)

                #for dict1 in tws.wrapper.positionsList:
                dict1={'Result':tws.wrapper.positionsList ,'Errors':[]}
                #response = rpc.call(pos_queue,json.dumps(dict1))
                print(response)
                tws.done = True
                tws.disconnect()
            else:
                dict1={'Result': None}
            response = dict1#json.loads('{"result":[]}')
    else:
        dict1={'Result': None,'Errors':['''
        A non-string value was supplied for self.routing_key
         AssertionError: A non-string value was supplied for self.routing_key
        '''  ]}


    # if queue_name=='test2':
    #     j = json.loads(body)
    #     r  =  j['a']+j['b']
    #     response = json.loads('{"return":'+str(r)+'}')
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def disconnect():
    print('disconnect')
    channel.close()

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=pos_queue, on_message_callback=on_request)
channel.basic_consume(queue=order_queue, on_message_callback=on_request)
channel.basic_consume(queue=order_active_queue, on_message_callback=on_request)

#channel.basic_consume(queue='test2', on_message_callback=on_request)

connection.call_later(600,disconnect)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
