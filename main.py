# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import logging
import os

from flask import Flask, render_template, request, Response
import sqlalchemy

# Remember - storing secrets in plaintext is potentially unsafe. Consider using
# something like https://cloud.google.com/kms/ to help keep secrets secret.
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


@app.route('/drop_off_bikes_list', methods=['GET'])
def drop_off_bikes_list():
    # todo: where clouse (start date == today and user email)
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
    # todo: where clouse (end date == today and user email)
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
    # I want to see a bike that is not in orders
    # and
    # in orders but start date > today
    # in orders but end date is not overlapping
    # todo: where clouse
    q = """
        SELECT 
           b.plates plate, b.name bike_name, b.id b_id, l.name loc_name, 
           l.address loc_address, o.id order_id
        FROM 
           "bike" b
           left join "order" o on o.bike = b.id
           left join "location" l on o.location_start = l.id
       """
    with db.connect() as conn:
        bikes = conn.execute(q).fetchall()

    start_date = request.args.get('start_date')

    print('s_d', start_date)

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
        response=f"updated order {order_id}. the order is not active"
    )


@app.route('/', methods=['GET'])
def index():
    votes = []
    with db.connect() as conn:
        # Execute the query and fetch all results
        recent_votes = conn.execute(
            "SELECT candidate, time_cast FROM votes "
            "ORDER BY time_cast DESC LIMIT 5"
        ).fetchall()
        # Convert the results into a list of dicts representing votes
        for row in recent_votes:
            votes.append({
                'candidate': row[0],
                'time_cast': row[1]
            })

        stmt = sqlalchemy.text(
            "SELECT COUNT(vote_id) FROM votes WHERE candidate=:candidate")
        # Count number of votes for tabs
        tab_result = conn.execute(stmt, candidate="TABS").fetchone()
        tab_count = tab_result[0]
        # Count number of votes for spaces
        space_result = conn.execute(stmt, candidate="SPACES").fetchone()
        space_count = space_result[0]

    return render_template(
        'index.html',
        recent_votes=votes,
        tab_count=tab_count,
        space_count=space_count
    )


@app.route('/', methods=['POST'])
def save_vote():
    # Get the team and time the vote was cast.
    team = request.form['team']
    time_cast = datetime.datetime.utcnow()
    # Verify that the team is one of the allowed options
    if team != "TABS" and team != "SPACES":
        logger.warning(team)
        return Response(
            response="Invalid team specified.",
            status=400
        )

    # [START cloud_sql_postgres_sqlalchemy_connection]
    # Preparing a statement before hand can help protect against injections.
    stmt = sqlalchemy.text(
        "INSERT INTO votes (time_cast, candidate)"
        " VALUES (:time_cast, :candidate)"
    )
    try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with db.connect() as conn:
            conn.execute(stmt, time_cast=time_cast, candidate=team)
    except Exception as e:
        # If something goes wrong, handle the error in this section. This might
        # involve retrying or adjusting parameters depending on the situation.
        # [START_EXCLUDE]
        logger.exception(e)
        return Response(
            status=500,
            response="Unable to successfully cast vote! Please check the "
                     "application logs for more details."
        )
        # [END_EXCLUDE]
    # [END cloud_sql_postgres_sqlalchemy_connection]

    return Response(
        status=200,
        response="Vote successfully cast for '{}' at time {}!".format(
            team, time_cast)
    )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
