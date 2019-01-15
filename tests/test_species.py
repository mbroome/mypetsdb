import pytest

'''
[
  {
    "complete_name": "Neolamprologus multifasciatus",
    "tsn": 648810,
    "unit_name1": "Neolamprologus",
    "unit_name2": "multifasciatus"
  }
]'''
def test_index(client):
   response = client.get('/species/neolamprologus%20mul')
   json_data = response.get_json()

   assert 'Neolamprologus' in json_data[0]['complete_name']
   assert json_data[0]['tsn'] == 648810


