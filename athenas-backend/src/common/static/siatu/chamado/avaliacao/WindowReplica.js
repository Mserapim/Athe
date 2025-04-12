/**
 *
 **/
Ext._define('common.siatu.chamado.avaliacao.WindowReplica', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.avaliacao.Restful',

    width: 400,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 90,
                items: [
                    {
                        xtype: 'textfield',
                        width: 275,
                        name: 'satisfacao_display',
                        fieldLabel: 'Satisfacao',
                        allowBlank: true,
                        readOnly: true,
                    },
                    {
                        xtype: 'textfield',
                        width: 275,
                        name: 'presteza_display',
                        fieldLabel: 'Presteza',
                        allowBlank: true,
                        readOnly: true,
                    },
                    {
                        xtype: 'textfield',
                        width: 275,
                        name: 'esclarecimento_display',
                        fieldLabel: 'Esclarecimento',
                        allowBlank: true,
                        readOnly: true,
                    },
                    {
                        xtype: 'textfield',
                        width: 275,
                        name: 'tempo_display',
                        fieldLabel: 'Tempo',
                        allowBlank: true,
                        readOnly: true,
                    },
                    {
                        xtype: 'textarea',
                        width: 275,
                        name: 'sugestao',
                        fieldLabel: 'Sugestão',
                        allowBlank: true,
                        readOnly: true,
                    },
                    {
                        xtype: 'textarea',
                        width: 276,
                        height: 120,
                        name: 'replica',
                        fieldLabel: 'Réplica',
                        allowBlank: true,
                    },
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        common.siatu.chamado.avaliacao.WindowReplica.superclass.constructor.call(this, cfg);

        if (this.values.avaliacao_pk){
            var rest = Ext._create('common.siatu.chamado.avaliacao.Restful', {});
            rest.get(
                this.values.avaliacao_pk,
                {
                    success: {
                        scope: this,
                        fn: function(instance) {
                            this.getFormPanel().getForm().setValues(
                                instance
                            );
                        }
                    }
                }
            )
        }
    }
});

                    