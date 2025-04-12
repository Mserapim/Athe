Ext._define('corregedoria.cirdir.health.healtharea.EvaluatorRestful', {
    extend: 'core.Restful',

    resource: 'CIRDIREvaluator',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.health.healtharea.EvaluatorRestful.superclass.getFields.call(this, cfg).concat([
              {type: "string", name: "name" },
            ]);

        return this._fields;
    }
});
