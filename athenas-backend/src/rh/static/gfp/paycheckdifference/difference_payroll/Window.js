 Ext._define('rh.gfp.paycheckdifference.difference_payroll.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.paycheckdifference.difference_payroll.Restful',

    width: 500,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                {
                    xtype: "combo", 
                    fieldLabel: "Folha", 
                    allowBlank: false, 
                    lazyRender: true, 
                    hiddenName: "folha", 
                    mode: "local", 
                    triggerAction: "all", 
                    store: cfg.ownerGrid.extraConf, 
                    name: "folha",
                    width: 300
                },
                ]
            });

        return this._formPanel;
    }
});
