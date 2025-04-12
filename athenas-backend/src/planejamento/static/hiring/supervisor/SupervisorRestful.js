Ext._define('planning.hiring.supervisor.SupervisorRestful', {
  extend: 'core.Restful',

  resource: 'PHAAgreementSupervisor',

  getFields: function(cfg) {
    if(!this._fields) {
      this._fields = planning.hiring.supervisor.SupervisorRestful.superclass.getFields.call(this, cfg).concat([
        {type: "int", name: "employee", useNull: false},
        {type: "string", name: "employee_unicode"},
        {type: "int", name: "kind"},
        {type: "string", name: "kind_display"},
        {type: "string", name: "publication_document"},
        {type: "string", name: "publication_document_unicode"},
        {type: "date", name: "publication_document_date", dateFormat: "d/m/Y", useNull: true},
        {type: "date", name: "begin", dateFormat: "d/m/Y", useNull: false},
        {type: "date", name: "end", dateFormat: "d/m/Y", useNull: true},
        {type: "string", name: "observation"},
      ]);
    }

    return this._fields;
  }
});
