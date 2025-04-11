Ext._define('rh.gfp.extern.NeoConsig', {
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
                    '<p style="font-size: 20px;"><b>Passos para realizar uma consignação:</b></p>'+
                    '<ol style="text-align:justify">'+
                    '<li style="width: 400px; margin-bottom:7px; font-size: small;">Acessar o link abaixo para entrar no sistema de consignação, mas leia as instruções abaixo;</li>'+
                    '<li style="width: 400px; margin-bottom:7px; font-size: small;">Verificar sua margem, em caso de dúvida ligue no RH (3216-7565);</li>'+
                    '<li style="width: 400px; margin-bottom:7px; font-size: small;">Ao lado do campo Selecione a Matricula, clique em "<b>Gerar Token</b>"</li>'+
                    '<li style="width: 400px; margin-bottom:7px; font-size: small;">Selecione o prazo de tempo que seu token terá validade.</li>'+
                    '<li style="width: 400px; margin-bottom:7px; font-size: small;">Informe sua senha da Consignação e clique em confirmar (botão verde)</li>'+
                    '<li style="width: 400px; margin-bottom:7px; font-size: small;">Após seguir os passos acima será gerado o Token, que deve ser instituição financeira desejada.</li>'+
                    '</ol>'+
                    '<a style="text-decoration: none; color:#2779aa" href="{url}" target="_blank"> Clique aqui para acesso ao Sistema de Consignação </a>'+
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
			    title: 'Sistema de Consignações',
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

		rh.gfp.extern.NeoConsig.superclass.constructor.call(this, cfg);
	}
});