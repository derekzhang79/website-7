var search_results = $('#search_results');

$('#search_submit').click(function() {
    Dajaxice.recipient.search(function(result) {
        process_result(result);
    }, {
        'title': $('#search_title').val(),
        'entities_include': true
    });
});

function process_result(result)
{
    console.log(result);
    if(result.success)
    {
        search_results.empty();
        if(result.items.length > 0)
        {
            for(var i = 0; i < result.items.length; i++)
            {
                var result_html =  '<li class="span4" style="background: white;">' +
                                      '<div class="thumbnail">' +
                                         '<div class="caption">' +
                                            '<h4>' + result.items[i].title + '</h4>' +
                                            '<span class="label">' + result.items[i].type_label + '</span>' +
                                            '<ul>';
                for(var j = 0; j < result.items[i].entities.length; j++)
                {
                    if(result.items[i].entities[j].type == 2)
                    {
                        result_html +=          '<li>' + result.items[i].entities[j].artist + '</li>';
                    } else {
                        result_html +=          '<li>' + result.items[i].entities[j].title + '</li>';
                    }
                }
                if('entities_more' in result.items[i])
                {
                    if(result.items[i].entities_more == 1)
                    {
                        result_html +=         '<li><em>and ' + result.items[i].entities_more + ' more entity</em></li>';
                    } else {
                        result_html +=         '<li><em>and ' + result.items[i].entities_more + ' more entities</em></li>';
                    }
                }
                result_html +=              '</ul>' +
                                         '<button class="btn btn-mini pull-right">Claim</button>' +
                                         '<div class="clearfix"></div>' +
                                         '</div>' +
                                      '</div>' +
                                   '</li>';
                search_results.append(result_html);
            }
        } else {
            // TODO: Allow a recipient lookup here
        }
    }
}