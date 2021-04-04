from service import db


class Couriers(db.Model):
    __tablename__ = 'Couriers'
    types = ['foot', 'bike', 'car']
    earning_by_order = 500

    courier_id = db.Column(db.Integer, primary_key=True)
    courier_type = db.Column(db.Integer, nullable=False)
    working_hours_start = db.Column(db.String(32), nullable=False)
    working_hours_end = db.Column(db.String(32), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    earnings = db.Column(db.Integer, nullable=True)


class CourierRegions(db.Model):
    __tablename__ = 'CourierRegions'

    unneccessary_column = db.Column(db.Integer, primary_key=True, unique=True)
    courier_id = db.Column(db.Integer, db.ForeignKey('Couriers.courier_id'), nullable=False)
    courier_region = db.Column(db.Integer, nullable=False)


class Orders(db.Model):
    __tablename__ = 'Orders'

    order_id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    region = db.Column(db.Integer, nullable=False)
    delivery_hours_start = db.Column(db.DateTime, nullable=False)
    delivery_hours_end = db.Column(db.DateTime, nullable=False)


class CourierOrders(db.Model):
    __tablename__ = 'CourierOrders'
    max_weights = [4, 8, 16]

    courier_id = db.Column(db.Integer, db.ForeignKey('Couriers.courier_id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'), primary_key=True)
    assign_time = db.Column(db.String(32), nullable=False)
    complete_time = db.Column(db.String(32), nullable=True)


db.create_all()
