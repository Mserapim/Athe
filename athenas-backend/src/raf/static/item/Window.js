Ext._define('raf.item.Window', {
    extend: 'core.RestfulWindow',

    rest: 'raf.item.Restful',

    width: 600,

    itemQuiz: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._item = value;

            if(dispatch) this.observerItem();
        }

        return this._item;
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
        var item = this.itemQuiz();

        if(value && item) {

            this.getTaxonomyGrid().setParam('taxonomy_type', value);
            this.getTaxonomyGrid().setFilterProperty('classification__taxonomy_type', value, 101, true);

            this.getExcludeTaxonomyGrid().setParam('taxonomy_type', value);
            this.getExcludeTaxonomyGrid().setFilterProperty('exclude_classification__taxonomy_type', value, 101, true);

        }

    },

    observerItem: function() {
        var value = this.itemQuiz();

        if(value) {

            this.getSelectionTaxonomy().enable();
            this.getTaxonomyGrid().enable();
            this.getExcludeTaxonomyGrid().enable();

            this.getTaxonomyGrid().setParam('item', value);
            this.getTaxonomyGrid().setFilterProperty('item', value, 100, true);

            this.getExcludeTaxonomyGrid().setParam('item', value);
            this.getExcludeTaxonomyGrid().setFilterProperty('item', value, 100, true);


        } else {

            this.getSelectionTaxonomy().disable();
            this.getTaxonomyGrid().disable();

            this.getTaxonomyGrid().setParam('item', 0);
            this.getTaxonomyGrid().removeFilterProperty('item', 100, false);
            this.getTaxonomyGrid().getStore().removeAll();

            this.getExcludeTaxonomyGrid().setParam('item', 0);
            this.getExcludeTaxonomyGrid().removeFilterProperty('item', 100, false);
            this.getExcludeTaxonomyGrid().getStore().removeAll();
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
                disabled: true,
                frame: false,
                border: false,
                height: 250,
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
                height: 250,
                region: 'center',
                columnAction: false,
                gridAutoLoad: false,
            });

            this._excludeTaxonomyGrid.setParam('excludeTaxonomy', true);
        }
        return this._excludeTaxonomyGrid;
    },

    getItemPanel: function(cfg) {
        if(!this._itemPanel)
            this._itemPanel = Ext._create('Ext.Panel',{
                layout: 'form',
                border: false,
                frame: false,
                items: [
                    {
                        id: 'item-panel-title-field',
                        width: 465,
                        allowBlank: false,
                        fieldLabel: "Titulo",
                        name: "title",
                        xtype: "textfield",
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
                            }
                        ]
                    },
                ]
            });
        return this._itemPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getItemPanel(cfg),
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

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.apply(cfg, {
            defaultButton: 'item-panel-title-field'
        });

        Ext.applyIf(cfg, {
            width: 600,
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.itemQuiz(instance.pk);
                    this.observerSelection();
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        raf.item.Window.superclass.constructor.call(this, cfg);

        if(this.oId) this.itemQuiz(this.oId, false);

        this.observerItem();
        this.observerSelection();
    }
});
