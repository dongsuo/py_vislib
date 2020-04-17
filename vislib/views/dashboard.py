import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from vislib.models import Chart, Dashboard, ChartBoardMap, BoardOrder
from django.utils import timezone
import uuid

def default_datetime():
    now = timezone.now()
    return now

@csrf_exempt
def createDashboard(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  name = body['name']
  desc = body.get('desc', '')
  content = body.get('content', '')
  creator = request.user
  dashboard_id = uuid.uuid4()

  Dashboard.objects.create(
    dashboard_id=dashboard_id,
    name=name,
    desc=desc,
    content=json.dumps(body.get('content', {})),
    creator=creator,
    is_private=True,
    status=1,
    updated_at=default_datetime()
  )
  return JsonResponse({'code': 20000, 'message': 'success', 'data': {'id': dashboard_id}})

@csrf_exempt
def updateDashboard(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  dashboard_id = body.get('dashboard_id')
  board = Dashboard.objects.get(dashboard_id=dashboard_id)
  board.name = body['name']
  board.desc = body.get('desc', '')
  board.content = json.dumps(body.get('content', {}))
  board.updated_at = default_datetime()
  board.save()
  return JsonResponse({'code': 20000, 'message': 'success', 'data': {'id': dashboard_id}})

@csrf_exempt
def dashboardDetail(request, dashboardId):
  dashboard = Dashboard.objects.get(dashboard_id= dashboardId)
  dashboard = serializers.serialize('json',[dashboard])
  dashboard = json.loads(dashboard)[0]
  dashboard['fields']['dashboard_id'] = dashboardId
  return JsonResponse({'code': 20000, 'message': 'success', 'data': dashboard['fields']})

@csrf_exempt
def deleteDashboard(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  dashboard = Dashboard.objects.get(dashboard_id=body['dashboard_id'])
  dashboard.delete()
  return JsonResponse({'code': 20000, 'message': 'success'})

@csrf_exempt
def dashboardList(request):
  dashboards = Dashboard.objects.filter(creator=request.user)
  dashboards = serializers.serialize('json', dashboards)
  dashboards = json.loads(dashboards)
  dbArr = []
  for db in dashboards:
    db['fields']['dashboard_id'] = db['pk']
    db['fields']['content'] = json.loads(db['fields']['content'])
    dbArr.append(db['fields'])
  order = BoardOrder.objects.filter(creator=request.user)
  order = json.loads(serializers.serialize('json', order))
  if len(order)!=0:
    order = order[0]
    order = order['fields']['order']
    order = order.split('|')
  else:
    order = []
  return JsonResponse({'code': 20000, 'message': 'success', 'data':{'dashboards': dbArr, 'order': order} })

@csrf_exempt
def chartBoardMap(request):
  body = request.body.decode('utf-8')
  body = json.loads(body)
  dashboard = Dashboard.objects.get(dashboard_id=body['dashboard_id'])
  chart = Chart.objects.get(chart_id=body['chart_id'])

  ChartBoardMap.objects.create(
    id=uuid.uuid4(),
    chart=chart,
    dashboard=dashboard,
    updated_at=default_datetime()
  )
  return JsonResponse({'code': 20000, 'message': 'success'})

@csrf_exempt
def chartBoardUnmap(request):
  body = request.body.decode('utf-8')
  body = json.loads(body)
  chart_id = body['chart_id']
  dashboard_id = body['dashboard_id']
  map = ChartBoardMap.objects.get(chart=chart_id, dashboard=dashboard_id)
  map.delete()
  return JsonResponse({'code': 20000, 'message': 'success'})

@csrf_exempt
def chartByBoard(request):
  map = ChartBoardMap.objects.filter(dashboard=request.GET['dashboard_id'])
  charts = []
  for item in map:
    chart = serializers.serialize('json', [item.chart])
    chart = json.loads(chart)[0]
    chart['fields']['chart_id'] = chart['pk']
    charts.append(chart['fields'])

  return JsonResponse({'code': 20000, 'message': 'success', 'data': charts})

@csrf_exempt
def boardByChart(request):
  map = ChartBoardMap.objects.filter(chart=request.GET['chart_id'])
  boards = []
  for item in map:
    board = serializers.serialize('json', [item.dashboard])
    board = json.loads(board)[0]
    board['fields']['dashboard_id'] = board['pk']
    boards.append(board['fields'])
  return JsonResponse({'code': 20000, 'message': 'success', 'data': boards})

@csrf_exempt
def dashboardOrder(request):
  body = json.loads(request.body)
  split = '|'
  orderStr = split.join(body['order'])
  order = BoardOrder.objects.filter(creator=request.user)
  if order:
    order[0].order = orderStr
    order[0].save()
  else:
    BoardOrder.objects.create(
      order=orderStr,
      id=uuid.uuid4(),
      creator=request.user,
      updated_at=default_datetime()
    )
  return JsonResponse({'code': 20000, 'message': 'success'})
