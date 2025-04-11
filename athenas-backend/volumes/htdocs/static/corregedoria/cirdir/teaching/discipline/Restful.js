Ext._define('corregedoria.cirdir.teaching.discipline.Restful', {
    extend: 'core.Restful',

    resource: 'CIRDIRDiscipline',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.teaching.discipline.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "name" },
            ]);

        return this._fields;
    }
});
