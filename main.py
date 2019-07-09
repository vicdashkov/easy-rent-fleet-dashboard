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
if db_user:
    cloud_sql_connection_name = sqlalchemy.engine.url.URL(
        drivername='postgres+pg8000',
        username=db_user,
        password=db_pass,
        database=db_name,
        query={
            'unix_sock': '/cloudsql/{}/.s.PGSQL.5432'.format(
                cloud_sql_connection_name)
        }
    )

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

    return render_template('success_creating_resource.html')


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
        INSERT INTO public."vehicle"(
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

    return render_template('success_creating_resource.html')


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

    return render_template('success_creating_resource.html')


@app.route('/order_new/<vehicle_id>', methods=['GET'])
def order_new(vehicle_id):
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

    vehicle_q = """
        SELECT b.id id, b.name "name", b.mileage mileage, 
            b.plates plates, l.name l_name, l.address l_address, l.id l_id
        FROM public.vehicle b
        JOIN public.location l on b.location = l.id
        WHERE b.id=%s;
    """

    vehicles_q = """
        SELECT v.id id, v.name "name", v.mileage mileage, 
            v.plates plates, l.name l_name, l.address l_address, l.id l_id
        FROM public.vehicle v
        JOIN public.location l on v.location = l.id
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
        vehicle_data = conn.execute(vehicle_q, vehicle_id).fetchone()
        vehicles = conn.execute(vehicles_q).fetchall()
        customers = conn.execute(customers_q).fetchall()

    return render_template(
        'order_new.html',
        locations=locations,
        currencies=currencies,
        vehicle_data=vehicle_data,
        customers=customers,
        vehicles=vehicles
    )


@app.route('/order_edit/<order_id>', methods=['GET'])
def order_edit(order_id):
    order_q = f"""
        SELECT 
          b.plates plate, 
          b.name vehicle_name, 
          b.id b_id, 
          l_s.name loc_s_name, 
          l_s.address loc_s_address, 
          l_e.name loc_e_name, 
          l_e.address loc_e_address, 
          c.l_name cus_l_name, 
          c.phone cus_phone, 
          c.email cus_email,
          c.f_name cus_f_name, 
          {get_sql_date_formatted('o."start"', 'o_start')}
          {get_sql_date_formatted('o."end"', 'o_end')}
          o.amount::numeric o_amount, 
          o.a_currency o_a_currency, 
          o.deposit::numeric o_deposit, 
          o.d_currency o_d_currency, 
          o.id order_id, 
          o.status order_status, 
          o.notes o_notes,
          c.id cus_id,
          l_e.id loc_e_id,
          l_s.id loc_s_id
        FROM 
          "order" o 
          inner join vehicle b on o.vehicle = b.id
          inner join customer c on o.cus_id = c.id
          inner join "location" l_s on o.location_start = l_s.id
          inner join "location" l_e on o.location_end = l_e.id
        WHERE
          o.id = %s
    """

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

    statuses_q = """
            SELECT
                pg_type.typname, 
                pg_enum.enumlabel status_code
            FROM
                pg_type 
            JOIN
                pg_enum ON pg_enum.enumtypid = pg_type.oid
            WHERE pg_type.typname = 'status';
        """

    vehicle_q = """
        SELECT b.id id, b.name "name", b.mileage mileage, 
            b.plates plates, l.name l_name, l.address l_address, l.id l_id
        FROM public.vehicle b
        JOIN public.location l on b.location = l.id
        WHERE b.id=%s;
    """

    vehicles_q = """
        SELECT b.id id, b.name "name", b.mileage mileage, 
            b.plates plates, l.name l_name, l.address l_address, l.id l_id
        FROM public.vehicle b
        JOIN public.location l on b.location = l.id
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
        order_data = conn.execute(order_q, order_id).fetchone()
        vehicle_data = conn.execute(vehicle_q, order_data.b_id).fetchone()
        vehicles = conn.execute(vehicles_q).fetchall()
        customers = conn.execute(customers_q).fetchall()
        statuses = conn.execute(statuses_q).fetchall()

    print('order data', order_data)
    return render_template(
        'order_edit.html',
        locations=locations,
        currencies=currencies,
        vehicle_data=vehicle_data,
        customers=customers,
        vehicles=vehicles,
        order_data=order_data,
        statuses=statuses
    )


@app.route('/order', methods=['post'])
def fill_order_submit():
    # todo: <feature> need to check if the vehiclecan be inserted

    f = request.form

    stmt = sqlalchemy.text("""
        INSERT INTO public."order"(
            start, "end", cus_id, amount, mileage_start, 
            mileage_end, vehicle, notes, location_start, location_end, 
            deposit, d_currency, a_currency,
            status)
        VALUES (:start, :end, :cus_id, :amount, :m_start, 
                :m_end, :vehicle, :notes, :l_start, :l_end, 
                :deposit, :dep_curr, :a_currency, 
                'IN_PROGRESS')
        RETURNING id;
    """)
    start_date = parser.parse(f.get('start-date'))
    end_date = parser.parse(f.get('end-date'))

    try:
        with db.connect() as conn:
            r = conn.execute(
                stmt,
                start=start_date,
                end=end_date,
                cus_id=f.get('customer-id'),
                amount=f.get('t-amount'),
                m_start=f.get('vehicle-mileage'),
                m_end=f.get('vehicle-mileage'),
                vehicle=f.get('vehicle-id'),
                notes=f.get('notes'),
                l_start=f.get('start-location-id'),
                l_end=f.get('end-location-id'),
                deposit=f.get('d-amount'),
                dep_curr=f.get('deposit-cur-code'),
                a_currency=f.get('amount-cur-code')
            ).fetchone()
    except Exception as e:
        logger.exception(e)
        return Response(
            status=500,
            response="Unable to submit the order"
        )

    return render_template('success_creating_resource.html')


@app.route('/drop_off_vehicles_list', methods=['GET'])
def drop_off_vehicles_list():
    d = get_req_date_or_today('date')

    q = """
        SELECT 
            b.plates plate, b.name vehicle_name, b.id b_id, l.name loc_name, 
            l.address loc_address, c.l_name cus_l_name, o.id order_id
        FROM 
            "order" o 
            inner join vehicle b on o.vehicle = b.id
            inner join customer c on o.cus_id = c.id
            inner join "location" l on o.location_start = l.id
        WHERE
            o.start = %s AND o.status != 'DELETED'
    """
    with db.connect() as conn:
        orders = conn.execute(q, d).fetchall()

    return render_template(
        'drop_off_vehicles_list.html',
        orders=orders,
        date=d
    )


@app.route('/pickup_vehicle_list', methods=['GET'])
def pickup_vehicles_list():
    d = get_req_date_or_today('date')

    q = """
           SELECT 
               b.plates plate, b.name vehicle_name, b.id b_id, l.name loc_name, 
               l.address loc_address, c.l_name cus_l_name, o.id order_id
           FROM 
               "order" o 
               inner join vehicle b on o.vehicle = b.id
               inner join customer c on o.cus_id = c.id
               inner join "location" l on o.location_start = l.id
           WHERE
                o.end=%s AND o.status != 'DELETED'
       """
    with db.connect() as conn:
        orders = conn.execute(q, d).fetchall()

    return render_template(
        'pickup_vehicles_list.html',
        orders=orders,
        date=d
    )


@app.route('/order_list', methods=['GET'])
def orders_list():
    q = f"""
           SELECT 
               b.plates plate, b.name vehicle_name, b.id b_id, l.name loc_name, 
               l.address loc_address, c.l_name cus_l_name, o.id order_id, o.status order_status,
               {get_sql_date_formatted('o."end"', 'end_date')},
               {get_sql_date_formatted('o."start"', 'start_date')}
           FROM 
               "order" o 
               inner join vehicle b on o.vehicle = b.id
               inner join customer c on o.cus_id = c.id
               inner join "location" l on o.location_start = l.id
       """
    with db.connect() as conn:
        orders = conn.execute(q).fetchall()

    return render_template(
        'orders_list.html',
        orders=orders
    )


@app.route('/order_update', methods=['post'])
def change_order():
    f = request.form

    start_date = parser.parse(f.get('start-date'))
    end_date = parser.parse(f.get('end-date'))
    order_id = f.get('order-id')
    stmt = sqlalchemy.text("""
        UPDATE public."order"
        SET
            "start"=:start,
            "end"=:end,
            cus_id=:cus_id,
            amount=:amount,
            mileage_start=:m_start,
            mileage_end=:m_end,
            vehicle=:vehicle,
            notes=:notes,
            location_start=:l_start,
            location_end=:l_end,
            deposit=:deposit,
            d_currency=:dep_curr,
            a_currency=:a_currency,
            status=:status
        WHERE
            "id"=:order_id
        """)
    try:
        with db.connect() as conn:
            conn.execute(
                stmt,
                start=start_date,
                end=end_date,
                cus_id=f.get('customer-id'),
                amount=f.get('t-amount'),
                m_start=f.get('vehicle-mileage'),
                m_end=f.get('vehicle-mileage'),
                vehicle=f.get('vehicle-id'),
                notes=f.get('notes'),
                l_start=f.get('start-location-id'),
                l_end=f.get('end-location-id'),
                deposit=f.get('d-amount'),
                dep_curr=f.get('deposit-cur-code'),
                a_currency=f.get('amount-cur-code'),
                order_id=order_id,
                status=f.get('order-status')
            )
    except Exception as e:
        logger.exception(e)
        return Response(
            status=500,
            response="Unable to successfully update order"
        )

    return render_template('success_creating_resource.html')


@app.route('/available_vehicles', methods=['GET'])
def available_vehicles():
    q = f"""  
        select 
            b.plates plate, b.name vehicle_name, b.id b_id, l.name loc_name, 
            l.address loc_address, 
            {get_sql_date_formatted('o."end"', 'o_end')},
            {get_sql_date_formatted('o."start"', 'o_start')},
            o.status o_status
        from vehicle b
        left join "location" l on b.location = l.id
        left join (
            select * from "order" o
            where 
                %s::date between o.start::date and o.end::date
                or (o.start is null and o.end is null)
        ) o on b.id = o.vehicle
       """

    start_date = get_req_date_or_today('s_date')

    with db.connect() as conn:
        available_v = conn.execute(q, start_date).fetchall()

    return render_template(
        'available_vehicles.html',
        available_vehicles=available_v,
        start_date=start_date
    )


@app.route('/hand_off_vehicle/<order_id>', methods=['GET'])
def hand_off_vehicle(order_id):
    q = """
        SELECT 
            b.plates plates, c.l_name l_name, c.f_name f_name, l.name loc_name, l.address loc_address,
            b.mileage mileage, o.start "start", o."end" "end", b.name b_name, o.deposit deposit, 
            o.d_currency d_curr, o.amount amount, o.a_currency a_currency, o.id order_id,
            b.id vehicle_id
        FROM 
            "order" o 
            inner join vehicle b on o.vehicle = b.id
            inner join customer c on o.cus_id = c.id
            inner join "location" l on o.location_start = l.id
        WHERE 
            b.id = %s
    """

    with db.connect() as conn:
        data = conn.execute(q, order_id).fetchone()

    return render_template(
        'hand_off_vehicle.html',
        form_data=data
    )


@app.route('/hand_off_vehicle/<order_id>', methods=['POST'])
def hand_off_vehicle_start(order_id):
    print("form", request.form, order_id)
    f = request.form
    stmt_order = sqlalchemy.text("""
        UPDATE "order"
        SET 
            "status"='ENDED',
            "mileage_start"=:m_start
        WHERE "id" = :order_id
        """)

    stmt_vehicle = sqlalchemy.text("""
            UPDATE "vehicle"
            SET 
                "mileage"=:m
            WHERE "id" = :vehicle_id
            """)
    try:
        with db.connect() as conn:
            conn.execute(stmt_order, order_id=order_id, m_start=f.get('current-mileage'))
            conn.execute(stmt_vehicle, vehicle_id=f.get('vehicle-id'), m=f.get('current-mileage'))
    except Exception as e:
        logger.exception(e)
        return Response(
            status=500,
            response="Unable to successfully update order"
        )

    return render_template('success_creating_resource.html')


@app.route('/pickup_vehicle/<order_id>', methods=['GET'])
def pickup_vehicle(order_id):
    q = f"""
        SELECT 
            b.plates plates, c.l_name l_name, c.f_name f_name, l.name loc_name, l.address loc_address,
            b.mileage mileage, 
            {get_sql_date_formatted('o."end"', '"end"')},
            {get_sql_date_formatted('o."start"', '"start"')},
            b.name b_name, o.deposit deposit, 
            o.d_currency d_curr, o.amount amount, o.a_currency a_currency, b.id vehicle_id
        FROM 
            "order" o 
            inner join vehicle b on o.vehicle = b.id
            inner join customer c on o.cus_id = c.id
            inner join "location" l on o.location_end = l.id
        WHERE 
            b.id = %s
    """

    with db.connect() as conn:
        data = conn.execute(q, order_id).fetchone()

    return render_template(
        'pickup_vehicle.html',
        form_data=data
    )


@app.route('/pickup_vehicle/<order_id>', methods=['POST'])
def pickup_vehicle_start(order_id):
    print("form", request.form, order_id)
    f = request.form
    stmt_order = sqlalchemy.text("""
        UPDATE "order"
        SET 
            "status"='IN_PROGRESS',
            "mileage_end"=:m_end
        WHERE "id" = :order_id
        """)

    stmt_vehicle = sqlalchemy.text("""
            UPDATE "vehicle"
            SET 
                "mileage"=:m
            WHERE "id" = :vehicle_id
            """)
    try:
        with db.connect() as conn:
            conn.execute(stmt_order, order_id=order_id, m_end=f.get('current-mileage'))
            conn.execute(stmt_vehicle, vehicle_id=f.get('vehicle-id'), m=f.get('current-mileage'))
    except Exception as e:
        logger.exception(e)
        return Response(
            status=500,
            response="Unable to successfully update order"
        )

    return render_template('success_creating_resource.html')


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


def get_req_date_or_today(query_name):
    return parser.parse(request.args.get(query_name, str(datetime.date.today()))).strftime("%d-%b-%Y")


def get_sql_date_formatted(column, alias):
    return f"""to_char({column}, 'DD-MON-YYYY') {alias}"""


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

# todo <feature> rename PENDING enum value into SUBMITTED
# todo <feature> vehicle type
# todo <feature> usr mngtm
