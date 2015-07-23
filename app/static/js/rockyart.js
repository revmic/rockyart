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
        //{view:'image' , attr:'thumb', label: false},
        { view: function(item, column){
            return"<img src='"+item.get('image')+"'>";
        }, attr: 'image' },
        { attr: "name" , label: "Name" } ,
        { attr: "price" , label: "Price", view: 'currency' } ,
        //{ view: "decrement" , label: false , text: "-" } ,
        { attr: "quantity" , label: "Qty" } ,
        //{ view: "increment" , label: false , text: "+" } ,
        { attr: "total" , label: "SubTotal", view: 'currency' } ,
        { view: "remove" , text: "Remove" , label: false }
    ]
});

<!-- Assign Bootstrap styles to simpleCart table -->
simpleCart.bind("afterCreate", function() {
   $(".simpleCart_items table").addClass("table").addClass("table-hover");
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
        var image = '<img class="img-responsive" src="' + item.get('image') + '" />';
        var image_td = '<td width="25%">' + image + '</td>';
        var name_td = '<td>' + item.get('name') + '</td>';
        var row = '<tr>' + image_td + name_td + '</tr>';
        cart.append(row);
    });
}

function clearCartDropdown() {
    var shop_link = "/products";
    var row = '<tr><td>Your cart is empty, but you could <a href="'
        + shop_link + '">Go Shopping</a></tr></td>';
    var cart = $('#cart-dropdown-table');
    cart.empty();
    cart.append(row);
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



