import json
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from MySQLdb import _mysql
from django.core import serializers
from vislib.models import Chart, Dashboard, ChartBoardMap, BoardOrder
from django.utils import timezone
import uuid
# Create your views here.

def default_datetime():
    now = timezone.now()
    return now

def index(request):
  return HttpResponse('hello python and django')

@csrf_exempt
def user(request):
  if request.user.is_authenticated:
    username = request.user.get_username()
    return JsonResponse({'code': 20000, 'data': {'username': username}})
  else:
    return JsonResponse({'code': 40000, 'message': 'Please login'})

@csrf_exempt
def userSignup(request):
  body = json.loads(request.body)
  if User.objects.filter(username=body['userName']).exists():
    return JsonResponse({'code': 10000, 'message': 'User Name ' +  body['userName'] + ' is Already Tabken.'})
  if User.objects.filter(email=body['email']).exists():
    return JsonResponse({'code': 10000, 'message': 'Email ' +  body['emaul'] + ' is Registered.'})
  user = User.objects.create_user(body['userName'], body['email'], body['password'])
  user.first_name=body['userName']
  user.save()
  return JsonResponse({'code': 20000, 'message': 'success'})

@csrf_exempt
def userLogin(request):
  body = json.loads(request.body)
  user = authenticate(request, username=body['userName'], password=body['password'])
  if user is not None:
    login(request, user)
    return JsonResponse({'code': 20000, 'message': 'success'})
  else:
    return JsonResponse({'code': 10000, 'message': 'Name or Password Not Correct, Please Try Again.'})

@csrf_exempt
def userLogout(request):
  logout(request)
  return JsonResponse({'code': 20000, 'message': 'success'})

def execSql(request):
  db=_mysql.connect( "127.0.0.1", "root", "123456xxf", "sql12298540", charset='utf8')
  db.query(request.GET['sql'])
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

@csrf_exempt
def chartList(request):
  charts = Chart.objects.filter(creator=request.user)
  charts = serializers.serialize('json', charts)
  charts = json.loads(charts)
  chartArr = []
  for chart in charts:
    chart['fields']['chart_id'] = chart['pk']
    chartArr.append(chart['fields'])
  return JsonResponse({'code': 20000, 'data': chartArr})

@csrf_exempt
def createChart(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  chart_name = body['chart_name']
  desc = body.get('desc', None)
  content = body['content']
  creator = request.user
  chart_id = uuid.uuid4()
  Chart.objects.create(
    chart_id=chart_id,
    chart_name=chart_name,
    desc=desc,
    content=json.dumps(content),
    creator=creator,
    is_private=True,
    status=1,
    updated_at=default_datetime()
  )
  return JsonResponse({'code': 20000, 'message': 'success', 'data': {'id': chart_id}})

@csrf_exempt
def updateChart(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  chart = Chart.objects.get(chart_id=body['id'])
  chart.chart_name = body['chart_name']
  chart.desc = body['desc']
  chart.content = json.dumps(body['content'])
  chart.updated_at = default_datetime()
  chart.save()
  return JsonResponse({'code': 20000, 'message': 'success', 'data': {'id': body['id']}})

@csrf_exempt
def deleteChart(request):
  body_unicode = request.body.decode('utf-8')
  body = json.loads(body_unicode)
  chart = Chart.objects.get(chart_id=body['chart_id'])
  chart.delete()
  return JsonResponse({'code': 20000, 'message': 'success'})

@csrf_exempt
def chartDetail(request, chartId):
  chartDetail = Chart.objects.get(chart_id=chartId)
  chartDetail = serializers.serialize('json', [chartDetail])
  chartDetail = json.loads(chartDetail)[0]

  return JsonResponse({'code': 20000, 'message': 'success', 'data':chartDetail['fields'] })

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
