from django.conf import settings

MONTHLY_CHART = getattr(settings, 'DASHBOARD_MONTHLY_CHART', True)