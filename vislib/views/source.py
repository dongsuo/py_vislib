import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.utils import timezone
from MySQLdb import _mysql
from vislib.models import SourceDataBase, SourceDataTable
from common.utils.aes import pc


def default_datetime():
  now = timezone.now()
  return now

@csrf_exempt
def createSource(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  host = body['host']
  port = body.get('port', 3306)
  username = body.get('username')
  password = pc.encrypt(body.get('password')).decode('utf-8')
  database = body.get('database')
  base_alias = body.get('base_alias')
  creator = request.user
  source_id = uuid.uuid4()

  SourceDataBase.objects.create(
    source_id=source_id,
    host=host,
    port=port,
    username=username,
    password=password,
    database=database,
    base_alias=base_alias,
    creator=creator,
    is_private=True,
    status=1,
    updated_at=default_datetime()
  )
  return JsonResponse({'code': 20000, 'message': 'success', 'data': {'id': source_id}})

@csrf_exempt
def deleteSource(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  source = SourceDataBase.objects.get(source_id=body['source_id'])
  source.delete()
  return JsonResponse({'code': 20000, 'message': 'success'})

@csrf_exempt
def updateSource(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  source = SourceDataBase.objects.get(source_id=body['source_id'])
  source.host = body['host']
  source.port = body.get('port', 3306)
  source.username = body.get('username')
  if body.get('password'):
    source.password = pc.encrypt(body.get('password')).decode('utf-8')
  else:
    source = serializers.serialize('json', [source])
    source = json.loads(source)[0]['fields']
    source.password = source['password']
  source.database = body.get('database')
  source.base_alias = body.get('base_alias')

  source.save()
  return JsonResponse({'code': 20000, 'message': 'success'})

@csrf_exempt
def sourceList(request):
  sources = SourceDataBase.objects.filter(creator=request.user)
  sources = serializers.serialize('json', sources)
  sources = json.loads(sources)
  sourceArr = []
  for source in sources:
    source['fields']['source_id'] = source['pk']
    source['fields']['password'] = None
    sourceArr.append(source['fields'])
  return JsonResponse({'code': 20000, 'data': sourceArr})

@csrf_exempt
def sourceDetail(request, sourceId):
  sourceItem = SourceDataBase.objects.get(source_id=sourceId)
  sourceItem = serializers.serialize('json', [sourceItem])
  sourceItem = json.loads(sourceItem)[0]

  return JsonResponse({'code': 20000, 'message': 'success', 'data':sourceItem['fields'] })

@csrf_exempt
def sourceTables(request, sourceId):
  json_data = []
  try:
    tables = SourceDataTable.objects.filter(database=sourceId)

    tables = serializers.serialize('json', tables)
    tables = json.loads(tables)
    for table in tables:
      json_data.append(table['fields'])

  except Exception as e:
    print('no linked tables before', e)

  source = SourceDataBase.objects.get(source_id=sourceId)
  source = serializers.serialize('json', [source])
  source = json.loads(source)[0]['fields']
  password = source['password'].encode(('utf-8'))
  host = source['host']
  username = source['username']
  port = source['port']
  password = pc.decrypt(password)
  database = source['database']

  db=_mysql.connect(
    host=host,
    port=int(port),
    user=username,
    passwd=password,
    db=database
  )
  db.query('show tables;')
  tables = db.store_result().fetch_row(maxrows=0, how=2)
  db.close()
  tables = list(tables)
  for i, table in enumerate(tables):
    tableName = list(table.values())[0].decode('utf-8')
    if next((x for x in json_data if x['table'] == tableName), None):
      print(tableName + ' linked')
    else:
      json_data.append({
        'table': tableName,
        'status': 0
      })

  return JsonResponse({'code': 20000, 'message': 'success', 'data': json_data })

@csrf_exempt

def sourceTableSave(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  print(body)
  source_id = body['source_id']
  SourceDataTable.objects.filter(database=source_id).delete()
  source = SourceDataBase.objects.get(source_id=source_id)

  for table in body['tables']:
    tableConfig = SourceDataTable.objects.create(
      id=uuid.uuid4(),
      database=source,
      table=table['table'],
      table_alias=table['table_alias'],
      creator=request.user,
      status=table['status'],
      updated_at=default_datetime()
    )
    tableConfig.save()
  return JsonResponse({'code': 20000, 'message': 'success' })

@csrf_exempt
def sourceLinkedTables(request, sourceId):
  try:
    tables = SourceDataTable.objects.filter(database=sourceId)
    tables = serializers.serialize('json', tables)
    tables = json.loads(tables)
    json_data = []
    for table in tables:
      json_data.append(table['fields'])
  except Exception as e:
    json_data = []
    print(e)


  return JsonResponse({'code': 20000, 'message': 'success', 'data': json_data })
