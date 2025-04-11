/**
 *
 **/
Ext._define('common.siatu.chamado.WindowCancelar', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.Restful',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 70,
                items: [
                	{
                        xtype: 'textarea',
                        width: 240,
                        name: 'motivo_cancelado',
                        fieldLabel: 'Justificativa',
                        allowBlank: false,
                    },

                    
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        common.siatu.chamado.WindowCancelar.superclass.constructor.call(this, cfg);

       
    }
});
