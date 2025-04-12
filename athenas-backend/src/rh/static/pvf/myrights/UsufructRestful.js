Ext._define('rh.pvf.myrights.UsufructRestful', {
  extend: 'core.Restful',

  resource: 'PVFUsufruct',

  getFields: function (cfg) {
    if (!this._fields)
      this._fields = rh.pvf.myrights.UsufructRestful.superclass.getFields.call(this, cfg).concat([
        { name: 'icons', type: 'auto' },
        { name: 'created_by', type: 'int', useNull: true },
        { name: 'created_by_unicode', type: 'string' },
        { name: 'modified_by', type: 'int', useNull: true },
        { name: 'modified_by_unicode', type: 'string' },
        { name: 'created_at', type: 'date', dateFormat: 'd/m/Y H:i' },
        { name: 'modified_at', type: 'date', dateFormat: 'd/m/Y H:i' },
        { name: 'status', type: 'int', useNull: true },
        { name: 'status_display', type: 'string' },
        { name: 'start_date', type: 'date', dateFormat: 'd/m/Y' },
        { name: 'end_date', type: 'date', dateFormat: 'd/m/Y' },
        { name: 'end_date_extected', type: 'date', dateFormat: 'd/m/Y' },
        { name: 'days', type: 'int', useNull: true },
        { name: 'from_scale', type: 'bool' },
        { name: 'activity', type: 'int', useNull: true },
        { name: 'activity_unicode', type: 'string' },
        { name: 'employee_unicode', type: 'string' },
        { name: 'authorized_by_unicode', type: 'string' },
        { name: 'authorized_at', type: 'date', dateFormat: 'd/m/Y H:i' },
      ]);

    return this._fields;
  },

});
