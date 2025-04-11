Ext._define('judicial.secretary.Window', {
    extend: 'core.RestfulWindow',

    rest: 'judicial.secretary.Restful',

    width:535,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        title: 'Dados da Secretaria',
                        xtype: 'fieldset',
                        items: [
                            {
                                fieldLabel: 'Título',
                                xtype: 'textfield',
                                name: 'title',
                                allowBlank: false,
                                width: 380
                            },
                            {
                                fieldLabel: 'Lotação',
                                xtype: 'rest-autocompletefield',
                                rest: "judicial.params.WorkplaceRestful",
                                name: 'location',
                                width: 380
                            }                            
                        ]
                    },
                    {
                        title: 'Promotorias',
                        xtype: 'fieldset',
                        items: [
                            {
                                xtype: 'rest-relatedfield',
                                title: "Promotorias",
                                hideLabel: true,
                                name: 'execution_organs',
                                displayField: 'nome',
                                relatedname: 'as_secretaries',
                                width: 485,
                                height: 220,
                                rest: 'judicial.secretary.Restful',
                                sourceRest: 'judicial.county.ExecutionOrganRestful',
                                oId: cfg.oId,
                                emptyText: 'Descrição',
                            }
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.getFormPanel().getForm().findField('execution_organs').objectId(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        judicial.secretary.Window.superclass.constructor.call(this, cfg);
    }
});

