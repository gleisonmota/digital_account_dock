def search_notes():
    notes = {
        "created": "2020-03-24",
        "idRegistration": "7d5205a6-4574-4752-a751-19aa894c0609",
        "notes": [
            {
                "id": "ee4c3d08-859b-4045-883f-36575fc384ba",
                "create": "2022-07-29",
                "text": "note"
            },
            {
                "id": "ee4c3d08-859b-4045-883f-36575fc384ba",
                "create": "2022-07-28",
                "text": "note"
            },
            {
                "id": "ee4c3d08-859b-4045-883f-36575fc384ba",
                "create": "2022-07-20",
                "text": "note"
            },
            {
                "id": "ee4c3d08-859b-4045-883f-36575fc384ba",
                "create": "2022-01-01",
                "text": "note"
            },
            {
                "id": "ee4c3d08-859b-4045-883f-36575fc384ba",
                "text": "note"
            },
            {
                "id": "ee4c3d08-859b-4045-883f-36575fc384ba",
                "text": "note"
            }
        ]
    }

    return notes['notes'][-1]

if __name__ == "__main__":
    last_note = search_notes()
    print(last_note)
# note.sort(key=lambda e: (e is None, e))

