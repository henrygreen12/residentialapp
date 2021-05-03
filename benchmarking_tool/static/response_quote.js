$(document).ready(function(){
	var btnQuote = $('.btn-see-quote')

	btnQuote.click(function() {
		// get data-id du button cliqué
		var dataId = $(this).attr('data-id')
		
		// load dans modalbody "/respond_quote/id" dans le #container-fluid
		$('.modal-body').load("respond_quote/"+dataId+"/ .container-fluid")

	});

	
})