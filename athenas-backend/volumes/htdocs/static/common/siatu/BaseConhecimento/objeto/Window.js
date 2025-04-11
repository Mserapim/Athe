/**
 *
 **/
Ext._define('common.siatu.BaseConhecimento.objeto.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.BaseConhecimento.objeto.Restful',

    width: 500,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 60,
                items: [
                    {
                        xtype: 'textfield',
                        name: 'descricao',
                        fieldLabel: 'Descricao',
                        allowBlank: false,
                        width: 392,
                    },
                    {
                        fieldLabel: '&nbsp;',
                        labelSeparator: '&nbsp;',
                        boxLabel: 'Área de Informática',
                        name: 'informatica',
                        xtype: 'checkbox',
                    },
                    {
                        xtype: 'rest-relatedfield',
                        frame: true,
                        border: false,
                        title: "Modelos",
                        hideLabel: true,
                        name: 'modelos',
                        relatedname: 'modelos',
                        height: 270,
                        rest: this.rest,
                        sourceRest: 'common.siatu.BaseConhecimento.modelo.Restful',
                        oId: cfg.oId,
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
                    this.getFormPanel().getForm().findField('modelos').objectId(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        common.siatu.BaseConhecimento.objeto.Window.superclass.constructor.call(this, cfg);
    },
});
