
Ext._define('judicial.reminder.lawsuit.Restful', {
    extend: 'judicial.reminder.Restful',

    resource: 'EJudLawsuitReminder',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.reminder.lawsuit.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "lawsuit"
                }
            ]);

        return this._fields;
    }
});
