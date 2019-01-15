import time
import pytest

def XXXtest_create_note(client):
   note = {
      'note': 'testing: %s' % time.time(),
      'public': True,
   }

   response = client.post('/pets/mypets/2/note', json=note)
   json_data = response.get_json()

   assert len(json_data) > 0

def test_update_note(client):
   note = {
      'note': 'testing: %s' % time.time(),
      'public': True,
   }

   response = client.post('/pets/mypets/2/note/7', json=note)
   json_data = response.get_json()

   assert len(json_data) > 0

