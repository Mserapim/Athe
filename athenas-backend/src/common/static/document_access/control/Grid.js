Ext._define('common.document_access.control.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.document_access.control.Window',

    configOrderToolBar: ['menuOptions', '-', 'search', '->', 'filter', 'download'],

    keywordFieldMessage: 'Nº do documento, Tipo de documento, Origem ou Classificação',

    hiddenMenuItems: [],

    getFilterBySource: function (cfg) {
        if (!this._filterBySource) {
            this._filterBySource = Ext._create('Ext.menu.CheckItem', {
                text: 'Por origem do documento',
                checked: false,
                scope: this,
                checkHandler: function (item, checked) {
                    if (checked) {
                        Ext._create('common.document_access.control.filters.SourceWindow', {
                            title: 'Filtrar pela origem do documento',
                            scope: this,
                            handler: function (pk) {
                                this.setFilterProperty('source', pk, 1001, true);
                            }
                        }).show();
                    } else {
                        this.removeFilterProperty('source', 1001, true);
                    }
                }
            });
        }

        return this._filterBySource;
    },

    getFilterByDocType: function (cfg) {
        if (!this._filterByDocType) {
            this._filterByDocType = Ext._create('Ext.menu.CheckItem', {
                text: 'Por tipo de documento',
                checked: false,
                scope: this,
                checkHandler: function (item, checked) {
                    if (checked) {
                        Ext._create('common.document_access.control.filters.DocTypeWindow', {
                            title: 'Filtrar pelo tipo do documento',
                            scope: this,
                            handler: function (pk) {
                                this.setFilterProperty('document_type', pk, 1002, true);
                            }
                        }).show();
                    } else {
                        this.removeFilterProperty('document_type', 1002, true);
                    }
                }
            });
        }

        return this._filterByDocType;
    },

    getFilterByCtrlType: function (cfg) {
        if (!this._filterByCtrlType) {
            this._filterByCtrlType = Ext._create('Ext.menu.CheckItem', {
                text: 'Por nível de acesso',
                checked: false,
                scope: this,
                checkHandler: function (item, checked) {
                    if (checked) {
                        Ext._create('common.document_access.control.filters.CtrlTypeWindow', {
                            title: 'Filtrar por nível de acesso',
                            scope: this,
                            handler: function (pk) {
                                this.setFilterProperty('control_type', pk, 1003, true);
                            }
                        }).show();
                    } else {
                        this.removeFilterProperty('control_type', 1003, true);
                    }
                }
            });
        }

        return this._filterByCtrlType;
    },

    getFilterAction: function (cfg) {
        if (!this._filterAction) {
            this._filterAction = Ext._create('Ext.Button', {
                text: 'Filtrar',
                iconCls: 'icon-core icon-core-filter',
                scope: this,
                menu: [
                    this.getFilterBySource(cfg),
                    this.getFilterByDocType(cfg),
                    this.getFilterByCtrlType(cfg),
                    '-',
                    {
                        text: 'Desfazer filtros',
                        scope: this,
                        handler: function () {
                            this.getFilterBySource().setChecked(false, true);
                            this.getFilterByDocType().setChecked(false, true);
                            this.getFilterByCtrlType().setChecked(false, true);

                            this.removeFilterProperty('source', 1001, false);
                            this.removeFilterProperty('document_type', 1002, false);
                            this.removeFilterProperty('control_type', 1003, true);
                        }
                    },
                ]
            });
        }

        return this._filterAction;
    },

    menuOptionsItems: function(cfg) {
        var menuButtonItems = {
            'reclassify': this.getReclassifyAction(),
            'declassify': this.getDeclassifyAction(),
            'deadlineChange': this.getDeadlineChangeAction(),
            'log': this.getLogAction(),
            'allowedlist': this.getAllowedlistAction()
        };

        return Object.keys(
            menuButtonItems
        ).filter(function(key) {
            return cfg.hiddenMenuItems.indexOf(key) < 0;
        }).map(function(key) {
            return menuButtonItems[key];
        });
    },

    getMenuOptionsAction: function(cfg) {
        if (!this._menuOptionsAction) {
            this._menuOptionsAction = Ext._create('Ext.Button', {
                text: 'Ações',
                iconCls: 'icon-document_access icon-document_access-actions',
                tooltip: 'Desclassificar, Reclassificar, Allowed List, Detalhes',
                scope: this,
                menu: this.menuOptionsItems(cfg)
            });
        }

        return this._menuOptionsAction;
    },

    getAllowedlistAction: function(cfg) {
        if(!this._allowedlistAction) {
            this._allowedlistAction = Ext._create('Ext.menu.Item', {
                text: 'Credenciais de acesso',
                iconCls: 'icon-document_access icon-document_access-allowedlist',
                tooltip: 'Visualizar a lista de credenciais de acesso',
                scope: this,
                handler: function() {
                    var selection = this.getSelectionModel().getSelected();
                    if (selection) {
                        Ext._create('common.document_access.allowedlistitem.Modal', {
                            control: selection.id,
                            title: 'Credenciais de acesso',
                            gridConfig: {
                                allowUpdate: false,
                                allowRemove: false,
                                columnAction: false,
                            }
                        }).show();
                    }
                    else {
                        Ext.Msg.show({
                            title: 'Credenciais de acesso',
                            msg: 'Selecione um documento para visualizar sua lista de credenciais de acesso.',
                            icon: Ext.Msg.WARNING,
                            buttons: Ext.Msg.OK
                        });
                    }
                }
            });
        }

        return this._allowedlistAction;
    },

    getLogAction: function (cfg) {
        if (!this._logAction) {
            this._logAction = Ext._create('Ext.menu.Item', {
                text: 'Histórico',
                iconCls: 'icon-document_access icon-document_access-logs',
                tooltip: 'Visualizar o histórico de mudanças.',
                scope: this,
                handler: function () {
                    var selections = this.getSelectionModel().getSelections();

                    if (selections.length > 0) {
                        Ext._create('common.document_access.log.Modal', {
                            controlId: selections[0].data.pk,
                            title: 'Histórico',
                            gridConfig: {
                                allowCreate: false,
                                allowUpdate: false,
                                allowRemove: false,
                                columnAction: false,
                                configOrderToolBar: ['search', '->', 'download'],
                            }
                        }).show();
                    } else {
                        Ext.Msg.show({
                            title: 'Histórico',
                            msg: 'Selecione um documento para visualizar o histórico de mudanças.',
                            icon: Ext.Msg.WARNING,
                            buttons: Ext.Msg.OK
                        });
                    }
                }
            });
        }

        return this._logAction;
    },

    getDeclassifyAction: function (cfg) {
        if (!this._declassifyAction) {
            this._declassifyAction = Ext._create('Ext.menu.Item', {
                text: 'Desclassificar',
                iconCls: 'icon-document_access icon-document_access-declassify',
                tooltip: 'Justificativa de desclassificação de um Controle.',
                scope: this,
                handler: function () {
                    var selections = this.getSelectionModel().getSelections();

                    if (selections.length > 0) {
                        Ext._create('common.document_access.control.changes.Declassify', {
                            title: 'Desclassificação',
                            selections: selections,
                            controlGrid: this
                        }).show();
                    } else {
                        Ext.Msg.show({
                            title: 'Desclassificação',
                            msg: 'Selecione um documento para poder desclassificar.',
                            icon: Ext.Msg.WARNING,
                            buttons: Ext.Msg.OK,
                            width: 360
                        });
                    }
                }
            });
        }

        return this._declassifyAction;
    },

    getReclassifyAction: function (cfg) {
        if (!this._reclassifyAction) {
            this._reclassifyAction = Ext._create('Ext.menu.Item', {
                text: 'Reclassificar',
                iconCls: 'icon-document_access icon-document_access-reclassify',
                tooltip: 'Justificativa de reclassificação de um Controle.',
                scope: this,
                handler: function () {
                    var selections = this.getSelectionModel().getSelections();

                    if (selections.length > 0) {
                        Ext._create('common.document_access.control.changes.Reclassify', {
                            title: 'Reclassificação',
                            selections: selections,
                            controlGrid: this
                        }).show();
                    } else {
                        Ext.Msg.show({
                            title: 'Reclassificação',
                            msg: 'Selecione um documento para poder reclassificar.',
                            icon: Ext.Msg.WARNING,
                            buttons: Ext.Msg.OK,
                            width: 350
                        });
                    }
                }
            });
        }

        return this._reclassifyAction;
    },

    getDeadlineChangeAction: function (cfg) {
        if (!this._deadlineChange) {
            this._deadlineChange = Ext._create('Ext.menu.Item', {
                text: 'Alterar prazo',
                iconCls: 'icon-document_access icon-document_access-deadline-change',
                tooltip: 'Redução ou Prorrogação de prazo.',
                scope: this,
                handler: function () {
                    var selections = this.getSelectionModel().getSelections();

                    if (selections.length > 0) {
                        Ext._create('common.document_access.control.changes.DeadlineChange', {
                            title: 'Alteração de prazo',
                            selections: selections,
                            controlGrid: this
                        }).show();
                    } else {
                        Ext.Msg.show({
                            title: 'Alteração de prazo',
                            msg: 'Selecione um documento para poder alterar o prazo.',
                            icon: Ext.Msg.WARNING,
                            buttons: Ext.Msg.OK,
                            width: 360
                        });
                    }
                }
            });
        }

        return this._deadlineChange;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Cód.', dataIndex: 'pk', width: 50, hidden: true},
                    {header: 'Nº do documento', dataIndex: 'document_number', width: 120, sortable: true},
                    {header: 'Tipo', dataIndex: 'document_type_unicode', width: 100, sortable: true, sortDataIndex: 'document_type__slug'},
                    {header: 'Origem', dataIndex: 'source_unicode', width: 100},
                    {header: 'Assunto', dataIndex: 'subject', id: 'autoExpandColumn'},
                    {header: 'Data de produção', dataIndex: 'production_date', width: 110, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), sortable: true},
                    {header: 'Último movimento', dataIndex: 'last_movement_date', width: 110, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                    {
                        header: 'Termo final',
                        dataIndex: 'final_term',
                        width: 110,
                        sortable: true,
                        renderer: function(value) {
                            return [
                                '<div style="text-align: center">',
                                    (value == null ?
                                        '<span style="font-size: 1.5rem">&infin;</span>' :
                                        value.format('d/m/Y H:i')
                                    ),
                                '</div>'
                            ].join('')
                        }
                    },
                    {header: 'Sigiloso', dataIndex: 'is_secret', width: 60, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }},
                    {header: 'Nível de acesso', dataIndex: 'control_type_title', width: 90},
                    {header: 'Criado por', dataIndex: 'created_by_unicode', width: 120, hidden: true},
                    {header: 'Criado em', dataIndex: 'created_at', width: 110, hidden: true, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                    {header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120, hidden: true},
                    {header: 'Modificado em', dataIndex: 'modified_at', width: 110, hidden: true, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            hiddenMenuItems: []
        });

        common.document_access.control.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'common.document_access.control.Restful',
    'common.document_access.control.Grid'
);
