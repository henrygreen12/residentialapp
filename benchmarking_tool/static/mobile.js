
/*=====    Chart    ==========================================================*/
var colors = [
  '#636363',
  '#236623',
  '#349134',
  '#29ba29',
  '#13e813'
]

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

var options_rates = {
  series: [{
    // data: [21, 22, 10, 28, 16]
    data: all_bills
  }],
  title: {
    text: 'Best Rates in ' + capitalize(_city),
    align: 'center',
    offsetY: 50,
    style: {
      fontSize: '20px',
      fontFamily: 'calibri, sans serif'
    }
  },
  chart: {
  height: 350,
  type: 'bar',
  events: {
    click: undefined/*function(chart, w, e) {,
      style: {
      fontSize: '20px',
    }
      // console.log(chart, w, e)
    }*/
  },
  toolbar: {
    show: false
  }
},
colors: colors,
plotOptions: {
  bar: {
    // columnWidth: '45%',
    distributed: true,
    dataLabels: {
      position: 'top'
    }
  }
},
datalabels: {
  enabled: true,
  offsetY: -20,
  style: {
    colors: ["#4f4f4f"]
  },
  formatter: function(val) {
    return "$ " + val
  }
},
states: {
  hover: {
    filter: {
      type: 'none'
    }
  }
},
legend: {
  show: false
},
grid: {
  show: false
},
xaxis: {
  categories: rates_retailers,
  labels: {
    show: false
  },
  axisTicks: {
    show: false
  }
},
yaxis: {
    title: {
        text: "Utility Cost",
        style: {
          color: '#4f4f4f',
          fontWeight: 400
        },
        offsetX: 8
    },
    labels: {
      show: false
    }
}
};

var chart_rates = new ApexCharts(document.querySelector("#chart_rates"), options_rates);
chart_rates.render();
/*============================================================================*/

// init the values for the financial summary
var total_cost = 0;
var total_savings = 0;
$(".upgrade_card").each(function() {
  if ($(this).find(".u_cb").attr('checked')){
    total_cost += parseFloat($(this).find("._upgrade_cost").val());
    total_savings += parseFloat($(this).find("._upgrade_savings").val());
  }
});
var total_payback = (Math.ceil(total_cost / total_savings)) || 0;
$("#cost_data").val(total_cost);
$("#savings_data").val(total_savings);
$("#payback_data").val(total_payback);
updateFinancialSummary();

$(".upgrade_card").click(function () {
  $(this).toggleClass("active_upgrade");

  card_cost = parseFloat($(this).find("._upgrade_cost").attr("value"));
  card_savings = parseFloat($(this).find("._upgrade_savings").attr("value"));

  var mult = ($(this).hasClass("active_upgrade")) ? 1 : -1;

  var updated_total_cost = parseFloat($("#cost_data").val()) + parseFloat(mult * card_cost);
  $("#cost_data").val(updated_total_cost);

  var updated_total_savings = parseFloat($("#savings_data").val()) + mult * card_savings;
  $("#savings_data").val(updated_total_savings);

  var updated_total_payback = (Math.ceil(updated_total_cost / updated_total_savings)) || 0;
  $("#payback_data").val(updated_total_payback);

  updateFinancialSummary()

  // switch out the class of the e_rates cards?
});

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrf_token);
        }
    }
});

$(".u_cb").click(function () {
  var parent = $(this).parent().parent().parent().parent(); // there has to be a better way
  card_cost = parseFloat(parent.find("._upgrade_cost").attr("value"));
  card_savings = parseFloat(parent.find("._upgrade_savings").attr("value"));

  var mult = ($(this).is(':checked')) ? 1 : -1;

  var updated_total_cost = parseFloat($("#cost_data").val()) + parseFloat(mult * card_cost);
  $("#cost_data").val(updated_total_cost);

  var updated_total_savings = parseFloat($("#savings_data").val()) + mult * card_savings;
  $("#savings_data").val(updated_total_savings);

  var updated_total_payback = (Math.ceil(updated_total_cost / updated_total_savings)) || 0;
  $("#payback_data").val(updated_total_payback);

  updateFinancialSummary();

  var _id = parent.find(".card_id").val();
  console.log($(this).is(":checked"));
  $.ajax({
    data : {
      card_id : _id,
      checked : $(this).is(":checked")
    },
    type : 'POST',
    url : "/bg_upgrade_package_append/"
  });
});

// https://stackoverflow.com/questions/149055/how-to-format-numbers-as-currency-string -- 16-Dec-2020
function formatMoney(number, decPlaces, decSep, thouSep) {
  decPlaces = isNaN(decPlaces = Math.abs(decPlaces)) ? 2 : decPlaces,
  decSep = typeof decSep === "undefined" ? "." : decSep;
  thouSep = typeof thouSep === "undefined" ? "," : thouSep;
  var sign = number < 0 ? "-" : "";
  var i = String(parseInt(number = Math.abs(Number(number) || 0).toFixed(decPlaces)));
  var j = (j = i.length) > 3 ? j % 3 : 0;

  return sign +
  	(j ? i.substr(0, j) + thouSep : "") +
  	i.substr(j).replace(/(\decSep{3})(?=\decSep)/g, "$1" + thouSep) +
  	(decPlaces ? decSep + Math.abs(number - i).toFixed(decPlaces).slice(2) : "");
}

function updateFinancialSummary() {
  $("#cost_display").html("$ " + formatMoney($("#cost_data").val()));
  $("#savings_display").html("$ " + formatMoney($("#savings_data").val()));
  $("#payback_display").html($("#payback_data").val() + " mos");
}
