Ext._define('rh.gfp.familysalary.FamilySalaryRangeRestful', {
    extend: 'core.Restful',

    resource: 'GFPFamilySalaryRange',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gfp.familysalary.FamilySalaryRangeRestful.superclass.getFields.call(this, cfg).concat([
                {type: "float", name: "inferior_limit", useNull: true},
                {type: "int", name: "family_salary", useNull: true},
                {type: "string", name: "family_salary_unicode"},
                {type: "float", name: "value", useNull: true},
                {type: "float", name: "upper_limit", useNull: true}
            ]);

        return this._fields;
    }
});
