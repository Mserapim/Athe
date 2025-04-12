Ext._define('rh.pvf.myrights.RightTypeRestful', {
  extend: 'core.Restful',

  resource: 'PVFRightType',

  getFields: function (cfg) {
    if (!this._fields)
      this._fields = rh.pvf.myrights.RightTypeRestful.superclass.getFields.call(this, cfg).concat([
        { type: 'string', name: 'title' },
        { type: 'int', name: 'days_balance' },
      ]);

    return this._fields;
  }
});
