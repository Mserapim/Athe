Ext._define('judicial.movementlog.Window', {
    extend: 'core.RestfulWindow',
    rest: 'judicial.movementlog.Restful',

    getFormPanel: function() {
    if(!this._formPanel) {
        this._formPanel = Ext._create('Ext.form.FormPanel', {
            border: false,
            frame: true,
            items: []
        });
    }

        return this._formPanel;
    }
});
