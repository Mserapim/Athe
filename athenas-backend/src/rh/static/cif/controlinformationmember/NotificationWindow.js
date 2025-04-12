

Ext._define('cif.controlinformationmember.NotificationWindow', {
    extend: 'Ext.Window',

    width: 600,

    height: 360,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'hidden',
                        name: 'pk',
                        value: cfg.params.pk
                    },
                    {
                        title: 'Enviar texto para: ' + cfg.params.employee_name_unicode,
                        flex: 1,
                        border: false,
                        items: [
                            {
                                allowBlank: true,
                                name: "message",
                                xtype: "ckeditor"
                            },
                        ]
                    },
                ]
                    
            });
        return this._formPanel;
    },

    save: function(){
        var form = this.getFormPanel().getForm();
        var rest = Ext._create('cif.controlinformationmember.ControlInformationMemberRestful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('notification', false, 'POST', {
                scope: this,
                params: {
                    pk: form.getValues().pk,
                    message: form.getValues().message,
                },
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                        this.destroy();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Atenção',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponível no momento.'
                    });
                },
            })
        );
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
        	cfg,
        	{
        		title: 'Notificação',
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
                        text: 'Enviar',
                        scope: this,
                        handler: this.save
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]   
			}
		);

		cif.controlinformationmember.NotificationWindow.superclass.constructor.call(this, cfg);
    }
});