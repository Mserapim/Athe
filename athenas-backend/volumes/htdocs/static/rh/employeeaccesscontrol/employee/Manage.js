/**
 *
 **/

Ext._define('rh.employeeaccesscontrol.employee.Manage', {
  extend: 'toolkit.widget.TabPanel',

  getGrid: function () {
    if (!this._grid)
      this._grid = Ext._create('rh.employeeaccesscontrol.employee.Grid', {
        region: 'center'
      });

    return this._grid;
  },

  constructor: function (cfg) {
    cfg = cfg ? cfg : {};

    Ext.applyIf(
      cfg,
      {
        title: 'Controle de Acesso/Servidor'
      }
    );

    Ext.apply(
      cfg,
      {
        layout: 'border',
        items: this.getGrid()
      }
    );

    rh.employeeaccesscontrol.employee.Manage.superclass.constructor.call(this, cfg);
  }
});
