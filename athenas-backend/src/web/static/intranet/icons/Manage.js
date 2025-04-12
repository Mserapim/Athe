Ext._define('web.intranet.icons.Manage', {
  extend: 'toolkit.widget.TabPanel',

  getGrid: function () {
    if (!this._grid) {
      this._grid = Ext._create('web.intranet.icons.Grid', {
        region: 'center',
        gridAutoLoad: true
      });
    }

    return this._grid;
  },

  constructor: function (cfg) {
    cfg = core.nullValue(cfg, {});

    Ext.applyIf(
      cfg,
      {
        title: 'Menu/Intranet'
      }
    );

    Ext.apply(
      cfg,
      {
        layout: 'border',
        items: [
          this.getGrid(),
        ]
      }
    );

    web.intranet.icons.Manage.superclass.constructor.call(this, cfg);
  }
});

