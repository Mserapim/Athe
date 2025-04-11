 Ext._define('rh.gfp.gcpp.payroll.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.gcpp.payroll.Restful',
    width: 490,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "rest-autocompletefield", 
                        fieldLabel: "Folha", 
                        allowBlank: false,
                        rest: "rh.gfp.gcpp.payroll.Restful",
                        name: "folha"
                    }, 
                ]
            });

        return this._formPanel;
    }
});

