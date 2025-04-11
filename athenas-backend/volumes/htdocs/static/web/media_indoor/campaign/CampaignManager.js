Ext._define('media_indoor.campaign.CampaignManager',{
  extend: 'toolkit.widget.TabPanel',

  getCampaignGrid: function() {
    if (!this._campaignGrid){
      this._campaignGrid = Ext._create('media_indoor.campaign.Grid',{
        resource: 'MICampaignManager',
        restWindow: 'media_indoor.campaign.CampaignManagerWindow',
        region: 'north',
        split: true,
        minHeight: 200,
        height: 200,
        hideActions: ['remove']
      });

      this._campaignGrid.getSelectionModel().on({
        scope:  this,
        selectionchange: function(selm){
          if(selm.getSelections().length > 0){
            this.campaign(selm.getSelections()[0].get('pk'));
          }
          else{
            this.campaign(null)
          }
        }
      });
    }

    return this._campaignGrid;
  },

  getContentGrid: function(){
    if (!this._contentGrid){
      var me = this;

      this._contentGrid = Ext._create('media_indoor.content.Grid',{
        title: 'Conteúdos Disponíveis',
        flex: 1.0,
        doubleClickHandler: function(){
          me.addContent();
        },
        border: false,
        gridAutoLoad: false,
        columnAction: false
      });

    }

    return this._contentGrid;
  },

  getContentSelectedGrid: function () {
    if (!this._contentListGrid) {
      var me = this;

      this._contentListGrid = Ext._create('media_indoor.content_list.Grid', {
        title: 'Conteúdos Selecionados',
        flex: 1.0,
        doubleClickHandler: function () {
          me.removeContent();
        },
        border: false,
        gridAutoLoad: false,
        columnAction: false,
        configOrderToolBar: ['search', 'upPosition', 'downPosition', '->'],
        hideColumns: ['campaign_unicode', 'content_unicode']
      });
    }

    return this._contentListGrid;
  },

  campaign: function(value, dispatch){
    dispatch = (dispatch === undefined ? true : dispatch)

    if (value !== undefined){
      this._campaign = value;

      if (dispatch)
        this.observeCampaign();
    }

    return this._campaign;
  },

  observeCampaign: function(){
    var value = this.campaign();

    if(value){
      this.getContentGrid().enable();
      this.getContentGrid().setParam('content_lists__campaign', value);
      this.getContentGrid().setFilterProperty('content_lists__campaign', value, -100);

      this.getContentSelectedGrid().enable();
      this.getContentSelectedGrid().setParam('campaign', value);
      this.getContentSelectedGrid().setFilterProperty('campaign', value, 100);

    }else{
      this.getContentGrid().disable();
      this.getContentGrid().setParam('content_lists__campaign', 0);
      this.getContentGrid().setFilterProperty('content_lists__campaign', 0, -100, false)
      this.getContentGrid().getStore().removeAll();

      this.getContentSelectedGrid().disable();
      this.getContentSelectedGrid().setParam('campaign', 0);
      this.getContentSelectedGrid().setFilterProperty('campaign', 0, 100, false);
      this.getContentSelectedGrid().getStore().removeAll();

    }
  },

  _addContent: function (pkset) {
    var rest = this.getCampaignGrid().factoryRestful();
    var mask = new Ext.LoadMask(this.getEl(), { msg: 'adicionando itens...' });

    mask.show();
    rest.addContent(
      this.campaign(),
      pkset,
      {
        scope: this,
        fn: function () {
          this.getContentGrid().getStore().reload();
          this.getContentSelectedGrid().getStore().reload();
          this.getCampaignGrid().getStore().reload();
        }
      },
      {
        fn: function (message) {
          Ext.Msg.show({
            title: 'Adicionando',
            msg: message,
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
          });
        }
      },
      {
        fn: function () {
          mask.hide();
        }
      }
    );
  },

  addContent: function (selected) {
    selected = (selected || this.getContentGrid().getSelectionModel().getSelections());

    if (selected.length > 0)
      this._addContent(selected.map(function (data) { return data.get('pk'); }));
    else
      Ext.Msg.show({
        title: 'Adicionando itens',
        msg: 'Primeiro selecione os itens que deseja adicionar.',
        icon: Ext.Msg.ERROR,
        buttons: Ext.Msg.OK
      });
  },

  _removeContent: function (pkset) {
    var rest = this.getCampaignGrid().factoryRestful();
    var mask = new Ext.LoadMask(this.getEl(), { msg: 'removendo itens...' });

    mask.show();
    rest.removeContent(
      this.campaign(),
      pkset,
      {
        scope: this,
        fn: function () {
          this.getContentGrid().getStore().reload();
          this.getContentSelectedGrid().getStore().reload();
          this.getCampaignGrid().getStore().reload();
        }
      },
      {
        fn: function (message) {
          Ext.Msg.show({
            title: 'Removendo',
            msg: message,
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
          });
        }
      },
      {
        fn: function () {
          mask.hide();
        }
      }
    );
  },

  removeContent: function (selected) {
    selected = (selected || this.getContentSelectedGrid().getSelectionModel().getSelections());

    if (selected.length > 0)
      this._removeContent(selected.map(function (data) { return data.get('pk'); }));
    else
      Ext.Msg.show({
        title: 'Removendo itens',
        msg: 'Primeiro selecione os itens que deseja remover.',
        icon: Ext.Msg.ERROR,
        buttons: Ext.Msg.OK
      });
  },

  getControlPanel: function () {
    if (!this._controlPanel)
      this._controlPanel = Ext._create('Ext.Panel', {
        width: 40,
        frame: true,
        layout: 'vbox',
        bodyStyle: {
          'border-top': 0,
          'border-bottom': 0
        },
        items: [
          {
            xtype: 'panel',
            flex: 1.0
          },

          {
            xtype: 'button',
            iconCls: 'icon-core icon-core-add-selected',
            width: 28,
            height: 30,
            style: {
              padding: '2px 0 0 0'
            },
            scope: this,
            handler: function () { this.addContent(); }
          },

          {
            xtype: 'button',
            iconCls: 'icon-core icon-core-remove-selected',
            width: 28,
            height: 30,
            style: {
              padding: '2px 0 0 0'
            },
            scope: this,
            handler: function () { this.removeContent(); }
          },
          {
            xtype: 'panel',
            flex: 1.0
          }
        ]
      });

    return this._controlPanel;
  },

  constructor: function (cfg) {
    cfg = cfg ? cfg : {};

    Ext.applyIf(
      cfg,
      {
        title: 'Gestor de Campanhas'
      }
    );

    Ext.apply(
      cfg,
      {
        layout: 'border',
        border: false,
        items: [
          this.getCampaignGrid(),
          {
            region: 'center',
            layout: 'hbox',
            minHeight: 150,
            bodyStyle: {
              'border-left': 0,
              'border-right': 0
            },
            layoutConfig: {
              align: 'stretch'
            },
            items: [
              this.getContentGrid(),
              this.getControlPanel(),
              this.getContentSelectedGrid()
            ]
          }
        ]
      }
    );

    media_indoor.campaign.CampaignManager.superclass.constructor.call(this, cfg);
    this.observeCampaign();
  }
});