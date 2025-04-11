Ext._define('rh.pvf.absence.paternity.Restful', {
    extend: 'core.Restful',

    resource: 'PVFPaternityAbsence',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.pvf.absence.paternity.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    name: "created_by",
                    type: "int",
                    useNull: true
                },
                {
                    name: "created_by_unicode",
                    type: "string"
                },
                {
                    name: "modified_by",
                    type: "int",
                    useNull: true
                },
                {
                    name: "modified_by_unicode",
                    type: "string"
                },
                {
                    name: "created_at",
                    type: "date",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    name: "modified_at",
                    type: "date",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    name: "employee",
                    type: "int",
                    useNull: true
                },
                {
                    name: "employee_unicode",
                    type: "string"
                },
                {
                    name: "start_date",
                    type: "date",
                    dateFormat: "d/m/Y"
                },
                {
                    name: "end_date",
                    type: "date",
                    dateFormat: "d/m/Y"
                },
                {
                    name: "days",
                    type: "int",
                    useNull: true
                },
                {
                    name: "observation",
                    type: "string"
                },
                {
                    name: "absence_ptr",
                    type: "string"
                },
                {
                    name: "birth_certificate",
                    type: "int",
                    useNull: true
                },
                {
                    name: "birth_certificate_unicode",
                    type: "string"
                },
                {
                    name: "dependent",
                    type: "int",
                    useNull: true
                },
                {
                    name: "dependent_unicode",
                    type: "string"
                },
                {
                    name: "is_childcare_assistence",
                    type: "bool"
                },
                {
                    name: "is_incoming_tax",
                    type: "bool"
                },
                {
                    name: "dependent_type",
                    type: "int"
                }
            ]);

        return this._fields;
    }
});
