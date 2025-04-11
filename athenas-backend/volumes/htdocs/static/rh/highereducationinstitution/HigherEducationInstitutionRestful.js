 Ext._define('rh.highereducationinstitution.HigherEducationInstitutionRestful', {
    extend: 'core.Restful',

    resource: 'RHHigherEducationInstitution',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.highereducationinstitution.HigherEducationInstitutionRestful.superclass.getFields.call(this, cfg).concat([
                {type: 'string', name: 'code'},
                {type: 'string', name: 'name'},
                {type: 'string', name: 'acronym'},
                {type: 'int', name: 'municipality'},
                {type: 'string', name: 'municipality_unicode'},
            ]);

        return this._fields;
    }
});
