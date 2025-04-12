Ext._define('rh.pvf.absence.familyhealthtreatment.Restful', {
    extend: 'core.Restful',

    resource: 'PVFFamilyHealthTreatmentAbsence',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = rh.pvf.absence.familyhealthtreatment.Restful.superclass.getFields.call(this, cfg).concat([
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
                    name: "medical_certificate",
                    type: "int",
                    useNull: true
                },
                {
                    name: "medical_certificate_unicode",
                    type: "string"
                },
                {
                    name: "person",
                    type: "int",
                    useNull: true
                },
                {
                    name: "person_unicode",
                    type: "string"
                },
                {
                    name: "cid",
                    type: "int",
                    useNull: true
                },
                {
                    name: "cid_unicode",
                    type: "string"
                },
            ]);

        return this._fields;
    }
});
