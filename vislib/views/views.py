import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from MySQLdb import _mysql
from django.core import serializers
from vislib.models import SourceDataBase
from django.utils import timezone
from common.utils.aes import pc
# Create your views here.

def default_datetime():
  now = timezone.now()
  return now


@csrf_exempt
def execSql(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  sql = body['sql']
  sourceId = body['source_id']
  source = SourceDataBase.objects.get(source_id=sourceId)
  source = serializers.serialize('json', [source])
  source = json.loads(source)[0]['fields']
  host = source['host']
  username = source['username']
  port = source['port']
  password = pc.decrypt(source['password'])
  database = source['database']

  db=_mysql.connect(
    host=host,
    port=int(port),
    user=username,
    passwd=password,
    db=database,
  )
  db.query(sql)
  data = db.store_result().fetch_row(maxrows=0, how=2)
  db.close()
  json_data = []
  for index in range(len(data)):
    row = data[index]
    json_data.append({})
    for key in row:
      if(key.find('.')>0):
        column = (key.split('.'))[1]
      else:
        column = key
      if isinstance(row[key], bytes):
        json_data[index][column] = row[key].decode('UTF-8')
      else:
        json_data[index][column] = row[key]
  response = {
    'code': 20000,
    'message': 'success',
    'data': json_data
  }
  return JsonResponse(response)
