var page_count = 0;
function snipMe() {
    page_count++;
    var long = $(this)[0].scrollHeight - Math.ceil($(this).innerHeight());
    var children = $(this).find('.content').toArray();
    var removed = [];
    while (long > 0 && children.length > 0) {
        var child = children.pop();
        $(child).detach();
        removed.push(child);
        long = $(this)[0].scrollHeight - Math.ceil($(this).innerHeight());
    }
    if (removed.length > 0) {
        var a4 = $('<div class="page"></div>');
        a4.append(removed);
        $(this).after(a4);
        snipMe.call(a4[0]);
    }
}

$(document).ready(function() {
    $('.page').each(function() {
        snipMe.call(this);
    });
});
