Ext._define('auth.jwt.VoucherWindow', {
    extend: 'core.RestfulWindow',

    rest: 'auth.jwt.VoucherRestful',

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
