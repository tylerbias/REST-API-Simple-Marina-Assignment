# REST-API-Simple-Marina-Assignment
REST API Demo, "The Simple Marina," built with Python, Flask, and Google NoSQL Cloud Datastore - Tyler Bias, Oregon State University 2018

https://erudite-phalanx-193815.appspot.com/

GET /
- Displays a brief welcome page.

GET /boats
- Returns all boat entities as JSON objects. Returns boat names, types, lengths, IDs,
URLs for specific boat entities, and whether they are at sea or in a slip. If in a slip, this
will return the slip number and a URL to the slip entity.

POST /boats
- Receives JSON data containing a boat’s name, type, and length, and creates a boat
entity using that data. The boat is automatically set to be at sea when created. The boat
is assigned an ID automatically, and this ID is returned when this request is received.

GET /slips
- Returns all slip entities as JSON objects. Returns slip numbers and IDs. Returns URLs
to specific slip entities. If slip contains a boat, returns an arrival date, the boat’s name,
and a URL to the boat.

POST /slips
- Receives JSON data containing a slip number, which is used to generate a slip entity.
The slip will automatically have no boat when it is generated, and an ID will be assigned
to it. The ID is returned by this request. Will reject a slip if the provided number value is
already assigned to an existing slip.

GET /boats/{boat_id}
- Returns information about a specific boat entity. Boat name, type, length, ID number,
and the boat’s URL. If at sea, that information will be displayed. If in a slip, this will
contain the slip number and a URL to the slip entity that contains this boat.

DELETE /boats/{boat_id}
- Removes a boat entity from the database. If that boat was occupying a slip, then that slip
will be updated to show that it is now empty.

GET /slips/{slip_id}
- Returns information about a specific slip entity. Number, ID, and the slip’s URL. If the slip
contains a boat, the boat’s name, the boat’s arrival date, and the boat’s URL will be
returned.

DELETE /slips/{slip_id}
- Removes a slip entity from the database. If the slip was holding a boat, then that boat
will be updated to show that it is now at sea.

GET /boats/{boat_id}/name
- Displays the name belonging the the boat entity.
PATCH /boats/{boat_id}/name

- Receives JSON data containing a new name for a boat entity and updates that entity to
reflect the new name.

GET /boats/{boat_id}/type
- Displays the type of a boat

PATCH /boats/{boat_id}/type
- Receives JSON data containing new type information for a boat entity and updates that
entity

GET /boats/{boat_id}/length
- Displays the length of a boat

PATCH /boats/{boat_id}/length
- Receives JSON data containing new boat length information and updates the specified
boat entity to reflect the change

GET /slips/{slip_id}/number
- Displays a slip’s number

PATCH /slips/{slip_id}/number
- Receives JSON data containing a new slip number and updates the specified slip entity
to reflect the change. Also checks to ensure that there is not already a slip that the given
number is assigned to.

GET /slips/{slip_id}/date
- Displays a slip’s arrival date value.

PATCH /slips/{slip_id}/date
- Receives JSON data containing a new arrival date value and updates the specified slip
entity to reflect the change.

POST /boats/{boat_id}/arrival
- Receives JSON data containing the number of the slip to which the boat should be
assigned and the arrival date. Updates the slip to reflect that it now contains a boat.
Updates the boat to reflect that it is now docked at a slip. Checks that the boat in
question is at sea and will refuse to process the request if it is not.

POST /boats/{boat_id}/departure
- Checks that a boat is docked at a slip, and if it is, sets the boat to be at sea again.
Updates the slip that the boat was formerly docked at to indicate that the slip once again
is empty
