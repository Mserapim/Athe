
Ext._define('planning.hiring.manager.Restful', {
    extend: 'core.Restful',

    resource: 'SPCGestorRestful',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.manager.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "user"
                },
                {
                    type: "string",
                    name: "user_unicode"
                },
                {
                    type: "int",
                    name: "tipo"
                },
                {
                    type: "string",
                    name: "tipo_display"
                },
            ]);

        return this._fields;
    }
});
