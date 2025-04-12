Ext._define('rh.gfp.familysalary.FamilySalaryRestful', {
    extend: 'core.Restful',

    resource: 'GFPFamilySalary',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gfp.familysalary.FamilySalaryRestful.superclass.getFields.call(this, cfg).concat([
                {type: "date", name: "start_date", dateFormat: "d/m/Y"},
                {type: "date", name: "end_date", dateFormat: "d/m/Y"},
                {type: "int", name: "publication", useNull: true},
                {type: "string", name: "publication_unicode"},
                {type: "string", name: "description"}
            ]);

        return this._fields;
    }
});
