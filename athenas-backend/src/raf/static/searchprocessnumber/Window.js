Ext._define('raf.searchprocessnumber.Window', {
    extend: 'core.RestfulWindow',

    rest: 'raf.searchprocessnumber.Restful',

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
