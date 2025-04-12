

Ext._define('rh.falta.AnotacaoWindow', {
    extend: 'Ext.Window',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'container',
                        flex: 1,
                        style: {
                            paddingTop: '5px',
                            paddingBottom: '5px',
                        },
                        items: [
                            {
                                allowBlank: false,
                                fieldLabel: "Considerações",
                                name: "observation",
                                xtype: "ckeditor",
                                value: cfg.params.anotacao,
                                disabled: true
                            },
                        ]
                    },
                ]
            });
        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
        	cfg,
        	{
        		title: 'Anotação',
        		closable: true,
				height: 300,
        		width: 800
        	}
        );
		Ext.apply(
			cfg,
			{
				border: false,
				layout: 'fit',
				items: [
					this.getFormPanel(cfg)
				]
			}
		);
		rh.falta.AnotacaoWindow.superclass.constructor.call(this, cfg);
    }
});