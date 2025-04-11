/**
 *
 **/
Ext._define('common.siatu.chamado.status.concluirWindow', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.Restful',

    width: 705,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelAlign: 'top',
                items: [
                    {
                        xtype: 'ckeditor',
                        name: 'relatorio',
                        fieldLabel: 'Relatório de diagnóstico (4000 caracteres)',
                        toolbar: [
                            ['Source'], ['PasteFromWord'], ['Scayt'],
                            ['Link','Unlink','Anchor'],
                            ['NumberedList','BulletedList'],
                            ['Bold','Italic','Underline', 'Styles','Format', 'TextColor','BGColor']
                        ],
                        autoScroll: true,
                        width: 675,
                        height: 215
                    },
                    {
                    xtype: 'checkbox',
                    width: 295,
                    hideLabel: true,
                    name: 'nao_institucional',
                    boxLabel: 'Não institucional',
                    inputValue:'true',
                    allowBlank: true,
                },
                ]
            });

        return this._formPanel;
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                {
                    text: 'Salvar relatório',
                    scope: this,
                    handler: this.save,
                },
                {
                    text: "Salvar e concluir",
                    handler: function() {
                        Ext.Msg.show({
                            scope: this,
                            title: 'PERGUNTA',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.OKCANCEL,
                            msg: 'Deseja realmente concluir o chamado ' + this.values.identificacao + ' ?',
                            fn: function(button) {
                                if(button == 'ok'){
                                    this.salvar_concluir();
                                }
                            },
                        });
                    },
                    scope: this
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];
        }

        return this._buttons;
    },

    salvar_concluir: function() {
        var form = this.getFormPanel().getForm();
        var restChamado = this.factoryRestful();
        restChamado.update(
            this.oId,
            {
                externalCallback: {
                    scope: this,
                    success: {
                        scope: this,
                        fn: function() {
                            this.concluir();
                            this.destroy();
                        }
                    }
                },
                params: Ext.applyIf(
                    form.getValues(),
                    this.getParams()
                )
            },
            {
                el: this.getEl(),
                waitMessage: 'Persistindo os dados.'
            }
        );
    },


    concluir: function() {
        var rest = Ext._create('common.siatu.chamado.status.Restful', {});
        var cfg = {
            externalCallback: this.status_callback,
            params: {
                status: 4,
                chamado: this.oId,
                insert: true,
            } //status 4 == Aguardando avaliação representado como concluido para atendentes..
        };
        rest.create(
            cfg,
            {
                el: this.getEl(),
                waitMessage: 'Persistindo os dados.'
            }
        );
    }
});
