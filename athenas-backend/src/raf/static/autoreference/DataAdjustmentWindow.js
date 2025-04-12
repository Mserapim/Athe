var storeCache = {};

Ext._define('raf.autoreference.DataAdjustmentWindow', {
    extend: 'core.RestfulWindow',

    factoryStore: function(cfg) {
        if(!this._factoryStore) {
            this._factoryStore = Ext._create('Ext.data.Store', {
              autoLoad: true,
              proxy: Ext._create('Ext.data.HttpProxy', {
                  url: core.callAction('RAFAutoReference', 'get_dataadjustment')
              }),
              baseParams: {
                  autoreference: cfg.params.autoreference,
              },
              reader: Ext._create('Ext.data.JsonReader', {
                  totalProperty: 'count',
                  root: 'collection',
                  fields: [
                      {name: 'dataadjustment_rendered', type: 'auto'},
                  ]
              }),
            });
            this._factoryStore.load({
                'scope': this,
                'callback': function() {
                    this._document = storeCache.data.items["0"].data.dataadjustment_rendered;
                    this.getTilePanel().enable();
                    this.getTilePanel().setPageContent(this._document);
                }
            });
        }
        return this._factoryStore;

    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                items: [
                    this.getTilePanel()
                ]
            });
        }

        return this._formPanel;
    },

    getTilePanel: function() {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
              disabled: true,
              height: 550,
              minHeight: 300,
            });
        return this._tilePanel;
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [

                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                }
            ];

        return this._buttons;
    },

    constructor: function(cfg) {

        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Solicitação de Ajuste de Atividade',
            width: 900,
            height: 600,
        });

        Ext.apply(cfg, {
            ds: this.factoryStore(cfg),
            items: this.getFormPanel(),
            buttons: [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });

        raf.autoreference.DataAdjustmentWindow.superclass.constructor.call(this, cfg);
        storeCache = this.factoryStore(cfg);
    }
});
