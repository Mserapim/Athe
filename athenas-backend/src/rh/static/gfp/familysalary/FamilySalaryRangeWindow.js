Ext._define('rh.gfp.familysalary.FamilySalaryRangeWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.familysalary.FamilySalaryRangeRestful',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                {
                    xtype: "rest-autocompletefield",
                    fieldLabel: "Salário Familia",
                    allowBlank: false, 
                    rest: "rh.gfp.familysalary.FamilySalaryRestful", 
                    name: "family_salary"
                }, 
                {
                    xtype: "numberfield",
                    decimalPrecision: 2,
                    fieldLabel: "Limite Inferior",
                    allowBlank: false,
                    allowDecimals: true,
                    name: "inferior_limit"
                }, 
                {
                    xtype: "numberfield",
                    decimalPrecision: 2,
                    fieldLabel: "Limite Superior",
                    allowBlank: false,
                    allowDecimals: true,
                    name: "upper_limit"
                },
                {
                    xtype: "numberfield",
                    decimalPrecision: 2,
                    fieldLabel: "Valor",
                    allowBlank: false,
                    allowDecimals: true,
                    name: "value"
                }
            ]
            });

        return this._formPanel;
    }
});

