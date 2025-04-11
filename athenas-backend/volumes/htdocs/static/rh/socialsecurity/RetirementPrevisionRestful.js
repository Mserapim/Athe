Ext._define('rh.socialsecurity.RetirementPrevisionRestful', {
    extend: 'core.Restful',

    resource: 'SSRetirementPrevision',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.socialsecurity.RetirementPrevisionRestful.superclass.getFields.call(this, cfg).concat([
                {name: 'icons'},
                {type: 'string', name: 'person_sex'},
                {type: 'int', name: 'natural_person', useNull: true},
                {type: 'string', name: 'natural_person_unicode'},
                {type: 'date', name: 'birth_date', dateFormat: 'd/m/Y'},
                {type: 'int', name: 'age'},
                {type: 'int', name: 'last_occupation', useNull: true},
                {type: 'string', name: 'last_occupation_unicode'},
                {type: 'date', name: 'exercise_date', dateFormat: 'd/m/Y'},
                {type: 'date', name: 'age_prevision_date', dateFormat: 'd/m/Y'},
                {type: 'date', name: 'contribution_prevision_date', dateFormat: 'd/m/Y'},
                {type: 'date', name: 'integral_prevision_date', dateFormat: 'd/m/Y'},
                {type: 'bool', name: 'active'},
                {type: 'bool', name: 'before_ec_20_98'},
                {type: 'int', name: 'rgps_liquid_days'},
                {type: 'int', name: 'rpps_liquid_days'},
                {type: 'bool', name: 'negative_previous_bond'}
            ]);

        return this._fields;
    }
});
