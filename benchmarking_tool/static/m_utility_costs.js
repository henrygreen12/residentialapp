$(".e_rate_card").click(function () {
  var _id = parseFloat($(this).find(".rate_id").val());
  $("#redirect_id").val(_id)
  document.getElementById("rate_details").submit();
});