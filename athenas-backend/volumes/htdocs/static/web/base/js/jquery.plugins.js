(function($){	
	$.fn.ajaxit = function(options)
	{
		var element_name = $(this).get(0).nodeName.toLowerCase();
		if( element_name == 'form' )
		{
			var default_options = {success:null, error:null, dataType:'json', async:true};	
			options = $.extend(default_options, options);
			
			if( $(this).find('input:file').length > 0 )
			{
				var iname = 'ajaxit-iframe-' + new Date().getTime();
				var iframe = $('<iframe name="'+iname+'">').css('display', 'none').one(
					'load',
					function()
					{					
						if( options.success )
						{
							var response = null;
							if( options.dataType == 'json' )
							{
								try
								{ response = eval( "("+$(this).contents().find('body').html()+")" ); }
								catch(e)
								{ if( options.error ) options.error( $(this).contents().find('body').html() ); }								
							}
							else response = $(this).contents().find('body').html();
							
							if( response ) options.success( response ); 	
						}															
											
						iframe.remove();
					}
				);
				$('body').append(iframe);
				$(this).attr('target', iname);
			}
			else
			{			
				$.ajax({
					async:options.async,
					url:$(this).attr('action'),
					type:$(this).attr('method'),
					data:$(this).serialize(),
					dataType:options.dataType,
					success:options.success,
					error:options.error
				});
			}
		}
		else if( element_name == 'a' )
		{
			var default_options = {success:null, error:null, dataType:'html', async:false};	
			options = $.extend(default_options, options);
			
			$.ajax({
				async:options.async,
				dataType:options.dataType,
				url:$(this).attr('href'),				
				success:options.success,
				error:options.error		
			});
		}
		
	}	
})(jQuery);

(function($){
    $.link_modal = function()
    {
        if($(this).get(0).nodeName.toLowerCase() == 'a')
        {
            options = {title:''};
            options.src = $(this).attr('href');
            if( $(this).attr('title') ) options.title = $(this).attr('title');
            
            $('.modal').live(
                'click',
                function()
                {
                    var modal = $('<div style="display:none;" title="'+options.title+'">');                              
                    modal.load(options.src);
                    $('body').append(modal);
                    modal.dialog({
                        close:function()
                        { 
                            modal.dialog('destroy');
                            try {modal.remove();}
                            catch(e){}
                        }
                    });

                    return false;
                }
            );
        }
    }
})(jQuery);

(function($){
	$.fn.mask = function(pattern)
	{
		if( pattern && pattern.length > 0 && $(this).val().length > 0 )
		{
			var out = $(this).val().match(/[a-zA-Z0-9]/g);
			var patt = pattern.split('');			
			var marker = 0;
			$.each(
				pattern.match(/[^#]/g),
				function(index, value)
				{				
					for(i=marker; i<patt.length; i++)
					{					
						if( value == patt[i] )
						{					
							out.splice(i, 0, value);
							marker = i + 1;					
							break;
						}
					}					
				}
			);
			$(this).val(out.join(''));
		}
	}	
})(jQuery);
