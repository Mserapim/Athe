Ext._define('rh.afastamento.afastamentosindicanciaadm.Window', {
    extend: 'rh.afastamento.afastamento.Window',
    rest: 'rh.afastamento.afastamentosindicanciaadm.Restful',

    constructor: function(cfg) {
        rh.afastamento.afastamentosindicanciaadm.Window.superclass.constructor.call(this, cfg);
    },

    getPanelInformationItems: function(cfg_window){
        var items = rh.afastamento.afastamentosindicanciaadm.Window.superclass.getPanelInformationItems.call(this, cfg_window);
        items.push({
            xtype: "numberfield",
            fieldLabel: "Prazo em dias",
            allowBlank: false,
            allowDecimals: false,
            name: "prazo_dias"
        });
        items.push({
            xtype: "checkbox",
            boxLabel: "Remunerado(influencia na remuneração do servidor)",
            allowBlank: true,
            hideLabel: true,
            checked: true,
            name: "remunerado"
        });
        return items;
    },
});

