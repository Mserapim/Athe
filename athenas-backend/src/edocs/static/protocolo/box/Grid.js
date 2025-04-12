var SquareScreen = function(margin) {
    this.width = screen.width * margin;
    this.height = screen.height * margin;
    this.left = (screen.width - this.width) / 2;
    this.top = (screen.height - this.height) / 2;
};

SquareScreen.prototype = {
    strWidth: function() {
        return 'width=' + this.width;
    },

    strHeight: function() {
        return 'height=' + this.height;
    },

    strLeft: function() {
        return 'left=' + this.left;
    },

    strTop: function() {
        return 'top=' + this.top;
    },

    toString: function() {
        var params = [
            this.strWidth(),
            this.strHeight(),
            this.strLeft(),
            this.strTop()
        ];

        return params.join(', ');
    }
};

Ext._define('edocs.protocolo.box.Grid', {
    extend: 'Ext.grid.GridPanel',

    __resource: 'EDOCManage',

    __boxAction: 'box',

    simpleTitle: 'Box',

    customTitle: 'Box',

    toolbarConfig: ['search', '-', '->', '-', 'filter'],

    keywordFieldWidth: 350,

    statics: {
        defaultFilter: function() {
            return [
            ]
        },
    },

    __signReceived: function(pkset) {
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Recebendo protocolos...'});

        mask.show();
        Ext.Ajax.request({
            url: core.callAction('EDOCManage', 'sign_received'),
            params: {
                pkset: pkset
            },
            scope: this,
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success)
                    this.getStore().reload();
                else
                    Ext.Msg.show({
                        title: 'Recebendo protocolos',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Recebendo protocolos',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    signReceived: function() {
        var selection = this.getSelectionModel().getSelections().filter(
          function(data) {
            return !data.get('with_workflow');
          }
        );

        if(selection.length > 0)
            Ext.Msg.show({
                title: 'Recebendo protocolos',
                msg: 'Tem certeza que deseja receber os protocolos selecionados?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn == 'no') return;

                    this.__signReceived(selection.map(function(data) {
                        return data.get('pk');
                    }));
                }
            });
        else
            Ext.Msg.show({
                title: 'Recebendo protocolos',
                msg: 'Primeiro selecione os protocolos que deseja receber.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    reportProtocol: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            var report = new toolkit.widget.ExtReportBuild('EDOCPrintAthenasProtocolo', '/to/mpe/protocolo/athenas/documento_movimentacoes');
            report.runReport('', {
                protocolo: selected.get('code')
            });
        }
        else
            Ext.Msg.show({
                title: 'Relatório de protocolo',
                msg: 'Primeiro selecione o protocolo que deseja gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    reportProtocolRenderer: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            var wnd = window.open(
                '/athenas/EDOCProtocoloRestful/renderer_document_to_print/?movement=' + selected.get('pk'),
                '_to_printer',
                (new SquareScreen(0.85)).toString() + ', scrollbars=yes'
            );

            if(!wnd)
                Ext.Msg.show({
                    title: 'Preparando para imprimir',
                    msg: 'Não foi possivel preparar o documento para impressão, devido ao bloqueador de popup.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            else
                wnd.onload = wnd.print;
        }
        else
            Ext.Msg.show({
                title: 'Relatório de protocolo',
                msg: 'Primeiro selecione o protocolo que deseja gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    reportQuitter: function() {
        var selected = this.getSelectionModel().getSelections();

        if(selected.length > 0) {
            var report = new toolkit.widget.ExtReportBuild('EDOCPrintAthenasRecebimento', '/to/mpe/protocolo/athenas/recebimento/protocolo');

            report.runReport('', {
                movimentacoes: selected.map(function(item) { return item.get('pk'); })
            });
        }
        else
            Ext.Msg.show({
                title: 'Relatório de protocolo',
                msg: 'Primeiro selecione o protocolo que deseja gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    reportLabel: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            var report = new toolkit.edocs.protocolo.ImprimirFormNew(
                this,
                selected.get('pk')
            );

            report.show();
        }
        else
            Ext.Msg.show({
                title: 'Etiqueta de protocolo',
                msg: 'Primeiro selecione o protocolo que deseja gerar a etiqueta.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    updateTextDepartmentItem: function(text){
        if(text !== undefined) {
            this.getDepartmentToolbarItem().setText(text);
            // this.getDepartmentToolbarItem().setText(text.substr(0, 22).concat("..."));
            this.getDepartmentToolbarItem().setTooltip(text);
        } else {
            this.getDepartmentToolbarItem().setText("TODOS OS DEPARTAMENTOS");
            this.getDepartmentToolbarItem().setTooltip("Todos locais de trabalho");
        }
    },

    updateItemToolbar: function() {
        this.updateTextDepartmentItem();
    },

    getFilterMenu: function(cfg) {
        return [];
    },

    getFilter: function() {
        this._filter = core.nullValue(this._filter, []);
        return this._filter;
    },

    setFilter: function(filter, autoLoad) {
        autoLoad = core.nullValue(autoLoad, true);

        this._filter = filter;
        this.getStore().setBaseParam('filter', Ext.encode(this._filter));
        if(autoLoad) this.getStore().load();
    },

    addFilterProperty: function(property, value, stage, autoLoad) {
        var flag = false;

        autoLoad = core.nullValue(autoLoad, true);
        this.getFilter().every(function(item) {
            if(item.property === property && item.stage === stage) {
                flag = true;
                return false;
            }
            else
                return true;
        });

        if(!flag) {
            var filter = this.getFilter();

            filter.push({
                property: property,
                value: value,
                stage: stage
            });

            this.setFilter(
                filter,
                autoLoad
            );
        }
    },

    removeFilterProperty: function(property, stage, autoLoad) {
        autoLoad = core.nullValue(autoLoad, true);

        var filter = this.getFilter().filter(function(item) {
            var flag = false;

            if(item.property !== property)
                flag = true;
            else if(item.property === property && item.stage !== stage)
                flag = true;

            return flag;
        });

        this.setFilter(filter, autoLoad);
    },

    setFilterProperty: function(property, value, stage, autoLoad) {
        autoLoad = core.nullValue(autoLoad, true);

        this.removeFilterProperty(property, stage, false);
        this.addFilterProperty(property, value, stage, autoLoad);
    },

    getFilterToolbarItem: function(cfg) {
        if(!this._filterToolbarItem)
            this._filterToolbarItem = Ext._create('Ext.Button', {
                text: 'Filtrar',
                iconCls: 'icon-edocs icon-protocolo-search',
                menu: this.getFilterMenu()
            });

        return this._filterToolbarItem;
    },

    doKeywordSearch: function(text) {
        this._lastKeywordSearch = (this._lastKeywordSearch || null);

        if(this._lastKeywordSearch !== text && text !== '') {
            this._lastKeywordSearch = text;
            this.getStore().setBaseParam('keyword', this._lastKeywordSearch);
            this.getStore().load({});
        }
        else if(text === '') {
            this.getStore().setBaseParam('keyword', undefined);
            this.getStore().load({});
        }
    },

    getSearchToolbarItem: function(cfg) {
        if (!this._searchToolbarItem) {
            this._searchToolbarItem = Ext._create('Ext.Container', {
                layout: 'form',
                height: 20,
                labelWidth: 55,
                width: 300,
                items: [
                    {
                        hideLabel: true,
                        //width: (cfg.keywordFieldWidth || this.keywordFieldWidth),
                        anchor: '100%',
                        xtype: 'textfield',
                        name: 'keyword',
                        emptyText: 'Buscar por assunto, conteúdo, número de protocolo, chancela ou protocolo externo',
                        enableKeyEvents: true,
                        listeners: {
                            scope: this,
                            specialkey: function(field, evt) {
                                if(evt.getKey() == evt.ENTER)
                                    this.doKeywordSearch(field.getValue());
                            },
                            blur: function(field) {
                                this.doKeywordSearch(field.getValue());
                            }
                        }
                    }
                ]
            });
        }

        return this._searchToolbarItem;
    },

    getDepartmentToolbarItem: function() {
        if(!this._departmentToolbarItem){
            this._departmentToolbarItem = Ext._create('Ext.Button', {
                xtype: 'button',
                width: 400,
                text: 'TODOS OS DEPARTAMENTOS',
                iconCls: 'icon-edocs icon-protocolo-folder',
                tooltip: "Todos locais de trabalho",
                scope: this,
                handler: this.selectDepartment,
                cls: 'customToolBar'
            });
        }
        return this._departmentToolbarItem;
    },

    selectDepartment: function() {
        Ext._create('edocs.protocolo.filters.DepartmentWindow', {
            grid: this,
            filterProperties: this.getFilterBoxDepartment()
        }).show();
    },

    getFilterBoxDepartment: function() {
        return [];
    },

    getToolbarItems: function(cfg) {
        var me = this;

        if(!this._toolbarItems) {
            this._toolbarItems = [];

            this._toolbarItems = (cfg.toolbarConfig || this.toolbarConfig).map(
                function(label) {
                    var fnName = 'get' + label.charAt(0).toUpperCase() + label.substr(1) + 'ToolbarItem';
                    var fn = me[fnName];

                    if(fn)
                        return fn.call(me, cfg);
                    else
                        return label;
                }
            );
        }

        return this._toolbarItems;
    },

    getToolbar: function(cfg) {
        if(!this._toolbar)
            this._toolbar = Ext._create('Ext.Toolbar', {
                items: this.getToolbarItems(cfg)
            });

        return this._toolbar;
    },

    factoryStore: function(autoLoad, disableCaching) {
        autoLoad = core.nullValue(autoLoad, true);

        return Ext._create('Ext.data.Store', {
            proxy: Ext._create('Ext.data.HttpProxy', {
                'api': {
                    'read': {
                        url: ['', 'athenas', this.__resource, this.__boxAction, ''].join('/'),
                        method: 'GET'
                    }
                },
                disableCaching: core.nullValue(disableCaching, this.disableCaching),
            }),
            reader: Ext._create('Ext.data.JsonReader', {
                root: 'collection',
                totalProperty: 'count',
                successProperty: 'success',
                messageProperty: 'message',
                fields: [
                    {name: 'pk', type: 'int'},
                    {name: 'step', type: 'int'},
                    {name: 'icons', type: 'auto'},
                    {name: 'is_read', type: 'bool'},
                    {name: 'code', type: 'string'},
                    {name: 'external_number', type: 'string'},
                    {name: 'subject', type: 'string'},
                    {name: 'seal_number', type: 'string'},
                    {name: 'media', type: 'int'},
                    {name: 'home_court', type: 'int'},
                    {name: 'home_court_unicode', type: 'string'},
                    {name: 'interested', type: 'int'},
                    {name: 'interested_unicode', type: 'string'},
                    {name: 'user', type: 'int'},
                    {name: 'user_unicode', type: 'string'},
                    {name: 'protocol', type: 'int'},
                    {name: 'protocol_unicode', type: 'string'},
                    {name: 'document_type', type: 'int'},
                    {name: 'document_type_unicode', type: 'string'},
                    {name: 'content', type: 'string'},
                    {name: 'content_stripedtags', type: 'string'},
                    {name: 'from_location', type: 'string'},
                    {name: 'from_person', type: 'string'},
                    {name: 'send_to_unicode', type: 'string'},
                    {name: 'send_to', type: 'int'},
                    {name: 'com_workflow', type: 'bool', mapping: 'withworkflow'},
                    {name: 'with_workflow', type: 'bool', mapping: 'withworkflow'},
                    {name: 'send_date', type: 'string'},
                    {name: 'user', type: 'int'},
                    {name: 'special_type', type: 'string'},
                    {name: 'confidential', type: 'bool'},

                    // Controle de Acesso (app document_access)
                    {name: 'control', type: 'int'},
                    {name: 'control_type', type: 'int'},
                    {name: 'legal_prerogative', type: 'int'},
                    {name: 'is_committed', type: 'bool'},
                    {name: 'is_secret', type: 'bool'},
                ]
            }),
            autoLoad: autoLoad,
            listeners: {
                scope: this,
                load: function(store) {
                    if (store.reader.jsonData.unReadCount > 0)
                        this.customTitle = this.simpleTitle + ' (' + store.reader.jsonData.unReadCount + ')';
                    else
                        this.customTitle = this.simpleTitle;
                    this.setTitle(this.customTitle);
                    this.selectItems();
                },
                beforeload: function(store) {
                    this.selections(this.getSelectionModel().getSelections());
                }
            }
        });
    },

    selectItems: function(){
        var item = this.selections();
        for(var i = 0; i < item.length; i++) {
            var row = this.store.find('pk', item[i].get('pk'));
            this.getSelectionModel().selectRow(row, true);
        }
    },

    selections: function(selm){

        if(!this._selections)
            this._selections = [];

        if(selm !== undefined)
            this._selections = selm;

        return this._selections;
    },

    getFooterbar: function(cfg) {
        if(!this._footerbar)
            this._footerbar = Ext._create('Ext.PagingToolbar', {
                // 'style': cfg.footerStyle,
                store: cfg.store,
                pageSize: 30,
                displayInfo: true
            });

        return this._footerbar;
    },

    __rendererItem: function(value, cell, data) {
        var tpl = new Ext.XTemplate(
            '<div class="edoc-row">',
                '<div class="edoc-iconset">',
                    core.rendererIconGrid(data.get('icons')),
                '</div>',
                '<div class="edoc-item">',
                    '<div>',
                        '<div class="subject inline-with-crop" ext:qtip="Assunto">{subject}</div>',
                    '</div>',
                    '<div>',
                        '<div class="subject inline-with-crop" ext:qtip="Interessado">{interested_unicode}</div>',
                    '</div>',
                    '<div class="two-column">',
                        '<tpl if="seal_number">',
                            '<div class="one" ext:qtip="Protocolo - Chancela">{code} - {seal_number}</div>',
                        '</tpl>',
                        '<tpl if="!seal_number">',
                            '<div class="one" ext:qtip="Protocolo">{code}</div>',
                        '</tpl>',
                        '<div class="two" ext:qtip="Data de envio">{send_date}</div>',
                    '</div>',
                    '<div class="two-column">',
                        '<div class="one" ext:qtip="De onde veio">{from_location}</div>',
                        '<div class="two" ext:qtip="Enviado por">{from_person}</div>',
                    '</div>',
                '</div>',
            '</div>'
        );

        return tpl.apply(data.data);
    },

    readView: function(movement, context) {
        var mask = new Ext.LoadMask(this.detailView.getEl(), {msg: 'Carregando informações...'});

        mask.show();
        this.detailView.setPageContent('');

        Ext.Ajax.request({
            url: core.callAction('EDOCProtocoloRestful', 'renderer_document'),
            scope: this,
            autoAbort: true,
            params: {
                movement: movement,
                context: context
            },
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var me = this;

                if(rst.success) {
                    this.detailView.setPageContent(rst.content);
                    rst.appends.forEach(function(page) { me.detailView.addPageContent(page); });
                }
                else
                    Ext.Msg.show({
                        title: 'Carregando informações',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Carregando informações',
                    msg: 'Recurso indisponivel no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    generateFlowchart: function () {
        var selected = this.getSelectionModel().getSelected();

        if (selected) {
            edocs.reports.Flowchart.generate({
                el: this.getEl(),
                waitMessage: 'Gerando fluxograma...',
                params: {
                    protocol: selected.get('protocol'),
                    output_format: 'pdf'
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Fluxograma',
                msg: 'Selecione o protocolo para o qual deseja gerar o fluxograma.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            store: this.factoryStore(false),
        });

        this.toolBar = Ext._create('Ext.Container', {
            height: 54,
            layout: 'anchor',
            xtype: 'container',
            defaults: {
                anchor: '100%',
                height: 27,
            },
            items: [
                this.getDepartmentToolbarItem(),
                this.getToolbar(cfg),
            ]
        });

        Ext.apply(
            cfg,
            {
                viewConfig: {
                    getRowClass: function(data) {
                        if(data.get('with_workflow'))
                          return 'x-grid3-read-only';
                        else if(!data.get('is_read'))
                          return 'x-grid3-orange-simple';
                    }
                },
                autoExpandColumn: 'autoExpanded',
                cm: Ext._create('Ext.grid.ColumnModel', [
                    {
                        menuDisabled: true,
                        id: 'autoExpanded',
                        dataIndex: '__ghost__',
                        header: 'Descrição',
                        renderer: this.__rendererItem
                    }
                ]),
                loadMask: true,
                tbar: this.toolBar,
                bbar: this.getFooterbar(cfg),
                listeners: {
                    scope: this,
                    resize: function (grid, adjWidth) {
                        grid.getSearchToolbarItem().setWidth(adjWidth - 240);
                    },
                }
            }
        );

        edocs.protocolo.box.Grid.superclass.constructor.call(this, cfg);

        this.setFilter(cfg.preFilter || edocs.protocolo.box.Grid.defaultFilter(), false);

        if(this.detailView) {
            this.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();

                    if(selection.length > 0){
                        this.readView(selection[0].get('pk'), this.__boxAction);
                    } else {
                        this.detailView.setPageContent('');
                    }
                }
            });
        }
    }
});
