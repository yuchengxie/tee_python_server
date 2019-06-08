
let WEB_SERVER = 'http://127.0.0.1:3000';
function hello() {
    $.get(WEB_SERVER, function (data, status) {
        console.log('data:', data);
    })
}

function getpass() {
    var pwd = $('#input_pin').val();
    let params = { 'pass': pwd };
    $.ajax({
        url: 'http://127.0.0.1:3000/getpass',
        data: params,
        type: 'POST',
        success: function (res) {
            alert(res);
        },
        error: function (error) {
            alert(error);
        }
    })
}

function get_info() {
    $.ajax({
        url: 'http://127.0.0.1:3000/info',
        data: null,
        type: 'POST',
        success: function (res) {
            alert(res);
        },
        error: function (error) {
            alert(error);
        }
    })
}

function sign() {
    let params = { 'payload': '123', 'pincode': '000000' };
    $.post('http://127.0.0.1:3000/sign', params, function (data, status) {
        alert(data);
    });
}