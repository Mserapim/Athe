Ext._define('rh.pvf.sendpointsheet.Restful', {
    extend: 'core.Restful',

    resource: 'PVFSendPointSheet',


    getFields: function (cfg) {
        if (!this._fields)
            this._fields = rh.pvf.sendpointsheet.Restful.superclass.getFields.call(this, cfg).concat([
            

            ]);

        return this._fields;
    },

});
   