Ext._define('raf.nonproceduralactivities.Restful', {
  extend: 'core.Restful',
  resource: 'RAFNonProceduralActivities',

  getFields: function(cfg) {
    if(!this._fields) {
      this._fields = raf.nonproceduralactivities.Restful.superclass.getFields.call(this, cfg).concat([
          {type: "int", name: "member", useNull: true},
          {type: "string", name: "member_unicode"},
          {type: "int", name: "legal_procedure", useNull: true},
          {type: "string", name: "legal_procedure_unicode"},
          {type: "date", name: "date", dateFormat: "d/m/Y"},
          {type: "string", name: "description"},
          {type: "string", name: "title"},
          {type: "int", name: "created_by", useNull: true},
          {type: "string", name: "created_by_unicode"},
          {type: "date", name: "created_at"},
          {type: "int", name: "modified_by", useNull: true},
          {type: "string", name: "modified_by_unicode"},
          {type: "date", name: "modified_at"},
      ]);
    }
    return this._fields;
  }
});
