Ext._define('corregedoria.cirdir.health.healtharea.attendance.Restful', {
    extend: 'core.Restful',

    resource: 'CIRDIRHealthAreaEvaluation',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.health.healtharea.attendance.Restful.superclass.getFields.call(this, cfg).concat([
              {type: "string", name: "evaluate_unicode" },
            ]);
        return this._fields;
    }
});
