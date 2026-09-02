import json
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from vislib.db import run_sql
from vislib.models import SourceDataBase
from common.utils.aes import pc
# Create your views here.

def default_datetime():
  now = timezone.now()
  return now


@csrf_exempt
def execSql(request):
  try:
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

    db_type = source.get('db_type') or SourceDataBase.DB_MYSQL
    json_data = run_sql(
      db_type,
      host,
      int(port),
      username,
      password,
      database,
      sql,
    )
    response = {
      'code': 20000,
      'message': 'success',
      'data': json_data
    }
  except Exception as e:
    print(e)
    response = {
      'code': 10000,
      'message': str(e),
      'data': {}
    }
  return JsonResponse(response)
