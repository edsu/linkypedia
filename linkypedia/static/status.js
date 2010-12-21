refresh_rate = 5000;

$(document).ready(function() { setTimeout("get_last_update()", refresh_rate);});

function get_last_update(since) {
    $.getJSON('/status.json', function(data) {
        var html = '<b>just added: </b>' +
               '<a href="' + data.wikipedia_url + '">' +
               data.wikipedia_page_title + '</a> referencing <a href="' + 
               data.target + '">' + data.host + '</a>';

        if (since != data.created) {
            $('#last_link').fadeOut('slow', function() {
                $('#last_link').html(html);
                $('#last_link').fadeIn('slow');
            });
        }
        setTimeout('get_last_update("' + data.created + '")', refresh_rate);
    });
}
