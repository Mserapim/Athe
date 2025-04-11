

Ext._define('estagio.decisaoestagio.DecisaoEstagioWindowForm', {
    extend: 'Ext.Window',

    width: 750,

    height: 450,

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
                        xtype: 'combo',
                        width: 600,
                        allowBlank: false,
                        hiddenName: 'decisao',
                        fieldLabel: 'Decisão',
                        store: [
                            [ 1, 'HOMOLOGA A RECOMENDAÇÃO DA COMISSÃO'],
                            [ 2, 'NÃO HOMOLOGA A RECOMENDAÇÃO DA COMISSÃO'],
                        ],
                        triggerAction: 'all',
                    },
                    {
                        title: 'Considerações',
                        flex: 1,
                        border: false,
                        items: [
                            {
                                allowBlank: true,
                                height: 350,
                                fieldLabel: "Fundamentação",
                                name: "fundamentacao",
                                xtype: "ckeditor"
                            },
                        ]
                    }

                ]
                    
            });
        return this._formPanel;
    },

    save: function(){
        var form = this.getFormPanel().getForm();
        var rest = Ext._create('estagio.decisaoestagio.DecisaoEstagioRestful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('decisao_gestor_orgao', false, 'POST', {
                scope: this,
                params: {
                    pk: form.getValues().pk,
                    decisao: form.getValues().decisao,
                    fundamentacao: form.getValues().fundamentacao,
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
        		title: 'Decisão',
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
                        text: 'Salvar',
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

		estagio.decisaoestagio.DecisaoEstagioWindowForm.superclass.constructor.call(this, cfg);
    }
});