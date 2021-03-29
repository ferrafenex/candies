#!ferrafenex_candies/bin/python

"""README.md

# ferrafenex candies

Запускать:
 > ferrafenex_candies/bin/uvicorn main:router --host 0.0.0.0 --port 8080

Рекомендуется наличие:
 * окружение virtualenv - для управления проектом
 * конвертер yaml->json - для генерации openapi.json

Обязательные зависимости:
 * openapi_to_fastapi - валидатор и генератор сервиса
 * fastapi            - фреймворк для REST
 * uvicorn            - сервер
 * sqlite3            - база данных
 * os.path            - проверка наличия файлов

"""

from pathlib import Path
from fastapi import Header, HTTPException
from openapi_to_fastapi.routes import SpecRouter
from sqlite3 import connect
from os.path import exists

class Candies:
    def __init__(self, file = "candies.db"):
        if exists(file):
            self.connect = connect(file)
        else:
            self.connect = connect(file)
            self.create()

    def create(self):
        """инициализация пустой БД"""
        cursor = self.connect.cursor()
        
        cursor.execute("CREATE TABLE couriers (courier_id integer, courier_type text)")
        cursor.execute("CREATE TABLE orders   (order_id integer, weight integer, region integer)")

        cursor.execute("CREATE TABLE courier_regions       (id integer, courier_id integer, region integer)")
        cursor.execute("CREATE TABLE courier_working_hours (id integer, courier_id integer, working_hours string)")

        cursor.execute("CREATE TABLE order_delivery_hours (id integer, order_id integer, delivery_hours integer)")

        cursor.execute("CREATE TABLE assign_times   (courier_id integer, order_id integer, time string)")
        cursor.execute("CREATE TABLE complete_times (courier_id integer, order_id integer, time string)")

        cursor.execute("CREATE TABLE ratings  (courier_id integer, last_order_id integer, value integer)")
        cursor.execute("CREATE TABLE earnings (courier_id integer, last_order_id integer, value integer)")

        self.connect.commit()

    def couriers_append(self, couriers):
        cursor = self.connect.cursor()

        for courier in couriers:
            cursor.execute("INSERT INTO couriers                  (courier_id, courier_type)      VALUES    (?, ?)",     (courier.courier_id, courier.courier_type))
            for region in courier.regions:
                cursor.execute("INSERT INTO courier_regions       (id, courier_id, region)        VALUES (?, ?,   ?)",   (courier.courier_id, region))
            for working_hours in courier.working_hours:
                cursor.execute("INSERT INTO courier_working_hours (id, courier_id, working_hours) VALUES (?, ?,     ?)", (courier.courier_id, working_hours))

        self.connect.commit()
    
    def orders_append(self, orders):
        cursor = self.connect.cursor()
        
        for order in orders:
            cursor.execute("INSERT INTO orders                        (order_id, weight, region) VALUES    (?, ?, ?)",   (order.order_id, order.weight, order.region))
             for delivery_hours in order.delivery_hours:
                 cursor.execute("INSERT INTO order_delivery_hours (id, order_id, delivery_hours) VALUES (?, ?,      ?)", (order.order_id, delivery_hours))

        self.connect.commit()

    def order_assign(self, courier_id, order_id, time):
        cursor = self.connect.cursor()

        cursor.execute("INSERT INTO assign_times (courier_id, order_id, time) VALUES (?, ?, ?)", (courier_id, order_id, time))

        self.connect.commit()

    def order_complete(self, courier_id, order_id, time):
        cursor = self.connect.cursor()

        cursor.execute("INSERT INTO complete_times (courier_id, order_id, time) VALUES (?, ?, ?)", (courier_id, order_id, time))

        self.connect.commit()

candies = Candies()

"""TEST /couriers

class CourierItem:
    def __init__(self):
        self.courier_id = 0
        self.courier_type = "bike"
        self.regions = []
        self.working_hours = []

candies.couriers_append([CourierItem()])
"""

specs = Path("./specs/openapi.json")
router = SpecRouter(specs).to_fastapi_router()
