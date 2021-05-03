// functions for  Register.html

function validatePersonal(fieldset, callback) {
  var inputs = $(fieldset).find("input[required]");
  var password = $('input[name=password]');
  var confirm_password = $('input[name=confirm_password]');
  var validated = _.map(inputs, function (input) {
    return input.checkValidity();
  });
  var isInvalid = _.includes(validated, false);
  if (isInvalid) {
    _.each(_.reverse(inputs), function (input) {
      input.reportValidity();
    });
    return false;
  } else if (password.val() !== confirm_password.val()){
    // Check Password
    confirm_password[0].setCustomValidity("Password confirmation doesn't match, please change it!");
    confirm_password[0].reportValidity();
  }
  else {
    callback();
  }
}

function validateLocation(fieldset, callback) {
  var inputs = $(fieldset).find("input[required]")
  
  var validated = _.map(inputs, function (input) {
    return input.checkValidity();
  });
  var isInvalid = _.includes(validated, false);
  if (isInvalid) {
    _.each(_.reverse(inputs), function (input) {
      input.reportValidity();
    });
    return false;
  }
  else {
    callback();
  }
}
function validateSecret(fieldset,callback){
  // check secret code

  var gas_photo_bill = $('input[name=gas_photo_bill]')
  var electrical_photo_bill = $('input[name=electrical_photo_bill]')
  gas_photo_bill.prop('required',false);
  electrical_photo_bill.prop('required',false);
  var secret_code = $('input[name=secret_code]')

  if (secret_code.val() === ""){
    callback();
  }
  else {
    var csrf_token = $('#csrf_token').val();
    $.ajax({
      type: 'POST',
      url: '/accounts/check_code',
      headers: {
        "X-CSRFToken": csrf_token,
      },
      data: {
        secret_code: secret_code.val(),
      }
    }).done(function(data){
      var success = data["success"];
      console.log(success);
      if (success) {
        callback();
      } else {
        alert("Secret code is wrong");
        return false;
      }
    })
  }
}

function validateGas(fieldset, callback) {

  var address_input = $('#gas .address_input')
  var address_found = $('#gas .address_found')
  var button_yes = $('#gas .button_yes')
  var button_no = $('#gas .button_no')

  button_yes.click(function(){
    callback();
  })
  button_no.click(function(){
    alert('Please check your picture')
  })

  var secret_code = $('input[name=secret_code]')
  if (secret_code.val() === ""){
    var gas_photo_bill = $('input[name=gas_photo_bill]')
    if (gas_photo_bill.val() === "") {
      gas_photo_bill.prop('required',true);
      gas_photo_bill[0].reportValidity();
      return false;
    }
    else{
      var csrf_token = $('#csrf_token').val()
      var gas_picture = gas_photo_bill.prop('files')[0]
      var form_data = new FormData()
      form_data.append('gas_photo_bill', gas_picture)
      $.ajax({
        type: 'POST',
        url: '/accounts/check_address',
        headers: {
          "X-CSRFToken": csrf_token,
        },
        data: form_data,
        processData: false, // tell jQuery not to process the data
        contentType: false, // tell jQuery not to set contentType
      }).done(function(data){
        var success = data['success']
        if (success){
          $('input[name=gas_address]').val(data['address'])
          address_found.html('Is it your address ? : ' + data['address'])
          address_input.show();
        }
        else {
          alert("Please check your picture");
          return false;
        }
      })
      return false;
    }
  }
  callback();
}

function validateElectrical(fieldset, callback) {
  var address_input = $('#electrical .address_input')
  var address_found = $('#electrical .address_found')
  var button_yes = $('#electrical .button_yes')
  var button_no = $('#electrical .button_no')

  button_yes.click(function(){
    callback();
  })
  button_no.click(function(){
    alert('Please check your picture')
  })


  var secret_code = $('input[name=secret_code]')
  if (secret_code.val() === ""){
    var electrical_photo_bill = $('input[name=electrical_photo_bill]')
    if (electrical_photo_bill.val() === "") {
      electrical_photo_bill.prop('required',true);
      electrical_photo_bill[0].reportValidity();
      return false;
    }
    else{
      var csrf_token = $('#csrf_token').val()
      var electrical_picture = electrical_photo_bill.prop('files')[0]
      var form_data = new FormData()
      form_data.append('electrical_photo_bill', electrical_picture)
      $.ajax({
        type: 'POST',
        url: '/accounts/check_address',
        headers: {
          "X-CSRFToken": csrf_token,
        },
        data: form_data,
        processData: false, // tell jQuery not to process the data
        contentType: false, // tell jQuery not to set contentType
      }).done(function(data){
        var success = data['success']
        if (success){
          $('input[name=electrical_address]').val(data['address'])
          address_found.html('Is it your address ? : ' + data['address'])
          address_input.show();
        }
        else {
          alert("Please check your picture");
          return false;
        }
      })
      return false;
    }
  }
  callback();
}


//functions for survey.html

function validatePhone(fieldset, callback) {
  var inputs = $(fieldset).find("input[required]");
  var validated = _.map(inputs, function (input) {
    return input.checkValidity();
  });
  var isInvalid = _.includes(validated, false);
  if (isInvalid) {
    _.each(_.reverse(inputs), function (input) {
      input.reportValidity();
    });
    return false;
  }
  else {
    callback();
  }
}

// functions for diyAudit.html

function validateHouse(fieldset, callback) {
  var inputs = $(fieldset).find("input[required]");
  var validated = _.map(inputs, function (input) {
    return input.checkValidity();
  });
  var isInvalid = _.includes(validated, false);
  if (isInvalid) {
    _.each(_.reverse(inputs), function (input) {
      input.reportValidity();
    });
    return false;
  }
  else {
    callback();
  }
}

function validateWaterHeating(fieldset,callback){
  var inputs = $(fieldset).find("input[required]");
  var validated = _.map(inputs, function (input) {
    return input.checkValidity();
  });
  var isInvalid = _.includes(validated, false);
  if (isInvalid) {
    _.each(_.reverse(inputs), function (input) {
      input.reportValidity();
    });
    return false;
  }
  else {
    callback();
  }
}

function validateCode(fieldset,callback){
  var code =  $('input[name=code]')
  console.log(code)
  var csrf_token = $('#csrf_token').val();
  $.ajax({
    type:'POST',
    url:'/fitters/check_company',
    headers: {
      "X-CSRFToken": csrf_token,
    },
    data: {
      code: code.val(),
    }
  }).done(function(data){
    var success = data['success'];
    console.log(success);
    if (success){
      callback();
    } else {
      alert("The code of the company you entered is wrong");
      return false
    }
  })
}

validationFn = {
  Personal: validatePersonal,
  Location : validateLocation,
  Secret : validateSecret,
  Gas : validateGas,
  Electrical : validateElectrical,
  Phone : validatePhone,
  House : validateHouse,
  WaterHeating : validateWaterHeating,
  Code : validateCode,
};

$(document).ready(function () {
  var current_fs, next_fs, previous_fs; //fieldsets
  var opacity;


  $(".next").click(function () {
    current_fs = $(this).parent();
    next_fs = $(this).parent().next();
    fieldsetSection = current_fs.data()["name"];
    console.log(fieldsetSection)

    if (fieldsetSection !== undefined) {
      validationFn[fieldsetSection](current_fs, function () {
        $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

        //show the next fieldset
        next_fs.show();
        //hide the current fieldset with style
        current_fs.animate(
          { opacity: 0 },
          {
            step: function (now) {
              // for making fielset appear animation
              opacity = 1 - now;

              current_fs.css({
                display: "none",
                position: "relative",
              });
              next_fs.css({ opacity: opacity });
            },
            duration: 600,
          }
        );
      });
    }

    //Add Class Active
    else {
      $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");
       //show the next fieldset
       next_fs.show();
       //hide the current fieldset with style
       current_fs.animate(
         { opacity: 0 },
         {
           step: function (now) {
             // for making fielset appear animation
             opacity = 1 - now;

             current_fs.css({
               display: "none",
               position: "relative",
             });
             next_fs.css({ opacity: opacity });
           },
           duration: 600,
         }
       );
    }
  });

  $(".previous").click(function () {
    current_fs = $(this).parent();
    previous_fs = $(this).parent().prev();

    //Remove class active
    $("#progressbar li")
      .eq($("fieldset").index(current_fs))
      .removeClass("active");

    //show the previous fieldset
    previous_fs.show();

    //hide the current fieldset with style
    current_fs.animate(
      { opacity: 0 },
      {
        step: function (now) {
          // for making fielset appear animation
          opacity = 1 - now;

          current_fs.css({
            display: "none",
            position: "relative",
          });
          previous_fs.css({ opacity: opacity });
        },
        duration: 600,
      }
    );
  });

  $(".radio-group .radio").click(function () {
    $(this).parent().find(".radio").removeClass("selected");
    $(this).addClass("selected");
  });

  $(".submit").click(function () {
    return false;
  });
});


if ('serviceWorker' in navigator) {
  navigator.serviceWorker
    .register("/sw.js")
    .then(registration => {
      console.log("ServiceWorker running");
    })
    .catch(err => {
       console.log(err);
    })
}

