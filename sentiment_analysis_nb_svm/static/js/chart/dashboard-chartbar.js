// Memuat data dari atribut data
var chartDataElement = document.getElementById("chartData");
var countEverySentiment = JSON.parse(chartDataElement.dataset.sentiment);

// Mendapatkan total jumlah data
var totalData = Object.values(countEverySentiment).reduce((a, b) => a + b, 0);
document.getElementById('totalData').textContent = totalData;

// Bar Chart Example
var ctx = document.getElementById("myBarChart").getContext('2d');
var myBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: Object.keys(countEverySentiment),
        datasets: [{
            label: "Jumlah Sentimen",
            backgroundColor: ["#198754", "#dc3545"],
            hoverBackgroundColor: ["#198754", "#dc3545"],
            borderColor: "#8E919B",
            data: Object.values(countEverySentiment),
        }],
    },
    options: {
        maintainAspectRatio: false,
        layout: {
            padding: {
                left: 10,
                right: 25,
                top: 25,
                bottom: 0
            }
        },
        scales: {
            xAxes: [{
                gridLines: {
                    display: false,
                    drawBorder: false
                },
                ticks: {
                    maxTicksLimit: 6
                },
            }],
            yAxes: [{
                ticks: {
                    min: 0,
                    maxTicksLimit: 5,
                    padding: 10,
                },
                gridLines: {
                    color: "rgb(142,145,155)",
                    zeroLineColor: "rgb(142,145,155)",
                    drawBorder: false,
                    borderDash: [2],
                    zeroLineBorderDash: [2]
                }
            }],
        },
        legend: {
            display: false
        },
        tooltips: {
            enabled: true,
            callbacks: {
                label: function(tooltipItem, data) {
                    var dataset = data.datasets[tooltipItem.datasetIndex];
                    var currentValue = dataset.data[tooltipItem.index];
                    var percentage = parseFloat((currentValue / totalData * 100).toFixed(1));
                    return currentValue + ' (' + percentage + '%)';
                }
            }
        },
    }
});