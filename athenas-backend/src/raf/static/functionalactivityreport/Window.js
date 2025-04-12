Ext._define('raf.functionalactivityreport.Window', {
    extend: 'core.RestfulWindow',

    rest: 'raf.functionalactivityreport.Restful',

    width: 500,

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
