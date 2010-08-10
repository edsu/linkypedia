refresh_rate = 5000;

$(document).ready(function() { setTimeout("get_last_update()", refresh_rate);});

function get_last_update() {
    $.getJSON('/status.json', function(data) {

        link = '<b>recently found: </b>' +
               '<a href="' + data.wikipedia_url + '">' +
               data.wikipedia_page_title + '</a> referencing <a href="' + 
               data.target + '">' + data.website_name + '</a>';
    
        if (link != $('#last_link').html()) {
            $('#last_link').fadeOut('slow', function() {
                $('#last_link').html(link);
                $('#last_link').fadeIn('slow');
            });
        }

        if (data.current_crawl) {
            crawl = '<b>currently crawling:</b> ' + 
                   '<a href="' + data.current_crawl.link + '">' +
                   data.current_crawl.name +
                   '</a>';
            if (crawl != $('#current_crawl').html()) {
                $('#current_crawl').fadeOut('slow', function() {
                    $('#current_crawl').html(crawl);
                    $('#current_crawl').fadeIn('slow');
                });
            }
        }

    });
    setTimeout("get_last_update()", refresh_rate);
}
