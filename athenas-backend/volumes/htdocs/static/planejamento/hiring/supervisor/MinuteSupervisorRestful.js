Ext._define('planning.hiring.supervisor.MinuteSupervisorRestful', {
  extend: 'planning.hiring.supervisor.SupervisorRestful',

  resource: 'PHMMinuteSupervisor',

  getFields: function(cfg) {
      if(!this._fields) {
          this._fields = planning.hiring.supervisor.MinuteSupervisorRestful.superclass.getFields.call(this, cfg).concat([
              {type: "int", name: "minute", useNull: false},
              {type: "string", name: "minute_unicode"},
          ]);
      }

      return this._fields;
  }
});
