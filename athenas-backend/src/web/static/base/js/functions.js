function ajax_loading(pars)
{
	if( $('.ajax-load').length == 0 )
	{
		css1 = {
			display: 'none',
			position: 'fixed',
			top: 0,
			left: 0,
			width: '100%',
			height: '100%',
			opacity: 0.5,
			background: '#000',
			zIndex: 2000
		};

		$.extend(css1, pars);
		overlay = $('<div>').addClass('ajax-load').css(css1);

		css2 = {
			position:'absolute',
			border:'2px solid #777',
			'border-radius':'7px',
			'-moz-border-radius':'7px',
			'-webkit-border-radius':'7px',
			background:'#fff',
			padding: '5px 8px',
			top: '50%',
			left: '50%',
			transform: 'translate(-50%, -50%)',
			zIndex: 2001
		};
		ajax = $('<div>').addClass('ajax-load').css(css2);
		ajax.html('Aguarde...');

		$('body').append(overlay).append(ajax);
		overlay.fadeIn(
			'slow',
			function()
			{ ajax.fadeIn('slow'); }
		);
	}
	else $('.ajax-load').fadeOut('slow', function(){ $('.ajax-load').remove() });
}
