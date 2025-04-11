
Ext._define('rh.seriousdiseases.Restful', {
    extend: 'core.Restful',

    resource: 'RHSeriousDiseasesRestful',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.seriousdiseases.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string",  name: "name"},
                {type: "date",  name: "modified_at",  dateFormat: "d/m/Y H:i"},
                {type: "int",  name: "modified_by",  useNull: true},
                {type: "string", name: "modified_by_unicode"},
                {type: "date",  name: "created_at",  dateFormat: "d/m/Y H:i"},
                {type: "int",  name: "created_by",  useNull: true},
                {type: "string", name: "created_by_unicode"},
            ]);

        return this._fields;
    }
});
