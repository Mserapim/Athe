Ext._define('judicial.outcourtlawsuit.LawsuitMatterWindow', {
    extend: 'core.RestfulWindow',

    rest: 'judicial.outcourtlawsuit.LawsuitMatterRestful',

    width: 550,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: []
            });

        return this._formPanel;
    },
});

