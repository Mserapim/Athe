/**
 *
 **/
Ext._define('engine.TaskMessageRestful', {
    extend: 'core.Restful',

    resource: 'ENGTaskMessageRestful',

    getFields: function() {
        if(!this._fields)
            this._fields = engine.TaskMessageRestful.superclass.getFields.call(this).concat([
                {name: 'session_unicode', type: 'string'},
                {name: 'session', type: 'int'},
                {name: 'message', type: 'string'},
                {name: 'icons', type: 'auto'},
                {name: 'file_ged_permalink', type: 'string'},
            ]);

        return this._fields;
    }
});
