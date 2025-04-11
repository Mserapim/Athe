

Ext._define('adm.patrimonio.parametro.EspecieMovimentacaoWindow', {
    extend: 'Ext.Window',

    width: 500,

    height: 100,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'hidden',
                        name: 'pks',
                        value: cfg.params.pks
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Grupo Espécie',
                        name: 'grupo',
                        allowBlank: false,
                        rest: 'adm.patrimonio.parametro.GrupoEspecieRestful',
                    },
                ]

            });
        return this._formPanel;
    },

    save: function(){
        var form = this.getFormPanel().getForm();
        // console.log(form.getValues());
        var rest = Ext._create('adm.patrimonio.parametro.EspecieRestful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('movimentar_grupo', false, 'POST', {
                scope: this,
                params: {
                    pks: form.getValues().pks,
                    grupo: form.getValues().grupo,
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
                        this.scope.getStore().reload();
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
                title: 'Movimentar Grupo Espécie',
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


		adm.patrimonio.parametro.EspecieMovimentacaoWindow.superclass.constructor.call(this, cfg);
    }
});
