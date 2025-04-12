Ext._define('rh.gfp.extern.ConsigFacil', {
	extend: 'toolkit.widget.TabPanel',

	getMain: function(url){
		if(!this._panel)
		this._panel = new Ext.Panel({
		    region: 'center',
		    autoEl: {tag: 'center'},
		    tpl: this.getTpl(),
            data: {url: url},
            preventBodyReset: true,
	    });

		return this._panel;
	},


    getTpl: function() {

        if(!this._tpl){
            this._tpl = new Ext.XTemplate(
                '<div style="border:none; margin:30px auto; display:table">'+
                    '<p style="font-size: 20px;"><b>Acesse <a href="{url}" target="_blank"> aqui</a></b></p>'+                    
                    '<ol style="width: 400px; margin-bottom:7px; text-align:justify;">Caso seja o primeiro acesso:</ol>'+
                    '<ol style="text-align:justify">'+
                    '<li style="width: 400px; margin-bottom:7px; font-size: small;">Clicar no link <b>CRIAR OU RECUPERAR SENHA</b>, localizado no canto inferior esquerdo da tela de login</li>'+
                    '<li style="width: 400px; margin-bottom:7px; font-size: small;">Preencher os dados solicitados em tela: <b>CPF</b> e <b>Matrícula</b> e confirmar o <b>CAPTCHA</b></b></li>'+
                    '<li style="width: 400px; margin-bottom:7px; font-size: small;">o sistema vai gerar uma senha provisória. Copie-a</li>'+
                    '<li style="width: 400px; margin-bottom:7px; font-size: small;">Retorne à página de login e acesso o sistema inserindo sua folha, matrícula e a senha que acabou de copiar</li>'+
                    '<li style="width: 400px; margin-bottom:7px; font-size: small;">Nesse primeiro acesso, o sistema exigirá a troca da senha e você poderá criar a sua. Essa nova senha, precisa ter pelo menos 8 caracteres e conter letras (a, b, c...), números (1, 2, 3...) e símbolos (@, #, %...).</li>'+
					'<p>Também disponível para <a href="https://play.google.com/store/apps/details?id=com.consigfacilapp" target="_blank"> Android</a> e <a href="https://apps.apple.com/br/app/consigfacil/id1385054142" target="_blank">iOS</a></p>'+
                    '</ol>'+
                '</div>'
            );
        }
        return this._tpl;
    },


	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			    title: 'Agora é ConsigFácil',
                layout: 'border',
                autoScroll: false,
                items:[this.getMain(cfg.url)]
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[ 
					this.getMain(),
				]
			}
		);

		rh.gfp.extern.ConsigFacil.superclass.constructor.call(this, cfg);
	}
});