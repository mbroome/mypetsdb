import pytest

'''
[
  {
    "collection_point": null,
    "description": null,
    "end": null,
    "notes": [
      {
        "note": "this is a test",
        "note_id": 1,
        "pet": 1,
        "public": false,
        "timestamp": "2019-01-13T20:24:47+00:00"
      },
      {
        "note": "this is a test",
        "note_id": 2,
        "pet": 1,
        "public": false,
        "timestamp": "2019-01-13T21:20:36+00:00"
      },
      {
        "note": "test3",
        "note_id": 3,
        "pet": 1,
        "public": false,
        "timestamp": "2019-01-13T21:23:40+00:00"
      },
      {
        "note": "test3",
        "note_id": 4,
        "pet": 1,
        "public": true,
        "timestamp": "2019-01-13T21:23:55+00:00"
      }
    ],
    "pet_id": 1,
    "public": false,
    "species": [
      {
        "cares": 0,
        "common_name": null,
        "endangered_status": 0,
        "genus": "neolamprologus",
        "iucn_category": "LC",
        "iucn_id": "60602",
        "pet": [
          1
        ],
        "scientific_name": "neolamprologus multifasciatus",
        "species": "multifasciatus"
      }
    ],
    "start": null,
    "userid": "bob.broome@gmail.com",
    "variant": null
  }
]
'''
def test_get_mypets(client):
   response = client.get('/pets/mypets')
   json_data = response.get_json()

   assert len(json_data) > 0

'''
{
  "collection_point": null,
  "description": null,
  "end": null,
  "notes": [
    {
      "note": "this is a test",
      "note_id": 1,
      "pet": 1,
      "public": false,
      "timestamp": "2019-01-13T20:24:47+00:00"
    },
    {
      "note": "this is a test",
      "note_id": 2,
      "pet": 1,
      "public": false,
      "timestamp": "2019-01-13T21:20:36+00:00"
    },
    {
      "note": "test3",
      "note_id": 3,
      "pet": 1,
      "public": false,
      "timestamp": "2019-01-13T21:23:40+00:00"
    },
    {
      "note": "test3",
      "note_id": 4,
      "pet": 1,
      "public": true,
      "timestamp": "2019-01-13T21:23:55+00:00"
    }
  ],
  "pet_id": 1,
  "public": false,
  "species": [
    {
      "cares": 0,
      "common_name": null,
      "endangered_status": 0,
      "genus": "neolamprologus",
      "iucn_category": "LC",
      "iucn_id": "60602",
      "pet": [
        1
      ],
      "scientific_name": "neolamprologus multifasciatus",
      "species": "multifasciatus"
    }
  ],
  "start": null,
  "userid": "bob.broome@gmail.com",
  "variant": null
}
'''
def test_get_mypets(client):
   response = client.get('/pets/mypets/1')
   json_data = response.get_json()

   assert json_data['pet_id'] == 1

