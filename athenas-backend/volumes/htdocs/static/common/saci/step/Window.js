
Ext._define('common.saci.step.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.saci.step.Restful',

    width: 400,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: []
            });

        return this._formPanel;
    }
});
