Ext._define('auth.jwt.VoucherRestful', {
    extend: 'core.Restful',

    resource: 'AUTHVoucherManager',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = auth.jwt.VoucherRestful.superclass.getFields.call(this, cfg).concat([
                {type: "int",  name: "user", useNull: true},
                {type: "string", name: "user_unicode"},
                {type: "string", name: "token"},
                {type: "int", name: "voucher_type", useNull: true},
                {type: "string", name: "voucher_type_display"}
            ]);

        return this._fields;
    }
});
