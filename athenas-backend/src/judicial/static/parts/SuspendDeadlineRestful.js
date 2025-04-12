Ext._define('judicial.parts.SuspendDeadlineRestful', {
    extend: 'judicial.PartLawsuitRestful',

    resource: 'EJudSuspendDeadline',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.parts.SuspendDeadlineRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "remaining_days",
                }
            ]);

        return this._fields;
    }
});
