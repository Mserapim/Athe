Ext._define('judicial.workerreminder.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'judicial.workerreminder.Restful',
    restWindow: 'judicial.workerreminder.Window',

    configOrderToolBar: ['closedSelectedWorker', '-', 'search', '->'],

    openDocument: function() {
        var selected = this.getSelectionModel().getSelected();
        var width, height, left, top;

        width = (Ext.getBody().getBox().width * 0.9);
        height = (Ext.getBody().getBox().height * 0.9);
        left = screenX + (screen.width / 2) - (width / 2);
        top = (screen.height / 2) - (height / 2);

        var spec = [
            'width=' + width,
            'height=' + height,
            'top=' + top,
            'left=' + left,
            'scrollbars',
            'resizable',
            'status',
            'titlebar'
        ];

        if(this._wndP) this._wndP.close();

        this._wndP = window.open(
            '/athenas/EJudOutCourtLawsuit/viewer/#' + selected.get('lawsuit'),
            'ejud-proccess',
            spec.join(', ')
        );

        if(!this._wndP)
            Ext.Msg.show({
                title: 'Abrindo procedimento!',
                msg: 'O bloqueador de popup interceptou a abertura do procedimento!',
                buttons: Ext.Msg.OK,
                icons: Ext.Msg.ERROR
            });

        this._wndP.config = function() {
            return selected.data;
        };
    },

    updateItem: function() {
        this.openDocument();
    },

    openConfirmationClosedWorker: function() {
        var params = {};
        var selections = this.getSelectionModel().getSelections();
        params.selections = selections
        params.rest = rest
        params.storage = this.getStore()

        if(selections.length > 0) {
            params.selections = selections.map(function(data) {
                return {
                    id: data.get('pk'),
                    lawsuit: data.get('lawsuit_cache_number'),
                    description: data.get('part_unicode')
                };
            });
            params.rest = this.factoryRestful()

            Ext._create('judicial.workerreminder.ConfirmClosedWorderwindow', {
                params: params,
                success: {
                    scope: this,
                    fn: function() {
                        this.getStore().reload();
                    }
                }
            }).show();
        } else {
            Ext.Msg.show({
                title: 'Selecione uma comunicação',
                msg: 'Selecione ao menos uma comunicação para concluir',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            })
        }
    },

    getClosedSelectedWorkerAction: function(cfg) {
        if(!this._closedSelectedWorkerAction)
            this._closedSelectedWorkerAction = Ext._create('Ext.Button', {
                text: 'Concluir selecionados',
                icon: '/'+ global.Context + '/static/images/accept.png',
                scope: this,
                handler: this.openConfirmationClosedWorker
            });

        return this._closedSelectedWorkerAction;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'status', hidden: true, width: 80},
                    {header: 'Procedimento', dataIndex: 'lawsuit_cache_number', width: 90},
                    {header: 'Documento', dataIndex: 'part_unicode', id: 'autoExpandColumn'},
                    {header: 'Solicitante', dataIndex: 'solicited_by', width: 200},
                    {header: 'Destinatário', dataIndex: 'receiver_unicode', width: 200},
                    {header: 'Prioridade', dataIndex: 'priority_display', width: 80},
                    {header: 'Solicitado em', dataIndex: 'created_at', width: 80, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Prazo', hidden: false, dataIndex: 'deadline', width: 80, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Concluído em', dataIndex: 'resolved_at', width: 80, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Concluído por', dataIndex: 'resolved_by_unicode', width: 80, hidden: true},
                    {header: 'Resolvido', dataIndex: 'resolved', hidden: true, width: 40},
                    {
                        xtype: 'actioncolumn',
                        header:'Ações',
                        dataIndex: 'action_button',
                        width: 60,
                        scope: this,
                        items: [
                            {
                                tooltip:'Concluir',
                                icon: '/'+ global.Context + '/static/images/accept.png',
                                scope:this,
                                handler:function(grid, row, col) {
                                    grid.getSelectionModel().selectRow(row);

                                    Ext.Msg.show({
                                       title:'Deseja concluir?',
                                       msg: 'Realmente deseja concluir essa comunicação?',
                                       buttons: Ext.Msg.YESNO,
                                       icon: Ext.MessageBox.QUESTION,
                                       fn: function(btn){
                                            if(btn=='yes') {
                                                var rest = grid.factoryRestful();
                                                var record = grid.getStore().getAt(row);
                                                rest.resolve(
                                                    record.get('pk'),
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            core.invokeCallback((this.callback || {}).success);
                                                            grid.getStore().reload();
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Concluído',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() {}
                                                    }
                                                );
                                            }
                                        }
                                    });

                                },
                            },
                        ]
                    }
                ]
            );

        return this._columnModel;
    },

    finishedFilter: function(checked) {
        if(!checked)
            this.setFilterProperty('resolved', 'true', -100);
        else
            this.removeFilterProperty('resolved', -100);
    },

    priorityFilter: function(checked) {
        // console.log(checked);
        // if(!checked)
        //     this.setFilterProperty('resolved', 'true', -100);
        // else
        //     this.removeFilterProperty('resolved', -100);
    },

    priorityFilter: function(value) {
        if(this._filterPriority.indexOf(value) >= 0)
            this._filterPriority.remove(value);
        else
            this._filterPriority.push(value);

        this.setFilterProperty('priority__in', this._filterPriority, 101);
    },

    cleanPriorityFilter: function(noLoad) {
        this._filterPriority = [1, 2, 3];
        noLoad = core.nullValue(noLoad, false);

        this.setFilterProperty('priority__in', this._filterPriority, 101, !noLoad);
    },

    getFilterMenu: function(cfg) {
        if(!this._filterMenu)
            this._filterMenu = [
                {
                    text: 'Concluído',
                    // FIXME: deveria chegar a variavel cfg com valores passados pelo construtor do objeto.
                    checked: false,
                    scope: this,
                    hideOnClick: false,
                    listeners: {
                        scope: this,
                        checkchange: function(menu, checked) {
                            this.finishedFilter(checked);
                        }
                    }
                },
                {
                    text: 'Por Prioridade',
                    menu: [
                        {
                            text: 'Normal',
                            checked: true,
                            scope: this,
                            hideOnClick: false,
                            listeners: {
                                scope: this,
                                checkchange: function(menu, checked) {
                                    this.priorityFilter(1);
                                }
                            }
                        },
                        {
                            text: 'Urgente',
                            checked: true,
                            scope: this,
                            hideOnClick: false,
                            listeners: {
                                scope: this,
                                checkchange: function(menu, checked) {
                                    this.priorityFilter(2);
                                }
                            }
                        },
                        {
                            text: 'Imediata',
                            checked: true,
                            scope: this,
                            hideOnClick: false,
                            listeners: {
                                scope: this,
                                checkchange: function(menu, checked) {
                                    this.priorityFilter(3);
                                }
                            }
                        },
                    ]
                }

            ];
        return this._filterMenu;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                showFinished: true,
                viewConfig: {
                    getRowClass: function(record, rowIndex, rp, ds){

                        if(record.get('resolved'))
                            return 'x-grid3-green-simple';
                        else
                            return 'x-grid3-yellow-simple';
                    }
                }
            }
        );

        judicial.workerreminder.Grid.superclass.constructor.call(this, cfg);

        this.cleanPriorityFilter(true);
    }

});

core.RestfulGrid.register(
    'judicial.workerreminder.Restful',
    'judicial.workerreminder.Grid'
);
