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
def test_scientific_name(client):
   response = client.get('/species/neolamprologus%20mul')
   json_data = response.get_json()

   assert 'Neolamprologus' in json_data[0]['complete_name']
   assert json_data[0]['tsn'] == 648810

'''
[
  {
    "complete_name": "Pterophyllum scalare",
    "tsn": 169845,
    "unit_name1": "Pterophyllum",
    "unit_name2": "scalare",
    "vernacular_name": "freshwater angelfish"
  }
]
'''
def test_common_name(client):
   response = client.get('/species/freshwater%20angelfish')
   json_data = response.get_json()

   assert 'Pterophyllum' in json_data[0]['complete_name']
   assert json_data[0]['tsn'] == 169845

