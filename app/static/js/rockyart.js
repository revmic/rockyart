/**/

////////////////////
// simpleCart(js) //
////////////////////

simpleCart({
    checkout: {
        type: "PayPal" ,
        //email: "mhilema@gmail.com"
        email: "rockyart_store@gmail.com",
        sandbox: true,
        //success: "http://test.rockyart.com",
        cancel: "/index"
    },
    shippingQuantityRate: 2,

    cartStyle : "table",

    cartColumns: [
        //{view:'image', attr:'thumb', label: false},
        { attr: "image",
            view: function(item, column) {
                if ($(window).width() > 600) {
                    return "<div class='text-center'><img width='150px' src='" + item.get('image') + "'></div>";
                } else {
                    return "";
                    //return "<div class='text-center'><img width='150px' src='" + item.get('image') + "'></div>";
                }
        }},

        //{ attr: "name", label: "Name" },
        { attr: "name",
            view: function(item, column){
                return '<div>' + item.get('name') + "</div>";
        },  label: "<div'>Item</div>" },

        { attr: "price", view: 'currency', label: "Price" },

        { view: "decrement" , label: false ,
            text: '<div class="text-center"><i class="fa fa-minus-square fa-2x cart-qty"></i></div>' },

        //{ attr: "quantity", label: "Qty" },
        { attr: "quantity",
            view: function(item, column){
                return '<div class="text-center">' + item.get('quantity') + "</div>";
        },  label: '<div class="text-center" style="width:0">Qty</div>' },

        { view: "increment" , label: false ,
            text: '<div class="text-center"><i class="fa fa-plus-square fa-2x cart-qty"></i></div>' },

        { attr: "total",
            view: function(item, column) {
                return '<div class="text-center">$' + item.get('total') + "</div>";
        }, label: '<div class="text-center">Subtotal</div>' },

        //{ view: "remove", text: "Remove", label: false }
        { view: "remove", text: '<div class="text-center"><i class="fa fa-times-circle fa-2x cart-remove"></div>',
            label: '<div style="width:0"></div>' }
    ]
});

simpleCart.currency({
    accuracy: 0
});

simpleCart.cancelUrl = "/shop"

// Populate some data before checking out
simpleCart.bind( 'beforeCheckout' , function( data ){
  data.invoiceNumber = "ABC-123456789";
});

<!-- Assign Bootstrap styles to simpleCart table -->
simpleCart.bind("afterCreate", function() {
    $(".simpleCart_items table").addClass("table").addClass("table-hover"); //.addClass("cart-table");
    //$(".simpleCart_items div").addClass("div").addClass("col-lg-12");
});

<!-- Handle cart opacity and animation -->
simpleCart.bind("update" , function(item) {
    // Fade out when there is nothing and fade in when there is 1
    if (simpleCart.quantity() == 0) {
        $(".cart-toggle").fadeTo('3000', '0.1');
        clearCartDropdown();
    }
    else if (simpleCart.quantity() == 1) {
        $(".cart-toggle").fadeTo('3000', '0.8');
    } else {
        $(".cart-toggle").css('opacity', '0.8');
    }
    // Update cart dropdown menu on update
    if (simpleCart.quantity() > 0) {
        updateCartDropdown();
        $("#checkout_btn").unbind('click');
    }
});

simpleCart.bind("afterAdd" , function( item ) {
    // Fade in and out when there are additional cart items
    if (simpleCart.quantity() > 1) {
        var cart = $('.cart-toggle');
        cart.fadeOut(150);
        cart.fadeIn(350);
    }
});

simpleCart.bind("checkoutSuccess", function ( data ) {
    window.location="/index"
});

simpleCart.bind('beforeAdd' , function( item ) {
    //updateCartDropdown();
    // Only allow one of an item in the cart
    if (simpleCart.has(item) != false) {
        //alert("This item is already in your cart");
        item.quantity(0);
    }
});

cart_items = [];

function updateCartDropdown() {
    // build the cart dropdown from simpleCart contents
    var cart = $('#cart-dropdown-table');
    cart.empty();

    simpleCart.each(function(item, x) {
        var image = '<img class="img-responsive" src="' + item.get('image') + '"/>';
        var image_td = '<td width="25%">' + image + '</td>';
        var name_td = '<td>' + item.get('name') + '</td>';
        var qty_td = '<td>' + item.get('quantity') + '</td>';
        var row = '<tr>' + image_td + name_td + qty_td + '</tr>';
        cart.append(row);
    });
}

function clearCartDropdown() {
    var cart = $('#cart-dropdown-table');
    cart.empty();
    var row = '<tr><td>Your cart is empty, but you could <br> <a href="/shop">Go Shopping</a></tr></td>';
    cart.append(row);
    $("#checkout_btn").bind('click', function(e){
        e.preventDefault();
    })
}


//////////////////
// Product Page //
//////////////////

<!-- category tooltips -->
$("[rel='tooltip']").tooltip();

$('.item-thumbnail').hover(
    function() {
        $(this).find('.item-caption').fadeIn(250);
    },
    function() {
        $(this).find('.item-caption').fadeOut(250);
    }
);

<!-- item image viewer -->
$('.flexslider').flexslider({
    animation: "slide",
    controlNav: "thumbnails",
    smoothHeight: true,
    useCss: true
});

//$('.flex-direction-nav').css({''})

//////////////////
// Contact Form //
//////////////////

$(document).ready(function() {
    var $store_grid = $('.store-grid');

    /* DESKTOP STORE FILTERS */
    // init isotope grid after images have loaded
    var $grid = $store_grid.imagesLoaded(function() {
        $grid.isotope({
            itemSelector: '.store-item',
            masonry: {
                columnWidth: 250,
                isFitWidth: true,
                gutter: 10
            },
            getSortData: {
                price_up: '.price parseInt',
                price_down: '.price parseInt',
                date: '.date'
            },
            sortAscending: {
                price_up: true,
                price_down: false,
                date: true
            }
        });
    });

    // filter items on button click
    $('.filter-button-group').on( 'click', 'button', function() {
      var filterValue = $(this).attr('data-filter');
      $grid.isotope({ filter: filterValue });
    });

    // sort items on button click
    $('.sortby-button-group').on( 'click', 'button', function() {
      var sortByValue = $(this).attr('data-sort-by');
      $grid.isotope({ sortBy: sortByValue });
    });


    /* MOBILE STORE FILTERS */
    var $mobile_grid = $store_grid,
    $category_select = $('#filters').find('select'),
    $sortby_select = $('#sorting').find('select');

    $mobile_grid.isotope({
        itemSelector: '.store-item',
        masonry: {
            columnWidth: 250,
            isFitWidth: true,
            gutter: 10
        },
        getSortData: {
            price_up: '.price parseInt',
            price_down: '.price parseInt',
            date: '.date'
        },
        sortAscending: {
            price_up: true,
            price_down: false,
            date: true
        }
    });
    // filter items on dropdown change
    $category_select.change(function() {
        var filters = $(this).val();
        $mobile_grid.isotope({ filter: filters });
    });
    // sort items on dropdown change
    $sortby_select.change(function() {
        var sortByValue = $(this).val();
        $mobile_grid.isotope({ sortBy: sortByValue });
    });

    /////////////////////////////////////////////////////////////

    // Email button spinner
    $('#send').click(function () {
        $("#btn_icon").attr('class', 'fa fa-spinner fa-spin fa-lg');
    });
    // Reset after a time in case of invalid form
    setInterval(function () { $("#btn_icon").attr('class', 'glyphicon glyphicon-envelope') }, 6000);

    // Contact phone is a tel link on mobile or a tooltip on desktop
    if ($(window).width() < 568) {
        $('#phone').append("<a href='tel://314-630-8983'>phone</a>");
        // Display the appropriate Shop filters
        $('#mobile-filters').show();
        $('#desktop-filters').hide();
        // Display appropriate Shopping Cart
        //$('#mobile-cart').show();
        //$('#desktop-cart').hide();
        // Make some icons smaller
        $("i.cart-button").removeClass("fa-2x");
        $("i.cart-qty").removeClass("fa-2x");
        $("i.cart-remove").removeClass("fa-2x");
        //simpleCart.cartStyle = "div";
    } else {
        $('#phone').append("<a href='#' data-toggle='tooltip' title='314-630-8983'>phone</a>");
        $('[data-toggle="tooltip"]').tooltip();
        // Display the appropriate Shop filters
        $('#mobile-filters').hide();
        $('#desktop-filters').show();
        // Display appropriate Shopping Cart
        //$('#mobile-cart').hide();
        //$('#desktop-cart').show();
        //simpleCart.cartStyle = "table";
    }
});

/////////////////////
// Admin Interface //
/////////////////////

//// Product images in admin interface
//$(document).ready( function() {
//    var $grid2 = $('.product-image-grid').imagesLoaded(function() {
//        $grid2.isotope({
//            itemSelector: '.product-image',
//            masonry: {
//                columnWidth: 150,
//                isFitWidth: true,
//                gutter: 10
//            }
//        });
//    });
//});
//
//function toggle_dropzone() {
//    $("#dropzone-area").toggle(500);
//    var toggle_btn = $("#toggle-dropzone-btn");
//
//    if (toggle_btn.text() === "Upload Images") {
//        toggle_btn.text("Hide Dropzone")
//    } else {
//        toggle_btn.text("Upload Images")
//    }
//}