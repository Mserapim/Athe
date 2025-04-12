Ext._define('planning.hiring.supervisor.AgreementSupervisorRestful', {
  extend: 'planning.hiring.supervisor.SupervisorRestful',

  resource: 'PHAAgreementSupervisor',

  getFields: function(cfg) {
      if(!this._fields) {
          this._fields = planning.hiring.supervisor.AgreementSupervisorRestful.superclass.getFields.call(this, cfg).concat([
              {type: "int", name: "agreement", useNull: false},
              {type: "string", name: "agreement_unicode"},
          ]);
      }

      return this._fields;
  }
});
