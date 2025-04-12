Ext._define('judicial.params.ActingZoneRestful', {
    extend: 'core.Restful',

    resource: 'EJudActingZone',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.params.ActingZoneRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string", 
                    name: "title"
                },
                {
                    type: "bool",
                    name: "enabled"
                }
            ]);

        return this._fields;
    }
});
