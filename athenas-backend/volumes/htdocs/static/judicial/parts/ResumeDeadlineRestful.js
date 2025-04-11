Ext._define('judicial.parts.ResumeDeadlineRestful', {
    extend: 'judicial.PartLawsuitRestful',

    resource: 'EJudResumeDeadline',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.parts.ReseumeDeadlineRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "suspend_deadline",
                    useNull: true
                }
            ]);

        return this._fields;
    }
});
