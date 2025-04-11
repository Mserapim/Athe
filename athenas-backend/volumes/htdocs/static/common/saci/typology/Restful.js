
Ext._define('common.saci.typology.Restful', {
    extend: 'core.Restful',

    resource: 'SACITypology',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = common.saci.typology.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "name"
                }
            ]);

        return this._fields;
    }
});
