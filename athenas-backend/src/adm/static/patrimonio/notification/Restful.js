Ext._define('adm.patrimony.notification.Restful', {
    extend: 'core.Restful',
    resource: 'PATNotification',

    getFields: function(cfg) {
        if(!this._fields) {
            this._fields = adm.patrimony.notification.Restful.superclass.getFields.call(this, cfg).concat([
                {type: 'auto',   name: 'icons'},

                {type: "int",    name: "id", useNull: true},

                {type: "int",    name: "assets_movement", useNull: true},
                {type: "string", name: "assets_movement_unicode"},

                {type: "int",    name: "destination", useNull: true},
                {type: "string", name: "destination_unicode"},

                {type: "int",    name: "protocol", useNull: true},
                {type: "string", name: "protocol_unicode"},

                {type: "int",    name: "protocol_movement", useNull: true},
                {type: "string", name: "protocol_movement_unicode"},

                {type: "string", name: "content"},

                {type: "int",    name: "received_by", useNull: true},
                {type: "string", name: "received_by_unicode"},
                {type: "date",   name: "received_at", dateFormat: "d/m/Y H:i"},
                {type: "string", name: "received_at_formatted",
                    convert: function(v, data) {
                        if(data.received_at)
                            return data.received_at;
                        return '';
                    }
                },

                {type: "int",    name: "notified_by", useNull: true},
                {type: "string", name: "notified_by_unicode"},
                {type: "date",   name: "notified_at", dateFormat: "d/m/Y H:i"},

                {type: "int",    name: "created_by", useNull: true},
                {type: "string", name: "created_by_unicode"},
                {type: "date",   name: "created_at", dateFormat: "d/m/Y H:i"},

                {type: "int",    name: "modified_by", useNull: true},
                {type: "string", name: "modified_by_unicode"},
                {type: "date",   name: "modified_at", dateFormat: "d/m/Y H:i"},

                {type: "bool", name: "was_sent"},
            ]);
        }

        return this._fields;
    }
});
