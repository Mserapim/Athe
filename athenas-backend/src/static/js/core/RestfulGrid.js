/**
 *
 **/
Ext._define('core.RestfulGrid', {
    extend: 'Ext.grid.GridPanel',

    restWindow: undefined,

    rest: undefined,

    /* @hideColumns
    * Este atributo possibilita que as colunas com seus dataIndex listado aqui sejam
    * ocultadas (hidden = true)
    * OBS.: Deve-se expecificar o dataIndex
    */
    hideColumns: [],

    /* @onlyColumns
    * Este atributo possibilita que as colunas com seus dataIndex listado aqui sejam
    * exclusivamente mostrados (hidden = true para os outros)
    * OBS.: Deve-se expecificar o dataIndex
    */
    onlyColumns: [],

    /* @hideItemsToolbar
    * Este atributo possibilita a remoção dos items padroes do toolbar:
    *  'add'=> botão adicionar
    *  'edit' => botão editar
    *  'remove' => botão remover
    *  'search' => items do field de busca
    *  'download' => botao de download
    */
    hideItemsToolbar: [],

    /* @hideActions
    * Este atributo possibilita a ocultação de algumas ou todas as actions. No entanto as custom actions serão sempre mostradas
    *  'add'=> botão adicionar
    *  'edit' => botão editar
    *  'remove' => botão remover
    *  'download' => botao de download
    */
    hideActions: [],

    actionColumnWidth: 70,

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'search', '->', 'download'],

    keywordFieldMessage: 'Motor de buscas',

    keywordFieldWidth: 320,

    toolbarHideLabel: false,

    updateMulti: false,

    pageSize: 30,

    /**
     * Driver de persistencia restful ou local
     **/
    driver: 'restful',

    statics: {
        'restfulRelations': {},

        'register': function(restClass, gridClass) {
            core.RestfulGrid.restfulRelations[restClass] = gridClass;
        },

        'factoryGrid': function(rest, extraConfig) {
            var classname = core.RestfulGrid.restfulRelations[rest];
            if(!classname)
                throw 'Nenhum grid foi registrado para ' + rest;
            else {
                return Ext._create(classname, extraConfig);
            }
        }
    },

    getFilter: function() {
        var store = this.getStore();
        var strFilter = core.nullValue(store.baseParams.filter, '[]');
        var filter;

        try {
            filter = Ext.decode(strFilter);
        }
        catch(e) {
            filter = [];
        }
        finally {
            return filter;
        }
    },

    setFilter: function(filter, autoload) {
        autoload = core.nullValue(autoload, true);

        var store = this.getStore();
        store.baseParams.filter = Ext.encode(filter);

        if(autoload) store.load({});
    },

    addFilterProperty: function(property, value, stage, autoload) {
        var filter = this.getFilter();
        stage = core.nullValue(stage, 0);

        filter.push({property: property, value: value, stage: stage});
        this.setFilter(filter, autoload);
    },

    removeFilterProperty: function(property, stage, autoload) {
        var oldFilter = this.getFilter();
        var newFilter = [];

        oldFilter.forEach(
            function(item) {
                if((item.property != property) ||
                   (item.property == property && (stage !== undefined && item.stage != stage)))
                    newFilter.push(item);
            }
        );

        this.setFilter(newFilter, autoload);
    },

    setFilterProperty: function(property, value, stage, autoload) {
        var flag = false;
        var oldFilter = this.getFilter();
        var newFilter = [];
        stage = core.nullValue(stage, 0);

        oldFilter.forEach(
            function(item) {
                if(!flag && item.property == property && item.stage == stage) {
                    item.value = value;
                    flag = true;
                }

                newFilter.push(item);
            }
        );

        if(!flag)
            this.addFilterProperty(property, value, stage, autoload);
        else
            this.setFilter(newFilter, autoload);
    },

    factoryRestfulWindow: function(cfg) {
        return Ext._create(this.restWindow, cfg);
    },

    factoryRestful: function(cfg) {
        cfg = cfg || {};

        if((cfg.rest || this.rest)) {
            return Ext._create((cfg.rest || this.rest), cfg);
        } else {
            var cfg_w = this.resource || cfg.resource ? {resource: this.resource || cfg.resource} : {};
            var restWnd = this.factoryRestfulWindow(cfg_w);
            return restWnd.factoryRestful(cfg_w);
        }
    },

    setStore: function(store){
        this._store = store;
    },

    getStore: function(cfg) {
        if(!this._store) {

            cfg = cfg || {};

            if (cfg.storeCustom) {
                this._store = cfg.storeCustom;
            } else {
                this._store = this.factoryRestful(cfg).getStore(
                    false,
                    (cfg.storeDisableCaching || this.storeDisableCaching),
                    (cfg.storeHeaders || this.storeHeaders),
                    (cfg.storeDefaultRoute || this.storeDefaultRoute)
                );
            }

            this._store.__state = {
                isLoaded: false,
                isFiltred: false,
                isSearched: false
            };

            this._store.on({
                scope: this,
                load: function(store, records, opts) {
                    store.__state = {
                        isLoaded: true,
                        isFiltred: (opts.params.filter !== undefined),
                        isSearched: (opts.params.keyword !== undefined)
                    };
                }
            });
        }

        if(cfg && cfg.baseParams){
            for(var key in cfg.baseParams){
                this._store.setBaseParam(key, cfg.baseParams[key]);
            }
        }

        return this._store;
    },

    copyItem: function(values) {
        this.createItem(values);
    },

    getConfigCustomActions: function(){
        return [];
    },

    getConfigActions: function(){
        if(!this._configActions){
            this._configActions = [];
            if(this.hideActions.indexOf('copy') < 0 && this.restWindow){
                this._configActions.push(
                    {
                        iconCls: 'icon-16px icon-core icon-core-copy',
                        tooltip: 'Copiar item.',
                        handler: function(action, index) {
                            var record = this.getStore().getAt(index);
                            if(record) this.copyItem(record.data);
                        }
                    }
                );
            }
            if(this.hideActions.indexOf('edit') < 0 && this.restWindow){
                this._configActions.push(
                    {
                        iconCls: 'icon-16px icon-core icon-core-edit',
                        tooltip: 'Editar item.',
                        handler: function(action, index) {
                            var record = this.getStore().getAt(index);
                            if(record) this.updateItem(record);
                        }
                    }
                );
            }
            if(this.hideActions.indexOf('remove') < 0){
                this._configActions.push(
                    {
                        iconCls: 'icon-16px icon-core icon-core-delete',
                        tooltip: 'Remover item.',
                        handler: function(action, index) {
                            var record = this.getStore().getAt(index);
                            if(record) this.removeItems(record);
                        }
                    }
                );
            }
            this._configActions = Ext.combine(this._configActions, this.getConfigCustomActions());
        }
        return this._configActions;
    },

    getActionColumn: function() {
        if(!this._actionColumn)
            this._actionColumn = Ext._create('Ext.grid.ActionColumn', {
                scope: this,
                width: this.actionColumnWidth,
                items: this.getConfigActions(),
            });

        return this._actionColumn;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    new Ext.grid.RowNumberer(),
                    {header: 'Chave', dataIndex: 'pk', width: 60},
                    {header: 'Descrição', dataIndex: 'unicode', id: 'autoExpandColumn'}
                ]
            );

        return this._columnModel;
    },

    getFooterbar: function(cfg) {
        if(!this._footerbar)
            this._footerbar = Ext._create('Ext.PagingToolbar', {
                'style': cfg.footerStyle,
                'store': this.getStore(),
                'pageSize': this.pageSize,
                displayInfo: true
            });

        return this._footerbar;
    },

    getKeywordField: function(cfg) {
        cfg = core.nullValue(cfg, {});

        if(!this._keywordField)
            this._keywordField = Ext._create('Ext.form.TextField', {
                emptyText: this.keywordFieldMessage,
                width: (cfg.keywordFieldWidth || this.keywordFieldWidth),
                enableKeyEvents: true,
                submitValue: false,
                listeners: {
                    scope: this,
                    specialkey: function(field, event) {
                        if(event.getKey() == event.ENTER || event.getKey() == event.TAB)
                            this.doKeywordFilter(field.getValue());
                    }
                }
            });

        return this._keywordField;
    },

    doKeywordFilter: function(keyword) {
        var store = this.getStore();
        if(keyword !== '')
            store.baseParams.keyword = keyword;
        else {
            store.baseParams.keyword = null;
            delete store.baseParams.keyword;
        }

        store.load({});
    },

    getSort: function() {
        var store = this.getStore();
        var strSort = core.nullValue(store.baseParams.sort, '[]');
        var sort;

        try {
            sort = Ext.decode(strSort);
        }
        catch(e) {
            sort = [];
        }
        finally {
            return sort;
        }
    },

    setSort: function(sort, autoload) {
        autoload = core.nullValue(autoload, true);

        var store = this.getStore();
        if (sort.length === 0)
            store.baseParams.sort = undefined;
        else
            store.baseParams.sort = Ext.encode(sort);

        if(autoload) store.load({});
    },

    addSortProperty: function(property, direction, autoload) {
        var sort = this.getSort();
        direction = core.nullValue(direction, 'ASC');

        sort.push({property: property, direction: direction});
        this.setSort(sort, autoload);
    },

    setSortProperty: function(property, direction, autoload) {
        var flag = false;
        var oldSort = this.getSort();
        var newSort = [];
        direction = core.nullValue(direction, 'ASC');

        oldSort.forEach(
            function(item) {
                if(!flag && item.property == property) {
                    item.direction = direction;
                    flag = true;
                }

                newSort.push(item);
            }
        );

        if(!flag)
            this.addSortProperty(property, direction, autoload);
        else
            this.setSort(newSort, autoload);
    },

    removeSortProperty: function(property, autoload) {
        var oldSort = this.getSort();
        var newSort = [];

        oldSort.forEach(
            function(item) {
                if (item.property != property)
                    newSort.push(item);
            }
        );

        this.setSort(newSort, autoload);
    },

    setParam: function(key, value) {
        this.params = core.nullValue(this.params, {});
        this.params[key] = value;
    },

    getParams: function() {
        return core.nullValue(this.params, {});
    },

    createItem: function(values) {
        if(!this.allowCreate)
            return;

        if(values instanceof Ext.Button)
            values = {};

        values = core.nullValue(values, {});

        if(this.safeMode && !this.getStore().__state.isSearched) {
            Ext.Msg.show({
                title: 'Criação de item bloqueada',
                msg: 'Realize primeiro uma busca do que deseja criar, se não encontrar será liberada a inclusão.',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK,
                scope: this,
                fn: function() {
                    this.getKeywordField().focus();
                }
            });

            this.getKeywordField().markInvalid('Primeiro realize busca aqui.');
        }
        else
            this.factoryRestfulWindow({
                resource: this.resource,
                action: 'create',
                params: this.getParams(),
                values: values,
                ownerGrid: this,
                callback: {
                    success: {
                        scope: this,
                        fn: function(instance) {
                            if(this.driver === 'restful') this.getStore().reload();
                            this.fireEvent('createdItemGrid', instance);
                        }
                    },
                    failure: {
                        scope: this,
                        fn: function() {
                            if(this.driver === 'restful') this.getStore().reload();
                            this.fireEvent('failureGrid', 'create');
                        }
                    }
                }
            }).show();
    },

    equalsItems: function(obj1, obj2){
        result = {}
        for(key in obj1){
            if(key in obj1 && key in obj2 && obj1[key] == obj2[key])
                result[key] = obj1[key]
        }
        return result
    },

    updateItem: function(record) {
        if(!this.allowUpdate)
            return;

        if(record instanceof Ext.Button)
            record = undefined;

        var selections = core.nullValue(record, this.getSelectionModel().getSelections());

        if (!Ext.isArray(selections)) selections = [selections];

        if(selections.length == 1){
            var selected = selections[0];
            this.factoryRestfulWindow({
                resource: this.resource,
                action: 'update',
                oId: selected.get('pk'),
                values: selected.data,
                params: this.getParams(),
                ownerGrid: this,
                callback: {
                    success: {
                        scope: this,
                        fn: function(instance) {
                            if(this.driver === 'restful') this.getStore().reload();
                            this.fireEvent('updatedItemGrid', instance);
                        }
                    },
                    failure: {
                        scope: this,
                        fn: function() {
                            if(this.driver === 'restful') this.getStore().reload();
                            this.fireEvent('failureGrid', 'update');
                        }
                    }
                }
            }).show();
        }else if(selections.length > 1){
            if(this.updateMulti){
                var result = selections[0].data
                var pks = [result.pk]
                for(var x=1; x<selections.length; x++){
                    obj2 = selections[x].data;
                    pks.push(obj2.pk);
                    result = this.equalsItems(result, obj2);
                }
                var params = this.getParams();
                if(!('filter' in params))
                    params['filter'] = [];
                params['filter'].push({"property":"pk__in","value":pks});
                params['filter'] = Ext.encode(params['filter']);
                this.factoryRestfulWindow({
                    resource: this.resource,
                    action: 'update',
                    oId: false,
                    values: result,
                    params: params,
                    ownerGrid: this,
                    callback: {
                        success: {
                            scope: this,
                            fn: function() {
                                if(this.driver === 'restful') this.getStore().reload();
                            }
                        }
                    }
                }).show();
            }else
                Ext.Msg.show({
                    title: 'Editando',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Selecione apenas um item para edição.'
                });

        }else
            Ext.Msg.show({
                title: 'Editando',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para editar.'
            });

    },

    removeItems: function(record, cfg) {
        /*
        * Com variavel cfg é possivel adicionar callbacks que podem ser
        * executados antes ou depois da confirmação de exclusão de algum item do grid.
        * As propriedades que denotam os callbacks são: beforeConfirm e afterConfirm.
        */

        cfg = cfg || {};

        Ext.applyIf(
            cfg,
            {
                afterSuccess: Ext.emptyFn
            }
        );

        if(!this.allowRemove)
            return;


        var selection,
            rest = (cfg.rest ? Ext._create(cfg.rest) : this.factoryRestful());

        if(!(record instanceof Ext.Button))
            selection = [record];
        else
            selection = this.getSelectionModel().getSelections();

        if(selection.length === 0) {
            Ext.Msg.show({
                title: 'Removendo',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Não foi selecionado nenhum item para remoção.'
            });
        }
        else {
            var message = 'Confirma a exclusão do item selecionado?',
                args = [
                    selection[0].get('pk'),
                    {
                        externalCallback: {
                            success: {
                                fn: function(instance) {
                                    if(this.driver === 'restful') this.getStore().reload();
                                    (this.afterSuccess || Ext.emptyFn)();
                                    this.fireEvent('removedItemGrid', instance);
                                },
                                scope: this
                            },
                            failure: {
                                scope: this,
                                fn: function() {
                                    if(this.driver === 'restful') this.getStore().reload();
                                    this.fireEvent('failureGrid', 'remove');
                                }
                            }
                        }
                    },
                    {
                        el: this.getEl(),
                        msg: 'Removendo item.'
                    }
                ];

            if(selection.length > 1) {
                message = 'Confirma a exclusão dos itens selecionados?';
                args[0] = false;
                args[1].params = {
                    filter: Ext.encode([
                        {
                            property: 'pk__in',
                            value: selection.map(function(selected) { return selected.get('pk'); })
                        }
                    ])
                };
            }

            var grid = this;

            Ext.Msg.confirm('Alerta', message,
                function(btn)
                {
                    if(btn == 'yes')
                    {
                        if(cfg.beforeConfirm)
                            cfg.beforeConfirm(grid);

                        if(grid.driver === 'restful')
                            rest.remove.apply(rest, args);
                        else if (grid.driver === 'local' )
                        {
                            Ext.each(selection, function(item){
                                grid.getStore().remove(item);
                            });
                        }
                        else
                            Ext.emptyFn();

                        if(cfg.afterConfirm)
                            cfg.afterConfirm(grid);
                    }
                }
            );
        }
    },

    getFilterMenu: function() {
        return false;
    },

    getConfigActionsItems: function(cfg){
        if(!this._configActionsItems){
            this._configActionsItems = {
                add:{
                    text: 'Novo',
                    iconCls: 'icon-16px icon-core icon-core-add',
                    scope: this,
                    handler: this.createItem,
                },
                edit:{
                    text: 'Editar',
                    iconCls: 'icon-core icon-core-edit',
                    scope: this,
                    handler: this.updateItem,
                },
                remove:{
                    text: 'Remover',
                    iconCls: 'icon-core icon-core-delete',
                    scope: this,
                    handler: this.removeItems,
                },
                search:[
                    'Buscar por: ',
                    this.getKeywordField(cfg),
                    '-'
                ],
                download:[
                    '-',
                    {
                        text: 'Download',
                        iconCls: 'icon-core icon-core-csv',
                        scope: this,
                        handler: this.doDownload
                    }
                ],
            };

        }
        return this._configActionsItems;
    },

    getConfigItemsToolbar: function(cfg) {
        hideItems = cfg.hideItemsToolbar || this.hideItemsToolbar;
        if(!this._configItemsToolbar){
            var configActionsItems = this.getConfigActionsItems(cfg);
            this._configItemsToolbar = [];
            Ext.each(
                (cfg.configOrderToolBar || this.configOrderToolBar),
                function(v){
                    if(hideItems.indexOf(v) < 0) {
                        item = configActionsItems[v];
                        if(Ext.isArray(item)){
                            Ext.each(
                                item,
                                function(subItem){
                                    if(Ext.isObject(subItem) || Ext.isString(subItem)){
                                        this._configItemsToolbar.push(subItem);
                                    }else
                                        console.warn(
                                            'Type of item('+v+') invalid! Os itens de getConfigActionsItems devem ser do ' +
                                            'tipo array de "Object" ou "string", "Object" ou "string"!'
                                        );
                                },
                                this
                            );
                        }
                        else if(Ext.isObject(item) || Ext.isString(item)) {
                            this._configItemsToolbar.push(item);
                        }
                        else if (!item) {

                            if(v != ' ' && v != '-' && v != '<-' && v != '->') {
                                var fnName = 'get' + v.substr(0, 1).toUpperCase() + v.substr(1) + 'Action';
                                var fn = this['get' + v.substr(0, 1).toUpperCase() + v.substr(1) + 'Action'];

                                if(fn){
                                    this._configItemsToolbar.push(fn.call(this, cfg));
                                }else {
                                    //this._configItemsToolbar.push(v);
                                    console.info("Não vai adicionar o menu " + v);
                                }
                            }
                            else
                                this._configItemsToolbar.push(v);
                        }else
                            console.warn(
                                'Type of item('+v+') invalid! Os itens de getConfigActionsItems devem ser do tipo array '+
                                'de "Object" ou "string", "Object" ou "string"!'
                            );
                    }
                },
                this
            );
        }

        return this._configItemsToolbar;
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = Ext._create('Ext.Toolbar', {
                style: cfg.toolbarStyle,
                items: this.getConfigItemsToolbar(cfg),
            });

            var filterMenu = this.getFilterMenu() ;
            if(filterMenu && !(cfg || this).hiddenFilter)
                this._toolbar.add([
                    '-',
                    {
                        text: 'Filtro',
                        iconCls: 'icon-patrimonio icon-pat-filter',
                        menu: filterMenu
                    }
                ]);

            if((this.toolbarHideLabel || cfg.toolbarHideLabel))
                this._toolbar.items.each(
                    function(item) {
                        item.tooltip = (item.tooltip || item.text);

                        if(item.text && core.nullValue(item.hideLabel, true))
                            item.text = null;
                    }
                );
        }

        return this._toolbar;
    },

    doDownload: function() {
        var config = {
            filter: Ext.encode(this.getFilter()),
            keyword: this.getKeywordField().getValue(),
            start: 0,
            limit: this.getStore().getTotalCount(),
            format: 'text/csv'
        };
        var rest = this.factoryRestful();
        var url = rest.getRoute('export').url + '?' + Ext.urlEncode(config);

        window.open(url, '_self');
    },

    _configureAddColumns: function() {
        this.getColumnModel();

        var columns = this._columnModel.config;
        if(this.getActionColumn().items.length > 0){
            columns.push(this.getActionColumn());

            this._columnModel = Ext._create('Ext.grid.ColumnModel', columns);

            /**
             * Foi feito assim somente para manter uma semantica poderia ter usado
             * direto o this._columnModel no segundo argumento.
             **/
            this.reconfigure(this.getStore(), this.getColumnModel());
        }
    },

    _configureHiddenColumns: function() {

    },

    _configureVisibleColumns: function() {
        if(this.hideColumns.length > 0) {
            var columnModel = this.getColumnModel();
            var columns = columnModel.getColumnsBy(
                function(c) {
                    return this.hideColumns.indexOf(c.dataIndex) >= 0 && c.hidden !== true;
                },
                this
            );

            Ext.each(
                columns,
                function(c) {
                    columnModel.setHidden(columnModel.getIndexById(c.id), true);
                }
            );
        } else if(this.onlyColumns.length > 0) {
            var columnModel = this.getColumnModel();
            var columns = columnModel.getColumnsBy(
                function(c) {
                    return (this.onlyColumns.indexOf(c.dataIndex) < 0);
                },
                this
            );

            Ext.each(
                columns,
                function(c) {
                    columnModel.setHidden(columnModel.getIndexById(c.id), true);
                }
            );

            columns = columnModel.getColumnsBy(
                function(c) {
                    return (this.onlyColumns.indexOf(c.dataIndex) >= 0 && c.hidden);
                },
                this
            );

            Ext.each(
                columns,
                function(c) {
                    columnModel.setHidden(columnModel.getIndexById(c.id), false);
                }
            );
        }
    },

    defaultClickFunction: function(grid) {
        if(this.getSelectionModel().getSelected()) this.updateItem();
    },

    postCreate: function(grid){
    },

    base64toBlob: function(base64Data, contentType) {
        const byteCharacters = atob(base64Data);
        const byteArrays = [];
    
        for (let offset = 0; offset < byteCharacters.length; offset += 512) {
            const slice = byteCharacters.slice(offset, offset + 512);
    
            const byteNumbers = new Array(slice.length);
            for (let i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }
    
            const byteArray = new Uint8Array(byteNumbers);
            byteArrays.push(byteArray);
        }
    
        return new Blob(byteArrays, { type: contentType });
    },
    
    downloadPdfFromBase64: function(base64Data, filename) {
        const blob = this.base64toBlob(base64Data, 'application/pdf');
    
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;
    
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    },

    reqDownload: function(controllerNome, metodoNome, params, arquivoNome){
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(controllerNome, metodoNome),
            params: params,
            success: function(request) {
                var obj = Ext.decode(request.responseText);
                this.downloadPdfFromBase64(obj.arquivo, arquivoNome);
                
            },
            failure: function() {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Download indisponivel no momento, tente novamente mais tarde.'
                });
            },
            scope: this
        });
    },
    //Funçãao para pegar o item selecionado na grid
    getSelected: function () {
        return this.getSelectionModel().getSelected();
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                storeCustom: null,
                columnAction: true,
                gridAutoLoad: true,
                allowCreate: true,
                allowUpdate: true,
                allowRemove: true,
                doubleClickHandler: this.defaultClickFunction
            }
        );

        Ext.apply(
            cfg,
            {
                store: this.getStore(cfg),
                tbar: this.getToolbar(cfg),
                bbar: this.getFooterbar(cfg),
                stripeRows: true,
                autoExpandColumn: 'autoExpandColumn',
                cm: this.getColumnModel(cfg),
                loadMask: true,
                listeners: {
                    scope: this,
                    dblclick: function(evt) {
                        this.doubleClickHandler(this);
                    },
                    render: function(grid) {
                        if(cfg.gridAutoLoad) grid.getStore().load({});
                    }
                }
            }
        );


        // this.callParent([cfg]);
        core.RestfulGrid.superclass.constructor.call(this, cfg);

        this.addEvents('createdItemGrid', 'updatedItemGrid', 'removedItemGrid', 'failureGrid');
        this.addListener('createdItemGrid', function(){}, this);
        this.addListener('updatedItemGrid', function(){}, this);
        this.addListener('removedItemGrid', function(){}, this);
        this.addListener('failureGrid', function(){}, this);

        /*
        * Este código verificará se algum collumn foi passado através de hideColumns
        * para ser ocultado (hidden = true)
        */
        if(this.hideCollumns && this.hideCollumns.length > 0) {
            this.hideColumns = this.hideCollumns;
            console.warn('Uso incorreto no Grid, substitua hideCollumns por hideColumns');
            console.trace();
        }

        this._configureVisibleColumns();

        if(this.columnAction) this._configureAddColumns();

        this.postCreate(this);

        /*
         * A implementação do sortchange a seguir chama setSortProperty para ordenar
         * os dados no back-end ao invés de um fazer um mero sort local.
         *
         * Funciona assim: A coluna a ser ordenada precisa ter a config sortable
         * setada como true e também poderá precisar de uma config customizada chamada
         * sortDataIndex. Porém, se sortDataIndex não for setada, o valor da config
         * dataIndex (armazenado em sortInfo.field) será utilizado como valor padrão.
         *
         * Nós precisamos do sortDataIndex porque nem sempre o dataIndex corresponderá
         * a um atributo do modelo Django, ou seja, pode ter vindo de um model_to_dict
         * customizado, e portanto não poderia ser utilizado como campo lookup em
         * uma query.
         */
        this.on({
            scope: this,
            sortchange: function(grid, sortInfo) {
                var column = this.getColumnModel().getColumnById(
                    this.getColumnModel().getColumnId(
                        this.getColumnModel().findColumnIndex(sortInfo.field)
                    )
                );

                var property = sortInfo.field;
                if (typeof column.sortDataIndex === 'string') {
                    property = column.sortDataIndex;
                }

                this.setSortProperty(property, sortInfo.direction);
            }
        });
    }
});


Ext._define('core.EditorRestfulGrid', {
    extend: 'Ext.grid.EditorGridPanel',

    mixins: {
        0: 'core.RestfulGrid'
    }
});
