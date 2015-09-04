
/////////////////////
// Admin Interface //
/////////////////////

<!-- Image controls popover -->
$("[rel='tooltip']").tooltip();

$('.item-thumbnail').hover(
    function() {
        $(this).find('.image-controls').fadeIn(250);
    },
    function() {
        $(this).find('.image-controls').fadeOut(250);
    }
);

function toggle_dropzone() {
    $("#dropzone-area").toggle(500);
    var toggle_btn = $("#toggle-dropzone-btn");

    if (toggle_btn.text() === "Upload Images") {
        toggle_btn.text("Hide Dropzone")
    } else {
        toggle_btn.text("Upload Images")
    }
}

function add_option() {
    var uri = $('#option_uri').val();
    var formData = {
        "option_value": $('#option_name').val()
    };

    if (! $('#option_name').val()) {
        alert("Must enter an option name");
        return;
    }

    $.ajax({
        type: 'POST',
        url: uri,
        data: formData,
        dataType: 'json',
        encode: true,
        success: function(res) {
            console.log(res)
        },
        error: function(err) {
            console.log(err)
        }
    })
}

function toggle_gallery(img_id) {
    //alert("Add to gallery " + img_id);

    var toggle = $.ajax({
        type: 'POST',
        url: '/admin/image/'+img_id+'/gallery',
        dataType: 'html',
        async:false
    });

    $('#user_options').toggle();
    //$(this).toggleClass('active');


    toggle.done(function() {
        var icon = $("#image-gallery"+img_id);

        if (icon.css('color') == 'rgb(255, 255, 255)') {
            icon.css("color", "forestgreen")
        } else {
            icon.css("color", "white")
        }

        //
        //if (icon.css("color") == "forestgreen") {
        //    icon.css("color", "white")
        //} else {
        //    icon.css("color", "forestgreen")
        //}
    });
}

function toggle_main(img_id) {
    //alert("Set as main image " + img_id);

    var toggle = $.ajax({
        type: 'POST',
        url: '/admin/image/'+img_id+'/main',
        dataType: 'html',
        async:false
    });
    toggle.success(function() {
        var img_class = $(".image-main");
        var img_main = $("#image-main"+img_id);
        img_class.css("color", "white");
        img_main.css("color", "#017DFF");
    });
}

$(document).ready(function() {
    $("#dropzone-area").hide();

    // Product images in admin interface
     var $grid = $('.product-image-grid').imagesLoaded(function() {
        $grid.isotope({
            itemSelector: '.product-image',
            masonry: {
                columnWidth: 250,
                isFitWidth: true,
                gutter: 10
            }
        });
    });

    //var image_dropzone = new Dropzone("#image-dropzone");
    /*
    image_dropzone.on("sending", function(file) {
        var pid = document.getElementById("product_id").value;

        var create_product = $.ajax({
            type: 'POST',
            url: '/admin/product/new/?id='+pid,
            dataType: 'html',
            success: alert("successfully created product"),
            error: alert("error on product create"),
            async:false
        });
        alert(create_product.returnValue)
    });
    */
});

