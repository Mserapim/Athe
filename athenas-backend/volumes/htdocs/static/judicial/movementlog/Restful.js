Ext._define('judicial.movementlog.Restful', {
    extend: 'core.Restful',
    resource: 'EJudMovementLog',

    getFields: function(cfg) {
        if(!this._fields) {
            this._fields = judicial.movementlog.Restful.superclass.getFields.call(this, cfg).concat([
                {type: 'int', name: 'out_court_lawsuit', useNull: true},
                {type: 'string', name: 'out_court_lawsuit_unicode'},
                {type: 'int', name: 'from_location', useNull: true},
                {type: 'string', name: 'from_location_unicode'},
                {type: 'int', name: 'sended_by', useNull: true},
                {type: 'string', name: 'sended_by_unicode'},
                {type: 'date', name: 'sended_at', dateFormat: "d/m/Y H:i"},
                {type: 'int', name: 'to_location', useNull: true},
                {type: 'string', name: 'to_location_unicode'},
                {type: 'int', name: 'received_by', useNull: true},
                {type: 'string', name: 'received_by_unicode'},
                {type: 'date', name: 'received_at', dateFormat: "d/m/Y H:i"},
            ]);
        }

        return this._fields;
    }
});
