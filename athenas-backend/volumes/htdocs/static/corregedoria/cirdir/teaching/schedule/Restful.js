Ext._define('corregedoria.cirdir.teaching.schedule.Restful', {
    extend: 'core.Restful',

    resource: 'CIRDIRSchedule',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.teaching.schedule.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "pk" },
                {type: "string", name: "unicode" },
                {type: "int", name: "day_week" },
                {type: "int", name: "day_week_unicode" },
                {type: "int", name: "type_schedule" },
                {type: "int", name: "type_schedule_unicode" },
                {type: "date", name: "date_module", dateFormat: "d/m/Y" },
                {type: "string", name: "start_time" },
                {type: "string", name: "end_time" },
            ]);

        return this._fields;
    }
});
