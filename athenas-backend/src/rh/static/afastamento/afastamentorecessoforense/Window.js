Ext._define('rh.afastamento.afastamentorecessoforense.Window', {
    extend: 'rh.afastamento.afastamento.Window',
    rest: 'rh.afastamento.afastamentorecessoforense.Restful',

    constructor: function(cfg) {
        rh.afastamento.afastamentorecessoforense.Window.superclass.constructor.call(this, cfg);
    },

    getPanelInformationItems: function(cfg_window){
        var items = [];
        items.push(rh.afastamento.afastamento.Window.superclass.getPanelInformationItems.call(this, cfg_window));
        items.push({
            allowBlank: false,
            fieldLabel: "Data In\u00edcio",
            name: "data_inicio",
            xtype: "datefield"
        });
        items.push({
            allowBlank: false,
            fieldLabel: "Data Prevista Fim",
            name: "data_prevista",
            xtype: "datefield"
        });
        return items;
    },

    getTabPanelItems: function(cfg_window){
        return [
            this.getPanelInformation(cfg_window, {}),
            this.getPanelChange(cfg_window, {}),
            this.getPanelPronlogation(cfg_window, {}),
            this.getPanelDesignationExercise(cfg_window, {}),
            this.getPanelText(cfg_window, {}),
            this.getPanelAttachment(cfg_window, {})
        ];
    },

});

