/**
 *
 **/
Ext._define('core.fields.RelatedSelectWindow', {
    'extend': 'Ext.Window',

    'toChangeStore': function(record, added) {
        var index = this._changeStore.findExact('pk', record.get('pk'));
        var existRecord;

        if(index >= 0)
            existRecord = this._changeStore.getAt(index);
        else
            existRecord = false;

        if(existRecord && (existRecord && existRecord.get('added') != added))
            this._changeStore.remove(existRecord);
        else if(!existRecord) {
            this._changeStore.add(Ext._create('Ext.data.Record',
                Ext.apply(
                    {
                        'pk': record.get('pk'),
                        'unicode': record.get('unicode'),
                        'added': added
                    }
                )
            ));
        }
    },

    'addAllItems': function() {
        this.getGridFrom().getStore().each(
            function(record) {
                try {
                    this.getGridTo().getStore().add(
                        Ext._create('Ext.data.Record', {
                            'pk': record.get('pk'),
                            'unicode': record.get('unicode')
                        })
                    );
                    this.toChangeStore(record, true);
                }
                catch(e) { /* não faz nada */}
            },
            this
        );

        this.getGridFrom().getStore().reload();
    },

    'addSelectedItems': function() {
        var selection = this.getGridFrom().getSelectionModel().getSelections();

        Ext.each(
            selection,
            function(record) {
                try {
                    this.getGridTo().getStore().add(
                        Ext._create('Ext.data.Record', record.data)
                    );
                    this.toChangeStore(record, true);
                }
                catch(e) { /* não faz nada */}
            },
            this
        );

        this.getGridFrom().getStore().reload();
    },

    'removeSelectedItems': function() {
        var selection = this.getGridTo().getSelectionModel().getSelections();

        Ext.each(
            selection,
            function(record) {
                try {
                    this.getGridTo().getStore().remove(record);
                    this.toChangeStore(record, false);
                }
                catch(e) { /* não faz nada */}
            },
            this
        );

        this.getGridFrom().getStore().reload();
    },

    'removeAllItems': function() {
        this.getGridTo().getStore().each(
            function(record) {
                try {
                    this.getGridTo().getStore().remove(record)
                    this.toChangeStore(record, false);
                }
                catch(e) { /* não faz nada */}
            },
            this
        );

        this.getGridFrom().getStore().reload();
    },

    'getControlPanel': function() {
        if(!this._controlPanel)
            this._controlPanel = Ext._create('Ext.Panel', {
                'xtype': 'panel',
                'width': 52,
                'frame': true,
                'border': false,
                'layout': 'vbox',
                'layoutConfig': {
                    'align': 'stretch'
                },
                'items': [
                    {
                        'xtype': 'panel',
                        'flex': 1.0
                    },
                    {
                        'defaults': {
                            'width': 32,
                            'height': 32
                        },
                        'height': 250,
                        'layout': 'vbox',
                        'items': [
                            {
                                'xtype': 'button',
                                'iconCls': 'icon-core icon-core-add-all',
                                'margins': '4',
                                'scope': this,
                                'handler': this.addAllItems
                            },
                            {
                                'xtype': 'button',
                                'iconCls': 'icon-core icon-core-add-selected',
                                'margins': '4',
                                'scope': this,
                                'handler': this.addSelectedItems
                            },
                            {
                                'xtype': 'button',
                                'iconCls': 'icon-core icon-core-remove-selected',
                                'margins': '4',
                                'scope': this,
                                'handler': this.removeSelectedItems
                            },
                            {
                                'xtype': 'button',
                                'iconCls': 'icon-core icon-core-remove-all',
                                'margins': '4',
                                'scope': this,
                                'handler': this.removeAllItems
                            }
                        ]
                    },
                    {
                        'xtype': 'panel',
                        'flex': 1.0
                    }
                ]
            });

        return this._controlPanel;
    },

    'getGridFrom': function(cfg) {
        if(!this._gridFrom) {
            var scope = this;
            this._gridFrom = core.RestfulGrid.factoryGrid(cfg.field.sourceRest, {
                'flex': 1.0,
                'border': false,
                'doubleClickHandler': function() {
                    scope.addSelectedItems()
                },
                'viewConfig': {
                    'scope': this,
                    'getRowClass': function(record) {
                        if(scope.getGridTo().getStore().findExact('pk', record.get('pk')) >= 0) {
                            return 'x-grid3-unabled';
                        }
                    }
                }
            });

            if((cfg || this).preFilter)
                this._gridFrom.setFilter((cfg || this).preFilter);

            this._gridFrom.getSelectionModel().on({
                'scope': this,
                'beforerowselect': function(sm, rowIndex, keepExisting, record) {
                    return !(this.getGridTo().getStore().findExact('pk', record.get('pk')) >= 0)
                }
            });

            this._gridFrom.reconfigure(
                this._gridFrom.getStore(),
                Ext._create('Ext.grid.ColumnModel', [
                    {
                        'header': 'Id',
                        'dataIndex': 'pk',
                        'width': 60
                    },
                    {
                        'header': 'Descrição',
                        'dataIndex': 'unicode',
                        'id': 'autoExpandColumn'
                    }
                ])
            );
        }

        return this._gridFrom;
    },

    'getGridTo': function(cfg) {
        if(!this._gridTo) {
            var initialData = [];

            cfg.field.getGridPanel().getStore().each(function(record) {
                initialData.push(record.data);
            });

            var store = Ext._create('Ext.data.Store', {
                'reader': Ext._create('Ext.data.JsonReader', {
                    'fields': [
                        {'name': 'pk', 'type': 'int'},
                        {'name': 'unicode', 'type': 'string'}
                    ]
                }),
                'data': initialData
            });

            this._gridTo = Ext._create('Ext.grid.GridPanel',  {
                'flex': 1.0,
                'border': false,
                'autoExpandColumn': 'autoExpandColumn',
                'store': store,
                'viewConfig': {
                    'markDirt': true
                },
                'listeners': {
                    'scope': this,
                    'dblclick': function() {
                        if(this.getGridTo().getSelectionModel().getSelections().length > 0)
                            this.removeSelectedItems()
                    }
                },
                'cm': Ext._create('Ext.grid.ColumnModel', [
                    {
                        'header': 'Id',
                        'dataIndex': 'pk',
                        'width': 60
                    },
                    {
                        'header': 'Descrição',
                        'dataIndex': 'unicode',
                        'id': 'autoExpandColumn'
                    }
                ])
            });
        }

        return this._gridTo;
    },

    'applyAddChanges': function(rest, toAdd, wait, mask) {
        var xhrConf = rest.getRoute('related', this.field.objectId());

        Ext.apply(xhrConf, {
            'method': 'POST',
            'scope': this,
            'params': {
                'field': this.field.name
            },
            'success': function(request) {
                wait.add = false;

                if(!wait.add && !wait.remove) {
                    this._changeStore.removeAll();
                    this.field.getGridPanel().getStore().reload();
                    mask.hide();
                    delete mask;
                }
            },
            'failure': function(request) {
                Ext.Msg.show({
                    'title': 'Adicionado itens',
                    'icon': Ext.Msg.ERROR,
                    'buttons': Ext.Msg.OK,
                    'msg': 'Ocorreu um erro persistido as modifcações.'
                });
            }
        });

        xhrConf.params[this.field.name] = toAdd;
        wait.add = true;
        mask.show();
        rest.doRequest(xhrConf);
    },

    'applyRemoveChanges': function(rest, toRemove, wait, mask) {
        var xhrConf = rest.getRoute('related', this.field.objectId());

        Ext.apply(xhrConf, {
            'method': 'DELETE',
            'scope': this,
            'params': {
                'field': this.field.name
            },
            'success': function(request) {
                wait.remove = false;

                if(!wait.add && !wait.remove) {
                    this._changeStore.removeAll();
                    this.field.getGridPanel().getStore().reload();
                    mask.hide();
                    delete mask;
                }
            },
            'failure': function(request) {
                Ext.Msg.show({
                    'title': 'Removendo itens',
                    'icon': Ext.Msg.ERROR,
                    'buttons': Ext.Msg.OK,
                    'msg': 'Ocorreu um erro persistido as modifcações.'
                });
            }
        });

        xhrConf.params[this.field.name] = toRemove;
        wait.remove = true;
        mask.show();
        rest.doRequest(xhrConf);
    },

    'applyChanges': function(waitEl) {
        var rest = this.field.factoryRestful()
        var toAdd = [];
        var toRemove = [];
        var mask = new Ext.LoadMask((waitEl || this.getEl()), {'msg': 'Persistindo modificações...'});

        var wait = {
            'add': false,
            'remove': false
        }

        this._changeStore.each(
            function(record) {
                if(record.get('added'))
                    toAdd.push(record.get('pk'))
                else
                    toRemove.push(record.get('pk'))
            }
        );

        toRemove.length > 0 && this.applyRemoveChanges(rest, toRemove, wait, mask);
        toAdd.length > 0 && this.applyAddChanges(rest, toAdd, wait, mask);
    },

    'getApplyButton': function(cfg) {
        if(!this._applyButton)
            this._applyButton = Ext._create('Ext.Button', {
                'text': 'Aplicar',
                'scope': this,
                'handler': function() { this.applyChanges(this.getEl()) }
            });

        return this._applyButton;
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        var bodyBox = Ext.getBody().getBox();

        Ext.applyIf(
            cfg,
            {
                'width': bodyBox.width * 0.9,
                'height': bodyBox.height * 0.9,
                'title': 'Selecionar Itens'
            }
        );

        Ext.apply(
            cfg,
            {
                'layout': 'hbox',
                'layoutConfig': {
                    'align': 'stretch'
                },
                'items': [
                    this.getGridFrom(cfg),
                    this.getControlPanel(),
                    this.getGridTo(cfg)
                ],
                'buttons': [
                    this.getApplyButton(),
                    {
                        'text': 'Fechar',
                        'scope': this,
                        'handler': this.destroy
                    }
                ]
            }
        );

        // this.callParent([cfg]);
        core.fields.RelatedSelectWindow.superclass.constructor.call(this, cfg);

        this._changeStore = Ext._create('Ext.data.Store', {
            'reader': Ext._create('Ext.data.JsonReader', {
                'fields': [
                    {'name': 'pk', 'type': 'int'},
                    {'name': 'unicode', 'type': 'string'},
                    {'name': 'added', 'type': 'boolean'}
                ]
            }),
            'data': [],
            'listeners': {
                'scope': this,
                'add': function(store) {
                    this.getApplyButton()
                        .setDisabled(!(store.getCount() > 0));
                },
                'remove': function(store) {
                    this.getApplyButton()
                        .setDisabled(!(store.getCount() > 0));
                },
                'clear': function(store) {
                    this.getApplyButton()
                        .setDisabled(!(store.getCount() > 0));
                }
            }
        });

        this.getApplyButton()
            .setDisabled(!(this._changeStore.getCount() > 0));

        this.on({
            'scope': this,
            'beforedestroy': function() {
                if(this._changeStore.getCount() > 0)
                    Ext.Msg.show({
                        'title': 'Selecionando itens',
                        'icon': Ext.Msg.ERROR,
                        'buttons': Ext.Msg.YESNO,
                        'msg': 'As modificações não foram gravas. Deseja salvar antes de fechar?',
                        'scope': this,
                        'fn': function(b) {
                            if(b == 'no') return;
                            this.applyChanges(this.field.getGridPanel().getEl());
                        }
                    });
            }
        });
    }
})