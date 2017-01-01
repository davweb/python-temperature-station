function loadData() {
	{{ daily_data|safe }}
	{{ weekly_data|safe }}
	{{ monthly_data|safe }}
    {{ all_data|safe }}
	window.measurements = {
		daily_min: {{ daily_min.temperature }},
		daily_max: {{ daily_max.temperature }},
		weekly_min: {{ weekly_min.temperature }},
		weekly_max: {{ weekly_max.temperature }},
		daily_data: daily_data,
		weekly_data: weekly_data,
		monthly_data: monthly_data,
		all_data: all_data
	}
}
