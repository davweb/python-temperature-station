google.charts.load('current', {'packages':['gauge','corechart']});
google.charts.setOnLoadCallback(initialise);
window.onresize = drawCharts;

function initialise() {
	loadData();
	drawCharts();
}

function drawCharts() {
	console.log("drawCharts")
	temperatureGauge('daily_min', measurements.daily_min);
	temperatureGauge('daily_max', measurements.daily_max);
	temperatureGauge('weekly_min', measurements.weekly_min);
	temperatureGauge('weekly_max', measurements.weekly_max);
	historyChart('daily_chart', measurements.daily_data)
	historyChart('weekly_chart', measurements.weekly_data)
	waterfallChart('history_chart', measurements.all_data)
}

function temperatureGauge(id, temperature) {
	var data = google.visualization.arrayToDataTable([
		['Label', 'Value'],
		['°C', temperature]
	]);

	var options = {
		min: 12, max: 30,
		yellowFrom: 12, yellowTo: 18, yellowColor: '#33CCFF',
		greenFrom: 18, greenTo: 24,
		redFrom: 24, redTo: 30,
		majorTicks: ['12', '', '', '30'],
		minorTicks: 6
	};

	var element = document.getElementById(id);
	element.innerHTML = "";
	var chart = new google.visualization.Gauge(element);
	chart.draw(data, options);
}

function historyChart(id, data) {
	var options = {
		legend: 'none',
		vAxis: {
			viewWindow: {
				min: 10,
				max: 30
			}
		}
	};

	var element = document.getElementById(id);
	element.innerHTML = "";
	var chart = new google.visualization.LineChart(element);
	chart.draw(data, options);
}

function waterfallChart(id, data) {
	var options = {
		bar: {
			groupWidth: '90%',
		},
		legend: 'none',
		vAxis: {
			viewWindow: {
				min: 10,
				max: 30
			}

		}
	};

	var element = document.getElementById(id);
	element.innerHTML = "";
	var chart = new google.visualization.CandlestickChart(element);
	chart.draw(data, options);
}
