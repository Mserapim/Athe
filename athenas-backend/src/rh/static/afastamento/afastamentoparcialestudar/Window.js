Ext._define('rh.afastamento.afastamentoparcialestudar.Window', {
    extend: 'rh.afastamento.afastamento.Window',
    rest: 'rh.afastamento.afastamentoparcialestudar.Restful',

    constructor: function(cfg) {
        rh.afastamento.afastamentoparcialestudar.Window.superclass.constructor.call(this, cfg);
    },

    getPanelInformationItems: function(cfg_window){
        var items = rh.afastamento.afastamentoparcialestudar.Window.superclass.getPanelInformationItems.call(this, cfg_window);
        items.push(Ext._create('core.fields.AutocompleteField', {
            fieldLabel: "Órgão",
            allowBlank: false,
            rest: "rh.administrativeunit.Restful",
            name: "instituicao"
        }));
        items.push(Ext._create('core.fields.AutocompleteField', {
            fieldLabel: "Curso",
            allowBlank: true,
            rest: "rh.curso.Restful",
            name: "curso"
        }));
        items.push(Ext._create('core.fields.AutocompleteField', {
            fieldLabel: "Localidade",
            allowBlank: true,
            rest: "rh.localidade.Restful",
            name: "localidade"
        }));

        items.push({
            xtype: "checkbox",
            boxLabel: "Parcial",
            fieldLabel: "",
            allowBlank: false,
            checked: true,
            name: "parcial",
            hidden: true,
        });
        return items;
    },
});

