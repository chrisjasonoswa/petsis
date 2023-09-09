$(document).ready(function() {
    $('#example').DataTable( {
        search: {
            "smart": false,
          },
        order: [[0, 'desc']],
        lengthMenu: [[5, 10, 20, 50, 100, -1], [5, 10, 20, 50, 100, "All"]],
        "oLanguage": {
            "sSearch": "Filter/Search:",
            "sSearchPlaceholder": 'product, date, quantity, etc.'
          }  
    } );
} );