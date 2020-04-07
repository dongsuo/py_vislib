from django.urls import path
from . import views

urlpatterns = [
  path('user/info', views.user, name='userinfo'),
  path('user/signup', views.userSignup, name='signup'),
  path('user/login', views.userLogin, name='login'),
  path('user/logout', views.userLogout, name='logout'),
  path('exesql', views.execSql, name='execSql'),
  path('chart/list', views.chartList, name="chartList"),
  path('chart/create', views.createChart, name="createChart"),
  path('chart/update', views.updateChart, name="updateChart"),
  path('chart/delete', views.deleteChart, name="deleteChart"),
  path('chart/<uuid:chartId>', views.chartDetail, name="chartDetail"),
  path('chartboardmap/boardbychart', views.boardByChart, name="boardByChart"),
  path('dashboard/create', views.createDashboard, name="createDashboard"),
  path('dashboard/update', views.updateDashboard, name="updateDashboard"),
  path('dashboard/delete', views.deleteDashboard, name="deleteDashboard"),
  path('dashboard/<uuid:dashboardId>', views.dashboardDetail, name="dashboardDetail"),
  path('dashboard/list', views.dashboardList, name="dashboardList"),
  path('dashboard/order', views.dashboardOrder, name="dashboardOrder"),
  path('chartboard/map', views.chartBoardMap, name="chartBoardMap"),
  path('chartboard/unmap', views.chartBoardUnmap, name="chartBoardUnmap"),
  path('chartboardmap/chartbydashboard', views.chartByBoard, name="chartByBoard"),
  path('source/list', views.sourceList, name="sourceList"),
  path('source/create', views.createSource, name="createSource"),
  path('source/update', views.updateSource, name="updateSource"),
  path('source/delete', views.deleteSource, name="deleteSource"),
  path('source/<uuid:sourceId>', views.sourceDetail, name="sourceDetail"),

]