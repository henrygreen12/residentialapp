function uuidv4() {
  return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, (c) =>
    (
      c ^
      (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))
    ).toString(16)
  )
}

function genHexString(len) {
  let output = ''
  for (let i = 0; i < len; ++i) {
    output += Math.floor(Math.random() * 16).toString(16)
  }
  return output
}

function injectForm(prepend = false) {
  // var uuid = genHexString(12)
  var idNextElement = $('.form-group').length + 1 
  var formTemplate = $('#form-template')
  var fieldSet = formTemplate[0]
  var content = fieldSet.content.cloneNode(true)

  // Add id to fieldset
  $(content)
    .find('.form-group')
    .attr('id', 'group-' + idNextElement)
  // Prepare properties
  var length = 'windows-' + idNextElement + '-length'
  var height = 'windows-' + idNextElement + '-height'
  var location = 'windows-' + idNextElement + '-location'
  var roomType = 'windows-' + idNextElement + '-room_type'
  // find and set properties
  var lengthInput = $(content).find('[name=length]')
  $(lengthInput).attr('name', length)
  var heightInput = $(content).find('[name=height]')
  $(heightInput).attr('name', height)
  var locationInput = $(content).find('[name=location]')
  $(locationInput).attr('name', location)
  var roomTypeInput = $(content).find('[name=room_type]')
  $(roomTypeInput).attr('name', roomType)

  // Add attribute to remove button (makes it easier to target and delete parent)
  $(content)
    .find('button')
    .attr('data-remove', 'group-' + idNextElement)

  prepend === true
    ? $('#dynamic-form').prepend(content)
    : $('#dynamic-form .form-group').last().append(content)
}

function deleteForm(group){
  var formGroupSelected = $('#'+ group).remove()
 }

function updateForm(){
  
}

 

$(document).ready(function () {
  injectForm(true)
  $('#add_field').on('click', function (e) {
    e.preventDefault()
    injectForm()
  })

  $(document).on('click','.remove',function(e){
    e.preventDefault()
    var element = $(this).data('remove')
    deleteForm(element)

  })
 

})



