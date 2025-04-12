Ext._define('rh.pvf.progression_h.Restful', {
    extend: 'core.Restful',

    resource: 'PVFRequestProgressionH',


    getFields: function (cfg) {
        if (!this._fields)
            this._fields = rh.pvf.progression_h.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    name: "progression",
                    type: "int"
                },
                {
                    name: "config",
                    type: "int"
                },
                {
                    name: "publication",
                    type: "int"
                },
            ]);

        return this._fields;
    },

});
   