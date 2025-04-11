Ext._define('rh.pvf.sendtelework.Restful', {
    extend: 'core.Restful',

    resource: 'PVFSendTeleWork',


    getFields: function (cfg) {
        if (!this._fields)
            this._fields = rh.pvf.sendtelework.Restful.superclass.getFields.call(this, cfg).concat([
            

            ]);

        return this._fields;
    },

});
   