

Ext._define('apd.periodicevaluationperformance.TextReconsiderationWindow', {
    extend: 'Ext.Window',

    width: 800,

    height: 500,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'fieldset',
                        title: '',
                        layout: 'form',
                        id: 'info_fieldset',
                        items: [
                            {
                                xtype: 'displayfield',
                                labelAlign: 'top',
                                fieldLabel: 'Data do registro',
                                value: cfg.params.date_reconsideration,
                                name: 'date_reconsideration'
                            },
                            {
                                title: 'Texto redigido: ',
                                flex: 1,
                                border: false,
                                items: [
                                    {
                                        allowBlank: true,
                                        height:230,
                                        disabled:true,
                                        value: cfg.params.text_reconsideration,
                                        name: 'text_reconsideration',
                                        xtype: "ckeditor"
                                    },
                                ]
                            },
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
        		title: 'Informações do Pedido de Reconsideração',
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

		apd.periodicevaluationperformance.TextReconsiderationWindow.superclass.constructor.call(this, cfg);
    }
});