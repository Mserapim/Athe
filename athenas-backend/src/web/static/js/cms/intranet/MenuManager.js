Ext._define('web.cms.intranet.MenuManager', {
  extend: 'toolkit.widget.TabPanel',

  getGrid: function () {
    if (!this._grid) {
      this._grid = Ext._create('web.cms.area.Grid', {
        region: 'center',
        gridAutoLoad: false,
      });

      var filter = [
        {
          property: 'active',
          value: 'on',
          stage: 1
        },
        {
          property: "slug",
          value: 'intranet',
          stage: 2,
        },
        {
          property: "parent__slug",
          value: 'intranet',
          stage: 2,
        }
      ];

      this._grid.setFilter(filter);

      this._grid.getSelectionModel().on({
        scope: this,
        selectionchange: function (sm) {
          var selection = sm.getSelections();

          if (selection.length > 0) {
            this.area(selection[0].get("pk"));
          } else {
            this.area(null);
          }
        },
      });
    }

    return this._grid;
  },

  categoryPanel: function (cfg) {
    if (!this._categoryPanel) {
      this._categoryPanel = Ext._create("web.cms.category.Grid", {
        title: "Categorias",
        region: "south",
        minHeight: 320,
        height: 320,
        split: true,
        gridAutoLoad: false,
      });
    }

    return this._categoryPanel;
  },

  area: function (value, dispatch) {
    dispatch = dispatch === undefined ? true : dispatch;

    if (value) {
      this._area = value;

      if (dispatch) {
        this.observeArea();
      }
    }

    return this._area;
  },

  observeArea: function () {
    var value = this.area();

    if (value) {
      this.categoryPanel().enable();
      this.categoryPanel().setParam('sites', [value]);
      this.categoryPanel().setFilterProperty('sites', value, 100);
    } else {
      this.categoryPanel().disable();
      this.categoryPanel().setFilterProperty("sites", 0, 100, false);
      this.categoryPanel().getStore().removeAll();
    }
  },

  constructor: function (cfg) {
    cfg = cfg || {};

    this.state = cfg.initialState || {};

    var site = sessionStorage.getItem("site");
    if (site) this.state.site_pk = site;

    sessionStorage.setItem("cms-state", JSON.stringify(this.state));

    Ext.applyIf(cfg, {
      title: 'Gestor de Menus',
      layout: 'border',
      items: [
        this.getGrid(),
        this.categoryPanel()
      ]
    });

    web.cms.intranet.MenuManager.superclass.constructor.call(this, cfg);
  }
});
