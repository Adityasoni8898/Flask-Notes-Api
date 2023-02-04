from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
import json

app = Flask("VideoAPI")
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('title', required=True, location="form")
parser.add_argument('description', location="form")
parser.add_argument('uploadDate', type=int, location="form")

with open('notes.json', 'r') as f:
    notes = json.load(f)


def write_changes_to_file():
    global notes
    notes = {k: n for k, n in sorted(
        notes.items(), key=lambda note: note[1]['uploadDate'])}
    with open('notes.json', 'w') as f:
        json.dump(notes, f)


class Notes(Resource):
    def get(self, note_id):
        if note_id == "all":
            return notes
        if note_id not in notes:
            abort(404, message=f"Note {note_id} not found")
        return notes[note_id]

    def put(self, note_id):
        args = parser.parse_args()
        new_note = {
            'title': args['title'],
            'description': args['description'],
            'uploadDate': args['uploadDate']}
        notes[note_id] = new_note
        write_changes_to_file()
        return {note_id: notes[note_id]}

    def delete(self, note_id):
        if note_id not in notes:
            abort(404, message=f"Note {note_id} not found")
        del notes[note_id]
        write_changes_to_file()
        return "", 204


class AutoCreation(Resource):
    def get(self):
        return notes

    def post(self):
        args = parser.parse_args()
        new_note = {
            'title': args['title'],
            'description': args['description'],
            'uploadDate': args['uploadDate']}
        note_id = max(int(n.lstrip('notes')) for n in notes.keys()) + 1
        note_id = f"note{note_id}"
        notes[note_id] = new_note
        write_changes_to_file()
        return notes[note_id]


api.add_resource(Notes, '/notes/<note_id>')
api.add_resource(AutoCreation, '/notes')

if __name__ == '__main__':
    app.run(debug=True)
