from flask import Flask, request, jsonify
import psycopg2
import config


app = Flask(__name__)

connection = psycopg2.connect(config.DATABASE_URL)
cursor = connection.cursor()


@app.route('/discordid')
async def get_smmoid():
    try:
        discid = int(request.args.get('id'))
        stmt = "select smmoid from plebs where discid=%s and verified=true"
        cursor.execute(stmt, (str(discid),))
        data = cursor.fetchone()
        print(data)
        # data = await db.get_smmoid(discid)
        return jsonify({'smmoid': data[0] if data is not None else -1})
    except ValueError:
        return jsonify({'Error': "The 'id' field must be an integer"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8375, debug=True)
