

Ext._define('common.siatu.chamado.avaliacao.NeutralizarWindow', {
    extend: 'Ext.Window',

    width: 600,

    height: 400,

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
                        flex: 1,
                        border: false,
                        items: [
                            {
                                allowBlank: true,
                                name: "justificativa_netra",
                                xtype: "ckeditor",
                                height:215
                            },
                        ]
                    },
                ]
                    
            });
        return this._formPanel;
    },

    save: function(){
        var form = this.getFormPanel().getForm();
        var rest = Ext._create('common.siatu.chamado.avaliacao.Restful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('neutralizar_chamado', false, 'POST', {
                scope: this,
                params: {
                    pk: form.getValues().pk,
                    justificativa_netra: form.getValues().justificativa_netra,
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
        		title: 'Neutralizar Avaliação de Chamado',
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

		common.siatu.chamado.avaliacao.NeutralizarWindow.superclass.constructor.call(this, cfg);
    }
});