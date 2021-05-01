$(document).ready(function(){
    $.ajax({
        type: "GET",
        url: "/vulnerabilidades",
        success: function(data) {
            var ctxL = document.getElementById("graficoVulnerabilidades").getContext('2d');
            var myLineChart = new Chart(ctxL, {
                type: 'line',
                data: {
                    labels: data.nombresMeses,
                    datasets: data.valores
                },
                options: {
                    responsive: true
                },
                animation : {
                    duration: 3000
                }
            });
        }
    });
    $.ajax({
        type: "GET",
        url: "/estadistica",
        success: function(data) {
            var ctxB = document.getElementById("graficoEscaneos").getContext('2d');
            var myBarChart = new Chart(ctxB, {
                type: 'bar',
                data: {
                    labels: ["Crítico", "Alto", "Medio", "Bajo", "Info"],
                    datasets: [{
                        label: 'Vulnerabilidades Criticas',
                        data: data,
                        backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)'
                        ],
                        borderColor: [
                        'rgba(255,99,132,1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true
                            }
                        }]
                    },
                    animation : {
                        duration: 3000
                    }
                }
            });
        }
    });
});