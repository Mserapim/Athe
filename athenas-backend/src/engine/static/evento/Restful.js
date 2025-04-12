/**
 *
 **/
Ext._define('engine.evento.Restful', {
    'extend': 'core.Restful',

    'resource': 'EngEvento',

    'getFields': function() {
        if(!this._fields)
            this._fields = engine.evento.Restful.superclass.getFields.call(this).concat([
                {'name': 'title', 'type': 'string'},
                {'name': 'start_date', 'type': 'date', 'dateFormat': 'd/m/Y H:i'},
                {'name': 'end_date', 'type': 'date', 'dateFormat': 'd/m/Y H:i'},
                {'name': 'resource', 'type': 'string'},
                {'name': 'interface', 'type': 'string'}
            ]);

        return this._fields;
    }
});
