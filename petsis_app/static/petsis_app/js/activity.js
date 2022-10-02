$(document).ready(function() {
    $('#activity').DataTable( {
        search: {
            "smart": false,
          },
        order: [[0, 'desc']],
        lengthMenu: [[10, 20, 40, 50, 100, -1], [10, 20, 40, 50, 100, "All"]],
          
    } );
} );