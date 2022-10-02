$(document).ready(function() {
    $('#order_history').DataTable( {
        search: {
            "smart": false,
          },
        order: [[0, 'desc']],
        lengthMenu: [[10, 20, 40, 50, 100, -1], [10, 20, 40, 50, 100, "All"]],
        "oLanguage": {
            "sSearch": "Filter/Search:",
            "sSearchPlaceholder": 'status, product, etc.'
          }  
    } );
} );

