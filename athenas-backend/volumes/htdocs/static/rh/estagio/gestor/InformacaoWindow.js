

Ext._define('estagio.gestor.InformacaoWindow', {
    extend: 'Ext.Window',

    width: 700,

    height: 200,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'fieldset',
                        title: 'Informações do Servidor',
                        layout: 'form',
                        id: 'info_fieldset',
                        items: [
                        {
                            xtype: 'displayfield',
                            labelAlign: 'top',
                            fieldLabel: '<b>Servidor</b>',
                            value: cfg.params.posse_servidor,
                            name: 'lotacao'
                        },
                        {
                            xtype: 'displayfield',
                            labelAlign: 'top',
                            fieldLabel: '<b>Chefe Imediato</b>',
                            value: cfg.params.chefe,
                            name: 'chefe'
                        },
                        {
                            xtype: 'displayfield',
                            labelAlign: 'top',
                            fieldLabel: '<b>Período do Estágio</b>',
                            value: cfg.params.periodo_estagio,
                            name: 'periodo_estagio'
                        }
                        ]
                    }
                ]
                    
            });
        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
        	cfg,
        	{
        		title: 'Informações do Servidor',
        		closable: true,
        	}
        );
		Ext.apply(
			cfg,
			{
				border: false,
				layout: 'fit',
				items: [
					this.getFormPanel(cfg)
				],
                buttons: [
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]   
			}
		);

		estagio.gestor.InformacaoWindow.superclass.constructor.call(this, cfg);
    }
});