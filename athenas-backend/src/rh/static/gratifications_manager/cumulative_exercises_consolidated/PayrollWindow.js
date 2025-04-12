 Ext._define('rh.gratifications_manager.cumulative_exercises_consolidated.PayrollWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gratifications_manager.cumulative_exercises_consolidated.PayrollRestful',
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
                        rest: "rh.gratifications_manager.cumulative_exercises_consolidated.PayrollRestful",
                        name: "folha"
                    }, 
                ]
            });

        return this._formPanel;
    }
});

