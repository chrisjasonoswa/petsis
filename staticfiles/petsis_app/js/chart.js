const ctx = document.getElementById('myChart').getContext('2d');
var labels_orders = {{ labels1|safe}};
var orders_count = {{ orders|safe }};

const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: labels_orders,
        datasets: [{
            label: 'Orders',
            data: orders_count,
            backgroundColor: [
                '#0096BC'
            ],
            borderRadius: 7,
            borderSkipped: false,
            barPercentage: 1,
        }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            xAxes: [{
                categoryPercentage: 0.3,
                gridLines: {
                    color: 'rgba(255, 0, 0, 0.1)'
                  },
            }],

            y: {
                grid:{
                    display:false
                }
            },

            x: {
                grid:{
                    display:false
                }
            }
        }
    }
});


const ctx1 = document.getElementById('myChart1').getContext('2d');

var labels2 = ['April', 'May', 'June', 'July', 'August']
var sales = [30 , 19.760, 30.250, 25.078, 20.000]

const myChart1 = new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: labels2,
        datasets: [{
            label: 'Sales',
            data: sales,
            backgroundColor: [
                '#0096BC'
            ],
            borderRadius: 7,
            borderSkipped: false,
            barPercentage: 1,
        }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            xAxes: [{
                categoryPercentage: 0.3,
                gridLines: {
                    color: 'rgba(255, 0, 0, 0.1)'
                  },
            }],

            y: {
                grid:{
                    display:false
                }
            },

            x: {
                grid:{
                    display:false
                }
            }
        }
    }
});