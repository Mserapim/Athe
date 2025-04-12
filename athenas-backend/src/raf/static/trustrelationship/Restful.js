Ext._define('raf.trustrelationship.Restful', {
    extend: 'core.Restful',

    resource: 'RAFTrustRelationship',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.trustrelationship.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    name: "icons"
                },
                {
                    type: "string",
                    name: "employee_unicode"
                },
                {
                    type: "integer",
                    name: "employee",
                    useNull: true
                },
                {
                    type: "string",
                    name: "trust_employee_unicode"
                },
                {
                    type: "integer",
                    name: "trust_employee",
                    useNull: true
                },
                {
                    type: "bool",
                    name: "activated"
                },

            ]);

        return this._fields;
    }
});
