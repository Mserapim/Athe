Ext._define('rh.socialsecurity.EmploymentBondRestful', {
    extend: 'core.Restful',

    resource: 'SSEmploymentBond',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.socialsecurity.EmploymentBondRestful.superclass.getFields.call(this, cfg).concat([
                {name: 'icons'},
                {type: 'bool', name: 'public_employee'},
                {type: 'bool', name: 'contribution_double'},
                {type: 'int', name: 'modified_by', useNull: true},
                {type: 'string', name: 'modified_by_unicode'},
                {type: 'date', name: 'end_date', dateFormat: 'd/m/Y', useNull: true},
                {type: 'date', name: 'created_at', dateFormat: 'd/m/Y H:i'},
                {type: 'date', name: 'modified_at', dateFormat: 'd/m/Y H:i'},
                {type: 'int', name: 'liquid_days', useNull: true},
                {type: 'int', name: 'raw_days', useNull: true},
                {type: 'int', name: 'created_by', useNull: true},
                {type: 'string', name: 'created_by_unicode'},
                {type: 'string', name: 'employer'},
                {type: 'int', name: 'pension_system', useNull: true},
                {type: 'string', name: 'pension_system_display'},
                {type: 'date', name: 'begin_date', dateFormat: 'd/m/Y'},
                {type: 'int', name: 'deduction', useNull: true},
                {type: 'string', name: 'archive'},
                {type: 'string', name: 'function_name'},
                {type: 'string', name: 'possession_unicode'},
                {type: 'int', name: 'purpose', useNull: true},
                {type: 'string', name: 'purpose_display'},
            ]);

        return this._fields;
    }
});
