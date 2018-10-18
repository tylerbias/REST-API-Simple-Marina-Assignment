import logging
import datetime

from google.appengine.ext import ndb
from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
from flask import abort


app = Flask(__name__)

class Boat(ndb.Model):
    name = ndb.StringProperty()
    type = ndb.StringProperty()
    length = ndb.FloatProperty()
    at_sea = ndb.BooleanProperty()
    current_slip_number = ndb.IntegerProperty()
    current_slip_id = ndb.StringProperty()
    
class Slip(ndb.Model):
    number = ndb.IntegerProperty()
    current_boat_id = ndb.StringProperty()
    arrival_date = ndb.StringProperty()
    has_boat = ndb.BooleanProperty()
    

# A simple welcome page

@app.route('/')
def main_page():
    welcome_text = "Tyler's Simple Marina\n\nView Boats: https://erudite-phalanx-193815.appspot.com/boats\n\nView Slips: https://erudite-phalanx-193815.appspot.com/slips"
    return Response(welcome_text, mimetype='text/plain')

# /boats handler
# Can process both GET and POST
# Get will return all boats currently stored in the database
# POSTing valid json will create a new boat entity 
@app.route('/boats', methods=['GET', 'POST'])
def boats():
    data = {}
    n = 0
    if request.method == 'POST':
        jsonNew = request.json
        for key in jsonNew:
            if key not in ("Name", "Type", "Length"):
                return abort(403, "Invalid data")
        new_boat = Boat(name=jsonNew["Name"], type=jsonNew["Type"], length=jsonNew["Length"], at_sea=True)
        new_boat_key = new_boat.put()
        data["Generated ID"] = new_boat_key.id()
        json_resp = jsonify(data)
        return json_resp
    else:
        q = Boat.query()
        fetched = q.fetch()
        for x in fetched:
            data[n] = {}
            data[n]["ID"] = str(x.key.id())
            data[n]["Name"] = x.name
            data[n]["Type"] = x.type
            data[n]["length"] = x.length
            data[n]["URL"] = "https://erudite-phalanx-193815.appspot.com/boats/%s" % str(x.key.id())
            if x.at_sea:
                data[n]["At Sea"] = True
            else:
                data[n]["Current Slip Number"] = x.current_slip_number
                data[n]["Current Slip URL"] = "https://erudite-phalanx-193815.appspot.com/slips/%s" % x.current_slip_id
            n = n + 1
        json_resp = jsonify(data)
        return json_resp

# /slips handler
# Can process both GET and POST
# Get will return all slips that currently exist, as well as information about the boats in them
# POSTing valid json will generate a new slip in the database    
@app.route('/slips', methods=['GET', 'POST'])
def slips():
    data = {}
    n = 0
    if request.method == 'POST':
        jsonNew = request.json
        for key in jsonNew:
            if key not in ("Number"):
                return abort(403, "Invalid data")
        q = Slip.query(Slip.number == jsonNew["Number"])
        fetched = q.fetch()
        if not fetched:
            new_slip = Slip(number=jsonNew["Number"], has_boat=False)
            new_slip_key = new_slip.put()
            data["Generated ID"] = new_slip_key.id()
            json_resp = jsonify(data)
            return json_resp
        else:
            return abort(403, "There is already a slip with that number.")
    else:
        q = Slip.query()
        fetched = q.fetch()
        for x in fetched:
            data[n] = {}
            data[n]["ID"] = str(x.key.id())
            data[n]["Number"] = x.number
            if x.has_boat:
                data[n]["Current Boat URL"] = "https://erudite-phalanx-193815.appspot.com/boats/%s" % x.current_boat_id
                data[n]["Arrival Date"] = x.arrival_date
                the_boat = Boat.get_by_id(int(x.current_boat_id))
                data[n]["Current Boat Name"] = the_boat.name
            data[n]["URL"] = "https://erudite-phalanx-193815.appspot.com/slips/%s" % str(x.key.id())
            n = n + 1
        json_resp = jsonify(data)
        return json_resp
    
# /boats/IDNUM handler
# A GET request with a valid ID will return information on a specific boat
# A DELTE request will remove the specified boat
@app.route('/boats/<boat_id>', methods=['GET', 'DELETE'])
def specific_boat(boat_id):
    data = {}
    resulting_boat = Boat.get_by_id(int(boat_id))
    if not resulting_boat:
        return abort(404, "Boat not found.")
    if request.method == 'DELETE':
        slip_query = Slip.query(Slip.current_boat_id == boat_id)
        current_slip = slip_query.fetch()
        print current_slip
        for x in current_slip:
            x.current_boat_id = "0"
            x.has_boat = False
            x.put()
        resulting_boat.key.delete()
        return Response("Boat deleted.", mimetype='text/plain')
    data["ID"] = boat_id
    data["Name"] = resulting_boat.name
    data["Type"] = resulting_boat.type
    data["Length"] = resulting_boat.length
    if resulting_boat.at_sea:
        data["At Sea"] = resulting_boat.at_sea
    else:
        data["Current Slip Number"] = resulting_boat.current_slip_number
        data["Current Slip URL"] = "https://erudite-phalanx-193815.appspot.com/slips/%s" % resulting_boat.current_slip_id
    data["URL"] = "https://erudite-phalanx-193815.appspot.com/boats/%s" % boat_id
    json_resp = jsonify(data)
    return json_resp

# View specific boat's name or rename boat
@app.route('/boats/<boat_id>/name', methods=['GET', 'PATCH'])
def boat_name(boat_id):
    if request.method == 'PATCH':
        jsonNew = request.json
        for key in jsonNew:
            if key not in ("Name"):
                return abort(403, "Must specify a boat name")
        renamed_boat = Boat.get_by_id(int(boat_id))
        if not renamed_boat:
            return abort(404, "Boat not found.")
        renamed_boat.name = jsonNew["Name"]
        renamed_boat.put()
        post_text = "Rename successful."
        return Response(post_text, mimetype='text/plain')
    else:
        data = {}
        resulting_boat = Boat.get_by_id(int(boat_id))
        if not resulting_boat:
            return abort(404, "Boat not found.")
        data["Name"] = resulting_boat.name
        data["URL"] = "https://erudite-phalanx-193815.appspot.com/boats/%s" % boat_id
        json_resp = jsonify(data)
        return json_resp
    
# View specific boat's type or change a boat's type
@app.route('/boats/<boat_id>/type', methods=['GET', 'PATCH'])
def boat_type(boat_id):
    if request.method == 'PATCH':
        jsonNew = request.json
        for key in jsonNew:
            if key not in ("Type"):
                return abort(403, "Must specify a boat type")
        new_type = Boat.get_by_id(int(boat_id))
        if not new_type:
            return abort(404, "Boat not found.")
        new_type.type = jsonNew["Type"]
        new_type.put()
        post_text = "Type change successful."
        return Response(post_text, mimetype='text/plain')
    else:
        data = {}
        resulting_boat = Boat.get_by_id(int(boat_id))
        if not resulting_boat:
            return abort(404, "Boat not found.")
        data["Type"] = resulting_boat.type
        data["URL"] = "https://erudite-phalanx-193815.appspot.com/boats/%s" % boat_id
        json_resp = jsonify(data)
        return json_resp
    
# View specific boat's length or change a boat's length
@app.route('/boats/<boat_id>/length', methods=['GET', 'PATCH'])
def boat_length(boat_id):
    if request.method == 'PATCH':
        jsonNew = request.json
        for key in jsonNew:
            if key not in ("Length"):
                return abort(403, "Must specify a new length")
        new_length = Boat.get_by_id(int(boat_id))
        if not new_length:
            return abort(404, "Boat not found.")
        new_length.length = jsonNew["Length"]
        new_length.put()
        post_text = "Length change successful."
        return Response(post_text, mimetype='text/plain')
    else:
        data = {}
        resulting_boat = Boat.get_by_id(int(boat_id))
        if not resulting_boat:
            return abort(404, "Boat not found.")
        data["Length"] = resulting_boat.length
        data["URL"] = "https://erudite-phalanx-193815.appspot.com/boats/%s" % boat_id
        json_resp = jsonify(data)
        return json_resp
    

# ARRIVAL
@app.route('/boats/<boat_id>/arrival', methods=['POST'])
def arrival(boat_id):
    jsonInput = request.json
    matchCheck = False
    for key in jsonInput:
        if key not in ("Date", "Slip Number"):
            return abort(403, "Both an arrival date and a slip number must be specified.")
    arriving_boat = Boat.get_by_id(int(boat_id))
    if not arriving_boat.at_sea:
        return abort(403, "A boat that is not at sea cannot arrive at a slip.")
    slip_query = Slip.query()
    fetched = slip_query.fetch()
    if not fetched:
        return abort(403, "All slips are currently occupied.")
    for x in fetched:
        if jsonInput["Slip Number"] == x.number:
            if x.has_boat:
                return abort(403, "The specified slip is already occupied.")
            x.current_boat_id = boat_id
            x.arrival_date = jsonInput["Date"]
            x.has_boat = True
            slip_id = x.put()
            arriving_boat.at_sea = False
            arriving_boat.current_slip_id = str(slip_id.id())
            arriving_boat.current_slip_number = jsonInput["Slip Number"]
            arriving_boat.put()
            matchCheck = True
    if matchCheck:
        return Response("The boat has arrived at Slip #%s." % jsonInput["Slip Number"])
    else:
        return abort(403, "No slip with the specified number.")
    
@app.route('/boats/<boat_id>/departure', methods=['POST'])
def departure(boat_id):
    the_boat = Boat.get_by_id(int(boat_id))
    if the_boat.at_sea:
        return abort(403, "A boat at sea cannot depart from a slip.")
    else:
        slip_id = the_boat.current_slip_id
        the_boat.at_sea = True
        the_boat.current_slip_number = None
        the_boat.current_slip_id = "0"
        the_boat.put()
        the_slip = Slip.get_by_id(int(slip_id))
        slip_number = the_slip.number
        the_slip.has_boat = False
        the_slip.current_boat_id = "0"
        the_slip.arrival_date = None
        the_slip.put()
        return Response("The boat has successfully departed from Slip #%s" % slip_number)
    
# View specific slip's number or re-number
@app.route('/slips/<slip_id>/number', methods=['GET', 'PATCH'])
def slip_number(slip_id):
    if request.method == "PATCH":
        jsonNew = request.json
        for key in jsonNew:
            if key not in ("Number"):
                return abort(403, "Must specify a slip number")
        renumbered_slip = Slip.get_by_id(int(slip_id))
        if not renumbered_slip:
            return abort(404, "Slip not found.")
        q = Slip.query(Slip.number == jsonNew["Number"])
        fetched = q.fetch()
        if not fetched:
            renumbered_slip.number = jsonNew["Number"]
            renumbered_slip.put()
            post_text = "Slip re-numbering successful."
            return Response(post_text, mimetype='text/plain')
        else:
            return abort(403, "There is already a slip with that number.")
    else:
        data = {}
        resulting_slip = Slip.get_by_id(int(slip_id))
        if not resulting_slip:
            return abort(403, "Slip not found.")
        data["Number"] = resulting_slip.number
        data["URL"] = "https://erudite-phalanx-193815.appspot.com/boats/%s" % slip_id
        json_resp = jsonify(data)
        return json_resp

# Change a slip's arrival date
@app.route('/slips/<slip_id>/date', methods=['GET', 'PATCH'])
def slip_date(slip_id):
    if request.method == "PATCH":
        if not request.json:
            return abort(403, "Request must contain JSON data.")
        jsonNew = request.json
        for key in jsonNew:
            if key not in ("Arrival Date"):
                return abort(403, "Must specify an arrival date.")
        the_slip = Slip.get_by_id(int(slip_id))
        if not the_slip:
            return abort(404, "Slip not found.")
        if not the_slip.has_boat:
            return abort(403, "There is no boat docked at this slip.")
        the_slip.arrival_date = jsonNew["Arrival Date"]
        the_slip.put()
        return Response("The arrival date was changed successfully.")
    else:
        data = {}
        resulting_slip = Slip.get_by_id(int(slip_id))
        if not resulting_slip:
            return abort(403, "Slip not found.")
        data["Number"] = resulting_slip.number
        data["URL"] = "https://erudite-phalanx-193815.appspot.com/boats/%s" % slip_id
        json_resp = jsonify(data)
        return json_resp

# /slips/IDNUM handler
# A GET request with a valid ID will return information on a specific slip
@app.route('/slips/<slip_id>', methods=['GET', 'DELETE'])
def specific_slip(slip_id):
    data = {}
    resulting_slip = Slip.get_by_id(int(slip_id))
    if not resulting_slip:
        return abort(404, "Slip not found.")
    if request.method == 'DELETE':
        if resulting_slip.has_boat:
            docked_boat_id = resulting_slip.current_boat_id
            docked_boat = Boat.get_by_id(int(docked_boat_id))
            docked_boat.at_sea = True
            docked_boat.current_slip_number = None
            docked_boat.current_slip_id = "0"
            docked_boat.put()
        resulting_slip.key.delete()
        return Response("Slip successfully deleted.", mimetype='text/plain')
    else:
        data["Slip ID"] = slip_id
        data["Number"] = resulting_slip.number
        data["URL"] = "https://erudite-phalanx-193815.appspot.com/slips/%s" % slip_id
        if resulting_slip.has_boat:
            current_boat = Boat.get_by_id(int(resulting_slip.current_boat_id))
            data["Current Boat"] = current_boat.name
            data["Current Boat URL"] = "https://erudite-phalanx-193815.appspot.com/boats/%s" % resulting_slip.current_boat_id
            data["Arrival Date"] = resulting_slip.arrival_date
        json_resp = jsonify(data)
        return json_resp

@app.route('/test/<id>')
def test_route(numtest):
    resp = ("You have reached the page for \'%s.\' Unfortuantely nothing is here yet." % numtest)
    return Response(resp, mimetype='text/plain')
    
    
        

@app.route('/test')
def please():
    test_page = "You have reached a test page. Sorry about that. Quit poking around."
    return Response(test_page, mimetype="text/plain")




@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
 
#app.run(debug=True)
