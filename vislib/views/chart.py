import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from vislib.models import Chart, SourceDataBase
from django.utils import timezone
import uuid

def default_datetime():
    now = timezone.now()
    return now

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
  source_id = SourceDataBase.objects.get(source_id=body['source_id'])
  creator = request.user
  chart_id = uuid.uuid4()
  Chart.objects.create(
    chart_id=chart_id,
    source_id=source_id,
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
  chart.source_id = SourceDataBase.objects.get(source_id=body['source_id'])
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
