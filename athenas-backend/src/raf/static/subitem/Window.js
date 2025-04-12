Ext._define('raf.subitem.Window', {
    extend: 'core.RestfulWindow',

    rest: 'raf.subitem.Restful',

    subItem: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._subItem = value;

            if(dispatch) this.observerSubItem();
        }

        return this._subItem;
    },


    selection: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(!this._selection)
            this._selection = 'legalclass';

        if(value !== undefined) {
            this._selection = value;

            if(dispatch) this.observerSelection();
        }

        return this._selection;
    },

    observerSelection: function() {
        var value = this.selection();
        var item = this.subItem();

        if(value && item) {
            this.getTaxonomyGrid().setParam('taxonomy_type', value);
            this.getTaxonomyGrid().setFilterProperty('classification__taxonomy_type', value, 101, true);

            this.getExcludeTaxonomyGrid().setParam('taxonomy_type', value);
            this.getExcludeTaxonomyGrid().setFilterProperty('exclude_classification__taxonomy_type', value, 101, true);
        }

    },

    observerSubItem: function() {
        var value = this.subItem();

        if(value) {
            this.getSelectionTaxonomy().enable();
            this.getTaxonomyGrid().enable();
            this.getExcludeTaxonomyGrid().enable();
            this.getCalculateGrid().enable();

            this.getTaxonomyGrid().setParam('subitem', value);
            this.getTaxonomyGrid().setFilterProperty('subitem', value, 100, true);

            this.getExcludeTaxonomyGrid().setParam('subitem', value);
            this.getExcludeTaxonomyGrid().setFilterProperty('subitem', value, 100, true);

            this.getCalculateGrid().setParam('subitem', value);
            this.getCalculateGrid().setFilterProperty('subitem', value, 100, true);


        } else {
            this.getSelectionTaxonomy().disable();
            this.getTaxonomyGrid().disable();
            this.getExcludeTaxonomyGrid().disable();
            this.getCalculateGrid().disable();

            this.getTaxonomyGrid().setParam('subitem', 0);
            this.getTaxonomyGrid().removeFilterProperty('subitem', 100, false);
            this.getTaxonomyGrid().getStore().removeAll();

            this.getExcludeTaxonomyGrid().setParam('subitem', 0);
            this.getExcludeTaxonomyGrid().removeFilterProperty('subitem', 100, false);
            this.getExcludeTaxonomyGrid().getStore().removeAll();

            this.getCalculateGrid().setParam('subitem', 0);
            this.getCalculateGrid().removeFilterProperty('subitem', 100, false);
            this.getCalculateGrid().getStore().removeAll();
        }
    },


    getSelectionTaxonomy: function() {
        if(!this._selectionTaxonomy) {
            this._selectionTaxonomy = Ext._create('Ext.form.RadioGroup', {
                xtype: 'radiogroup',
                fieldLabel: 'Classificação',
                hideLabel: true,
                columns: 4,
                vertical: true,
                disabled: true,
                items: [
                    {boxLabel: 'Classe', name: 'classification', inputValue: 'legalclass', checked: true},
                    {boxLabel: 'Assunto', name: 'classification', inputValue: 'legalmatter'},
                    {boxLabel: 'Movimento', name: 'classification', inputValue: 'legalmoviment'},
                    {boxLabel: 'Não procedimental', name: 'classification', inputValue: 'legalprocedure'}
                ]
            });
            this._selectionTaxonomy.on({
                scope: this,
                change: function(me, checked) {
                    this.selection(checked.inputValue);
                }
            });
        }
        return this._selectionTaxonomy;
    },


    getTaxonomyGrid: function() {
        if(!this._taxonomyGrid)
            this._taxonomyGrid = Ext._create('raf.taxonomyclassification.Grid', {
                title: 'Classificação',
                disabled: true,
                frame: false,
                border: false,
                height: 240,
                region: 'center',
                columnAction: false,
                gridAutoLoad: false,
            });

        return this._taxonomyGrid;
    },

    getExcludeTaxonomyGrid: function() {
        if(!this._excludeTaxonomyGrid) {
            this._excludeTaxonomyGrid = Ext._create('raf.taxonomyclassification.Grid', {
                title: 'Exceção',
                disabled: true,
                frame: false,
                border: false,
                height: 200,
                region: 'center',
                columnAction: false,
                gridAutoLoad: false,
            });

            this._excludeTaxonomyGrid.setParam('excludeTaxonomy', true);
        }
        return this._excludeTaxonomyGrid;
    },

    getCalculateGrid: function(cfg) {
        if(!this._calculateGrid) {
            this._calculateGrid = Ext._create('raf.subitem.CalculateGrid', {
                title: 'Cálculo',
                disabled: true,
                frame: false,
                border: false,
                columnAction: false,
                gridAutoLoad: false,
            });
        }
        return this._calculateGrid;
    },

    getSubItemPanel: function() {
        if(!this._subItemPanel)
            this._subItemPanel = Ext._create('Ext.Panel',{
                layout: 'form',
                border: false,
                frame: false,
                items: [
                    {
                        id: 'subitem-panel-title-field',
                        width: 465,
                        allowBlank: false,
                        fieldLabel: "Título",
                        name: "title",
                        xtype: "textfield"
                    },
                    {
                      id: 'subitem-panel-description-field',
                      width: 465,
                      allowBlank: true,
                      fieldLabel: "Descrição",
                      name: "description",
                      xtype: "textarea"
                    },
                    {
                        id: 'subitem-panel-typesubitem-field',
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo',
                        hiddenName: 'typesubitem',
                        width: 465,
                        choiceId: 'raf.TYPE_SUBITEM',
                    },
                    {
                        id: 'subitem-panel-produtivity-field',
                        xtype: 'choicefield',
                        fieldLabel: 'Produtividade',
                        hiddenName: 'productivity',
                        width: 465,
                        choiceId: 'corregedoria.SCORE_TABLE',
                        store: {
                            sortInfo: {
                                field: 'label',
                                direction: 'ASC'
                            }
                        }
                    },
                    {
                        xtype: 'panel',
                        frame: false,
                        border: false,
                        layout: {
                            type: 'hbox',
                            align: 'stretch'
                        },
                        defaults: { flex: 1.0 },
                        height: 25,
                        items: [
                            {
                                xtype: 'checkbox',
                                name: 'activated',
                                boxLabel: 'Ativo',
                                checked: true
                            },
                            {
                                xtype: 'checkbox',
                                name: 'cnmp',
                                boxLabel: 'CNMP',
                                checked: true
                            },
                            {
                                xtype: 'checkbox',
                                name: 'blocked',
                                boxLabel: 'Bloqueado',
                                checked: false
                            },
                            {
                                xtype: 'checkbox',
                                name: 'manual_amount',
                                boxLabel: 'Contagem manual',
                                checked: false
                            },
                        ]
                    },
                ]
            });
        return this._subItemPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                items: [
                    {
                        xtype: 'tabpanel',
                        border: false,
                        frame: false,
                        activeTab: 0,
                        height: 731,
                        items: [
                            this.getMainPanel(cfg),
                            this.getCalculateGrid(cfg)
                        ]
                    }
                ]
            });

        return this._formPanel;
    },


    getMainPanel: function(cfg){
        if(!this._mainTab)
            this._mainTab = Ext._create('Ext.Panel',{
                layout: 'form',
                title: 'Geral',
                border: false,
                frame: true,
                scope: this,
                autoHeight: true,
                items: [
                    this.getSubItemPanel(),
                    {
                        xtype:'fieldset',
                        title: 'Taxonomia',
                        collapsible: false,
                        autoHeight:true,
                        items:[
                            this.getSelectionTaxonomy(),
                        ]
                    },
                    this.getTaxonomyGrid(),
                    this.getExcludeTaxonomyGrid()
                ]
            });
        return this._mainTab;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(cfg, {
            defaultButton: 'subitem-panel-title-field'
        });

        Ext.applyIf(cfg, {
            width: 600,
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.subItem(instance.pk);
                    this.observerSelection();
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });


        raf.subitem.Window.superclass.constructor.call(this, cfg);

        if(this.oId)
            this.subItem(this.oId, false);

        this.observerSubItem();
        this.observerSelection();

    }
});
