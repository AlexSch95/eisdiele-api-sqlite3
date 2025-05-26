from flask import Flask, jsonify, request
from flasgger import Swagger
import sqlite3

con = sqlite3.connect('eisdiele.db', check_same_thread=False)
cur = con.cursor()
app = Flask(__name__)
swagger = Swagger(app)

@app.route("/")
def welcome():
    return "Wilkommen auf der Homepage unserer Eisdiele"

@app.route('/api/flavours', methods=["GET"])
def get_flavours():
    """
    Liste aller Geschmackssorten
    ---
    responses:
        200:
            description: JSON-Liste aller Geschmackssorten
            examples:
                application/json:
                    - id: 1
                      name: schokolade
                      type: milch
                      price_per_serving: 1.5
                    - id: 2
                      name: vanille
                      type: frucht
                      price_per_serving: 1.5
    """
    cur.execute("SELECT * FROM flavours;")
    flavours = cur.fetchall()
    flav_list = []
    for row in flavours:
        flav_id, flav_name, flav_type, flav_price = row
        flav_dict = {
            "flavour-id": flav_id, 
            "name": flav_name, 
            "type": flav_type, 
            "price_per_serving": flav_price
            }
        flav_list.append(flav_dict)
    return jsonify(flav_list), 200

@app.route("/api/flavours", methods=["POST"])
def post_flavours():
    """
    Neue Geschmackssorte hinzufügen
    ---
    consumes:
        - application/json
    parameters:
        - in: body
          name: flavour
          required: true
          schema:
            type: object
            properties:
                name:
                    type: string
                    example: schokolade
                type:
                    type: string
                    example: milch
                price_per_serving:
                    type: number
                    example: 1.5
    responses:
        201:
            description: Sorten hinzugefügt
        400:
            description: Fehler, kein Objekt übergeben
    """
    new_flavour = request.get_json()
    if not new_flavour:
        return jsonify({"message": "Fehler, kein Objekt übergeben"}), 400
    cur.execute(f"""INSERT INTO flavours (name, type, price_per_serving)
        VALUES
        ("{new_flavour["name"]}", "{new_flavour["type"]}", {new_flavour["price_per_serving"]})
        ;""")
    con.commit()
    return jsonify({"message": "Sorten hinzugefügt"}), 201


@app.route("/api/flavours/<int:id>", methods=['DELETE'])
def delete_flavour(id):
    """
    Eine Geschmackssorte löschen
    ---
    parameters:
        - name: id
          in: path
          type: integer
          required: true
          description: die zu löschende Geschmackssorte
    responses:
        200:
            description: Sorte wurde erfolgreich gelöscht
        404:
            description: Sorte nicht gefunden
    """
    valid_flavour_ids = []
    cur.execute("SELECT flavour_id FROM flavours")
    while (row := cur.fetchone()) is not None:
        valid_flavour_ids.append(row[0])
    print(valid_flavour_ids)
    print(id)
    if id not in valid_flavour_ids:
        return jsonify({"message": "Sorte nicht vorhanden"}), 404
    cur.execute(f"""DELETE FROM flavours WHERE flavour_id = {id};""")
    con.commit()
    return jsonify({"message":"Sorte gelöscht"}), 200

@app.route("/api/flavours/<int:id>", methods=["PUT"])
def put_flavours(id):
    """
        Eine komplette Geschmackssorte mit neuen Werten überschreiben
        ---
        parameters:
            - name: id
              in: path
              type: integer
              required: true
              description: Der Name der Geschmackssorte bei der ein Wert überschrieben werden soll
            - in: body
              name: flavour
              required: true
              schema:
                type: object
                properties:
                    name:
                        type: string
                        example: schokolade
                    type:
                        type: string
                        example: milch
                    price_per_serving:
                        type: float
                        example: 1.5
        responses:
            200:
                description: Sorte überschrieben
            400:
                description: Fehler, kein Objekt übergeben
            404:
                description: Zu überschreibender Datensatz nicht gefunden

        """
    replace_flavour = request.get_json()
    
    cur.execute(f"SELECT * FROM flavours WHERE flavour_id = {id};")
    id_exists = cur.fetchone()
    if not replace_flavour:
        return jsonify({"message": "Fehler, kein Objekt übergeben"}), 400
    elif not id_exists:
        return jsonify({"message": "Zu überschreibender Datensatz nicht gefunden"}), 404
    cur.execute(f"""UPDATE flavours
            SET
            name = "{replace_flavour["name"]}", type = "{replace_flavour["type"]}", price_per_serving = {replace_flavour["price_per_serving"]}
            WHERE flavour_id = {id}
            ;""")
    con.commit()
    return jsonify({"message": "Sorte überschrieben"}), 200

@app.route("/api/flavours/<int:id>", methods=["PATCH"])
def patch_flavours(id):
    """
    Einen einzelnen Wert einer vorhandene Geschmackssorte überschreiben
    ---
    parameters:
        - name: id
          in: path
          type: integer
          required: true
          description: Der Name der Geschmackssorte bei der ein Wert überschrieben werden soll
        - in: body
          name: flavour
          required: anyOf
          schema:
            type: object
            properties:
                name:
                    type: string
                    example: schokolade
                type:
                    type: string
                    example: milch
                price_per_serving:
                    type: float
                    example: 1.5
    responses:
        200:
            description: Sorte wurde erfolgreich geupdatet
        400:
            description: Fehler, kein Objekt übergeben
        404:
            description: Zu aktualisierender Datensatz wurde nicht gefunden
    """
    update_flavour = request.get_json()
    cur.execute(f"SELECT * FROM flavours WHERE flavour_id = {id};")
    id_exists = cur.fetchone()
    if not update_flavour:
        return jsonify({"message": "Fehler, kein Objekt übergeben"}), 400
    if not id_exists:
        return jsonify({"message": "Zu aktualisierender Datensatz wurde nicht gefunden"}), 404
    for key, value in update_flavour.items():
        print(key, value)
        if isinstance(value, str):
            cur.execute(f"""UPDATE flavours SET
                    {key} = "{value}"
                    WHERE flavour_id = {id};""")
        else:
            cur.execute(f"""UPDATE flavours SET
                    {key} = {value}
                    WHERE flavour_id = {id};""")
        con.commit()
    return jsonify({"message": "Sorte wurde erfolgreich geupdatet"}), 200

if __name__ == "__main__":
    app.run(debug=True)
