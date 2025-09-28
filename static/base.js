$('.btn-password-toggle').on('click', function (event) {
    let input = $(event.currentTarget).parent().parent().find('input');
    if ('password' == $(input).attr('type')) {
        $(input).attr('type', 'text');
    } else {
        $(input).attr('type', 'password');
    }

    let svgs = $(event.currentTarget).parent().find('use');

    $(svgs[0]).toggle();
    $(svgs[1]).toggle();
});