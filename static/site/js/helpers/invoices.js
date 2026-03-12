function process_service(name_service, csrf_token ) {
    service = name_service;
    var code = name_service.parent('td').parent('tr').find('.code');
    rate = name_service.parent('td').parent('tr').find('.rate');
    comment = name_service.parent('td').parent('tr').find('.comment');
    price = name_service.parent('td').parent('tr').find('.price');
    postData('/Procedure/invoices/get_service/', {description: name_service.val()}, csrf_token)
        .then(data=> {
            code.val(data.code);
            price.val(data.cost);
            if(data.code !== 158 && data.code !== 216){
                rate.val(data.rate);
                var comment_project = 'id_details-'+ (comment.parent('td').parent('tr').index())+ '-comments_projects';
                if($('#' + comment_project).length){
                    $("#" + comment_project).remove();
                }
            } else {
                let url_modal = data.code === 158 ?url_category : url_floridatag;
                
                $("#modal-load-category").load(url_modal, function () {
                    $('#modal-category').modal('show');
                });
            }
        });
};

function calc() {
    $('#tblinvoice tbody tr').each(function(i, element) {
        var html = $(this).html();
        if(html !== '') {
            var qty = $(this).find('.qty').val();
            var rate = $(this).find('.rate').val();
            var price = $(this).find('.price').val();
            var typediscount = $(this).find('.typediscount').val();
            var discount = $(this).find('.discount').val();
            switch (typediscount) {
                case '$':
                    $(this).find('.total').val((qty*rate)-discount);
                    break;
                case '%':
                    var amount = qty*rate;
                    var percentage = discount/100;
                    discount = amount * percentage;
                    $(this).find('.total').val(amount-discount);
                    break;
                default:
                    $(this).find('.total').val(qty*rate);
            }
            calc_total();
        }
    });
}

function calc_total() {
    total = 0;
    $('.total').each(function() {
        $(this).val();
        total += parseFloat($(this).val());
    });
    $("#id_amount").val(total.toFixed(2));
}

function formset_action(csrf_token){
    calc_total();
    $('.formset_row').formset({
        addText: 'Add',
        addCssClass: 'btn btn-info btn-add btn-pill btn-sm',
        deleteText: 'X',
        deleteCssClass: 'btn btn-danger btn-remove btn-sm btn-pill',
        removed: function (row){
            var tdtotal = row.find('.total');
            var inptotal = $('#id_amount').val();
            row.find('textarea').val(' ');
            row.find('.qty').val(0);
            row.find('.code').val(0);
            var rest = parseFloat(inptotal).toFixed(2) - parseFloat(tdtotal.val()).toFixed(2);
            $('#id_amount').val(rest.toFixed(2));
            tdtotal.val(0);
        },
        prefix: 'details',
        added: function(row) {
            var txt = row.find('.services');
            var discount = row.find('.discount');
            var amount = row.find('.total');
            discount.val(0);
            amount.val(0);
            txt.change(function(e){
                e.preventDefault;
                process_service($(this), csrf_token);
            });
            txt.chosen({
                inherit_select_classes:true,
            });
        }
    });
}

function tblInvoice(csrf_token) {
    $('#tblinvoice tbody').on('keyup change',function(){
        calc();
    });
     $('#tblinvoice tbody').on('change', '#id_details-0-service',function(e) {
         e.preventDefault();
         process_service($(this), csrf_token);
     });

     $("#id_details-0-service").chosen({
         inherit_select_classes:true,
     });
}

function addInvoice(url, data_form, csrf_token, is_invoice= false) {
    HoldOn.open({ message: "Please wait..."});
    sendForm(url, data_form, csrf_token).then(
        result => {
            HoldOn.close();
            ({message, data}=result);
            notification(message.description, message.type);
            if(is_invoice){
                $("#btnpaid").removeAttr('hidden');
                $("#btnfinish").removeAttr('hidden');
                $("#btnpaid").val(data.idinvoice);
                $("input").prop("readonly",true);
                $("textarea").prop("readonly",true);
                $("select").prop("disabled",true);
            } else {
                $("#invoice-id-field").html(`<a href='/Procedure/invoices/pdf/${ data.idinvoice }'>${ data.idinvoice } <i class='fa fa-external-link'></i></a>`);
                $("#modal-invoice input").prop("readonly",true);
                $("#modal-invoice textarea").prop("readonly",true);
                $("#modal-invoice select").prop("disabled",true);
            }
            $("#btnsave").prop('hidden', 'true');
            $(".btn-remove").attr("disabled", true);
            $(".btn-add").attr("disabled", true);
            $("#id_amount").val(data.amount);
        }
    ).catch(error=>{
        HoldOn.close();
        $('#idfactura').html(error.idinvoice);
    })
}