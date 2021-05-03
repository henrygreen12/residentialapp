var chart_colors = ["#ffca18","#2eb8f3"]
    var options = {
        series: [{
            name: 'Usage Charges',
            data: [44, 55]
        }, {
            name: 'Delivery Fees',
            data: [53, 32]
        }],
        chart: {
            type: 'bar',
            stacked: true,
            toolbar: {
                show: false
            }
        },
        plotOptions: {
            bar: {
                horizontal: true,
                dataLabels: {
                    position: 'bottom'
                }
            },
        },
        title: {
            text: 'Your Electricity Bill',
            offsetX: 12,
            offsetY: 20,
            style: {
                fontFamily: "montserrat, sans-serif"
            }
        },
        xaxis: {
            categories: ["",""],
            labels: {
                show: true,
                formatter: function (val, opt) {
                    return '$' + val
                }
            }
        },
        fill: {
            opacity: 1
        },
        legend: {
            position: 'bottom',
            horizontalAlign: 'left',
            offsetX: 40
        },
        colors: chart_colors,
        dataLabels: {
            enabled: true,
            textAnchor: 'start',
            style: {
            colors: ['#fff']
            },
            formatter: function (val, opt) {
                console.log(opt.w.globals);
                console.log(opt)
                if (opt.seriesIndex == 0) {
                    if (opt.dataPointIndex == 0) {
                        return "This Utility Plan"
                    } else {
                        return "Your Current Plan"
                    }
                } else {
                    if (opt.dataPointIndex == 0) {
                        return "$ " + this_plan_bill
                    } else {
                        return "$ " + user_plan_bill
                    }
                }
            },
            offsetX: 0,
            dropShadow: {
            enabled: true
            }
        }
    };

  var chart = new ApexCharts(document.querySelector("#chart"), options);
  chart.render();