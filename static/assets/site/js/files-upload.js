var settings = {
    url: url,
    maxFileSize: 5000000, // 5 Megs max
    auto: false,
    queue: true,
    extFilter: ['pdf', 'docx', 'xlsx'],
    fieldName: "path",
    extraData: function(){
        return {
            "folder": $("#folder").val(),
            "csrfmiddlewaretoken": $('input[name="csrfmiddlewaretoken"]').val(),
            "customer": $('#customer').val(),
            "uploaded_by": $('#uploaded_by').val(),
        }
    },
    dataType: 'json',
    onDragEnter: function(){
        // Happens when dragging something over the DnD area
        this.addClass('active');
    },
    onDragLeave: function(){
        // Happens when dragging something OUT of the DnD area
        this.removeClass('active');
    },
    onInit: function(){
        // Plugin is ready to use
        ui_add_log('Penguin initialized :)', 'info');
    },
    onComplete: function(data){
        // All files in the queue are processed (success or error)
        ui_add_log('All pending tranfers finished');
        $('#folder').val('');
    },
    onNewFile: function(id, file){
        // When a new file is added using the file selector or the DnD area
        ui_add_log('New file added #' + id);
        ui_multi_add_file(id, file);
    },
    onBeforeUpload: function(id){
        // about tho start uploading a file
        ui_add_log('Starting the upload of #' + id);
        ui_multi_update_file_status(id, 'uploading', 'Uploading...');
        ui_multi_update_file_progress(id, 0, '', true);
        ui_multi_update_file_controls(id, false, true);  // change control buttons status
    },
    onUploadProgress: function(id, percent){
        // Updating file progress
        ui_multi_update_file_progress(id, percent);
    },
    onUploadSuccess: function(id, data){
        // A file was successfully uploaded
        ui_add_log('Server Response for file #' + id + ': ' + JSON.stringify(data));
        ui_add_log('Upload of file #' + id + ' COMPLETED', 'success');
        ui_multi_update_file_status(id, 'success', 'Upload Complete');
        ui_multi_update_file_progress(id, 100, 'success', false);
        ui_multi_update_file_controls(id, false, false);  // change control buttons status
        table = $('#tbfiles').closest('table.dataTable');
        table.DataTable().ajax.reload(null, false);
        $('#folder').removeClass('is-invalid');
    },
    onUploadCanceled: function(id) {
        // Happens when a file is directly canceled by the user.
        ui_multi_update_file_status(id, 'warning', 'Canceled by User');
        ui_multi_update_file_progress(id, 0, 'warning', false);
        ui_multi_update_file_controls(id, true, false);
    },
    onUploadError: function(id, xhr, status, message){
        // Happens when an upload error happens
        ui_multi_update_file_status(id, 'danger', message);
        if(xhr.responseJSON.type == 'warning'){
            var errors = xhr.responseJSON.description.folder ? xhr.responseJSON.description: JSON.parse(xhr.responseJSON.description);
            if (errors.folder ){
                toastr.error('The directory is required', 'Field required');
                $('#folder').addClass('is-invalid');
            }
        }else{
            ui_multi_update_file_status(id, 'danger', xhr.responseJSON.description);
        }
        ui_multi_update_file_progress(id, 0, 'danger', false);
        ui_multi_update_file_controls(id, true, false, true); // change control buttons status
    },
    onFallbackMode: function(){
        // When the browser doesn't support this plugin :(
        ui_add_log('Plugin cant be used here, running Fallback callback', 'danger');
        toastr.error('Plugin cant be used here, running Fallback callback','Error');
    },
    onFileSizeError: function(file){
        ui_add_log('File \'' + file.name + '\' cannot be added: size excess limit', 'danger');
        toastr.error('File \'' + file.name + '\' cannot be added: size excess limit', 'Error');
    },
    onFileExtError: function (file) {
        toastr.error('File \'' + file.name + '\' cannot be added: extension not allowed', 'Check your file type');
    }
};
var uploadfile = $('#drag-and-drop-zone').dmUploader(settings);
 /*
 Global controls
 */
 $('#btnApistart').on('click', function(evt){
     evt.preventDefault();
     $('#drag-and-drop-zone').dmUploader('start');
 });

 $('#btnApireset').on('click', function(evt){
     evt.preventDefault();
     $('#drag-and-drop-zone').dmUploader('reset');
     $('#files').html('<li class="text-muted text-center empty">No files uploaded</li>');
     $('#folder').val();
 });
 /*
    Each File element action
 */
 $('#files').on('click', 'button.start', function(evt){
     evt.preventDefault();
     var id = $(this).closest('li.media').data('file-id');
     $('#drag-and-drop-zone').dmUploader('start', id);
 });

 $('#files').on('click', 'button.cancel', function(evt){
     evt.preventDefault();
     var id = $(this).closest('li.media').data('file-id');
     $('#drag-and-drop-zone').dmUploader('cancel', id);
 });

 function delete_file(id) {
    $.ajax({
        url: '/Procedure/delete_files_customer/'+id,
        dataType: 'JSON',
        headers: {
			'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
		},
        //data:{'erased_by': $('#uploaded_by').val() },
        type: 'DELETE',
        beforeSend: function(){
          //HoldOn.open({ message: "Please wait"});
        },
        success: function (response, status) {
            notification(response.description, response.type);
            table = $('#tbfiles').closest('table.dataTable');
            table.DataTable().ajax.reload(null, false);
            //HoldOn.close();
        },
        error: function (response) {
            //notification(response.responseJSON.description, response.responseJSON.type);
            //HoldOn.close();
        }
    });
 }