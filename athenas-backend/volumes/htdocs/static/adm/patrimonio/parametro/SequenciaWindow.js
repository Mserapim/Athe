/**
 *
 **/
Ext._define('adm.patrimonio.parametro.SequenciaWindow', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.parametro.SequenciaRestful',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                defaults: {
                    width: 215
                },
                items: [
                    {
                        fieldLabel: 'Título',
                        xtype: 'textarea',
                        name: 'titulo',
                        allowBlank: false
                    },
                    {
                        fieldLabel: 'Próximo numero',
                        xtype: 'numberfield',
                        name: 'proximo',
                        allowBlank: false,
                        value: 1
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

            }
        );

        Ext.apply(
            cfg,
            {
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.parametro.SequenciaWindow.superclass.constructor.call(this, cfg);
    }
});
