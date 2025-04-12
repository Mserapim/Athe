Ext._define('web.cms.post.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'web.cms.post.Window',
    hideItemsToolbar: ['edit', 'download'],
    configOrderToolBar: [
        'add',
        'edit',
        'remove',
        '-',
        'classify',
        '-',
        'categoriesManager',
        '-',
        'categoriesFilter',
        '-',
        'areasFilter',
        '-',
        'search',
    ],
    hideActions: ['copy'],
    keywordFieldMessage: 'Digite o termo para busca e tecle Enter',
    actionColumnWidth: 85,

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create('Ext.grid.ColumnModel', [
                {
                    header: 'Item de publicação',
                    dataIndex: 'title',
                    id: 'autoExpandColumn',
                },
                {
                    header: 'Categoria',
                    dataIndex: 'category_unicode',
                    width: 450,
                },
                {
                    header: 'Criado em',
                    dataIndex: 'create_date',
                },
                {
                    header: 'Ano',
                    dataIndex: 'ref_year',
                    width: 40,
                },
            ]);

        return this._columnModel;
    },

    publish: function (pk) {
        var rest = this.factoryRestful();
        var myMask = new Ext.LoadMask(this.getEl(), {
            msg: 'Processando...',
        });
        myMask.show();
        rest.publish({
            pk: pk,
            success: {
                scope: this,
                fn: function (obj) {
                    this.getStore().reload();
                    myMask.hide();
                },
            },
        });
    },

    getConfigActions: function (cfg) {
        var actions = web.cms.post.Grid.superclass.getConfigActions.call(this, cfg);

        if( this.hideActions.indexOf('publication') < 0 )
        {
            var baseAction = {
                    scope: this,
                    handler: function (action, index) {
                        var record = this.getStore().getAt(index);
                        if (record) this.publish(record.get('pk'));
                    },
                },
                publishAction = {
                    tooltip: 'Remover publicação',
                    getClass: function (v, meta, record) {
                        return (record.get('published')) ? 'icon-16px icon-core icon-core-success' : '';
                    },
                },
                unpublishAction = {
                    tooltip: 'Publicar',
                    getClass: function (v, meta, record) {
                        return (!record.get('published')) ? 'icon-16px icon-core icon-core-error' : '';
                    },
                };

            publishAction = Object.assign(publishAction, baseAction)
            unpublishAction = Object.assign(unpublishAction, baseAction)

            actions.unshift(publishAction);
            actions.unshift(unpublishAction);
        }

        return actions;
    },

    getConfigActionsItems: function(cfg)
    {
        var actionsItems = web.cms.post.Grid.superclass.getConfigActionsItems.call(this, cfg)

        if (actionsItems.add)
        {
            var addButton = Object.assign(actionsItems.add, {text: 'Item de publicação'})
            actionsItems.add = addButton
        }

        if (actionsItems.remove)
        {
            var removeButton = Object.assign(actionsItems.remove, {text: 'Remover Item'})
            actionsItems.remove = removeButton
        }

        return actionsItems;
    },

    getCategoriesGrid: function (cfg) {
        if (!this._categoriesGrid) {
            this._categoriesGrid = Ext._create('web.cms.category.Grid', {
                region: 'center',
                gridAutoLoad: false,
            });

            var filter = [];

            if(cfg.state)
            {
                if(cfg.state.site)
                {
                    filter.push({
                        property: 'sites__slug',
                        value: cfg.state.site,
                        stage: 1000,
                    })
                }

                if(cfg.state.site_pk)
                {
                    filter.push({
                        property: 'sites',
                        value: cfg.state.site_pk,
                        stage: 2000,
                    })
                }
            }

            if (this.category_id)
                filter.push({
                    property: 'parent',
                    value: this.category_id,
                    stage: 3000,
                });

            this._categoriesGrid.setFilter(filter);
        }

        return this._categoriesGrid;
    },

    getCategoriesManagerAction: function (cfg) {
        if (!this._categoriesManagerAction) {
            this._categoriesManagerAction = Ext._create('Ext.Button', {
                tooltip: 'Gestor de Categorias',
                text: 'Gestor de Categorias',
                scope: this,
                iconCls: 'tag-icon',
                handler: function (action, index) {
                    this.getCategoriesManager(cfg).show();
                },
            });
        }

        return this._categoriesManagerAction;
    },

    getCategoriesManager: function (cfg) {
        if (!this._categoriesManager) {
            this._categoriesManager = Ext._create('Ext.Window', {
                width: 800,
                height: 550,
                modal: true,
                title: 'Gestor de Categorias',
                layout: 'border',
                items: [this.getCategoriesGrid(cfg)],
                listeners: {
                    scope: this,
                    close: function (cmp) {
                        cmp.destroy();
                        this._categoriesManager = null;
                        this._categoriesGrid = null;
                    },
                },
            });
        }

        return this._categoriesManager;
    },

    openClassifyByCategory: function() {
        var selected = this.getSelectionModel().getSelections();

        if (selected.length > 0) {
            Ext._create("web.cms.post.ClassifyCategoryWindow", {
                pkset: selected.map(function (row) {
                    return row.get("pk");
                }),
                callback: {
                    success: {
                        fn: function () {
                            this.getStore().reload();
                        },
                        scope: this,
                    },
                },
            }).show();
        } else {
            Ext.Msg.show({
                title: "Classificando categoria",
                msg: "Você precisa selecionar pelo menos um item para ser categorizado.",
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
            });
        }
    },

    openClassifyByYear: function() {
        var selected = this.getSelectionModel().getSelections();

        if (selected.length > 0) {
            Ext._create("web.cms.post.ClassifyYearWindow", {
                pkset: selected.map(function (row) {
                    return row.get("pk");
                }),
                callback: {
                    success: {
                        fn: function () {
                            this.getStore().reload();
                        },
                        scope: this,
                    },
                },
            }).show();
        } else {
            Ext.Msg.show({
                title: "Classificando categoria",
                msg: "Você precisa selecionar pelo menos um item para ser categorizado.",
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
            });
        }
    },

    getClassifyAction: function (cfg) {
        if (!this._classifyAction) {
            this._classifyAction = Ext._create("Ext.Button", {
                tooltip: "Reclassificar",
                text: "Reclassificar",
                scope: this,
                menu: [
                    {
                        text: "Reclassificar por Ano",
                        scope: this,
                        handler: function () {
                            this.openClassifyByYear();
                        },
                    },
                    {
                        text: "Reclassificar por Categoria",
                        scope: this,
                        handler: function () {
                            this.openClassifyByCategory();
                        },
                    },
                ],
            });
        }

        return this._classifyAction;
    },

    getClassifyWindow: function (cfg) {
        Ext.apply(cfg, {
            modal: true,
            width: 800,
            autoHeight: true,
            layout: 'fit',
            api: this.factoryRestful(),
        });

        return Ext._create('web.cms.post.ClassifyWindow', cfg);
    },

    getCategoriesFilterAction: function (cfg) {
        if (!this._categoriesFilterAction) {
            this._categoriesFilterAction = Ext._create('core.fields.ComboField', {
                rest: 'web.cms.category.Restful',
                emptyText: 'Filtrar por categoria',
                resizable: true,
                preFilter: [
                    {
                        property: 'posts__areas__parent__slug',
                        value: cfg.state.site,
                        stage: 1,
                    },
                ],
            });

            var store = this._categoriesFilterAction.getStore(),
                all = new Ext.data.Record({
                    pk: 'zero',
                    unicode: 'Todas as categorias',
                }),
                notClassified = new Ext.data.Record({
                    pk: 'not-classified',
                    unicode: 'Não classificados',
                });

            store.baseParams.limit = 1000;

            store.on('load', function () {
                store.insert(0, all);
                store.insert(1, notClassified);
                store.commitChanges();
            });

            var selected = null;

            this._categoriesFilterAction.on({
                scope: this,
                select: function (cmb) {
                    var value = cmb.getValue();

                    if (selected !== value) {
                        selected = value;

                        this.removeFilterProperty('categories', 1001, false);

                        if (selected === 'not-classified') {
                            this.setFilterProperty('categories', null, 1001, false);
                        } else if (!isNaN(selected)) {
                            this.setFilterProperty('categories', value, 1001, false);
                        }

                        this.getStore().reload();
                    }
                },
            });
        }

        return this._categoriesFilterAction;
    },

    getAreasFilterAction: function (cfg) {
        if (!this._areasFilterAction) {
            this._areasFilterAction = Ext._create('core.fields.ComboField', {
                rest: 'web.cms.area.Restful',
                emptyText: 'Filtrar por área',
                preFilter: [
                    {
                        property: 'parent__slug',
                        value: cfg.state.site,
                        stage: 1,
                    },
                    {
                        property: 'kind_of_content',
                        value: 'post',
                        stage: 2,
                    },
                ],
            });

            var store = this._areasFilterAction.getStore(),
                all = new Ext.data.Record({
                    pk: 'zero',
                    unicode: 'Todas as áreas',
                });

            store.on('load', function () {
                store.insert(0, all);
                store.commitChanges();
            });

            var selected = null;

            this._areasFilterAction.on({
                scope: this,
                select: function(cmb) {
                    var value = cmb.getValue();

                    if (selected !== value) {
                        selected = value;

                        if (selected == 'zero') {
                            this.removeFilterProperty('areas', 2, 1000);
                        } else {
                            this.setFilterProperty('areas', selected, 2, 1000);
                        }
                    }
                }
            });
        }

        return this._areasFilterAction;
    },
});

core.RestfulGrid.register('web.cms.post.Restful', 'web.cms.post.Grid');
