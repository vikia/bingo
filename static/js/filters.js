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
        item_url = $('#ipt-item').val()
        if (item_url == "") {
            item_url = $('#ipt-item').attr('placeholder')
        }
		console.log(item_url);
        $('#ipt-item').attr('disabled', true)

        var stra = $('#markopt').attr('width')

        $.ajax({
            //url: 'ad-rec',
            url: './req-filters',
            type: 'GET',
            data: {
                stra    : stra,
                img : item_url
            },
            //datatype: 'json',
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
        $('#ipt-item').attr('disabled', false)
    });
});
