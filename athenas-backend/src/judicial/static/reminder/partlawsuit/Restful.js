
Ext._define('judicial.reminder.partlawsuit.Restful', {
    extend: 'judicial.reminder.Restful',

    resource: 'EJudPartLawsuitReminder',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.reminder.lawsuit.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "part_lawsuit"
                }
            ]);

        return this._fields;
    }
});
