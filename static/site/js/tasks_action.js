//Popup Menu Task
function task_completed_check(event, is_calendar = 0){
	const url = '/Procedure/tasks/completed/'+event.val();
	$.post(url, {'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(), 'is_completed': event.prop('checked')} ,function (data){
		if(data.percentage === undefined){
			location.href = '/Procedure/login/';
		} else {
			notification(data.message.description, data.message.type);
			if( !is_calendar ){
				if(document.getElementById('percentage-number') !== undefined ){
					document.getElementById('percentage-number').innerHTML = data.percentage+"%";
					document.getElementById('percentage-indicator').style.width = data.percentage+"%";
				}
				enable_add_invoice(data.percentage);
			}
			total_notifications();
			if(is_calendar){
				load_tasks(`/Procedure/tasks/list/${is_calendar}`);
			}
		}
	}).fail(function (data){
		const message = data.responseJSON.message;
		notification(message.description, message.type);
	});
}

function load_tasks(url) {
	$('#tasks').load(url);
}

function enable_add_invoice (percentage){
	if(document.getElementById('btn-add-invoice')){
		if(percentage === 100){
			document.getElementById('btn-add-invoice').removeAttribute('disabled');
		}else {
			document.getElementById('btn-add-invoice').setAttribute('disabled', 'true');
		}
	}
}

function archive_task(url, is_calendar) {
	const form = $('#delete-form').serialize();
	let url_post = '/Procedure/tasks/archive/';
	url_post += is_calendar;
	$.post(url_post, form, function (response) {
		notification(response.message.description, response.message.type);
		if(is_calendar === 0){
			document.getElementById('percentage-number').innerHTML = response.percentage+"%";
			document.getElementById('percentage-indicator').style.width = response.percentage+"%";
			enable_add_invoice(response.percentage);
		}
		if(is_calendar === 1){
			 let event = calendar.getEventById(`T-${response.task_id}`);
			 event.remove();
		}
		load_tasks(url);
		total_notifications();
		$('body').removeClass('modal-open');
		$('.modal-backdrop').remove();
		$('#archive-modal').modal('hide');

	}).fail(function (response) {
		const message = response.responseJSON.message;
		notification(message.description, message.type);
	});

}

function total_notifications() {
	fetch('/Procedure/alert_notifications/').then(response => response.json()).then(
		data => {
			data.total_notifications !== 0? $('#notification-counter').addClass('active') : $('#notification-counter').removeClass('active')
			$('.alert-notification').html(data.total_notifications);
			$('#appointments-tomorrow').html(data.appointments_tomorrow);
			$('#appointments-today').html(data.appointments_today);
			$('#total-tasks').html(data.total_tasks);
		}
	);
}