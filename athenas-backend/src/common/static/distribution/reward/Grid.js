Ext._define('common.distribution.reward.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.distribution.reward.Window',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'distribute', 'cancel', 'certificate', '-', 'search', '->', 'filter', 'download'],

    _MSG_COULD_NOT_APPLY_FILTER: 'Não foi possível aplicar o filtro. Por favor, selecione uma distribuição e tente novamente.',

    keywordFieldMessage: 'Título ou Número Externo',

    generateCertificate: function () {
        var selections = this.getSelectionModel().getSelections();

        if (selections && selections.length > 0) {
            engine.mq.Report.request({
                report: '/to/mpe/common/distribution/certificate',
                params: {
                    reward_id: selections[0].get('pk'),
                    report_name: 'Certidão de distribuição',
                    outfile: ['certidao', 'distribuicao', selections[0].get('title')].join('-')
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Gerar certificado',
                msg: 'Primeiro selecione os Objetos para os quais deseja gerar o certificado.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getCertificateAction: function (cfg) {
        if (!this._certificateAction) {
            this._certificateAction = Ext._create('Ext.Button', {
                text: 'Certidão',
                iconCls: 'icon-core icon-core-reports',
                scope: this,
                handler: function () {
                    this.generateCertificate();
                }
            });
        }

        return this._certificateAction;
    },

    getAutomaticallyMenuItem: function () {
        if (!this._automaticallyMenuCheckItem) {
            this._automaticallyMenuCheckItem = Ext._create('Ext.menu.Item', {
                text: 'Por Sorteio',
                scope: this
            });

            this._automaticallyMenuCheckItem.on({
                scope: this,
                click: function () { this.distribute(); }
            });
        }
        return this._automaticallyMenuCheckItem;
    },

    getManuallyMenuItem: function () {
        if (!this._manuallyMenuCheckItem) {
            this._manuallyMenuCheckItem = Ext._create('Ext.menu.Item', {
                text: 'Manualmente',
                scope: this,
                handler: function () { this.distributeManually(); }
            });
        }
        return this._manuallyMenuCheckItem;
    },

    distribute: function () {
        var selection = this.getSelectionModel().getSelections();

        if (selection.length === 0) {
            Ext.Msg.show({
                title: 'Distribuindo',
                msg: 'Nenhum objeto foi selecionado para distribuição.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        } else {
            Ext.Msg.show({
                title: 'Distribuindo',
                msg: 'Tem certeza que deseja distribuir os objetos selecionados?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function (btn) {
                    if (btn === 'no') return;
                    this._doDistribute(
                        selection.map(function (data) { return data.get('pk'); })
                    );
                }
            });
        }
    },

    _doDistributeManually: function (player, pkset) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Distribuindo manualmente...' });

        mask.show();
        this.factoryRestful().distributeManually(
            player,
            pkset,
            {
                scope: this,
                fn: function (rst) {
                    if (rst.success) {
                        this.getStore().reload();
                    } else {
                        Ext.Msg.show({
                            title: 'Distribuindo manualmente',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                }
            },
            {
                fn: function (message) {
                    Ext.Msg.show({
                        title: 'Distribuindo manualmente',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function () { mask.hide(); }
            }
        );
    },

    _doDistribute: function (pkset) {
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'distribuindo...' });

        mask.show();
        this.factoryRestful().distribute(
            pkset,
            {
                scope: this,
                fn: function (rst) {
                    if (rst.success) {
                        this.getStore().reload();
                    } else {
                        Ext.Msg.show({
                            title: 'Distribuindo',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                }
            },
            {
                fn: function (message) {
                    Ext.Msg.show({
                        title: 'Distribuindo',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function () { mask.hide(); }
            }
        );
    },

    distributeManually: function () {
        var player = this.getParams().player;
        var selection = this.getSelectionModel().getSelections();

        if (!player) {
            Ext.Msg.show({
                title: 'Distribuindo manualmente',
                msg: 'Primeiro informe quem irá receber manualmente os objetos.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        } else if (selection.length === 0) {
            Ext.Msg.show({
                title: 'Distribuindo manualmente',
                msg: 'Nenhum objeto foi selecionado para distribuição.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        } else {
            Ext.Msg.show({
                title: 'Distribuindo manualmente',
                msg: 'Tem certeza que deseja distribuir os objetos selecionados manualmente?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function (btn) {
                    if (btn === 'no') return;
                    this._doDistributeManually(
                        player,
                        selection.map(function (data) { return data.get('pk'); })
                    );
                }
            });
        }
    },

    getDistributeAction: function () {
        if (!this._distributeAction) {
            this._distributeAction = Ext._create('Ext.Button', {
                text: 'Distribuir',
                iconCls: 'icon-distribution icon-dist-block-share',
                menu: [
                    this.getAutomaticallyMenuItem(),
                    this.getManuallyMenuItem()
                ]
            });
        }
        return this._distributeAction;
    },

    _getDistributionPk: function () {
        var params = this.getParams();
        if (params.hasOwnProperty('distribution')) {
            return params.distribution;
        }
        return 0;
    },

    _showFilterErrorMsg: function () {
        Ext.Msg.show({
            title: 'Filtrando',
            msg: this._MSG_COULD_NOT_APPLY_FILTER,
            icon: Ext.Msg.INFO,
            buttons: Ext.Msg.OK
        });
    },

    filterByDate: function () {
        var grid = this;
        var win = Ext._create('Ext.Window', {
            title: 'Filtrar por data de distribuição',
            modal: true,
            width: 250,
            border: false,
            items: [
                {
                    xtype: 'form',
                    border: false,
                    frame: true,
                    labelWidth: 25,
                    defaults: {anchor: '98%'},
                    items: [
                        {
                            xtype: 'datefield',
                            fieldLabel: 'De',
                            name: 'initialDate',
                            allowBlank: false
                        },
                        {
                            xtype: 'datefield',
                            fieldLabel: 'Até',
                            name: 'finalDate',
                            allowBlank: false
                        }
                    ]
                }
            ],
            buttons: [
                {
                    text: 'Aplicar',
                    scope: grid,
                    handler: function () {
                        var form = win.getComponent(0).getForm();

                        var initialDate = form.findField('initialDate').getValue();
                        var finalDate = form.findField('finalDate').getValue();

                        if (isNaN(Date.parse(initialDate)) || isNaN(Date.parse(finalDate))) {
                            Ext.Msg.show({
                                title: 'Erro de validação',
                                msg: 'As datas fornecidas são inválidas.',
                                buttons: Ext.Msg.OK,
                                icon: Ext.Msg.ERROR
                            });
                            return;
                        }

                        initialDate = Ext.util.Format.date(initialDate, 'Y-m-d') + ' 00:00:00';
                        finalDate = Ext.util.Format.date(finalDate, 'Y-m-d') + ' 23:59:59';

                        this.setFilterProperty('distributed_at__gte', initialDate, 1003, false);
                        this.setFilterProperty('distributed_at__lte', finalDate, 1004, false);
                        this.getStore().reload();

                        win.destroy();
                    }
                },
                {
                    text: 'Cancelar',
                    scope: grid,
                    handler: function () {
                        win.destroy();
                    }
                }
            ]
        }).show();
    },

    filterByPlayer: function () {
        var rewardGrid = this;
        var player = null;
        var win = Ext._create('Ext.Window', {
            title: 'Filtrar por participante',
            modal: true,
            closable: false,
            resizable: false,
            width: 640,
            height: 480,
            border: false,
            items: [
                Ext._create('common.distribution.player.Grid', {
                    height: 418,
                    border: true,
                    disabled: true,
                    gridAutoLoad: false,
                    allowUpdate: false,
                    columnAction: false,
                    keywordFieldWidth: 600,
                    configOrderToolBar: ['search', '->', 'download'],
                    sm: Ext._create('Ext.grid.RowSelectionModel', {
                        singleSelect: true,
                        listeners: {
                            scope: rewardGrid,
                            selectionchange: function (sm) {
                                var selectBtn = win.buttons[0];

                                if (sm.getSelected()) {
                                    player = sm.getSelected().get('pk');
                                    selectBtn.enable();
                                } else {
                                    selectBtn.disable();
                                }
                            }
                        }
                    })
                })
            ],
            buttons: [
                {
                    text: 'Selecionar',
                    scope: rewardGrid,
                    disabled: true,
                    handler: function () {
                        rewardGrid.setFilterProperty('winner', player, 1005, true);
                        win.destroy();
                    }
                },
                {
                    text: 'Cancelar',
                    scope: rewardGrid,
                    handler: function () {
                        win.destroy();
                    }
                }
            ]
        });

        win.on({
            scope: this,
            show: function () {
                var playerGrid = win.getComponent(0);
                var value = rewardGrid.getParams().distribution
                if (value) {
                    playerGrid.setParam('distribution', value);
                    playerGrid.setFilterProperty('distribution', value, 2000, true);
                    playerGrid.enable();
                }
            }
        });

        win.show();
    },

    player: function (value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if (value !== undefined) {
            this._player = value;

            if (dispatch)
                this.playerObserve();
        }

        return this._player;
    },

    playerObserve: function () {
        this.setParam('player', this.player());
    },

    filterByDistribution: function (filterType) {
        var filters = [
            { property: 'winner__isnull', value: true, stage: 1001 },
            { property: 'winner__isnull', value: false, stage: 1001 },
        ];

        var selectedFilter = filters[filterType] || false;

        this.removeFilterProperty('winner__isnull', 1001, false);
        if (selectedFilter) {
            this.setFilterProperty(
                selectedFilter.property,
                selectedFilter.value,
                selectedFilter.stage,
                false
            );
        }

        this.getStore().reload();
    },

    _cancelDistribution: function (pkset) {
        var mask = new Ext.LoadMask(
            this.getEl(),
            { msg: 'Cancelando distribuição...' }
        );
        mask.show();

        this.factoryRestful().cancelDistribution(
            pkset,
            {
                scope: this,
                fn: function (result) {
                    this.getStore().reload();
                }
            },
            {
                fn: function (error) {
                    Ext.Msg.show({
                        title: 'Cancelar distribuição',
                        msg: error,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function () {
                    mask.hide();
                }
            }
        );
    },

    cancelDistribution: function () {
        var selections = this.getSelectionModel().getSelections();

        if (selections.length > 0) {
            Ext.Msg.show({
                title: 'Cancelar distribuição',
                msg: ['Tem certeza que deseja cancelar a',
                    'distribuição dos Objetos selecionados?'].join(' '),
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function (btn) {
                    if (btn === 'no') {
                        return;
                    }

                    var pkset = selections.map(function (data) {
                        return data.get('pk');
                    });
                    this._cancelDistribution(pkset);
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Cancelar distribuição',
                msg: ['Selecione um ou mais Objetos ',
                    'para cancelar sua distribuição.'].join(' '),
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getCancelAction: function (cfg) {
        if (!this._cancelAction) {
            this._cancelAction = Ext._create('Ext.Button', {
                text: 'Cancelar',
                iconCls: 'icon-distribution icon-dist-cancel',
                tooltip: 'Cancela a distribuição de um Objeto.',
                scope: this,
                handler: this.cancelDistribution
            });
        }

        return this._cancelAction;
    },

    getFilterAction: function (cfg) {
        if (!this._filterAction) {
            var grid = this;

            this._filterAction = Ext._create('Ext.Button', {
                text: 'Filtros',
                iconCls: 'icon-distribution icon-dist-filter',
                menu: [
                    {
                        text: 'Não distribuídos',
                        group: 'byDistribution',
                        checked: (cfg.initialByDistributionType || 2) == 0,
                        handler: function () {
                            grid.filterByDistribution(0);
                        }
                    },
                    {
                        text: 'Distribuídos',
                        group: 'byDistribution',
                        checked: (cfg.initialByDistributionType || 2) == 1,
                        handler: function () {
                            grid.filterByDistribution(1);
                        }
                    },
                    {
                        text: 'Todos',
                        group: 'byDistribution',
                        checked: (cfg.initialByDistributionType || 2) == 2,
                        handler: function () {
                            grid.filterByDistribution(2);
                        }
                    },
                    '-',
                    {
                        xtype: 'menucheckitem',
                        text: 'Cancelados',
                        checked: false,
                        scope: this,
                        checkHandler: function (item, checked) {
                            if (checked) {
                                this.setFilterProperty('canceled_at__isnull', false, 1002, true);
                            } else {
                                this.removeFilterProperty('canceled_at__isnull', 1002, true);
                            }
                        }
                    },
                    {
                        xtype: 'menucheckitem',
                        text: 'Por data de distribuição',
                        checked: false,
                        scope: this,
                        checkHandler: function (item, checked) {
                            if (checked) {
                                this.filterByDate();
                            } else {
                                this.removeFilterProperty('distributed_at__gte', 1003, false);
                                this.removeFilterProperty('distributed_at__lte', 1004, false);
                                this.getStore().reload();
                            }
                        }
                    },
                    {
                        xtype: 'menucheckitem',
                        text: 'Por participante',
                        checked: false,
                        scope: this,
                        checkHandler: function (item, checked) {
                            if (checked) {
                                this.filterByPlayer();
                            } else {
                                this.removeFilterProperty('winner', 1005, true);
                            }
                        }
                    }
                ]
            });
        }
        return this._filterAction;
    },

    getColumnModel: function () {
        if (!this._columnModel) {

            var dateRenderer = Ext.util.Format.dateRenderer('d/m/Y H:i');

            this._columnModel = Ext._create('Ext.grid.ColumnModel', [
                Ext._create('Ext.grid.RowNumberer'),
                { header: 'Cod.', dataIndex: 'pk', width: 50, hidden: true },
                { header: 'Descrição', dataIndex: 'unicode', id: 'autoExpandColumn', hidden: true },
                { header: 'Título', dataIndex: 'title', width: 250 },
                { header: 'Número Externo', dataIndex: 'external_number', width: 170 },
                { header: 'Escolhido', dataIndex: 'winner_unicode', width: 125 },
                {
                    header: 'Método de Distribuição',
                    dataIndex: 'distributed_manually',
                    width: 160,
                    renderer: function (value, metaData, record, rowIndex, colIndex, store) {
                        if (record.data.winner === null) {
                            return '';
                        }

                        var display = (value ? 'MANUAL' : 'POR SORTEIO');

                        if (record.data.canceled_at !== null) {
                            display += ' <span style="color: red;">(CANCELADO)</span>';
                        }

                        return display;
                    }
                },
                { header: 'Distribuído em', dataIndex: 'distributed_at', width: 150, renderer: dateRenderer, hidden: true },
                { header: 'Distribuído por', dataIndex: 'distributed_by_unicode', width: 150 },
                { header: 'Cancelado em', dataIndex: 'canceled_at', width: 150, renderer: dateRenderer, hidden: true },
                { header: 'Cancelado por', dataIndex: 'canceled_by_unicode', width: 150, hidden: true },
                { header: 'Distribuição', dataIndex: 'distribution_unicode', width: 150, hidden: true },
                { header: 'Modificado em', dataIndex: 'modified_at', width: 150, renderer: dateRenderer, hidden: true },
                { header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 150, hidden: true },
                { header: 'Criado em', dataIndex: 'created_at', width: 150, renderer: dateRenderer, hidden: true },
                { header: 'Criado por', dataIndex: 'created_by_unicode', width: 150, hidden: true }
            ]);
        }
        return this._columnModel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            keywordFieldWidth: 200,
        });

        common.distribution.reward.Grid.superclass.constructor.call(this, cfg);

        //this.filterByDistribution(cfg.initialByDistributionType || 2);
    }
});

core.RestfulGrid.register(
    'common.distribution.reward.Restful',
    'common.distribution.reward.Grid'
);
