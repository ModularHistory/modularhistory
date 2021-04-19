/* eslint-disable no-undef */
/* eslint-disable no-mixed-spaces-and-tabs */
function cardTypeChange(card) {
	$("#cardform").removeClass().addClass(card.type);
	$('#card-image').removeClass().addClass(card.type);
	// $("#button-pay")
	$('header').addClass('header-slide');
}
$(document).ready(function() {
  $("#credit-card-number").on("keyup", function() {
	alert("OK");
  })
  $.ajax({
	headers: { "Access-Control-Allow-Origin": "*" },
	type: "get", 
	url: "http://localhost:5000/token",
	success: function(token) {
	  console.log(token);
	  // eslint-disable-next-line no-undef
	  braintree.setup(token, "custom", {
		id: "cardform",
		hostedFields: {
		  number: {
			selector: "#card-number",
			placeholder: "Card Number"
		  },
		  cvv: {
			selector: "#card-cvv",
			placeholder: "CVV"
		  },
		  expirationDate: {
			selector: "#card-exp",
			placeholder: "Exp Date"
		  },
		styles: {
		  "input": {
			"font-size": "13pt",
			"color": "#ffffff"
		  },
		  ".number": {
			"font-family": "monospace"
		  },
		  ":focus": {
			"color": "blue"
		  },
		  ".valid": {
			"color": "green"
		  },
		  ".invalid": {
			"color": "red"
		  },
		},
		onFieldEvent: function (event) {
			if(event.isValid){
			  if(event.target['fieldKey']==="number"){
				cardTypeChange(event.card);
			  }else{
				// catchange(event.target['fieldKey']+'.jpg');
			  }
			}
			else if(event.type === "blur"){
			  // catchange(event.target['fieldKey']+'-no.jpg');
			}
			jQuery('.litterbox').text("Target: "+event.target['fieldKey']+"\nEvent: "+event.type+'\nValid: '+event.isValid);
		  }
		}
	  });
	}
  })
})