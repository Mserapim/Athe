Ext._define('corregedoria.prontuary.individualperformance.institutionalparticipation.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYDetailInstitutionalParticipation',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.individualperformance.institutionalparticipation.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "validated" },
                {type: "string", name: "contribution" },
            ]);

        return this._fields;
    }
});
