/**
 *
 **/
Ext._define('engine.TaskSessionRestful', {
    extend: 'core.Restful',

    resource: 'ENGTaskSessionRestful',

    getFields: function() {
        if(!this._fields)
            this._fields = engine.TaskSessionRestful.superclass.getFields.call(this).concat([
                {name: 'sid', type: 'string'},
                {name: 'description', type: 'string'},
                {name: 'user_unicode', type: 'string'},
                {name: 'user', type: 'int'},
                {name: 'started_task', type: 'datetime'},
                {name: 'finished_task', type: 'datetime'},
            ]);

        return this._fields;
    }
});
