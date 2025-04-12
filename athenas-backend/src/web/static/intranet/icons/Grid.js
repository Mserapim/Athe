Ext._define('web.intranet.icons.Grid', {
  extend: 'core.RestfulGrid',

  restWindow: 'web.intranet.icons.Window',
  // rest: 'web.intranet.icons.Restful',

  hideItemsToolbar: ['add', 'remove', 'download'],
  hideActions: ['copy', 'edit', 'remove'],


  getColumnModel: function () {
    if (!this._columnModel)
      this._columnModel = Ext._create(
        'Ext.grid.ColumnModel',
        [
          Ext._create('Ext.grid.RowNumberer'),
          // {
          //   'header': '',
          //   'dataIndex': 'icons',
          //   'width': 25,
          //   'menuDisabled': true,
          //   'renderer': adm.daily.rendererIconGrid
          // },
          { 'header': 'Título', 'dataIndex': 'title', 'id': 'autoExpandColumn' },
          { 'header': 'Possui Ícone?',
            'dataIndex': 'icon_file',
            'width': 80,
            'renderer': function (value) {
              return (value ? "SIM" : "NÃO")
            }
          },
          {
            'header': 'Visivel',
            'dataIndex': 'active',
            'width': 65,
            'renderer': function (value) {
              return (value ? "SIM" : "NÃO")
            }
          },
          {
            'header': 'Posição',
            'dataIndex': 'position',
            'width': 65
          }
        ]
      );

    return this._columnModel;
  },
});

core.RestfulGrid.register(
  'web.intranet.icons.Restful',
  'web.intranet.icons.Grid'
);
