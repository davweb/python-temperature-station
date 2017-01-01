from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from datetime import datetime, timedelta
from .models import Measurement, DailySummary
from collections import defaultdict
import gviz_api

QUERY_HOURLY_AVERAGE = """
    SELECT
        STRFTIME('%Y-%m-%dT%H:00:00.000', time) AS time,
        AVG(temperature) AS temperature
    FROM dashboard_measurement
    WHERE time > '{:%Y-%m-%d %H:%M}'
    GROUP BY STRFTIME('%Y-%m-%dT%H:00:00.000',time)"""

def index(request):
    context = {
        'latest': Measurement.objects.latest()
    }
    return render(request, 'dashboard/index.html', context)
    
def data(request):
    now = datetime.now(None)
    seven_days_ago = now - timedelta(7)
    one_month_ago = now - timedelta(28)
    last_day = Measurement.objects.filter(time__range=[now - timedelta(1), now])
    last_week = Measurement.objects.filter(time__range=[seven_days_ago, now])
    last_week_averages = Measurement.objects.raw(QUERY_HOURLY_AVERAGE.format(seven_days_ago))
    last_month_averages = Measurement.objects.raw(QUERY_HOURLY_AVERAGE.format(one_month_ago))
    
    daily_data = gviz_api.DataTable(
        [("time", "datetime"), ("temperature", "number")],
        ((measurement.time, float(measurement.temperature)) for measurement in last_day)
    )
    
    weekly_data = gviz_api.DataTable(
        [("time", "datetime"), ("temperature", "number")],
        ((measurement.time, float(measurement.temperature)) for measurement in last_week_averages)
    )

    monthly_data = gviz_api.DataTable(
        [("time", "datetime"), ("temperature", "number")],
        ((measurement.time, float(measurement.temperature)) for measurement in last_month_averages)
    )
    
    all_summary = DailySummary.objects.raw('SELECT DATE(time) AS day, MIN(temperature) AS minimum, MAX(temperature) AS maximum FROM dashboard_measurement GROUP BY DATE(time)')

    all_data = gviz_api.DataTable(
        [("day", "date"), ("min", "number"), ("min_again", "number"), ("max", "number"), ("max_again", "number")],
        ([summary.day, summary.minimum, summary.minimum, summary.maximum, summary.maximum] for summary in all_summary)
    )
        
    context = {
        'latest': Measurement.objects.latest(),
        'daily_min': last_day.earliest('temperature'),
        'daily_max': last_day.latest('temperature'),
        'weekly_min': last_week.earliest('temperature'),
        'weekly_max': last_week.latest('temperature'),
        'daily_data': daily_data.ToJSCode("daily_data", columns_order=("time", "temperature"), order_by="time"),
        'weekly_data': weekly_data.ToJSCode("weekly_data", columns_order=("time", "temperature"), order_by="time"),
        'monthly_data': monthly_data.ToJSCode("monthly_data", columns_order=("time", "temperature"), order_by="time"),
        'all_data': all_data.ToJSCode("all_data", columns_order=("day", "min", "min_again", "max", "max_again"), order_by="day")
    }
        
    return render(request, 'dashboard/data.js', context)
