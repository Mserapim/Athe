Ext._define('raf.autoreference.Window', {
    extend: 'core.RestfulWindow',

    rest: 'raf.autoreference.Restful',

    title: 'Auto Referenciado',
    width: 400,
    height: 300,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                ]
            });

        return this._formPanel;
    }
});
