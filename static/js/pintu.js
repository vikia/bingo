$(document).ready(function() {
    var global_tpl = $(this).data("tpl")
    $('#render-div').hide()
    $('#dagain').hide()
    $("select").imagepicker({
        hide_select : false,
        show_label : true,
        selected : function() {
            //alert($(this).val())
            $('#markopt').attr('width', $(this).val())
        }
    })

    $('#btn_render').click(function() {
        title1_val = $('#ipt-title1').val()
        if (title1_val == "") {
            title1_val = $('#ipt-title1').attr('placeholder')
        }
		console.log(title1_val);

        title2_val = $('#ipt-title2').val()
        if (title2_val == "") {
            title2_val = $('#ipt-title2').attr('placeholder')
        }
		console.log(title2_val);

        title3_val = $('#ipt-title3').val()
        if (title3_val == "") {
            title3_val = $('#ipt-title3').attr('placeholder')
        }
		console.log(title3_val);

        logo_url = $('#ipt-logo').val()
        if (logo_url == "") {
            logo_url = $('#ipt-logo').attr('placeholder')
        }
		console.log(logo_url);

        item_url = $('#ipt-item').val()
        if (item_url == "") {
            item_url = $('#ipt-item').attr('placeholder')
        }
		console.log(item_url);
        $('#ipt-title1').attr('disabled', true)
        $('#ipt-title2').attr('disabled', true)
        $('#ipt-title3').attr('disabled', true)
        $('#ipt-logo').attr('disabled', true)
        $('#ipt-item').attr('disabled', true)

        var ftpl 
        if ($('#markopt').attr('width') == 1) {
            ftpl = '1.zip'
        } else if ($('#markopt').attr('width') == 2) {
            ftpl = '2.zip'
        }
        } else if ($('#markopt').attr('width') == 3) {
            ftpl = '3.zip'
        }

        $.ajax({
            //url: 'ad-rec',
            url: './bingo_url',
            type: 'GET',
            data: {
                tpl    : ftpl,
                title1 : title1_val,
                title2 : title2_val,
                title3 : title3_val,
                logo : logo_url,
                img : item_url
            },
            datatype: 'json',
            contentType: 'application/json; charset=gbk',
            success: function (returndata) {
                console.log(returndata);
                $('#f2hide').hide()
                $('.page-header').hide()
                $('#render-res').attr("src", returndata['img']);
                $('#render-div').show()
                $('#dagain').show()
            },
            error : function(data, type, error) {
                console.log(data);
                console.log(type);
                console.log(error);
            }
        });
    });

    $('#btn_again').click(function() {
        $('#render-res').attr("src", '');
        $('#render-div').hide()
        $('#dagain').hide()
        $('.page-header').show()
        $('#f2hide').show()
        $('#ipt-title1').attr('disabled', false)
        $('#ipt-title2').attr('disabled', false)
        $('#ipt-title3').attr('disabled', false)
        $('#ipt-logo').attr('disabled', false)
        $('#ipt-item').attr('disabled', false)
    });
});
