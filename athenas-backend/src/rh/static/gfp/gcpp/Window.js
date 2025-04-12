Ext._define('rh.gfp.gcpp.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.gcpp.Restful',

    width: 550,

    constructor: function(cfg) {
        rh.gfp.gcpp.Window.superclass.constructor.call(this, cfg);
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "textfield", 
                        fieldLabel: "Servidor", 
                        name: "servidor_unicode",
                        disabled: true,
                        width: 380,
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "Verba", 
                        name: "verba",
                        disabled: true,
                        width: 380,
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "Qtd Dias Confirmado",
                        name: "qtd_dias_confirmado",
                        disabled: true,
                        width: 150,
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "Qtd Dias Calculado",
                        name: "qtd_dias_calculado",
                        disabled: true,
                        width: 150,
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "Valor Calculado", 
                        name: "valor_calculado",
                        allowBlank: true,
                        disabled: true,
                        width: 150,
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "% Deferida", 
                        name: "pct",
                        allowBlank: true,
                        disabled: true,
                        width: 150,
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "Qtd Dias para Pgto",
                        name: "qtd_dias_pgto",
                        allowBlank: true,
                        width: 150,
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: 'Valor para Pgto',
                        name: 'valor_pgto',
                        allowBlank: true,
                    },
                ]
            });

        return this._formPanel;
    }

});