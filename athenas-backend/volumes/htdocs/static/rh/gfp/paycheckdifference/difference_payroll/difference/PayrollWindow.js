 Ext._define('rh.gfp.paycheckdifference.difference_payroll.difference.PayrollWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.paycheckdifference.difference_payroll.difference.PayrollRestful',
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
                        rest: "rh.gfp.paycheckdifference.difference_payroll.difference.PayrollRestful",
                        name: "folha",
                    }, 
                ]
            });

        return this._formPanel;
    }
});

