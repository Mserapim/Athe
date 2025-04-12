Ext._define('raf.solicitation.Window', {
    extend: 'core.RestfulWindow',

    rest: 'raf.solicitation.Restful',
    width: 600,

    
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
