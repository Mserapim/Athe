$(document).ready(
    function()
    {
        $('.opinion-button').click(
            function()
            {
                var td = $(this).parent();
                var div = td.find('div.opinion').clone();
                td.append(div);
                div.dialog({
                    modal:true,
                    width:'500px'
                });
                return false;
            }
        );

        $('.mask').blur(
        	function()
        	{ mask($(this)); }
        );

        $('.hide-when-web').hide();

        $('[name="cpf"], [name="cnpj"]').blur(function() {
            let params = {};
            params[$(this).attr('name')] = clearValue($(this).val());
            ajax_loading();
            $.getJSON('/athenas/OmbudsmanRPC/person_data/', params, fetchFields);
        });

        $('.more-file-slot').css({cursor: 'pointer'}).click(function(event){
            event.preventDefault();

            let next = $('.file-field').length + 1,
                newFileField = $('<input>').attr('name', 'file_' + next).attr('type', 'file').addClass('file-field'),
                p = $('<p>').append(newFileField);

            p.insertBefore($(this));
        })
    }
);

function mask(el)
{
    var pattern = null;

    if(el.attr('name') == 'cep')
        pattern = '#####-###';
    else if(el.attr('name') == 'telefone')
        pattern = (el.val().length > 10) ? '##-#####-####' : '(##) ####-####';
    else if(el.attr('name') == 'cpf')
        pattern = '###.###.###-##';
    else
        pattern = '##.###.###/####-##';

    el.mask(pattern);
}

function clearValue(val)
{ return val.match(/[a-zA-Z0-9]/g).join(''); }

function fetchFields(data)
{
    for(let attr in data)
    {
        let el = $('[name='+ attr +']');
        el.val(data[attr]);

        if (['cep', 'cpf', 'cnpj', 'telefone'].indexOf(attr) > -1)
            mask(el);
    }

    ajax_loading();
}