// ==== Energy Breakdown Chart =================================================
var options_energy_breakdown = {
    series: [44, 55, 41, 17, 15],
    chart: {
      type: 'donut',
    },
    responsive: [{
      breakpoint: 480,
      options: {
          chart: {
            width: "100%"
          },
        legend: {
          position: 'right'
        },
        dataLabels: {
          enabled: false
        }
      }
    }]
};

var chart = new ApexCharts(document.querySelector("#chart_energy_breakdown"), options_energy_breakdown);
chart.render();
