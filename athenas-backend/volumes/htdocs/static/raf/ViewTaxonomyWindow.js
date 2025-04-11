var storeCache = {};
Ext._define('raf.ViewTaxonomyWindow', {
    extend: 'Ext.Window',

    factoryStore: function(cfg) {
        if(!this._factoryStore) {
            this._factoryStore = Ext._create('Ext.data.Store', {
                  autoLoad: true,
                  proxy: Ext._create('Ext.data.HttpProxy', {
                      url: core.callAction('RAFActivity', 'get_taxonomy')
                  }),
                  baseParams: {
                      quiz_id: cfg.params.quiz_id,
                      item_id: cfg.params.item_id,
                      subitem_id: cfg.params.subitem_id,
                  },
                  reader: Ext._create('Ext.data.JsonReader', {
                      totalProperty: 'count',
                      root: 'collection',
                      fields: [
                          {name: 'quiz_id', type: 'auto'},
                          {name: 'quiz_display', type: 'auto'},
                          {name: 'item_id', type: 'auto'},
                          {name: 'item_display', type: 'auto'},
                          {name: 'subitem_id', type: 'auto'},
                          {name: 'subitem_display', type: 'auto'},
                      ]
                  })
              });
              this._factoryStore.load({
                  'scope': this,
                  'callback': function() {
                      this.getFormPanel().getForm().setValues(storeCache.data.items["0"].data);

                      this.getTaxonomyClassesGrid().enable();
                      this.getTaxonomyClassesGrid().addFilterProperty('quizzes', storeCache.data.items["0"].data.quiz_id, 101, true);
                      this.getExcludesTaxonomyClassesGrid().enable();
                      this.getExcludesTaxonomyClassesGrid().addFilterProperty('exclude_quizzez', storeCache.data.items["0"].data.quiz_id, 101, true);
                      this.getTaxonomyAssuntosGrid().enable();
                      this.getTaxonomyAssuntosGrid().addFilterProperty('classification__taxonomy_type__in', ['legalclass', 'legalmatter'], 100, false);
                      this.getTaxonomyAssuntosGrid().addFilterProperty('item', storeCache.data.items["0"].data.item_id, 101, true);
                      this.getExcludesTaxonomyAssuntosGrid().enable();
                      this.getExcludesTaxonomyAssuntosGrid().addFilterProperty('exclude_classification__taxonomy_type__in', ['legalclass', 'legalmatter'], 100, false);
                      this.getExcludesTaxonomyAssuntosGrid().addFilterProperty('item', storeCache.data.items["0"].data.item_id, 101, true);
                      this.getTaxonomyMovimentosGrid().enable();
                      this.getTaxonomyMovimentosGrid().addFilterProperty('classification__taxonomy_type', 'legalmoviment', 100, false);
                      this.getTaxonomyMovimentosGrid().addFilterProperty('subitem', storeCache.data.items["0"].data.subitem_id, 101, true);
                      this.getExcludesTaxonomyMovimentosGrid().enable();
                      this.getExcludesTaxonomyMovimentosGrid().addFilterProperty('exclude_classification__taxonomy_type', 'legalmoviment', 100, false);
                      this.getExcludesTaxonomyMovimentosGrid().addFilterProperty('subitem', storeCache.data.items["0"].data.subitem_id, 101, true);
                  }
              })
          }
          return this._factoryStore;
    },

    getTaxonomyClassesGrid: function() {
        if(!this._taxonomyClassesGrid)
            this._taxonomyClassesGrid = Ext._create('judicial.taxonomy.LegalClassGrid', {
                disabled: true,
                frame: false,
                border: false,
                height: 170,
                region: 'center',
                columnAction: false,
                gridAutoLoad: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'search', '-'],
                hideColumns: ['version_unicode'],
                doubleClickHandler: function() {},
            });
        return this._taxonomyClassesGrid;
    },

    getTaxonomyClasses: function() {
        if(!this._taxonomyClasse)
            this._taxonomyClasse = Ext._create('Ext.Panel',{
                title: 'Classificação',
                layout: 'form',
                border: false,
                frame: false,
                autoHeight: true,
                items: [
                  this.getTaxonomyClassesGrid(),
                ]
            });
        return this._taxonomyClasse;
    },

    getExcludesTaxonomyClassesGrid: function() {
        if(!this._excludesTaxonomyClassesGrid)
            this._excludesTaxonomyClassesGrid = Ext._create('judicial.taxonomy.LegalClassGrid', {
                disabled: true,
                frame: false,
                border: false,
                height: 170,
                region: 'center',
                columnAction: false,
                gridAutoLoad: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'search', '-'],
                hideColumns: ['version_unicode'],
                doubleClickHandler: function() {},
            });
        return this._excludesTaxonomyClassesGrid;
    },

    getExcludesTaxonomyClasses: function() {
        if(!this._excludesTaxonomyClasse)
            this._excludesTaxonomyClasse = Ext._create('Ext.Panel',{
                title: 'Exceção',
                layout: 'form',
                border: false,
                frame: false,
                autoHeight: true,
                items: [
                    this.getExcludesTaxonomyClassesGrid(),
                ]
            });
        return this._excludesTaxonomyClasse;
    },

    getTaxonomyAssuntosGrid: function() {
        if(!this._taxonomyAssuntosGrid)
            this._taxonomyAssuntosGrid = Ext._create('raf.taxonomyclassification.Grid', {
                disabled: true,
                frame: false,
                border: false,
                height: 170,
                region: 'center',
                columnAction: false,
                gridAutoLoad: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'search', '-'],
                doubleClickHandler: function() {},
            });
        return this._taxonomyAssuntosGrid;
    },

    getTaxonomyAssuntos: function() {
        if(!this._taxonomyAssuntos)
            this._taxonomyAssuntos = Ext._create('Ext.Panel',{
                title: 'Classificação',
                layout: 'form',
                border: false,
                frame: false,
                autoHeight: true,
                items: [
                  this.getTaxonomyAssuntosGrid(),
                ]
            });
        return this._taxonomyAssuntos;
    },

    getExcludesTaxonomyAssuntosGrid: function() {
        if(!this._excludesTaxonomyAssuntosGrid)
            this._excludesTaxonomyAssuntosGrid = Ext._create('raf.taxonomyclassification.Grid', {
                disabled: true,
                frame: false,
                border: false,
                height: 170,
                region: 'center',
                columnAction: false,
                gridAutoLoad: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'search', '-'],
                doubleClickHandler: function() {},
            });
        return this._excludesTaxonomyAssuntosGrid;
    },

    getExcludesTaxonomyAssuntos: function() {
        if(!this._excludesTaxonomyAssuntos)
            this._excludesTaxonomyAssuntos = Ext._create('Ext.Panel',{
                title: 'Exceção',
                layout: 'form',
                border: false,
                frame: false,
                autoHeight: true,
                items: [
                    this.getExcludesTaxonomyAssuntosGrid(),
                ]
            });
        return this._excludesTaxonomyAssuntos;
    },

    getTaxonomyMovimentosGrid: function() {
        if(!this._taxonomyMovimentosGrid)
            this._taxonomyMovimentosGrid = Ext._create('raf.taxonomyclassification.Grid', {
                disabled: true,
                frame: false,
                border: false,
                height: 170,
                region: 'center',
                columnAction: false,
                gridAutoLoad: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'search', '-'],
                doubleClickHandler: function() {},
            });
        return this._taxonomyMovimentosGrid;
    },

    getTaxonomyMovimentos: function() {
        if(!this._taxonomyMovimentos)
            this._taxonomyMovimentos = Ext._create('Ext.Panel',{
                title: 'Classificação',
                layout: 'form',
                border: false,
                frame: false,
                autoHeight: true,
                items: [
                  this.getTaxonomyMovimentosGrid(),
                ]
            });
        return this._taxonomyMovimentos;
    },

    getExcludesTaxonomyMovimentosGrid: function() {
        if(!this._excludesTaxonomyMovimentosGrid)
            this._excludesTaxonomyMovimentosGrid = Ext._create('raf.taxonomyclassification.Grid', {
                disabled: true,
                frame: false,
                border: false,
                height: 170,
                region: 'center',
                columnAction: false,
                gridAutoLoad: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'search', '-'],
                doubleClickHandler: function() {},
            });
        return this._excludesTaxonomyMovimentosGrid;
    },

    getExcludesTaxonomyMovimentos: function() {
        if(!this._excludesTaxonomyMovimentos)
            this._excludesTaxonomyMovimentos = Ext._create('Ext.Panel',{
                title: 'Exceção',
                layout: 'form',
                border: false,
                frame: false,
                autoHeight: true,
                items: [
                    this.getExcludesTaxonomyMovimentosGrid(),
                ]
            });
        return this._excludesTaxonomyMovimentos;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                  {
                      xtype:'fieldset',
                      title: 'Classes',
                      collapsible: false,
                      height: 250,
                      items:[
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Questionário',
                            name: 'quiz_display',
                            hideLabel: true,
                        },
                        {
                            xtype: 'tabpanel',
                            border: false,
                            frame: false,
                            activeTab: 0,
                            items: [
                                this.getTaxonomyClasses(),
                                this.getExcludesTaxonomyClasses(),
                            ]
                        }
                      ]
                  },
                  {
                      xtype:'fieldset',
                      title: 'Assuntos',
                      collapsible: false,
                      height: 250,
                      items:[
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Assunto',
                            name: 'item_display',
                            hideLabel: true,
                        },
                        {
                            xtype: 'tabpanel',
                            border: false,
                            frame: false,
                            activeTab: 0,
                            items: [
                                this.getTaxonomyAssuntos(),
                                this.getExcludesTaxonomyAssuntos(),
                            ]
                        }
                      ]
                  },
                  {
                      xtype:'fieldset',
                      title: 'Movimentos',
                      collapsible: false,
                      height: 250,
                      items:[
                        {
                            xtype: 'displayfield',
                            fieldLabel: 'Movimento',
                            name: 'subitem_display',
                            hideLabel: true,
                        },
                        {
                            xtype: 'tabpanel',
                            border: false,
                            frame: false,
                            activeTab: 0,
                            items: [
                                this.getTaxonomyMovimentos(),
                                this.getExcludesTaxonomyMovimentos(),
                            ]
                        }
                      ]
                  },
                ]
            });
        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            title: 'Classificação   Taxonômica',
            width: 700,
            height: 850,
        });
        Ext.apply(cfg, {
            ds: this.factoryStore(cfg),
            items: [
              this.getFormPanel(),
            ],
            buttons: [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });
        raf.ViewTaxonomyWindow.superclass.constructor.call(this, cfg);
        storeCache = this.factoryStore(cfg);
    }

});
