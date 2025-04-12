Ext._define('planning.hiring.supervisor.ClassificationRestful', {
  extend: 'core.Restful',

  resource: 'PHSupervisorClassification',

  getFields: function(cfg) {
    if(!this._fields) {
      this._fields = planning.hiring.supervisor.ClassificationRestful.superclass.getFields.call(this, cfg).concat([
        {type: "int", name: "kind", useNull: false},
        {type: "string", name: "kind_display"},
        {type: "bool", name: "active", useNull: true},
      ]);
    }

    return this._fields;
  }
});
