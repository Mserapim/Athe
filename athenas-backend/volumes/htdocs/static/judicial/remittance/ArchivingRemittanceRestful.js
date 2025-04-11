Ext._define('judicial.remittance.ArchivingRemittanceRestful', {
    extend: 'judicial.PartLawsuitRestful',

    resource: 'EJudArchivingRemittance',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.remittance.ArchivingRemittanceRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "department",
                    useNull: true
                },
                {
                    type: "string",
                    name: "department_unicode"
                }
            ]);

        return this._fields;
    }
});
