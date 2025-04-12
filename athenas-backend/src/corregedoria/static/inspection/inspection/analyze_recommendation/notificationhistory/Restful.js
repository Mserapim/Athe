Ext._define('corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONNotificationHistory',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "protocol"},
                {type: "string", name: "protocol_codigo"},
                {type: "string", name: "date"},
                {type: "string", name: "deadline"},
            ]);

        return this._fields;
    }
});
