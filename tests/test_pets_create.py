import pytest
'''
{
   "userid": "mitchell.broome@gmail.com",
   "description": "multis",
   "public": true,
   "scientific_name": "neolamprologus multifasciatus"
}
'''
def XXXtest_create_mypets(client):
   newpet = {
      'userid': 'mitchell.broome@gmail.com',
      'description': 'multis',
      'public': True,
      'scientific_name': 'neolamprologus multifasciatus'
   }

   response = client.post('/pets/mypets', json=newpet)
   json_data = response.get_json()

   assert len(json_data) > 0

def XXXtest_update_mypets(client):
   newpet = {
      'userid': 'mitchell.broome@gmail.com',
      'description': 'multis',
      'public': True,
      'scientific_name': 'neolamprologus multifasciatus'
   }

   response = client.post('/pets/mypets/2', json=newpet)
   json_data = response.get_json()

   assert len(json_data) > 0

def XXXtest_start_pet(client):
   response = client.get('/pets/mypets/2/start')
   json_data = response.get_json()

   assert len(json_data) > 0

def test_stop_pet(client):
   response = client.get('/pets/mypets/2/stop')
   json_data = response.get_json()

   assert len(json_data) > 0

