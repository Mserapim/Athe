Ext._define('rh.pvf.myrights.AcquisitionPeriodRestful', {
  extend: 'core.Restful',

  resource: 'PVFAcquisitionPeriod',

  getFields: function (cfg) {
    if (!this._fields)
      this._fields = rh.pvf.myrights.AcquisitionPeriodRestful.superclass.getFields.call(this, cfg).concat([
        { name: 'created_by', type: 'int', useNull: true },
        { name: 'created_by_unicode', type: 'string' },
        { name: 'modified_by', type: 'int', useNull: true },
        { name: 'modified_by_unicode', type: 'string' },
        { name: 'created_at', type: 'date', dateFormat: 'd/m/Y H:i' },
        { name: 'modified_at', type: 'date', dateFormat: 'd/m/Y H:i' },
        { name: 'group_period', type: 'int', useNull: true },
        { name: 'group_period_unicode', type: 'string' },
        { name: 'employee', type: 'int', useNull: true },
        { name: 'employee_unicode', type: 'string' },
        { name: 'status', type: 'int', useNull: true },
        { name: 'status_display', type: 'string' },
        { name: 'information', type: 'string' },
        { name: 'start_date_acquisition', type: 'date', dateFormat: 'd/m/Y' },
        { name: 'end_date_acquisition', type: 'date', dateFormat: 'd/m/Y' },
        { name: 'start_date_fruition', type: 'date', dateFormat: 'd/m/Y' },
        { name: 'end_date_fruition', type: 'date', dateFormat: 'd/m/Y' },
        { name: 'previous_period', type: 'int', useNull: true },
        { name: 'previous_period_unicode', type: 'string' },
        { name: 'continuous_period', type: 'bool' },
        { name: 'blocked', type: 'bool' },
        { name: 'automatic_created', type: 'bool' },
        { name: 'days', type: 'int', useNull: true },
        { name: 'paid_days_cache', type: 'int' },
        { name: 'days_not_booked_cache', type: 'int' },
        { name: 'paid_without_payroll', type: 'bool' },
        { name: 'indemnified', type: 'bool' },
        { name: 'suspended_days', type: 'string' },
        { name: 'paycheck_event', type: 'int', useNull: true },
        { name: 'paycheck_event_unicode', type: 'string' },
        { name: 'attachment', type: 'int', useNull: true },
        { name: 'attachment_unicode', type: 'string' },
        { name: 'description', type: 'string' },
        { name: 'booked_days_cache', type: 'int', useNull: true },
        { name: 'days_to_enjoy_cache', type: 'int', useNull: true },
        { name: 'real_days_cache', type: 'int', useNull: true },
        { name: 'icons', type: 'auto' },
        { name: 'annotation', type: 'int', useNull: true },
        { name: 'annotation_unicode', type: 'string' },
        { name: 'note', type: 'bool' },
        { name: 'info', type: 'string' },
      ]);

    return this._fields;
  },

});
