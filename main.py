import datetime
import logging
import os
from dateutil import parser

from flask import Flask, render_template, request, Response
import sqlalchemy

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

app = Flask(__name__)

logger = logging.getLogger()

db = sqlalchemy.create_engine(
    cloud_sql_connection_name,
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,  # 30 seconds
    pool_recycle=1800,  # 30 minutes
)


@app.route('/create_customer', methods=['GET'])
def create_customer_page():
    locations_q = """
        SELECT id loc_id, name loc_name, address loc_address
        FROM public.location;
    """

    with db.connect() as conn:
        locations = conn.execute(locations_q).fetchall()

    return render_template(
        'create_customer.html',
        locations=locations
    )


@app.route('/create_customer', methods=['post'])
def create_customer():
    f = request.form

    stmt = sqlalchemy.text("""
        INSERT INTO public."customer"(
            l_name, f_name, location, phone, email, notes)
        VALUES (:l_name, :f_name, :l_id, :phone, :email, :notes)
        RETURNING id;
    """)

    try:
        with db.connect() as conn:
            r = conn.execute(
                stmt, l_name=f.get('last-name'), f_name=f.get('first-name'), l_id=f.get('location-id'),
                email=f.get('email'), phone=f.get('phone'), notes=f.get('notes')
            ).fetchone()
    except Exception as e:
        logger.exception(e)
        return Response(
            status=500,
            response="Unable to create a customer"
        )

    return Response(
        status=200,
        response=f"created customer {r.id}"
    )


@app.route('/create_vehicle', methods=['GET'])
def create_vehicle_page():
    locations_q = """
        SELECT id loc_id, name loc_name, address loc_address
        FROM public.location;
    """

    with db.connect() as conn:
        locations = conn.execute(locations_q).fetchall()

    return render_template(
        'create_vehicle.html',
        locations=locations
    )


@app.route('/create_vehicle', methods=['post'])
def create_vehicle():
    f = request.form

    stmt = sqlalchemy.text("""
        INSERT INTO public."bike"(
            name, mileage, location, plates, notes)
        VALUES (:name, :mileage, :l_id, :plates, :notes)
        RETURNING id;
    """)

    try:
        with db.connect() as conn:
            r = conn.execute(
                stmt, name=f.get('name'), mileage=f.get('mileage'), l_id=f.get('location-id'),
                plates=f.get('plates'), notes=f.get('notes')
            ).fetchone()
    except Exception as e:
        logger.exception(e)
        return Response(
            status=500,
            response="Unable to create a vehicle"
        )

    return Response(
        status=200,
        response=f"created vehicle {r.id}"
    )


@app.route('/create_location', methods=['GET'])
def create_location_page():
    return render_template(
        'create_location.html'
    )


@app.route('/create_location', methods=['post'])
def create_location():
    print("form", request.form)

    f = request.form

    stmt = sqlalchemy.text("""
        INSERT INTO public."location"(
            name, address, notes)
        VALUES (:name, :address, :notes)
        RETURNING id;
    """)

    try:
        with db.connect() as conn:
            r = conn.execute(
                stmt, name=f.get('name'), address=f.get('address'), notes=f.get('notes')
            ).fetchone()
    except Exception as e:
        logger.exception(e)
        return Response(
            status=500,
            response="Unable to create a location"
        )

    return Response(
        status=200,
        response=f"created location {r.id}"
    )


@app.route('/fill_order/<bike_id>', methods=['GET'])
def fill_order_page(bike_id):
    print('bike id', bike_id)

    locations_q = """
        SELECT id loc_id, name loc_name, address loc_address
        FROM public.location;
    """

    currencies_q = """
        SELECT
            pg_type.typname, 
            pg_enum.enumlabel cur_code
        FROM
            pg_type 
        JOIN
            pg_enum ON pg_enum.enumtypid = pg_type.oid
        WHERE pg_type.typname = 'currency';
    """

    bike_q = """
        SELECT b.id id, b.name "name", b.mileage mileage, 
            b.plates plates, l.name l_name, l.address l_address, l.id l_id
        FROM public.bike b
        JOIN public.location l on b.location = l.id
        WHERE b.id=%s;
    """

    customers_q = """
        SELECT c.id "id", c.l_name l_name, c.f_name f_name, 
            c.email email, c.phone phone, l.name loc_name
        FROM public.customer c
        JOIN public.location l on c.location = l.id;
    """

    with db.connect() as conn:
        locations = conn.execute(locations_q).fetchall()
        currencies = conn.execute(currencies_q).fetchall()
        bike_data = conn.execute(bike_q, bike_id).fetchone()
        customers = conn.execute(customers_q).fetchall()

    return render_template(
        'fill_order.html',
        locations=locations,
        currencies=currencies,
        bike_data=bike_data,
        customers=customers
    )


@app.route('/fill_order/', methods=['post'])
def fill_order_submit():
    print("form", request.form)

    # todo: need to check if the bike can be inserted

    f = request.form

    stmt = sqlalchemy.text("""
        INSERT INTO public."order"(
            start, "end", cus_id, amount, milage_start, 
            milage_end, bike, notes, location_start, location_end, 
            deposit, d_currency, assign_p_up, assign_d_off, a_currency,
            status)
        VALUES (:start, :end, :cus_id, :amount, :m_start, 
                :m_end, :bike, :notes, :l_start, :l_end, 
                :deposit, :dep_curr, :assign_p_up, :assign_d_off, :a_currency, 
                'IN_PROGRESS')
        RETURNING id;
    """)
    start_date = parser.parse(f.get('start-date'))
    end_date = parser.parse(f.get('end-date'))

    # todo: assing d off pp
    # todo: assing p up pp
    # todo: notes

    try:
        with db.connect() as conn:
            r = conn.execute(
                stmt, start=start_date, end=end_date,
                cus_id=f.get('customer-id'), amount=f.get('t-amount'), m_start=f.get('bike-mileage'),
                m_end=f.get('bike-mileage'), bike=f.get('bike-id'), notes='', l_start=f.get('start-location-id'),
                l_end=f.get('end-location-id'), deposit=f.get('d-amount'), dep_curr=f.get('deposit-cur-code'),
                assign_p_up=1, assign_d_off=1, a_currency=f.get('amount-cur-code')
            ).fetchone()
            print('result returning', r)
    except Exception as e:
        logger.exception(e)
        return Response(
            status=500,
            response="Unable to submit the order"
        )

    return Response(
        status=200,
        response=f"submitted order {r.id}"

    )


@app.route('/drop_off_bikes_list', methods=['GET'])
def drop_off_bikes_list():
    # todo: where clouse
    #  (end date == today)
    #  user email == current user)
    q = """
        SELECT 
            b.plates plate, b.name bike_name, b.id b_id, l.name loc_name, 
            l.address loc_address, c.l_name cus_l_name, o.id order_id
        FROM 
            "order" o 
            inner join bike b on o.bike = b.id
            inner join customer c on o.cus_id = c.id
            inner join "location" l on o.location_start = l.id
    """
    with db.connect() as conn:
        orders = conn.execute(q).fetchall()

    return render_template(
        'drop_off_bikes_list.html',
        orders=orders
    )


@app.route('/pickup_bikes_list', methods=['GET'])
def pickup_bikes_list():
    # todo: where clouse
    #  (start date == today)
    #  user email == current user)
    q = """
           SELECT 
               b.plates plate, b.name bike_name, b.id b_id, l.name loc_name, 
               l.address loc_address, c.l_name cus_l_name, o.id order_id
           FROM 
               "order" o 
               inner join bike b on o.bike = b.id
               inner join customer c on o.cus_id = c.id
               inner join "location" l on o.location_start = l.id
       """
    with db.connect() as conn:
        orders = conn.execute(q).fetchall()

    return render_template(
        'pickup_bikes_list.html',
        orders=orders
    )


@app.route('/available_bikes', methods=['GET'])
def available_bikes():
    # todo: need to test it thoroughly

    # I want to see a bike that is not in orders
    # and
    # in orders but start date > today
    # in orders but end date is not overlapping
    # todo: where clouse complete

    # todo: make sure returns only one bike

    # todo: don't forget: SELECT ('2001-02-16'::date, '2001-12-21'::date) OVERLAPS ('2001-12-21'::date, '2002-10-30'::date); --> false
    # start <= time < end.

    q = """
        SELECT 
           b.plates plate, b.name bike_name, b.id b_id, l.name loc_name, 
           l.address loc_address, o.id order_id
        FROM 
           "bike" b
           left join "order" o on o.bike = b.id
           left join "location" l on o.location_start = l.id
        WHERE 
            (not (o.start::date, o.end::date) overlaps (%s::date, %s::date))
            or (o.start is null and o.end is null)
       """

    start_date = parser.parse(request.args.get('s_date', str(datetime.date.today())))
    end_date = parser.parse(request.args.get('e_date', str(datetime.date.today() + datetime.timedelta(days=1))))
    print('s_d / e_d', start_date, end_date)

    with db.connect() as conn:
        bikes = conn.execute(q, str(start_date), str(end_date)).fetchall()

    return render_template(
        'available_bikes.html',
        available_bikes=bikes
    )


@app.route('/hand_off_bike/<order_id>', methods=['GET'])
def hand_off_bike(order_id):
    q = """
        SELECT 
            b.plates plates, c.l_name l_name, c.f_name f_name, l.name loc_name, l.address loc_address,
            b.mileage mileage, o.start "start", o."end" "end", b.name b_name, o.deposit deposit, 
            o.d_currency d_curr, o.amount amount, o.a_currency a_currency
        FROM 
            "order" o 
            inner join bike b on o.bike = b.id
            inner join customer c on o.cus_id = c.id
            inner join "location" l on o.location_start = l.id
        WHERE 
            o.id = %s
    """

    with db.connect() as conn:
        data = conn.execute(q, order_id).fetchone()

    return render_template(
        'hand_off_bike.html',
        form_data=data
    )


@app.route('/hand_off_bike/<order_id>', methods=['POST'])
def hand_off_bike_start(order_id):
    stmt = sqlalchemy.text("""
        UPDATE "order"
        SET "status" = 'IN_PROGRESS'
        WHERE "id" = :order_id
        """)
    try:
        with db.connect() as conn:
            conn.execute(stmt, order_id=order_id)
    except Exception as e:
        logger.exception(e)
        return Response(
            status=500,
            response="Unable to successfully update order"
        )

    return Response(
        status=200,
        response=f"updated order {order_id}. the order is now active"
    )


@app.route('/pickup_bike/<order_id>', methods=['GET'])
def pickup_bike(order_id):
    q = """
        SELECT 
            b.plates plates, c.l_name l_name, c.f_name f_name, l.name loc_name, l.address loc_address,
            b.mileage mileage, o.start "start", o."end" "end", b.name b_name, o.deposit deposit, 
            o.d_currency d_curr, o.amount amount, o.a_currency a_currency
        FROM 
            "order" o 
            inner join bike b on o.bike = b.id
            inner join customer c on o.cus_id = c.id
            inner join "location" l on o.location_start = l.id
        WHERE 
            o.id = %s
    """

    with db.connect() as conn:
        data = conn.execute(q, order_id).fetchone()

    return render_template(
        'pickup_bike.html',
        form_data=data
    )


@app.route('/', methods=['GET'])
def index():
    return render_template(
        'index.html'
    )


@app.route('/admin_main', methods=['GET'])
def admin_main():
    return render_template(
        'admin_index.html'
    )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
