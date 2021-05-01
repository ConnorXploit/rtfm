$(function() {
    "use strict";
    // Dashboard 1 Morris-chart
    Morris.Area({
        element: 'morris-area-chart',
        data: [{
            period: '2020-09',
            vulnerabilidades: 1840,
            corregidas: 150,
            itouch: 200
        }, {
            period: '2020-10',
            vulnerabilidades: 1300,
            corregidas: 540,
            itouch: 200
        }, {
            period: '2020-11',
            vulnerabilidades: 1143,
            corregidas: 157,
            itouch: 200
        }, {
            period: '2020-12',
            vulnerabilidades: 875,
            corregidas: 269,
            itouch: 200
        }],
        xkey: 'period',
        ykeys: ['vulnerabilidades', 'corregidas'],
        labels: ['Vulnerabilidades', 'Corregidas'],
        pointSize: 0,
        fillOpacity: 0,
        pointStrokeColors: ['#f62d51', '#7460ee', '#009efb'],
        behaveLikeLine: true,
        gridLineColor: '#f6f6f6',
        lineWidth: 1,
        hideHover: 'auto',
        lineColors: ['#009efb', '#7460ee', '#009efb'],
        resize: true
    });

});