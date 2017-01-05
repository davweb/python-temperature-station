from django.shortcuts import render
from datetime import datetime, timedelta
from .models import Measurement, DailySummary
import gviz_api
from dashboard_settings import MONTHLY_CHART

QUERY_DAILY_SUMMARY = """
    SELECT
        DATE(time) AS day,
        MIN(temperature) AS minimum,
        MAX(temperature) AS maximum
    FROM dashboard_measurement
    GROUP BY DATE(time)"""
QUERY_HOURLY_AVERAGE = """
    SELECT
        STRFTIME('%%Y-%%m-%%dT%%H:00:00.000', time) AS time,
        AVG(temperature) AS temperature
    FROM dashboard_measurement
    WHERE time > %s
    GROUP BY STRFTIME('%%Y-%%m-%%dT%%H:00:00.000',time)"""

def index(request):
    context = {
        'latest': Measurement.objects.latest(),
        'monthly_chart': MONTHLY_CHART
    }
    return render(request, 'dashboard/index.html', context)
        
def data(request):
    now = datetime.now()
    yesterday = now - timedelta(1)
    seven_days_ago = now - timedelta(7)
    one_month_ago = now - timedelta(28)
    last_day = Measurement.objects.filter(time__gte = yesterday)
    last_week = Measurement.objects.filter(time__gte = seven_days_ago)
    last_week_averages = Measurement.objects.raw(QUERY_HOURLY_AVERAGE, [seven_days_ago])
    
    daily_data = gviz_api.DataTable(
        [("time", "datetime"), ("temperature", "number")],
        ((measurement.time, float(measurement.temperature)) for measurement in last_day)
    )
    
    weekly_data = gviz_api.DataTable(
        [("time", "datetime"), ("temperature", "number")],
        ((measurement.time, float(measurement.temperature)) for measurement in last_week_averages)
    )

    if MONTHLY_CHART:
        last_month_averages = Measurement.objects.raw(QUERY_HOURLY_AVERAGE, [one_month_ago])
        monthly_data = gviz_api.DataTable(
            [("time", "datetime"), ("temperature", "number")],
            ((measurement.time, float(measurement.temperature)) for measurement in last_month_averages)
            )
    
    all_summary = DailySummary.objects.raw(QUERY_DAILY_SUMMARY)

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
        'all_data': all_data.ToJSCode("all_data", columns_order=("day", "min", "min_again", "max", "max_again"), order_by="day")
    }
        
    if MONTHLY_CHART:
        context['monthly_data'] = monthly_data.ToJSCode("monthly_data", columns_order=("time", "temperature"), order_by="time");    
        
    return render(request, 'dashboard/data.js', context)
