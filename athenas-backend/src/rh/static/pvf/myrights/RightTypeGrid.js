Ext._define('rh.pvf.myrights.RightTypeGrid', {
  extend: 'core.RestfulGrid',

  rest: 'rh.pvf.myrights.RightTypeRestful',

  getColumnModel: function () {
    if (!this._columnModel)
      this._columnModel = Ext._create(
        'Ext.grid.ColumnModel',
        [
          Ext._create('Ext.grid.RowNumberer'),
          { header: 'Cod', dataIndex: 'pk', width: 50, hidden: true },
          { header: 'Identificação', dataIndex: 'title', id: 'autoExpandColumn' },

          { header: 'Saldo disponível', dataIndex: 'days_balance', width: 100 },
        ]
      );

    return this._columnModel;
  }
});

core.RestfulGrid.register(
  'rh.pvf.myrights.RightTypeRestful',
  'rh.pvf.myrights.RightTypeGrid'
);

