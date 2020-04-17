import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from vislib.models import SourceDataBase, SourceDataTable
from django.utils import timezone
import uuid

@csrf_exempt
def createSource(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  host = body['host']
  port = body.get('port', 3306)
  username = body.get('username')
  password = body.get('password')
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
  source.password = body.get('password')
  source.database = body.get('database')
  source.base_alias = body.get('base_alias')

  source.save()
  return JsonResponse({'code': 20000, 'message': 'success'})

@csrf_exempt
def sourceList(request):
  sourceList = SourceDataBase.objects.filter(creator=request.user)
  sourceList = serializers.serialize('json', sourceList)
  sourceList = json.loads(sourceList)
  sourceArr = []
  for source in sourceList:
    source['fields']['source_id'] = source['pk']
    source['fields']['password'] = None
    sourceArr.append(source['fields'])
  return JsonResponse({'code': 20000, 'data': sourceArr})

@csrf_exempt
def sourceDetail(request, sourceId):
  sourceDetail = SourceDataBase.objects.get(source_id=sourceId)
  sourceDetail = serializers.serialize('json', [sourceDetail])
  sourceDetail = json.loads(sourceDetail)[0]

  return JsonResponse({'code': 20000, 'message': 'success', 'data':sourceDetail['fields'] })

@csrf_exempt
def sourceTables(request, sourceId):
  try:
    tables = SourceDataTable.objects.get(database=sourceId)
    tables = serializers.serialize('json', [tables])
    tables = json.loads(tables)
    json_data = []
    for table in tables:
      json_data.append(table['fields'])

  except:
    source = SourceDataBase.objects.get(source_id=sourceId)
    source = serializers.serialize('json', [source])
    source = json.loads(source)[0]['fields']
    host = source['host']
    username = source['username']
    port = source['port']
    password = source['password']
    database = source['database']

    db=_mysql.connect(
      host=host, 
      port=int(port), 
      user=username, 
      passwd=password, 
      db=database,
      charset='utf8'
    )
    db.query('show tables;')
    tables = db.store_result().fetch_row(maxrows=0, how=2)
    db.close()
    json_data = list(tables[0].values())
    for i, table in enumerate(json_data):
      json_data[i] = {
        'table': table.decode('utf-8'),
        'status': 0
      }


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
    tables = SourceDataTable.objects.get(database=sourceId)
    tables = serializers.serialize('json', [tables])
    tables = json.loads(tables)
    json_data = []
    for table in tables:
      json_data.append(table['fields'])

  except:
    json_data = []


  return JsonResponse({'code': 20000, 'message': 'success', 'data': json_data })
