async function sendForm(url = '', data = {}, token, method='POST', sendFile=false
) {
	let jsonResponse;
	try {
		let config = {
			method: method, headers: {
				'X-CSRFToken': token,
			}, body:data
		}
		if(!sendFile){
			config.headers['Content-Type'] = "application/x-www-form-urlencoded";
			config.mode = 'cors';
			config.cache ='no-cache';
			config.credentials = 'same-origin';
			config.redirect = 'follow';
			config.referrerPolicy = 'no-referrer';
		}
		const response = await fetch(url, config);

		jsonResponse = await response.json();

		if (response.ok) {
			return jsonResponse
		}

		if (response.status === 400){
			( {message, data} = jsonResponse);
			if( message.description !== 'Validation'){
				notification(message.description, message.type);
			} else {
				let content = '';
				Object.entries(data.fields).forEach(([key, value])=>{
					content=`${key}: ${value}`;
					let element = $('input[name='+key+']');
					if(element.length){
						element.addClass('is-invalid');
					}else{
						$('select[name='+key+']').addClass('is-invalid');
					}
					notification(content, 'warning');
				});
			}
			throw (jsonResponse);
		}

		if(response.status === 500){
			notification(jsonResponse.message.description, jsonResponse.message.type);
		}
	} catch (jsonResponse) {
		throw jsonResponse;
	}
}

async function postData(url = '', data = {}, token) {
	const response = await fetch(url,{
		method: 'POST',
		mode: 'cors',
		cache: 'no-cache',
		credentials: 'same-origin',
		headers: {
			'X-CSRFToken': token
		},
		redirect: 'follow',
		referrerPolicy: 'no-referrer',
		body: JSON.stringify(data)
	});
	return response.json();
};

function RequestPost(form,url,reload){
   $.ajax({
   		url:url,
   		dataType: "json",
   		type:"POST",
   		data:form,
   		beforeSend: function(){
   			HoldOn.open({ message: "Please wait"});
   		},
   		success: function(response, status){
   		    HoldOn.close();
   		    notification(response.message.description, response.message.type);
   		    $("#modal-paid").modal("hide");
   		    $("#id_deu").val(response.data.total_paid);
   		    if(response.data.due == 0){
   		        $("#btnpaid").prop("hidden",true);
   		    }
   		    if(reload){
   		        location.reload();
   		    }
   		},
   		error:function (response) {
   			HoldOn.close();
   			var message = response.responseJSON.message;
   			notification(message.description, message.type);
   		}
   });
};

function getData(fn) {
  var data = fn();
  return data;
};

function RequestPost_data(form,url){
   var rest = $.ajax({
   		url:url,
   		dataType: "json",
   		type:"POST",
   		data:form,
   		beforeSend: function(){
   			HoldOn.open({ message: "Please wait"});
   		},
   		success:function (response, status){
   		    HoldOn.close();
   		    if(response.message){
   		    	notification(response.message.description, response.message.type);
			}
   		},
   		async: false,
   		error:function (response) {
   			HoldOn.close();
   			var message = response.responseJSON.message;
   			var error = response.responseJSON.errors;
   			notification(message.description, message.type);
   			return "Nothing";
   		}
   }).responseText;
   var data = JSON.parse(rest);
   return data.data;
};

function RequestPostGeneric(form,url, idModal,reload){
   $.ajax({
   		url:url,
   		dataType: "json",
   		type:"POST",
   		data:form,
   		beforeSend: function(){
   			HoldOn.open({ message: "Please wait"});
   		},
   		success: function(response, status){
   		    HoldOn.close();
   		    notification(response.message.description, response.message.type);
   		    setTimeout(function () {
				if(reload){
					location.reload();
				}
			}, 2000);
   		    $("#"+idModal).modal("hide");
   		},
   		error:function (response) {
   			HoldOn.close();
   			var message = response.responseJSON.message;
   			notification(message.description, message.type);
   		}
   });
};


