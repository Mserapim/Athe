/**
 *
 **/
Ext._define('rh.gfp.payroll.EventGrid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gfp.payroll.EventRestful',
    restWindow: 'rh.gfp.payroll.EventWindow',

    keywordFieldMessage: 'Texto',

    hideActions: ['add',],

    showBoolean: function(value){
        return value ? 'SIM' : 'NÃO'
    },

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'genre', 'specie' ,'-','search', '-', 'tags', '-', 'character' , '->', 'download'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: 'Número', dataIndex: 'numero_display', width: 60},
                    {header: 'Título', dataIndex: 'titulo', 'minWidth': 240, id: 'autoExpandColumn'},
                    {header: 'Carater', dataIndex: 'carater_display', width: 150},
                    {header: 'Lançamento', dataIndex: 'lancamento_display', width: 80},
                    {header: 'Tipo', dataIndex: 'tipo', width: 35},
                    {header: 'Tipo Cálculo', dataIndex: 'tipo_calculo_display', width: 90},
                    {header: 'Automático', dataIndex: 'automatico', width: 80, renderer: this.showBoolean},
                    {header: 'Gerenciar Consig?', dataIndex: 'consignment_manager', width: 80, renderer: this.showBoolean},
                    {header: 'Natureza', dataIndex: 'nature_event_unicode', width: 300, hidden: true},
                    {header: 'Ativo', dataIndex: 'active', width: 40, renderer: this.showBoolean},
                ]
            );

        return this._columnModel;
    },

    getConfigActionsItems: function(cfg){
        var menu = rh.gfp.payroll.EventGrid.superclass.getConfigActionsItems.call(this, cfg);

        menu['genre'] = {
                text: 'Gêneros',
                iconCls: 'icon-rh icon-core-indirect',
                scope: this,
                handler: this.genre_window
        };

        menu['specie'] = {
                text: 'Espécies',
                iconCls: 'icon-core icon-core-select',
                scope: this,
                handler: this.specie_window
        };

        menu['tags'] = this.getTagsField();
        menu['character'] = this.getCharacterField();

        return menu;
    },

    genre_window: function(){
        new Ext.Window({
             id: 'genre',
             layout: 'fit',
             title: 'Gêneros',
             autoScroll: false,
             modal: true,
             width:800,
             height: 500,
             items: [ new rh.gfp.payroll.GenreEventGrid({})],
             listeners: {}
         }).show();

    },

    specie_window: function(){
        new Ext.Window({
             id: 'genre',
             layout: 'fit',
             title: 'Gêneros',
             autoScroll: false,
             modal: true,
             width:800,
             height: 500,
             items: [ new rh.gfp.payroll.SpecieEventGrid({})],
             listeners: {}
         }).show();

    },

    getFilterMenu: function() {
        return [
            {
                'text': 'Apenas com Gênero/Espécie',
                'checked': true,
                'hideOnClick': false,
                'scope': this,
                'handler': this.filterTipo
            }
        ];
    },

    filterTipo: function(load) {
        this._filterTipo = core.nullValue(this._filterTipo, 1);

        if(this.canLoad && this._filterTipo == 1) {
            this.setFilterProperty('genre_event__isnull', false, 1011, load);
            this._filterTipo = 2;
        }
        else {
            this.removeFilterProperty('genre_event__isnull', 1011, load);
            this._filterTipo = 1;
        }
    },

    getTagsField: function(cfg) {
        if(!this._tagsField){
            this._tagsField = Ext._create('Ext.form.ComboBox', {
                emptyText: 'Tag',
                width: 200,
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction(
                            'GFPEvent', 'tags'
                        ),
                        disableCaching: false,
                        method: 'GET'
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {name: 'value', type: 'int'},
                            {name: 'description', type: 'string'}
                        ]
                    }),
                }),
                lazyRender: false,
                lazyInit: false,
                triggerAction: 'all',
                typeAhead: true,
                editable: false,
                autoLoad: true,
                displayField: 'description',
                valueField: 'value',
                listeners: {
                    scope: this,
                    select: {
                        buffer: 1,
                        fn: function (combo, record, index) {
                            var tagOld = this.tagObj();
                            this.tagObj(record.data.value);
                            if(tagOld != this.tagObj()){
                                this.filterTag(true);
                            }
                        }
                    }
                }
            });
            this._tagsField.getStore().load();
        }
        return this._tagsField;
    },

    tagObj: function(value, dispatch){
        dispatch = core.nullValue(dispatch, true);

        if(value !== undefined)
            this._tag = value;
        else
            return this._tag;
    },

    filterTag: function (load) {
        if (this.canLoad && this.tagObj() != undefined && this.tagObj() != -1 )
            this.setFilterProperty('tags__value__in', [this.tagObj()], 103, load);
        else
            this.removeFilterProperty('tags__value__in', 103, load);
    },

    getCharacterField: function(cfg) {
        if(!this._characterField){
            this._characterField = Ext._create('Ext.form.ComboBox', {
                emptyText: 'Caráter',
                width: 200,
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction(
                            'GFPEvent', 'character'
                        ),
                        disableCaching: false,
                        method: 'GET'
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {name: 'value', type: 'int'},
                            {name: 'description', type: 'string'}
                        ]
                    }),
                }),
                lazyRender: false,
                lazyInit: false,
                triggerAction: 'all',
                typeAhead: true,
                editable: false,
                autoLoad: true,
                displayField: 'description',
                valueField: 'value',
                listeners: {
                    scope: this,
                    select: {
                        buffer: 1,
                        fn: function (combo, record, index) {
                            var characterOld = this.characterObj();
                            this.characterObj(record.data.value);
                            if(characterOld != this.characterObj()){
                                this.filterCharacter(true);
                            }
                        }
                    }
                }
            });
            this._characterField.getStore().load();
        }
        return this._characterField;
    },

    characterObj: function(value, dispatch){
        dispatch = core.nullValue(dispatch, true);

        if(value !== undefined)
            this._character = value;
        else
            return this._character;
    },

    filterCharacter: function (load) {
        if (this.canLoad && this.characterObj() != undefined && this.characterObj() != -1 )
            this.setFilterProperty('carater', this.characterObj(), 104, load);
        else
            this.removeFilterProperty('carater', 104, load);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                gridAutoLoad: true,
            }
        );
        var gridAutoLoad = cfg.gridAutoLoad;
        cfg.gridAutoLoad = false;

        rh.gfp.payroll.EventGrid.superclass.constructor.call(this, cfg);

        this.gridAutoLoad = gridAutoLoad;
        this.canLoad = true;
        this.removeAllFilterProperty(this.gridAutoLoad);
    },

    __setFilterPropertyDefault: function (gridAutoLoad) {

        this.filterTipo(false);

        this.runLoad(gridAutoLoad);
    },

    removeAllFilterProperty: function (load) {
        this.removeFilterProperty('tags__value__in', 103, false);
        this.removeFilterProperty('carater', 104, false);
        this.removeFilterProperty('genre_event__isnull', 1011, false);

        this.canLoad = true;

        this.__setFilterPropertyDefault(load);
    },

    runLoad: function(gridAutoLoad){
        if (gridAutoLoad) {
            var store = this.getStore();
            store.load({});
        }
    }
});

core.RestfulGrid.register(
    'rh.gfp.payroll.EventRestful',
    'rh.gfp.payroll.EventGrid'
);
