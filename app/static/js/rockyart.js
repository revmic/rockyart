<!-- Activate Index Carousel -->
$('.carousel').carousel({
    interval: 5000 //changes the speed
});

////////////////////
// simpleCart(js) //
////////////////////

simpleCart({
    checkout: {
        type: "PayPal" ,
        email: "mhilema@gmail.com"
    },
    cartStyle : "table",

    cartColumns: [
        //{view:'image', attr:'thumb', label: false},
        { attr: "image",
            view: function(item, column) {
                if ($(window).width() > 768) {
                    return "<div class='col-md-4'><img width='100px' src='" + item.get('image') + "'></div>";
                } else {
                    return "";
                }
        }},

        //{ attr: "name", label: "Name" },
        { attr: "name",
            view: function(item, column){
                return '<div class="col-md-4">' + item.get('name') + "</div>";
        },  label: "<div class='col-md-3'>Item</div>" },

        { attr: "price", view: 'currency', label: "Price" },
        //{ attr: "price",
        //    view: function(item, column){
        //        return '<div class="col-md-4">' + item.get('currency') + "</div>";
        //},  label: "<div class='col-md-4'>Price</div>" },

        { view: "decrement" , label: false , text: "<i class='fa fa-minus'></i>" },

        { attr: "quantity", label: "Qty" },
        //{ attr: "quantity",
        //    view: function(item, column){
        //        return '<div class="col-md-4">' + item.get('currency') + "</div>";
        //},  label: "<div class='col-md-4'>Price</div>" },

        { view: "increment" , label: false , text: '<i class="fa fa-plus"></i>' },

        { attr: "total", view: 'currency', label: "SubTotal" },
        //{ attr: "total",
        //    view: function(item, column){
        //        return '<div class="col-md-4">' + item.get('currency') + "</div>";
        //},  label: "<div class='col-md-4'>Subtotal</div>" },

        //{ view: "remove", text: "Remove", label: false }
        { view: "remove", text: '<i class="fa fa-times-circle-o fa-2x cart-remove">',
            label: false }

    ]
});

simpleCart.currency({
    accuracy: 0
});

<!-- Assign Bootstrap styles to simpleCart table/div -->
simpleCart.bind("afterCreate", function() {
    $(".simpleCart_items table").addClass("table").addClass("table-hover");
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
        var row = '<tr>' + image_td + name_td + '</tr>';
        cart.append(row);
    });
}

function clearCartDropdown() {
    var cart = $('#cart-dropdown-table');
    cart.empty();
    var row = '<tr><td>Your cart is empty, but you could <a href="/shop">Go Shopping</a></tr></td>';
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
    controlNav: "thumbnails"
});

//////////////////
// Contact Form //
//////////////////

$(document).ready(function() {
    // init isotope grid after images have loaded
    var $grid = $('.store-grid').imagesLoaded(function() {
        $grid.isotope({
            itemSelector: '.store-item',
            masonry: {
                columnWidth: 250,
                isFitWidth: true,
                gutter: 10
            },

            getSortData: {
                price: '.price parseInt',
                date: '.date'
            }
        });
    });

    // filter items on button click
    $('.filter-button-group').on( 'click', 'button', function() {
      var filterValue = $(this).attr('data-filter');
      $grid.isotope({ filter: filterValue });
    });

    // sort items on button click
    $('.sort-by-button-group').on( 'click', 'button', function() {
      var sortByValue = $(this).attr('data-sort-by');
      $grid.isotope({ sortBy: sortByValue });
    });

    /////////////////////////////////////////////////////////////

    // Email button spinner
    $('#send').click(function () {
        $("#btn_icon").attr('class', 'fa fa-spinner fa-spin fa-lg');
    });
    // Reset after a time in case of invalid form
    setInterval(function () { $("#btn_icon").attr('class', 'glyphicon glyphicon-envelope') }, 6000);

    // Contact phone is a tel link on mobile or a tooltip on desktop
    if ($(window).width() < 768) {
        $('#phone').append("<a href='tel://314-630-8983'>phone</a>");
    } else {
        $('#phone').append("<a href='#' data-toggle='tooltip' title='314-630-8983'>phone</a>");
        $('[data-toggle="tooltip"]').tooltip();
    }

});


/*$('#contactForm').validator().on('submit', function (e) {
    if (e.isDefaultPrevented()) {
        // handle the invalid form...
    } else {
        $("#btn_icon").attr('class', 'fa fa-spinner fa-spin fa-lg');
    }
})*/