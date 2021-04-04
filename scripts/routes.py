from flask import request, jsonify
from service import app, db

import scripts.utils as utils
import scripts.data as data
from datetime import date, datetime, timedelta


def get_courier_data(courier_id):
    db_courier = data.Couriers.query.filter_by(courier_id=courier_id).first()
    db_regions = data.CourierRegions.query.filter_by(courier_id=courier_id).all()
    courier_regions = []

    for region in db_regions:
        courier_regions.append(region.courier_region)

    return db_courier, db_regions, courier_regions


def count_rating_earnings(courier_id):
    courier_orders_sum = data.CourierOrders.query.filter_by(courier_id=courier_id).count()
    courier_successful_sum = data.CourierOrders.query.filter(data.CourierOrders.courier_id == courier_id,
                                                             data.CourierOrders.complete_time <=
                                                             data.CourierOrders.assign_time).count()

    # try:
    k = courier_successful_sum / courier_orders_sum
    rating = k * 5
    earning_by_order = int(data.Couriers.earning_by_order * k)

    # except ZeroDivisionError:
    #     return False

    try:
        earnings = int(data.Couriers.query.filter_by(courier_id=courier_id).first().earnings) + earning_by_order
    except TypeError:
        earnings = earning_by_order

    data.Couriers.query.filter_by(courier_id=courier_id).update({
        'rating': rating,
        'earnings': earnings
    })

    db.session.commit()


@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({'data': 'hello!'}), 201


@app.route('/couriers', methods=['POST'])
def couriers():
    def get_courier_ids():
        courier_ids = data.Couriers.query.all()
        db_response = {'CourierIds': []}
        for line in courier_ids:
            db_response['CourierIds'].append(line.courier_id)

        return db_response

    if not request.json or 'data' not in request.json:
        return jsonify(get_courier_ids().update({'error': {'status': 400,
                                                           'description': 'bad request'}})), 400

    bad_couriers = {}

    for courier in request.json['data']:

        db_courier = data.Couriers.query.filter_by(courier_id=int(courier['courier_id'])).first()

        if db_courier is None:
            try:
                courier_id = int(courier['courier_id'])
                courier_type = int(data.Couriers.types.index(courier['courier_type']))
                working_hours_start = utils.valitime(str(courier['working_hours'][0]))
                working_hours_end = utils.valitime(str(courier['working_hours'][1]))

                db_courier = data.Couriers(courier_id=courier_id,
                                           courier_type=courier_type,
                                           working_hours_start=working_hours_start,
                                           working_hours_end=working_hours_end)
                db.session.add(db_courier)

            except ValueError:
                bad_couriers.update({str(courier['courier_id']): 'incorrect data format'})

            for region in courier['regions']:
                try:
                    courier_id = int(courier['courier_id'])
                    courier_region = int(region)

                    db_courier_regions = data.CourierRegions(courier_id=courier_id,
                                                             courier_region=courier_region)
                    db.session.add(db_courier_regions)

                except ValueError:
                    if courier['courier_id'] not in bad_couriers:
                        bad_couriers.update({str(courier['courier_id']): 'incorrect data format'})
                        break

        else:
            bad_couriers.update({str(courier['courier_id']): 'not unique id'})

    db.session.commit()

    if bad_couriers == {}:
        return jsonify(get_courier_ids()), 201
    else:
        db_response = get_courier_ids()
        db_response.update({'error': {'status': 400,
                                      'description': 'check by id',
                                      'problem ids': bad_couriers}})
        return jsonify(db_response), 400


@app.route('/couriers/<int:courier_id>', methods=['GET', 'PATCH'])
def courier(courier_id):
    db_courier, db_regions, courier_regions = get_courier_data(courier_id)

    if db_courier is not None:

        if request.json:

            if 'courier_type' in request.json and 'regions' in request.json and 'working_hours' in request.json:

                try:

                    regions = [int(i) for i in request.json['regions']]
                    courier_type = data.Couriers.types.index(request.json['courier_type'])
                    working_hours_start = request.json['working_hours'][0]
                    working_hours_stop = request.json['working_hours'][1]

                    if regions != courier_regions:
                        regions_to_add = list(set(regions) - set(courier_regions))
                        regions_to_delete = list(set(courier_regions) - set(regions))

                        for region in regions_to_delete:
                            region_to_delete_line = data.CourierRegions.query.filter_by(courier_id=courier_id,
                                                                                        courier_region=region).first()
                            db.session.delete(region_to_delete_line)

                        for region in regions_to_add:
                            region_to_add_line = data.CourierRegions(courier_id=courier_id, courier_region=region)
                            db.session.add(region_to_add_line)

                    data.Couriers.query.filter_by(courier_id=courier_id).update(
                        {'courier_type': courier_type,
                         'working_hours_start': working_hours_start,
                         'working_hours_end': working_hours_stop
                         })

                except ValueError:
                    return jsonify({'error': {'status': 400,
                                              'description': 'incorrect data format'}}), 400

                db.session.commit()

            else:
                return jsonify({'error': {'status': 400,
                                          'description': 'bad request'}}), 400

        db_courier, db_regions, courier_regions = get_courier_data(courier_id)

        query_response = {'courier_id': db_courier.courier_id,
                          'courier_type': data.Couriers.types[db_courier.courier_type],
                          'regions': courier_regions,
                          'working_hours': [db_courier.working_hours_start, db_courier.working_hours_end],
                          'rating': db_courier.rating,
                          'earnings': db_courier.earnings
                          }

        return jsonify(query_response), 200

    else:
        return jsonify({'error': {'status': 404,
                                  'description': 'courier not found'}}), 404


@app.route('/orders', methods=['POST'])
def orders():
    def get_order_ids():
        order_ids = data.Orders.query.all()
        response_from_db = {'OrderIds': []}
        for line in order_ids:
            response_from_db['OrderIds'].append(line.order_id)

        return response_from_db

    if not request.json or 'data' not in request.json:
        return jsonify(get_order_ids().update({'error': {'status': 400,
                                                         'description': 'bad request'}})), 400

    bad_orders = {}

    for order in request.json['data']:

        db_order = data.Orders.query.filter_by(order_id=int(order['order_id'])).first()

        if db_order is None:
            try:
                order_id = int(order['order_id'])
                weight = float(order['weight'])
                region = int(order['region'])
                delivery_hours_start = utils.validatetime(str(order['delivery_hours'][0]))
                delivery_hours_end = utils.validatetime(str(order['delivery_hours'][1]))

                db_order = data.Orders(order_id=order_id,
                                       weight=weight,
                                       region=region,
                                       delivery_hours_start=delivery_hours_start,
                                       delivery_hours_end=delivery_hours_end)
                db.session.add(db_order)

            except ValueError:
                bad_orders.update({str(order['order_id']): 'incorrect data format'})

        else:
            bad_orders.update({str(order['order_id']): 'not unique id'})

    db.session.commit()

    if bad_orders == {}:
        return jsonify(get_order_ids()), 201
    else:
        db_response = get_order_ids()
        db_response.update({'error': {'status': 400,
                                      'description': 'check by id',
                                      'problem ids': bad_orders}})

        return jsonify(db_response), 400


@app.route('/orders/assign', methods=['POST'])
def assign():
    if not request.json or 'courier_id' not in request.json:
        return jsonify({'error': {'status': 400,
                                  'description': 'bad request'}}), 400

    courier_id = request.json['courier_id']
    db_courier, db_regions, courier_regions = get_courier_data(courier_id)
    working_hours = [datetime.strptime(date.today().strftime("%d/%m/%y") +
                                       " " + db_courier.working_hours_start, "%d/%m/%y %H:%M"),
                     datetime.strptime(date.today().strftime("%d/%m/%y") +
                                       " " + db_courier.working_hours_end, "%d/%m/%y %H:%M")]

    max_weight = data.CourierOrders.max_weights[db_courier.courier_type]

    if db_courier is not None:

        db_orders_to_add = db.session.query(data.CourierOrders, data.Orders).outerjoin(data.CourierOrders,
                                                                                       data.CourierOrders.order_id ==
                                                                                       data.Orders.order_id). \
            filter(data.Orders.delivery_hours_end >= working_hours[0],
                   data.Orders.delivery_hours_start <= working_hours[1],
                   data.Orders.weight <= max_weight,
                   data.Orders.region.in_(set(courier_regions))). \
            order_by(data.Orders.delivery_hours_end,
                     data.Orders.delivery_hours_start.desc()).all()

        delivery_graphic = {}
        time_graphic = []

        del_time = working_hours[0] + timedelta(minutes=30)
        while del_time <= working_hours[1]:
            time_graphic.append(del_time)
            del_time = del_time + timedelta(minutes=30)
        for region in courier_regions:
            list_of_lists = []
            for i in range(len(time_graphic)):
                list_of_lists.append([])
            delivery_graphic.update({region: list_of_lists})

        for region in delivery_graphic:
            for working_time in time_graphic:
                for line in db_orders_to_add:
                    for order in line:
                        if order is not None:
                            if type(order) is not data.CourierOrders:
                                if order.region == region and order.delivery_hours_start <= working_time:
                                    if order.delivery_hours_end >= working_time:
                                        delivery_graphic[region][time_graphic.index(working_time)]. \
                                            append(order.order_id)

        length_of_lists = len(time_graphic)

        def count_deliveries(graphic):
            counters = {}
            for key, value in graphic.items():
                list_of_lens = list()
                for element in value:
                    list_of_lens.append(len(element))
                counters.update({key: list_of_lens})
            return counters

        def delete_order_id(order_id, list_to_delete, length):
            for i in range(length):
                list_of_orders = list(list_to_delete[i])
                if order_id in list_of_orders:
                    list_of_orders.remove(order_id)
                list_to_delete[i] = list_of_orders

            return list_to_delete

        counter_dict = count_deliveries(delivery_graphic)

        def find_best_region(length, dict_with_counters, graphic, start_pos=0):
            min_null_orders = length
            best_regions = []
            for region in dict_with_counters:
                counter = dict_with_counters[region][start_pos:].count(0)
                if min_null_orders > counter:
                    best_regions = []
                    best_regions.append(region)
                    min_null_orders = counter
                elif min_null_orders == counter:
                    best_regions.append(region)

            max_orders = -1
            best_choice = -1
            for region in best_regions:
                all_region_orders_set = set()
                for element in graphic[region][start_pos:]:
                    all_region_orders_set.update(element)
                region_orders_counter = len(list(all_region_orders_set))
                if max_orders < region_orders_counter:
                    max_orders = region_orders_counter
                    best_choice = region

            return best_choice

        best_region = find_best_region(length_of_lists, counter_dict, delivery_graphic)
        k = 2 + [2, 1, 0][db_courier.courier_type]
        best_route = delivery_graphic[best_region]
        best_route_counter_list = counter_dict[best_region]

        final_route = []

        for i in range(length_of_lists):
            if i + 1 - k < length_of_lists:
                compare_list = best_route_counter_list[i:i + k]
                if compare_list == [0] * k:
                    best_region = find_best_region(len(best_route_counter_list[i + k - 1:]),
                                                   counter_dict,
                                                   delivery_graphic,
                                                   i + k - 1)
                    best_route = best_route[:i + k] + delivery_graphic[best_region][i + k - 1:]
                    best_route_counter_list = best_route_counter_list[:i + k]
                    best_route_counter_list += counter_dict[best_region][i + k - 1:]

            order_ids = best_route[i]
            if len(order_ids) != 0:
                added_id = order_ids[0]
                final_route.append(added_id)
                best_route = delete_order_id(added_id, best_route, length_of_lists)
                delivery_graphic[best_region] = best_route
                counter_dict = count_deliveries(delivery_graphic)
                best_route_counter_list = counter_dict[best_region]
            else:
                final_route.append(None)

        for i in range(len(final_route)):
            if final_route[i] is not None:
                db_courier_order = data.CourierOrders(order_id=final_route[i],
                                                      courier_id=courier_id,
                                                      assign_time=time_graphic[i])
                db.session.add(db_courier_order)

        db.session.commit()

        assigned_orders = data.CourierOrders.query.filter_by(courier_id=courier_id, complete_time=None).all()
        response_dict = {}
        for order in assigned_orders:
            assign_time = datetime.strptime(str(order.assign_time), "%Y-%m-%d %H:%M:%S"). \
                strftime("%Y-%m-%dT%H:%M:%S.0Z")
            response_dict.update({order.order_id: assign_time})

        return jsonify(response_dict), 200

    else:
        return jsonify({'error': {'status': 400,
                                  'description': 'bad request'}}), 400


@app.route('/orders/complete', methods=['POST'])
def complete():
    if not request.json:
        if 'courier_id' not in request.json or 'order_id' not in request.json or 'complete_time' not in request.json:
            return jsonify({'error': {'status': 400,
                                      'description': 'bad request'}}), 400

    try:
        courier_id = request.json['courier_id']
        order_id = request.json['order_id']
        complete_time = utils.validatetime(request.json['complete_time'])
    except ValueError:
        return jsonify({'error': {'status': 400,
                                  'description': 'bad request'}}), 400

    data.CourierOrders.query.filter_by(order_id=order_id).update({
        'courier_id': courier_id,
        'complete_time': complete_time
    })

    db.session.commit()
    count_rating_earnings(courier_id)

    return jsonify({'order_id': order_id}), 200
