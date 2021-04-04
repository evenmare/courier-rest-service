import unittest
import requests
import random
import pathlib

from service import db
from scripts import data
from datetime import date, datetime
from threading import Thread

pathlib.Path(str(pathlib.Path(__file__).parent.absolute()) + "/data/data.db").unlink()
db.create_all()


class AsaThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._return = None  # child class's variable, not available in parent.

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args, **kwargs):
        super().join(*args, **kwargs)
        return self._return


class ApiTest(unittest.TestCase):
    BASE_URL = "http://0.0.0.0:8080/"

    IDS_LIST = list(range(0, 3000))
    TYPES_LIST = data.Couriers.types
    REGIONS_LIST = list(range(0, 10))
    ADDING_LIST = list(range(1, 50))
    HOURS_LIST = [("{0:0=2d}:00".format(i)) for i in range(0, 24)]

    def post_courier_to_test(self):
        courier_id = random.choice(self.IDS_LIST)
        self.IDS_LIST.remove(courier_id)
        requests.post(url="{}/couriers".format(self.BASE_URL), json={
            "data": [
                {
                    "courier_id": courier_id,
                    "courier_type": random.choice(self.TYPES_LIST),
                    "regions": list(self.REGIONS_LIST),
                    "working_hours": sorted([random.choice(self.HOURS_LIST[0:3]),
                                             random.choice(self.HOURS_LIST[20:23])])
                }
            ]
        })

        return courier_id

    def post_orders_to_test(self):
        adding_counter = random.choice(self.ADDING_LIST) * 10
        ids_list = self.IDS_LIST

        data_list = []
        for i in range(adding_counter):
            order_id = random.choice(ids_list)
            ids_list.remove(order_id)
            delivery_hours_start = random.choice(self.HOURS_LIST[3:13])
            delivery_hours_stop = ("{0:0=2d}:00".format(int(delivery_hours_start[:2]) +
                                                        random.choice(list(range(5, 10)))))

            data_list.append(
                {
                    "order_id": order_id,
                    "weight": random.uniform(0.1, 16.0),
                    "region": random.choice(self.REGIONS_LIST),
                    "delivery_hours": sorted([str(datetime.strptime(date.today().strftime("%d/%m/%y") +
                                                                    " " + delivery_hours_start,
                                                                    "%d/%m/%y %H:%M")),
                                              str(datetime.strptime(date.today().strftime("%d/%m/%y") +
                                                                    " " + delivery_hours_stop,
                                                                    "%d/%m/%y %H:%M"))])
                }
            )

        adding_data = {'data': data_list}
        response = requests.post(url="{}/orders".format(self.BASE_URL), json=adding_data)

        return response

    def post_order_to_test(self):
        order_id = random.choice(self.IDS_LIST)
        self.IDS_LIST.remove(order_id)
        requests.post(url="{}/orders".format(self.BASE_URL), json={"data": [{
            "order_id": order_id,
            "weight": random.uniform(0.1, 4.0),
            "region": random.choice(self.REGIONS_LIST),
            "delivery_hours": sorted([str(datetime.strptime(date.today().strftime("%d/%m/%y") +
                                                            " " + random.choice(self.HOURS_LIST),
                                                            "%d/%m/%y %H:%M")),
                                      str(datetime.strptime(date.today().strftime("%d/%m/%y") +
                                                            " " + random.choice(self.HOURS_LIST),
                                                            "%d/%m/%y %H:%M"))])
        }]})

        return order_id

    def assign_orders_to_test(self):
        order_id = self.post_order_to_test()
        courier_id = self.post_courier_to_test()
        db_assignment = data.CourierOrders(
            courier_id=courier_id,
            order_id=order_id,
            assign_time=str(datetime.strptime(date.today().strftime("%d/%m/%y") +
                                              " " + random.choice(self.HOURS_LIST),
                                              "%d/%m/%y %H:%M"))
        )
        db.session.add(db_assignment)
        db.session.commit()

        return order_id, courier_id

    def test_post_couriers(self):
        adding_counter = random.choice(self.ADDING_LIST)
        ids_list = self.IDS_LIST
        data_list = []
        for i in range(adding_counter):
            regions = []
            new_adding_counter = random.choice(list(range(0, 10)))
            regions_list = list(self.REGIONS_LIST)

            for j in range(new_adding_counter):
                region = random.choice(regions_list)
                regions_list.remove(region)

                regions.append(region)

            courier_id = random.choice(ids_list)
            ids_list.remove(courier_id)

            data_list.append(
                {
                    "courier_id": courier_id,
                    "courier_type": random.choice(self.TYPES_LIST),
                    "regions": regions,
                    "working_hours": sorted([random.choice(self.HOURS_LIST),
                                             random.choice(self.HOURS_LIST)])
                }
            )

        adding_data = {'data': data_list}
        response = requests.post(url="{}/couriers".format(self.BASE_URL), json=adding_data)

        self.assertEqual(response.status_code, 201)

    def test_get_courier_info(self):
        courier_id = self.post_courier_to_test()
        response = requests.get(url="{}/couriers/{}".format(self.BASE_URL, courier_id))

        self.assertEqual(response.status_code, 200)

    def test_patch_courier_info(self):
        courier_id = self.post_courier_to_test()

        response = requests.get(url="{}/couriers/{}".format(self.BASE_URL, courier_id), json=dict(
            courier_type=random.choice(self.TYPES_LIST),
            regions=[random.choice(self.REGIONS_LIST), random.choice(self.REGIONS_LIST) + 100],
            working_hours=sorted([random.choice(self.HOURS_LIST),
                                  random.choice(self.HOURS_LIST)])))

        self.assertEqual(response.status_code, 200)

    def test_post_orders(self):
        response = self.post_orders_to_test()

        self.assertEqual(response.status_code, 201)

    def test_assign_order(self):
        self.post_orders_to_test()
        response = requests.post(url="{}/orders/assign".format(self.BASE_URL),
                                 json={'courier_id': self.post_courier_to_test()})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()) >= 1, True)

    def test_complete_order(self):
        order_id, courier_id = self.assign_orders_to_test()
        response = requests.post(url="{}/orders/complete".format(self.BASE_URL),
                                 json={'courier_id': courier_id,
                                       'order_id': order_id,
                                       'complete_time': str(datetime.strptime(date.today().strftime("%d/%m/%y") +
                                                                              " " + random.choice(self.HOURS_LIST),
                                                                              "%d/%m/%y %H:%M"))})

        self.assertEqual(response.status_code, 200)

    @unittest.skip
    def test_parallel_work(self):
        t1, t2 = AsaThread(target=self.post_orders_to_test, ), AsaThread(target=self.post_orders_to_test, )
        t1.start()
        t2.start()
        self.assertEqual(t1.join().status_code, 201)
        self.assertEqual(t2.join().status_code, 201)


if __name__ == '__main__':
    unittest.main()
