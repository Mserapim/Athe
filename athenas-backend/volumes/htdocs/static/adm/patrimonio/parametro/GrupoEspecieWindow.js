/**
 *
 **/
Ext._define('adm.patrimonio.parametro.GrupoEspecieWindow', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.parametro.GrupoEspecieRestful',

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
                        fieldLabel: 'Código',
                        xtype: 'numberfield',
                        name: 'codigo',
                        allowBlank: false
                    },
                    {
                        fieldLabel: 'Título',
                        xtype: 'textarea',
                        name: 'titulo',
                        allowBlank: false
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
        adm.patrimonio.parametro.GrupoEspecieWindow.superclass.constructor.call(this, cfg);
    }
});
