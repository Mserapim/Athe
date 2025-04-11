Ext._define('media_indoor.campaign.CampaignManagerWindow', {
  extend: 'core.RestfulWindow',

  rest: 'media_indoor.campaign.Restful',

  width: 600,

  getConfigGroupGrid: function (cfg) {
    if (!this._getConfigGroupGrid) {
      this._getConfigGroupGrid = Ext._create('media_indoor.config_campaign.Grid', {
        title: 'Grupos',
        height: 400,
        restWindow: 'media_indoor.config_campaign.GroupWindow',
        hideColumns: ['campaign_unicode'],
      });
    }

    return this._getConfigGroupGrid;
  },

  getFormPanel: function (cfg) {
    if (!this._formPanel)
      this._formPanel = Ext._create('Ext.form.FormPanel', {
        border: false,
        frame: true,
        items: [
          {
            name: "name",
            fieldLabel: "Título",
            xtype: "textfield",
            allowBlank: false,
            maxLength: 150,
            width: 465
          },
          this.getConfigGroupGrid()
        ]
      });

    return this._formPanel;
  },

  observe: function (value, dispatch) {
    dispatch = (dispatch === undefined ? true : dispatch);

    if (value !== undefined) {
      this._campaign = value;

      if (dispatch)
        this.observeCampaign();
    }

    return this._campaign;
  },

  observeCampaign: function () {
    var value = this.observe();

    if (value) {
      this.getConfigGroupGrid().enable();
      this.getConfigGroupGrid().setParam('campaign', value);
      this.getConfigGroupGrid().setFilterProperty('campaign', value, 100);

    } else {
      this.getConfigGroupGrid().disable();
      this.getConfigGroupGrid().setParam('campaign', 0);
      this.getConfigGroupGrid().setFilterProperty('campaign', 0, 100)
      this.getConfigGroupGrid().getStore().removeAll();

    }
  },

  constructor: function (cfg) {
    cfg = core.nullValue(cfg, {});
    Ext.applyIf(cfg, {
      disableSaveAndNew: true,
      saveAndContinue: {
        scope: this,
        fn: function (instance) {
          this.oId = instance.pk;
          this.action = 'update';
          this.observe(instance.pk);
        }
      }
    });

    media_indoor.campaign.Window.superclass.constructor.call(this, cfg);
    this.observe(cfg.oId === undefined ? null:cfg.oId);
  },
});
