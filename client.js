let WEB_SERVER = 'http://127.0.0.1:3000';
const server_error = 'server error';

function hello() {
    
    $.ajax({
        url:WEB_SERVER,
        success:function(res){
            console.log('data:', data);
        },
        error:function(err){
            alert(server_error)
        }
    })
}

function verify_pin() {
    var pwd = $('#input_pin').val();
    let params = { 'pincode': pwd };
    $.ajax({
        url: 'http://127.0.0.1:3000/verify_pin',
        data: params,
        type: 'POST',
        success: function (res) {
            alert(res);
        },
        error: function (error) {
            alert(server_error)
        }
    })
}

function get_info() {
    $.ajax({
        url: 'http://127.0.0.1:3000/get_info',
        data: null,
        type: 'POST',
        success: function (res) {
            alert(res);
        },
        error: function (error) {
            alert(server_error)
        }
    })
}

function get_sign() {
    let params = { 'payload': '123', 'pincode': '000000' };
    $.ajax({
        url: 'http://127.0.0.1:3000/get_sign',
        data: params,
        type: 'POST',
        success: function (res) {
            alert(res);
        },
        error: function (error) {
            alert(server_error)
        }
    })
}

function get_block() {
    // let params = { 'payload': '123', 'pincode': '000000' };
    $.ajax({
        url: 'http://127.0.0.1:3000/get_block',
        data: null,
        type: 'POST',
        success: function (res) {
            alert(res);
        },
        error: function (error) {
            alert(server_error)
        }
    })
}