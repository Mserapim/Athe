/**
 *
 **/
 Ext._define('judicial.taxonomy.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGridTaxononomy: function() {
        if(!this._GridTaxonomy){
            this._GridTaxonomy = Ext._create('judicial.taxonomy.TaxonomyGrid', {
                region: 'north',
                split: true,
                minHeight: 200,
                maxHeight: 200,
                height: 200
            });
        }

        this._GridTaxonomy.getSelectionModel().on({
            scope: this,
            'rowselect': function(sm, index, record) {
                this.taxonomy(record.id);
            },
            'rowdeselect': function(sm) {
                this.taxonomy(null);
            }
        });

        this._GridTaxonomy.getStore().on({
            scope: this,
            'load': function() {
                this.taxonomy(null);
            }
        });

        this._GridTaxonomy.getStore().on({
            scope: this,
            'load': function() {
                var selected = (this._GridTaxonomy.getSelectionModel().getSelected());

                if(selected)
                    this.taxonomy(selected.get('pk'));
                else
                    this.taxonomy(null);
            }
        });

        return this._GridTaxonomy;
    },

    taxonomy: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._taxonomy = value;

            !prevent && this.observeTaxonomy();
        }

        return this._taxonomy;
    },

    observeTaxonomy: function() {
        value = this.taxonomy();

        if(value) {
            this.getClassTree().taxonomy(value);
            this.getMovimentTree().taxonomy(value);
            this.getMatterTree().taxonomy(value);
            this.getProcedureTree().taxonomy(value);

            this.getClassTree().enable();
            this.getMovimentTree().enable();
            this.getMatterTree().enable();
            this.getProcedureTree().enable();
        }
        else {
            this.getClassTree().taxonomy(null);
            this.getMovimentTree().taxonomy(null);
            this.getMatterTree().taxonomy(null);
            this.getProcedureTree().taxonomy(null);

            // this.getClassTree().disable();
            // this.getMovimentTree().disable();
            // this.getMatterTree().disable();
            // this.getProcedureTree().disable();

        }
    },

    getMovimentTree: function() {
        if(!this._movimentTree){
             this._movimentTree = Ext._create('judicial.taxonomy.LegalMovimentTree', {
                title: 'Movimento',
                autoScroll: true,
                flex: 1,
                margins: '0 4 0 0',
                rootVisible: false,
            });

        }

        return this._movimentTree;
    },

    getMatterTree: function() {
        if(!this._matterTree){
             this._matterTree = Ext._create('judicial.taxonomy.LegalMatterTree', {
                title: 'Assunto',
                autoScroll: true,
                flex: 1,
                margins: '0 4 0 0',
                rootVisible: false,
            });

        }

        return this._matterTree;
    },

    getProcedureTree: function() {
        if(!this._procedureTree){
             this._procedureTree = Ext._create('judicial.taxonomy.LegalProcedureTree', {
                title: 'Não Procedimental',
                autoScroll: true,
                flex: 1,
                rootVisible: false,
            });

        }

        return this._procedureTree;
    },

    getClassTree: function() {
        if(!this._classTree){
             this._classTree = Ext._create('judicial.taxonomy.LegalClassTree', {
                title: 'Classes',
                autoScroll: true,
                flex: 1,
                rootVisible: false,
            });

        }

        return this._classTree;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Taxonomia',
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getGridTaxononomy(),
                    {
                        xtype: 'tabpanel',
                        region: 'center',
                        activeTab: 0,
                        defaults: {
                            autoShow: true,
                        },
                        listeners: {
                            render: function(panel) {
                                var active = panel.getActiveTab();
                                panel.items.each(
                                    function(tab) {
                                        panel.setActiveTab(tab);
                                    }
                                );
                                panel.setActiveTab(0);
                            }
                        },
                        border: false,
                        items: [
                            this.getClassTree(),
                            this.getMovimentTree(),
                            this.getMatterTree(),
                            this.getProcedureTree(),
                        ]
                    }
                ]
            }
        );

        this.is_time = 0;

        judicial.taxonomy.Manage.superclass.constructor.call(this, cfg);
    }
});
