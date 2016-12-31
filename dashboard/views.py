from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from datetime import datetime, timedelta
from .models import Measurement
from collections import defaultdict
import gviz_api

def index(request):
    context = {
        'latest': Measurement.objects.latest()
    }
    return render(request, 'dashboard/index.html', context)
    
def data(request):
    now = datetime.now()
    last_day = Measurement.objects.filter(time__range=[now - timedelta(1), now])
    last_week = Measurement.objects.filter(time__range=[now - timedelta(7), now])
    all_measurements = Measurement.objects.all()
    
    daily_data = gviz_api.DataTable([
        ("time", "datetime"),
        ("temperature", "number")
    ])
    daily_data.LoadData((measurement.time, float(measurement.temperature)) for measurement in last_day)
    
    weekly_data = gviz_api.DataTable([
        ("time", "datetime"),
        ("temperature", "number")
    ])
    weekly_data.LoadData((measurement.time, float(measurement.temperature)) for measurement in last_week)
    
    all_summary = defaultdict(lambda: { "min": 1000, "max": -1000 })
    
    for measurement in all_measurements:
        date = measurement.time.date()
        summary = all_summary[date]
        summary['min'] = min(summary['min'], measurement.temperature)
        summary['max'] = max(summary['max'], measurement.temperature)
    
    all_rows = []
    
    for date in all_summary.keys():
        summary = all_summary[date]
        all_rows.append([date, float(summary['min']), float(summary['min']), float(summary['max']), float(summary['max'])])
    
    all_data = gviz_api.DataTable([
        ("day", "date"),
        ("min", "number"),
        ("min_again", "number"),
        ("max", "number"),
        ("max_again", "number")
    ])
    all_data.LoadData(all_rows)
    
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
    return render(request, 'dashboard/data.js', context)
