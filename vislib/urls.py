from django.urls import path
from .views import user, chart, dashboard, views, source

urlpatterns = [
    path('user/info', user.userInfo, name='userinfo'),
    path('user/signup', user.userSignup, name='signup'),
    path('user/login', user.userLogin, name='login'),
    path('user/logout', user.userLogout, name='logout'),

    path('exesql', views.execSql, name='execSql'),

    path('chart/list', chart.chartList, name="chartList"),
    path('chart/create', chart.createChart, name="createChart"),
    path('chart/update', chart.updateChart, name="updateChart"),
    path('chart/delete', chart.deleteChart, name="deleteChart"),
    path('chart/<uuid:chartId>', chart.chartDetail, name="chartDetail"),

    path('chartboardmap/boardbychart', dashboard.boardByChart, name="boardByChart"),
    path('dashboard/create', dashboard.createDashboard, name="createDashboard"),
    path('dashboard/update', dashboard.updateDashboard, name="updateDashboard"),
    path('dashboard/delete', dashboard.deleteDashboard, name="deleteDashboard"),
    path('dashboard/<uuid:dashboardId>', dashboard.dashboardDetail, name="dashboardDetail"),
    path('dashboard/list', dashboard.dashboardList, name="dashboardList"),
    path('dashboard/order', dashboard.dashboardOrder, name="dashboardOrder"),
    path('chartboard/map', dashboard.chartBoardMap, name="chartBoardMap"),
    path('chartboard/unmap', dashboard.chartBoardUnmap, name="chartBoardUnmap"),
    path('chartboardmap/chartbydashboard', dashboard.chartByBoard, name="chartByBoard"),

    path('source/list', source.sourceList, name="sourceList"),
    path('source/create', source.createSource, name="createSource"),
    path('source/update', source.updateSource, name="updateSource"),
    path('source/delete', source.deleteSource, name="deleteSource"),
    path('source/<uuid:sourceId>', source.sourceDetail, name="sourceDetail"),
    path('source/tables/<uuid:sourceId>', source.sourceTables, name="sourceTables"),
    path('source/tables/save', source.sourceTableSave, name="sourceTableSave"),
    path('source/tables/<uuid:sourceId>/linked', source.sourceLinkedTables, name="sourceLinkedTables"),
]
