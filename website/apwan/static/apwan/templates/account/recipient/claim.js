var search_results = $('#search_results');
var search_submit = $('#search_submit');
var search_title = $('#search_title');

var item_template = Mustache.template('account/recipient/claim_result_item');

search_submit.click(search);

var columnMargin = 0;

search_results.isotope({
    itemSelector: '.claim_item',
    resizable: false,
    masonry: { columnWidth: search_results.width() / 3 }
});

$(window).smartresize(function(){
    search_results.isotope({
        masonry: { columnWidth: search_results.width() / 3 }
    });
});

$(document).ready(function() {
    if(search_title.val() != '') search();
});

function search()
{
    Dajaxice.recipient.search(search_callback, {
        'title': search_title.val(),
        'entities_include': true,
        'limit': 9
    });
}

function search_callback(result)
{
    if(result.success)
    {
        search_results.empty().isotope('reLayout');
        if(result.items.length > 0)
        {
            var items = "";
            for(var i = 0; i < result.items.length; i++)
            {
                var recipient = result.items[i];

                for(var j = 0; j < recipient.entities.length; j++)
                {
                    recipient.entities[j].is_music = recipient.entities[j].type == 2;
                }

                if('entities_more' in recipient)
                {
                    if(recipient.entities_more == 1)
                    {
                        recipient.entities_more_tag = "entity";
                    } else {
                        recipient.entities_more_tag = "entities";
                    }
                }

                items += item_template.render({'recipient': recipient});
            }
            var $items = $(items);
            search_results.append($items).isotope('appended', $items);

        } else {
            // TODO: Allow a recipient lookup here
        }
    }
}

function claim(recipient_id)
{
    console.log("claim(" + recipient_id + ")");

    Dajaxice.recipient.claim(claim_callback, {
        'recipient_id': recipient_id
    });
}

function claim_callback(result)
{
    var claim_element = $('.claim_item[recipient_id="' + result.recipient.id + '"]');
    if(claim_element != null)
    {
        if(result.success)
        {
            console.log(result);
            $('.claim-actions', claim_element)
                .html('<a href="/account/recipient/' + result.recipient.slug + '" class="btn btn-mini btn-success">View</a>');

            menu_insert('a', 'recipient',
                '<li class="li-recipient">' +
                    '<a href="/account/recipient/' + result.recipient.slug + '">' +
                        $('.recipient-title', claim_element).text() +
                    '</a>' +
                '</li>'
            );
        } else {
            $('.claim-error', claim_element)
                .text("Failed")
                .delay(5000)
                .animate({
                    opacity: 0
                }, 2500, function() {
                    $(this).text('');
                    $(this).css('opacity', 1);
                });
        }
    } else {
        console.error("Bad 'claim_callback' result");
    }
}

function menu_insert(sort_selector, type, item)
{
    if(type != 'account' && type != 'payee' &&
        type != 'recipient' && type != 'report')
    {
        console.error("menu_insert: invalid 'type'");
        return;
    }

    var item_sort = $(sort_selector, item).text().toLowerCase();

    var closest = null;
    $('.account-menu .nav-list li.li-' + type).each(function() {
       if($(sort_selector, this).text().toLowerCase() < item_sort)
       {
           closest = $(this);
       }
    });

    if(closest != null)
    {
        closest.after(item);
    } else {
        $('.account-menu .nav-list li.nav-header-' + type).after(item);
    }
}